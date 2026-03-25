from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db, redis_client
from app.models.url import URL, Click
from app.schemas.url import URLCreate, URLResponse, ClickResponse, AnalyticsResponse
from app.core.utils import generate_short_code, parse_user_agent

router = APIRouter()

BASE_URL = "http://localhost:8000"


@router.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    """Create a shortened URL with optional custom alias and expiry."""

    # Use custom alias or generate short code
    short_code = payload.custom_alias or generate_short_code()

    # Check if short code already exists
    existing = db.query(URL).filter(
        (URL.short_code == short_code) | (URL.custom_alias == short_code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alias or short code already taken")

    url = URL(
        original_url=str(payload.original_url),
        short_code=short_code,
        custom_alias=payload.custom_alias,
        expires_at=payload.expires_at
    )
    db.add(url)
    db.commit()
    db.refresh(url)

    # Cache in Redis (TTL: 24 hours)
    try:
        redis_client.setex(short_code, 86400, str(payload.original_url))
    except Exception as e:
        # Log but don't fail the request if Redis caching fails
        print(f"Redis cache error: {e}")
        pass

    return URLResponse(
        short_code=url.short_code,
        short_url=f"{BASE_URL}/{short_code}",
        original_url=url.original_url,
        custom_alias=url.custom_alias,
        expires_at=url.expires_at,
        created_at=url.created_at
    )


@router.get("/{short_code}")
def redirect_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Redirect to original URL and track click analytics."""

    # Check Redis cache first
    cached_url = None
    try:
        cached_url = redis_client.get(short_code)
    except Exception as e:
        # Log but continue if Redis is unavailable
        print(f"Redis get error: {e}")
        pass

    if cached_url:
        original_url = cached_url
    else:
        # Fallback to DB
        url_obj = db.query(URL).filter(
            (URL.short_code == short_code) | (URL.custom_alias == short_code),
            URL.is_active == True
        ).first()

        if not url_obj:
            raise HTTPException(status_code=404, detail="Short URL not found")

        # Check expiry
        if url_obj.expires_at and url_obj.expires_at < datetime.utcnow():
            raise HTTPException(status_code=410, detail="This URL has expired")

        original_url = url_obj.original_url
        # Re-cache
        try:
            redis_client.setex(short_code, 86400, original_url)
        except Exception as e:
            print(f"Redis setex error: {e}")
            pass

    # Track click
    url_obj = db.query(URL).filter(URL.short_code == short_code).first()
    if url_obj:
        ua_info = parse_user_agent(request.headers.get("user-agent", ""))
        click = Click(
            url_id=url_obj.id,
            device_type=ua_info["device_type"],
            browser=ua_info["browser"],
            referrer=request.headers.get("referer"),
            ip_address=request.client.host
        )
        db.add(click)
        db.commit()

    return RedirectResponse(url=original_url, status_code=302)
