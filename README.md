# LinkSnap — URL Shortener & Analytics API

A production-ready REST API for shortening URLs with real-time click analytics, Redis caching, and Docker support.

## Features

- Shorten any URL with auto-generated or custom alias
- Set expiry dates on short URLs
- Track clicks with device type, browser, and referrer
- Redis caching for fast redirects
- Fully containerized with Docker Compose

## Tech Stack

`Python` `FastAPI` `PostgreSQL` `Redis` `Docker` `SQLAlchemy`

## Project Structure

```
linksnap/
├── app/
│   ├── core/
│   │   ├── database.py       # DB + Redis config
│   │   └── utils.py          # Short code generator, UA parser
│   ├── models/
│   │   └── url.py            # URL and Click models
│   ├── routers/
│   │   ├── url.py            # Shorten + Redirect endpoints
│   │   └── analytics.py      # Analytics endpoint
│   ├── schemas/
│   │   └── url.py            # Pydantic schemas
│   └── main.py               # FastAPI app entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites
- Docker & Docker Compose installed

### Run with Docker

```bash
git clone https://github.com/yourusername/linksnap.git
cd linksnap
cp .env.example .env
docker-compose up --build
```

API will be available at `http://localhost:8000`

### API Docs
Visit `http://localhost:8000/docs` for interactive Swagger UI.

## API Endpoints

### Shorten a URL
```http
POST /shorten
Content-Type: application/json

{
  "original_url": "https://www.example.com/very/long/url",
  "custom_alias": "mylink",        // optional
  "expires_at": "2025-12-31T00:00:00"  // optional
}
```

**Response:**
```json
{
  "short_code": "mylink",
  "short_url": "http://localhost:8000/mylink",
  "original_url": "https://www.example.com/very/long/url",
  "created_at": "2025-01-15T10:00:00"
}
```

### Redirect
```http
GET /{short_code}
```
Redirects to the original URL and tracks the click.

### Get Analytics
Use this endpoint (preferred) for click reports:
```http
GET /analytics/{short_code}
```

> Note: `GET /{short_code}/analytics` is redundant and removed in this version.

**Response:**
```json
{
  "short_code": "mylink",
  "original_url": "https://www.example.com/very/long/url",
  "total_clicks": 42,
  "clicks": [
    {
      "clicked_at": "2025-01-15T10:05:00",
      "device_type": "Desktop",
      "browser": "Chrome",
      "referrer": "https://google.com"
    }
  ]
}
```

## Author

**Swapnil Chitalkar**
[LinkedIn](https://www.linkedin.com/in/swapnil-chitalkar)
