import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
from redis.connection import ConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/linksnap")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # Add connection pool options for psycopg2
    database_url_with_options = DATABASE_URL + "?connect_timeout=10&application_name=linksnap"
    # Database engine with connection pool
    engine = create_engine(
        database_url_with_options,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=False,
        pool_recycle=3600,
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"
        }
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis connection pool
redis_pool = ConnectionPool(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    },
    max_connections=10,
    retry_on_timeout=True
)

redis_client = Redis(connection_pool=redis_pool)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
