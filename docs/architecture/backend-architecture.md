# Backend Architecture

FastAPI-based backend architecture with hybrid serverless approach, emphasizing async performance, subscription management, and reliable notification delivery.

## Service Architecture

The backend employs a **hybrid serverless architecture** combining the reliability of containerized FastAPI services with the scalability of Lambda functions for critical notification delivery.

### FastAPI Monolith Structure
```
apps/api/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py             # Environment configuration
│   │   ├── database.py           # SQLAlchemy setup and connection
│   │   ├── security.py           # JWT and authentication utilities
│   │   └── middleware.py         # CORS, logging, rate limiting
│   ├── api/
│   │   ├── deps.py               # Dependency injection for routes
│   │   └── v1/
│   │       ├── auth.py           # Authentication endpoints
│   │       ├── quotes.py         # Quote management endpoints
│   │       ├── users.py          # User profile management
│   │       ├── subscriptions.py  # Premium subscription handling
│   │       └── webhooks.py       # Stripe webhook processing
│   ├── services/
│   │   ├── auth_service.py       # Business logic for authentication
│   │   ├── quote_service.py      # Quote selection and curation
│   │   ├── subscription_service.py # Stripe integration and billing
│   │   ├── notification_service.py # FCM integration helpers
│   │   └── analytics_service.py  # Event tracking and A/B testing
│   ├── repositories/
│   │   ├── base.py               # Base repository with common operations
│   │   ├── user_repository.py    # User data access layer
│   │   ├── quote_repository.py   # Quote data access with search
│   │   └── subscription_repository.py # Subscription data management
│   ├── models/
│   │   ├── database/             # SQLAlchemy ORM models
│   │   └── schemas/              # Pydantic request/response models
│   ├── utils/
│   │   ├── email.py              # SES email utilities
│   │   ├── cache.py              # Redis caching helpers
│   │   └── validators.py         # Custom validation logic
│   └── tests/
│       ├── conftest.py           # Pytest configuration and fixtures
│       ├── test_auth.py          # Authentication endpoint tests
│       ├── test_quotes.py        # Quote functionality tests
│       └── test_subscriptions.py # Payment and subscription tests
├── lambda_functions/
│   ├── notification_delivery/    # Daily quote delivery Lambda
│   ├── webhook_processor/        # Stripe webhook Lambda
│   └── analytics_processor/      # Batch analytics Lambda
└── infrastructure/
    ├── docker/                   # Containerization configs
    ├── ecs/                      # ECS task definitions
    └── lambda/                   # Lambda deployment packages
```

### FastAPI Application Template
```python
# Main FastAPI application setup with comprehensive middleware
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from core.config import get_settings
from core.database import engine
from core.middleware import LoggingMiddleware, AuthenticationMiddleware
from api.v1 import auth, quotes, users, subscriptions, webhooks

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
settings = get_settings()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

def create_application() -> FastAPI:
    app = FastAPI(
        title="Quote of the Day API",
        version="1.0.0",
        description="Premium quote delivery service for intelligent professionals",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Security middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthenticationMiddleware)

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    # API routes
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["quotes"])
    app.include_router(users.router, prefix="/api/v1/user", tags=["users"])
    app.include_router(subscriptions.router, prefix="/api/v1/subscription", tags=["subscriptions"])
    app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

    return app

app = create_application()

# Global exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error("HTTP exception occurred",
                status_code=exc.status_code,
                detail=exc.detail,
                path=request.url.path)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request.state.request_id,
            }
        }
    )
```

## Database Architecture

SQLAlchemy-based data access layer with repository pattern, connection pooling, and query optimization for quote search and user management.

### Database Connection Management
```python
# Core database configuration with connection pooling
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog

from core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# SQLAlchemy engine with optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency for FastAPI
async def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Connection event logging
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DEBUG:
        logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    if settings.DEBUG:
        logger.debug("Database connection checked out from pool")
```

