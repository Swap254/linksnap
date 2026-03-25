from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.routers import url, analytics
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LinkSnap API",
    description="A production-ready URL shortener with click analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url.router, tags=["URL"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "LinkSnap API is running"}
