from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    custom_alias: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ClickResponse(BaseModel):
    id: int
    clicked_at: datetime
    device_type: Optional[str]
    browser: Optional[str]
    referrer: Optional[str]

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    clicks: list[ClickResponse]