### Repository Pattern Implementation
```python
# Base repository with common CRUD operations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = jsonable_encoder(obj_in)
        for field, value in obj_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: Any) -> Optional[ModelType]:
        obj = self.db.query(self.model).get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj

# Quote repository with advanced search capabilities
class QuoteRepository(BaseRepository[Quote, QuoteCreate, QuoteUpdate]):
    def __init__(self, db: Session):
        super().__init__(Quote, db)

    def search_quotes(
        self,
        *,
        query: str,
        category: Optional[QuoteCategory] = None,
        user_id: Optional[str] = None,
        starred_only: bool = False,
        skip: int = 0,
        limit: int = 20
    ) -> List[Quote]:
        """Full-text search with optional filtering"""
        base_query = self.db.query(Quote).filter(Quote.is_active == True)

        # Full-text search using PostgreSQL tsvector
        if query:
            base_query = base_query.filter(
                Quote.search_vector.match(query)
            ).order_by(
                desc(func.ts_rank(Quote.search_vector, func.plainto_tsquery(query)))
            )

        # Category filtering
        if category:
            base_query = base_query.filter(Quote.category == category)

        # User-specific filtering for starred quotes
        if user_id:
            if starred_only:
                base_query = base_query.join(UserQuoteHistory).filter(
                    and_(
                        UserQuoteHistory.user_id == user_id,
                        UserQuoteHistory.starred_at.is_not(None)
                    )
                )
            else:
                # Left join to include star status
                base_query = base_query.outerjoin(
                    UserQuoteHistory,
                    and_(
                        UserQuoteHistory.quote_id == Quote.id,
                        UserQuoteHistory.user_id == user_id
                    )
                )

        return base_query.offset(skip).limit(limit).all()

    def get_undelivered_quotes_for_user(self, user_id: str, limit: int = 50) -> List[Quote]:
        """Get quotes not yet delivered to specific user"""
        subquery = self.db.query(UserQuoteHistory.quote_id).filter(
            UserQuoteHistory.user_id == user_id
        ).subquery()

        return self.db.query(Quote).filter(
            and_(
                Quote.is_active == True,
                ~Quote.id.in_(subquery)
            )
        ).order_by(func.random()).limit(limit).all()

    def get_quote_performance_metrics(self, quote_id: str) -> Dict[str, Any]:
        """Analytics for quote engagement"""
        metrics = self.db.query(
            func.count(UserQuoteHistory.id).label('total_deliveries'),
            func.count(UserQuoteHistory.viewed_at).label('views'),
            func.count(UserQuoteHistory.starred_at).label('stars'),
            func.avg(UserQuoteHistory.engagement_score).label('avg_engagement')
        ).filter(UserQuoteHistory.quote_id == quote_id).first()

        return {
            'total_deliveries': metrics.total_deliveries or 0,
            'views': metrics.views or 0,
            'stars': metrics.stars or 0,
            'avg_engagement': float(metrics.avg_engagement or 0),
            'view_rate': metrics.views / max(metrics.total_deliveries, 1),
            'star_rate': metrics.stars / max(metrics.views, 1),
        }
```

## Authentication and Authorization

JWT-based authentication with Firebase integration, role-based access control, and subscription-based feature gating.

### Authentication Flow Implementation
```python
# JWT and Firebase Auth integration
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth
from jose import JWTError, jwt
from datetime import datetime, timedelta
import structlog

from core.config import get_settings
from models.database.user import User
from repositories.user_repository import UserRepository

logger = structlog.get_logger(__name__)
settings = get_settings()
security = HTTPBearer()

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_access_token(self, user_id: str, email: str) -> str:
        """Generate JWT access token for API authentication"""
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def verify_firebase_token(self, token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and extract user info"""
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False)
            }
        except Exception as e:
            logger.error("Firebase token verification failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> User:
        """Extract current user from JWT token"""
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = self.user_repo.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account deactivated"
            )

        return user

# Dependency for premium feature access control
async def require_premium_subscription(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency that requires active premium subscription"""
    if current_user.subscription_tier != SubscriptionTier.PREMIUM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )

    # Additional check for subscription status
    if hasattr(current_user, 'subscription') and current_user.subscription:
        if current_user.subscription.status != 'ACTIVE':
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription payment required"
            )

    return current_user

# Rate limiting decorator for sensitive endpoints
def rate_limit(requests: int, window: int):
    def decorator(func):
        @limiter.limit(f"{requests}/{window}seconds")
        async def wrapper(request: Request, *args, **kwargs):
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Subscription-Based Middleware
```python
# Middleware for automatic subscription status checking
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class SubscriptionMiddleware(BaseHTTPMiddleware):
    """Middleware to check subscription status for premium endpoints"""

    PREMIUM_ENDPOINTS = {
        "/api/v1/quotes/search",
        "/api/v1/analytics/advanced",
        "/api/v1/quotes/export"
    }

    async def dispatch(self, request, call_next):
        # Check if this is a premium endpoint
        if request.url.path in self.PREMIUM_ENDPOINTS:
            # Extract user from JWT token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"error": {"code": "UNAUTHORIZED", "message": "Authentication required"}}
                )

            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = payload.get("sub")

                # Check subscription status from cache first
                cache_key = f"user_subscription:{user_id}"
                cached_tier = await redis_client.get(cache_key)

                if cached_tier != "PREMIUM":
                    # Verify from database
                    async with database.transaction():
                        user = await user_repo.get_with_subscription(user_id)
                        if not user or user.subscription_tier != "PREMIUM":
                            return JSONResponse(
                                status_code=403,
                                content={
                                    "error": {
                                        "code": "PREMIUM_REQUIRED",
                                        "message": "Premium subscription required for this feature"
                                    }
                                }
                            )

                        # Cache the result
                        await redis_client.setex(cache_key, 300, "PREMIUM")  # 5 min cache

            except JWTError:
                return JSONResponse(
                    status_code=401,
                    content={"error": {"code": "INVALID_TOKEN", "message": "Invalid authentication token"}}
                )

        response = await call_next(request)
        return response
```
