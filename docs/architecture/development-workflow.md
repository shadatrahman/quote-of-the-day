# Development Workflow

## Local Development Setup

### Prerequisites

```bash
# Required software versions
flutter --version    # Flutter 3.16.0 or higher
python --version     # Python 3.11 or higher
node --version       # Node.js 18.0 or higher
docker --version     # Docker 24.0 or higher
aws --version        # AWS CLI v2

# Development tools
git --version
make --version       # For build automation
melos --version      # Dart monorepo management
```

### Initial Setup

```bash
# Clone repository and navigate to project
git clone https://github.com/company/quote-of-the-day.git
cd quote-of-the-day

# Install root dependencies and configure workspaces
npm install

# Install Flutter dependencies using Melos
melos bootstrap

# Setup Python environment for API
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your local configuration values

# Initialize local database
docker-compose up -d postgres redis
cd apps/api && alembic upgrade head

# Seed database with sample quotes
python scripts/seed_database.py

# Setup Firebase configuration for mobile
cd apps/mobile
# Download and place google-services.json (Android) and GoogleService-Info.plist (iOS)
# from Firebase Console
```

### Development Commands

```bash
# Start all services in development mode
npm run dev
# This runs:
# - FastAPI server with hot reload on :8000
# - Flutter mobile app with hot reload
# - PostgreSQL and Redis containers
# - File watchers for shared packages

# Start individual services
npm run dev:api          # Start FastAPI backend only
npm run dev:mobile       # Start Flutter mobile app only
npm run dev:db           # Start database services only

# Database operations
npm run db:migrate       # Run latest migrations
npm run db:seed          # Seed with sample data
npm run db:reset         # Reset database and reseed

# Testing commands
npm run test            # Run all tests
npm run test:api        # Run FastAPI tests with pytest
npm run test:mobile     # Run Flutter unit and widget tests
npm run test:e2e        # Run end-to-end tests with Patrol

# Code quality checks
npm run lint            # Run linters for all packages
npm run format          # Format code using Prettier and dart format
npm run type-check      # Run TypeScript and Dart analysis

# Build commands (mobile apps deployed manually to stores)
npm run build           # Build API for production
npm run build:api       # Build API Docker image
```

## Environment Configuration

### Required Environment Variables

```bash
# Frontend (.env.local for apps/mobile)
FLUTTER_APP_ENV=development
API_BASE_URL=http://localhost:8000/api/v1
FIREBASE_PROJECT_ID=quote-of-the-day-dev
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=quote-of-the-day-dev.firebaseapp.com
SENTRY_DSN=your_sentry_dsn_for_flutter
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Backend (.env for apps/api)
DATABASE_URL=postgresql://user:password@localhost:5432/quote_of_the_day_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_super_secret_jwt_key_min_32_chars
FIREBASE_ADMIN_CREDENTIALS_PATH=/path/to/firebase-admin-key.json
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
SES_EMAIL_FROM=noreply@quoteoftheday.com
FCM_SERVER_KEY=your_fcm_server_key
SENTRY_DSN=your_sentry_dsn_for_python
DEBUG=true
ENVIRONMENT=development

# Shared (for both frontend and backend)
APP_NAME=Quote of the Day
APP_VERSION=1.0.0
SUPPORT_EMAIL=support@quoteoftheday.com
PRIVACY_POLICY_URL=https://quoteoftheday.com/privacy
TERMS_OF_SERVICE_URL=https://quoteoftheday.com/terms
```
