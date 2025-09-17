# Environment Variables Guide

This document describes all environment variables used in the Quote of the Day application.

## 📁 Configuration Files

Environment variables are managed through the following files:

- **`.env`** - Root-level API configuration
- **`apps/mobile/.env.local`** - Mobile app configuration
- **`infrastructure/aws/.env`** - AWS deployment configuration

## 🔧 API Configuration (`.env`)

### General Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | Yes | `development` | Application environment (`development`, `staging`, `production`) |
| `DEBUG` | No | `true` | Enable debug mode |
| `LOG_LEVEL` | No | `info` | Logging level (`debug`, `info`, `warning`, `error`) |

### API Server Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_HOST` | No | `0.0.0.0` | API server host |
| `API_PORT` | No | `8000` | API server port |
| `SECRET_KEY` | Yes | - | JWT signing secret (use strong random key) |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token expiration time |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection URL |
| `DATABASE_HOST` | No | `localhost` | Database host |
| `DATABASE_PORT` | No | `5432` | Database port |
| `DATABASE_NAME` | No | `quote_of_the_day_dev` | Database name |
| `DATABASE_USER` | No | `quote_user` | Database username |
| `DATABASE_PASSWORD` | No | `quote_password` | Database password |
| `DATABASE_POOL_SIZE` | No | `10` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | No | `20` | Max pool overflow |

### Redis Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | Yes | - | Redis connection URL |
| `REDIS_HOST` | No | `localhost` | Redis host |
| `REDIS_PORT` | No | `6379` | Redis port |
| `REDIS_DB` | No | `0` | Redis database number |
| `REDIS_PASSWORD` | No | - | Redis password |

### Security Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ALLOWED_ORIGINS` | No | `["http://localhost:3000"]` | CORS allowed origins (JSON array) |
| `ALLOWED_HOSTS` | No | `["localhost"]` | Trusted hosts (JSON array) |

### Firebase Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIREBASE_PROJECT_ID` | Yes | - | Firebase project ID |
| `FIREBASE_ADMIN_CREDENTIALS_PATH` | Yes | - | Path to Firebase admin credentials JSON |
| `FCM_SERVER_KEY` | No | - | Firebase Cloud Messaging server key |

### AWS Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | No | `us-east-1` | AWS region |
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key (use IAM roles in production) |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret key (use IAM roles in production) |
| `AWS_S3_BUCKET` | No | - | S3 bucket for file storage |
| `AWS_CLOUDFRONT_DOMAIN` | No | - | CloudFront domain for CDN |

### Email Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SES_EMAIL_FROM` | No | - | SES sender email address |
| `SES_REGION` | No | `us-east-1` | SES region |

### Payment Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | No | - | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | No | - | Stripe webhook secret |

### Monitoring Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | - | Sentry DSN for error tracking |
| `CLOUDWATCH_LOG_GROUP` | No | - | CloudWatch log group name |
| `CLOUDWATCH_LOG_STREAM` | No | - | CloudWatch log stream name |

### Development Features

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_SWAGGER_UI` | No | `true` | Enable Swagger UI |
| `ENABLE_REDOC` | No | `true` | Enable ReDoc |
| `ENABLE_DEBUG_TOOLBAR` | No | `true` | Enable debug toolbar |

### Test Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TEST_DATABASE_URL` | No | - | Test database URL (for CI/CD) |

## 📱 Mobile Configuration (`apps/mobile/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLUTTER_APP_ENV` | Yes | `development` | App environment |
| `API_BASE_URL` | Yes | `http://localhost:8000` | API base URL |
| `FIREBASE_PROJECT_ID` | Yes | - | Firebase project ID |
| `FIREBASE_API_KEY` | Yes | - | Firebase web API key |
| `FIREBASE_AUTH_DOMAIN` | Yes | - | Firebase auth domain |
| `FIREBASE_STORAGE_BUCKET` | Yes | - | Firebase storage bucket |
| `FIREBASE_MESSAGING_SENDER_ID` | Yes | - | FCM sender ID |
| `FIREBASE_APP_ID` | Yes | - | Firebase app ID |
| `SENTRY_DSN` | No | - | Sentry DSN for error tracking |
| `STRIPE_PUBLISHABLE_KEY` | No | - | Stripe publishable key |

## 🏗️ Environment-Specific Configurations

### Development Environment

```bash
# .env for development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Local database
DATABASE_URL=postgresql://quote_user:quote_password@localhost:5432/quote_of_the_day_dev
REDIS_URL=redis://localhost:6379/0

# Relaxed security for development
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
ALLOWED_HOSTS=["localhost", "127.0.0.1", "*"]

# Development features enabled
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
ENABLE_DEBUG_TOOLBAR=true
```

### Staging Environment

