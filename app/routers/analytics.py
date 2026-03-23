from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.url import URL, Click
from app.schemas.url import AnalyticsResponse, ClickResponse

router = APIRouter()


@router.get("/{short_code}", response_model=AnalyticsResponse)
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    """Get click analytics for a shortened URL."""

    url_obj = db.query(URL).filter(
        (URL.short_code == short_code) | (URL.custom_alias == short_code)
    ).first()

    if not url_obj:
        raise HTTPException(status_code=404, detail="Short URL not found")

    clicks = db.query(Click).filter(Click.url_id == url_obj.id).all()

    return AnalyticsResponse(
        short_code=url_obj.short_code,
        original_url=url_obj.original_url,
        total_clicks=len(clicks),
        clicks=[
            ClickResponse(
                id=c.id,
                clicked_at=c.clicked_at,
                device_type=c.device_type,
                browser=c.browser,
                referrer=c.referrer
            ) for c in clicks
        ]
    )