```bash
# .env for staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=info

# Staging database (managed by CDK)
DATABASE_URL=postgresql://username:password@staging-db.region.rds.amazonaws.com:5432/quote_db
REDIS_URL=redis://staging-redis.region.cache.amazonaws.com:6379/0

# Production-like security
ALLOWED_ORIGINS=["https://staging.quoteapp.com"]
ALLOWED_HOSTS=["staging.quoteapp.com"]

# Monitoring enabled
SENTRY_DSN=https://your-staging-sentry-dsn@sentry.io/project-id
CLOUDWATCH_LOG_GROUP=/quote-of-the-day/staging/api

# Limited development features
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
ENABLE_DEBUG_TOOLBAR=false
```

### Production Environment

```bash
# .env for production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning

# Production database (managed by CDK)
DATABASE_URL=postgresql://username:password@prod-db.region.rds.amazonaws.com:5432/quote_db
REDIS_URL=redis://prod-redis.region.cache.amazonaws.com:6379/0

# Strict security
ALLOWED_ORIGINS=["https://quoteapp.com", "https://www.quoteapp.com"]
ALLOWED_HOSTS=["quoteapp.com", "www.quoteapp.com"]

# Full monitoring
SENTRY_DSN=https://your-production-sentry-dsn@sentry.io/project-id
CLOUDWATCH_LOG_GROUP=/quote-of-the-day/production/api

# Development features disabled
ENABLE_SWAGGER_UI=false
ENABLE_REDOC=false
ENABLE_DEBUG_TOOLBAR=false
```

## 🔐 Security Best Practices

### Secret Management

1. **Never commit secrets** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate secrets regularly** in production
4. **Use IAM roles** instead of access keys in AWS
5. **Encrypt secrets at rest** using AWS Secrets Manager

### Secret Generation

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate a UUID
python -c "import uuid; print(uuid.uuid4())"

# Generate a random password
openssl rand -base64 32
```

### Environment Validation

The application validates required environment variables at startup:

```python
# Required variables are checked
required_vars = ['DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 'FIREBASE_PROJECT_ID']

# Missing variables cause startup failure
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} not set")
```

## 🚀 Deployment Configuration

### GitHub Actions Secrets

Set these secrets in your GitHub repository for CI/CD:

```bash
# AWS Deployment
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# Container Registry
AWS_ECR_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com

# Environment-specific secrets
STAGING_CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/staging-cert-id
PRODUCTION_CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/prod-cert-id

# Optional: Third-party integrations
SENTRY_AUTH_TOKEN=your-sentry-auth-token
STRIPE_API_KEY=your-stripe-api-key
```

### CDK Context

The AWS CDK uses context for environment-specific configuration:

```bash
# Deploy to staging
cdk deploy --context environment=staging

# Deploy to production
cdk deploy --context environment=production
```

## 🧪 Testing Configuration

### Test Environment Variables

```bash
# Test-specific .env.test
ENVIRONMENT=test
DATABASE_URL=postgresql://test_user:test_password@localhost:5432/quote_test_db
REDIS_URL=redis://localhost:6379/1

# Use different database/cache for tests
TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5432/quote_test_db
```

### CI/CD Test Configuration

GitHub Actions automatically provides test services:

```yaml
# .github/workflows/ci.yaml
services:
  postgres:
    image: postgres:17.6
    env:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: quote_test_db

  redis:
    image: redis:8.2.1-alpine
```

## 🔍 Environment Variable Validation

The application includes built-in validation:

```python
# Example validation in src/core/config.py
class Settings(BaseSettings):
    # Required fields will raise validation errors
    DATABASE_URL: str
    SECRET_KEY: str

    # Optional with defaults
    DEBUG: bool = False
    LOG_LEVEL: str = "info"

    # Validated formats
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Custom validation
    @validator("SECRET_KEY")
    def secret_key_strength(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

## 📋 Environment Checklist

Before running the application, ensure:

- [ ] All required variables are set
- [ ] Database connection works
- [ ] Redis connection works
- [ ] Firebase credentials are valid
- [ ] AWS credentials are configured (if needed)
- [ ] Secrets are secure and not committed
- [ ] Environment-specific values are correct

## 🆘 Troubleshooting

### Common Issues

1. **Missing required variables**: Check the validation errors at startup
2. **Database connection failed**: Verify DATABASE_URL and service status
3. **Redis connection failed**: Check REDIS_URL and Redis service
4. **Firebase auth failed**: Verify Firebase credentials and project setup
5. **AWS access denied**: Check AWS credentials and permissions

### Debug Commands

```bash
# Check environment variables
env | grep -E "(DATABASE|REDIS|FIREBASE)"

# Test database connection
python -c "from src.core.database import db_manager; import asyncio; asyncio.run(db_manager.get_session().__anext__())"

# Test Redis connection
python -c "from src.core.cache import cache_manager; import asyncio; print(asyncio.run(cache_manager.ping()))"
```

---

For questions about environment configuration, check the [troubleshooting guide](troubleshooting.md) or open an issue.