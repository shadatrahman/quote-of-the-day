# Quote of the Day

A personalized Quote of the Day mobile application with subscription tiers, built with Flutter and FastAPI.

## 📱 Project Overview

Quote of the Day delivers personalized, motivational quotes to users through a beautiful mobile application. The platform features multiple subscription tiers, smart quote curation, and seamless cross-platform synchronization.

### Key Features

- 🎯 **Personalized Quotes** - AI-powered quote recommendations based on user preferences
- 📱 **Cross-Platform Mobile App** - Built with Flutter for iOS and Android
- ⚡ **Real-time Notifications** - Daily quote delivery via push notifications and email
- 💎 **Subscription Tiers** - Free, Premium, and Enterprise plans with different features
- 🔒 **Secure Authentication** - Firebase Auth integration with JWT tokens
- 📊 **Analytics & Insights** - User engagement tracking and quote performance metrics
- 🌩️ **Cloud Infrastructure** - Scalable AWS-based architecture
- 🔍 **Smart Search** - Advanced quote search with filters and categories

## 🏗️ Architecture

This is a full-stack monorepo with the following structure:

```
quote-of-the-day/
├── apps/
│   ├── mobile/          # Flutter mobile application
│   └── api/             # FastAPI backend service
├── packages/
│   ├── shared-types/    # Shared TypeScript types
│   └── ui-components/   # Reusable Flutter UI components
├── infrastructure/
│   └── aws/             # AWS CDK infrastructure definitions
├── scripts/             # Build and deployment scripts
├── docs/                # Project documentation
└── .github/workflows/   # CI/CD pipelines
```

### Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Frontend** | Flutter 3.32.8 | Cross-platform mobile development |
| **Backend** | FastAPI 0.116.2 | High-performance REST API |
| **Database** | PostgreSQL 17.6 | Primary data storage |
| **Cache** | Redis 8.2.1 | Session storage and caching |
| **Infrastructure** | AWS CDK 2.100.0 | Infrastructure as code |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | CloudWatch + Sentry | Application monitoring and error tracking |
| **Authentication** | Firebase Auth + JWT | User authentication and authorization |

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18.0+
- **Python** 3.13+
- **Flutter** 3.32.8+
- **Docker** 24.0+
- **AWS CLI** v2 (for deployment)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourorg/quote-of-the-day.git
cd quote-of-the-day

# Install all dependencies
npm run install:all
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your configuration
# See docs/development/environment-variables.md for details
```

### 3. Start Development Services

```bash
# Start PostgreSQL and Redis
npm run dev:services

# Start the API server
npm run dev:api

# Start the mobile app (in a new terminal)
npm run dev:mobile
```

### 4. Database Setup

```bash
# Run database migrations
npm run db:migrate

# Seed with sample data
npm run db:seed
```

🎉 **You're ready!** The API will be running at `http://localhost:8000` and the mobile app will launch in your device/simulator.

## 📚 Documentation

- [Getting Started Guide](docs/development/getting-started.md) - Detailed setup instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Architecture Overview](docs/architecture/) - System design and patterns
- [Deployment Guide](docs/deployment/) - Production deployment instructions
- [Contributing Guidelines](docs/development/contributing.md) - How to contribute

## 🛠️ Development Commands

### Root Level Commands

```bash
# Development
npm run dev              # Start all services
npm run dev:services     # Start only database services
npm run dev:api         # Start API server
npm run dev:mobile      # Start mobile app

# Testing
npm run test            # Run all tests
npm run test:api        # Run API tests
npm run test:mobile     # Run mobile tests

# Database
npm run db:migrate      # Run database migrations
npm run db:seed         # Seed database
npm run db:reset        # Reset database
npm run db:shell        # Access database shell

# Linting & Formatting
npm run lint            # Lint all code
npm run format          # Format all code
npm run clean           # Clean all build artifacts

# Deployment
npm run deploy:staging  # Deploy to staging
npm run deploy:prod     # Deploy to production
```

### Mobile App Commands

```bash
cd apps/mobile

flutter pub get         # Install dependencies
flutter test           # Run tests
flutter build apk      # Build Android APK
flutter build ios      # Build iOS app
flutter analyze        # Analyze code
```

### API Commands

```bash
cd apps/api

# Development
python -m uvicorn src.main:app --reload

# Testing
pytest tests/ -v --cov=src

# Database
alembic upgrade head    # Run migrations
alembic revision --autogenerate -m "message"  # Create migration

# Linting
ruff check .
mypy src/
```

## 🐳 Docker Development

```bash
# Full stack with Docker
npm run dev:full-stack

# With development tools (Adminer, Redis Commander)
npm run dev:tools

# View logs
npm run logs
npm run logs:api
npm run logs:db
```

## 📦 Project Structure

### Mobile App (`apps/mobile/`)

```
lib/
├── core/              # Core utilities and configuration
├── features/          # Feature-based modules
│   ├── auth/         # Authentication
│   ├── quotes/       # Quote management
│   ├── profile/      # User profile
│   └── settings/     # App settings
├── shared/           # Shared widgets and utilities
└── main.dart         # App entry point
```

### API (`apps/api/`)

```
src/
├── core/             # Core configuration and utilities
├── api/              # API route definitions
├── models/           # Database models
├── services/         # Business logic services
├── repositories/     # Data access layer
└── main.py           # FastAPI entry point
```

## 🔧 Configuration

### Environment Variables

Key environment variables for development:

```bash
# API Configuration
DATABASE_URL=postgresql://quote_user:quote_password@localhost:5432/quote_of_the_day_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key

# AWS (for deployment)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

See [Environment Variables Guide](docs/development/environment-variables.md) for complete documentation.

## 🧪 Testing

### Running Tests

```bash
# All tests
npm run test

# API tests with coverage
cd apps/api && pytest tests/ -v --cov=src --cov-report=html

# Mobile tests with coverage
cd apps/mobile && flutter test --coverage

# Integration tests
npm run test:integration
```

### Test Structure

- **API Tests**: `apps/api/tests/` - Unit, integration, and E2E tests
- **Mobile Tests**: `apps/mobile/test/` - Widget, unit, and integration tests
- **E2E Tests**: End-to-end tests using Patrol framework

## 📊 Monitoring & Logging

### Development

- **API Logs**: Structured JSON logging to console
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics` (development only)

### Production

- **CloudWatch**: Infrastructure and application metrics
- **Sentry**: Error tracking and performance monitoring
- **Structured Logging**: JSON logs to CloudWatch Logs

## 🚀 Deployment

### Environments

- **Development**: Local development with Docker services
- **Staging**: AWS staging environment for testing
- **Production**: AWS production environment

### Deployment Process

1. **Push to `develop`** → Triggers staging deployment
2. **Create release tag** → Triggers production deployment
3. **Manual deployment** → Use GitHub Actions workflow dispatch

See [Deployment Guide](docs/deployment/) for detailed instructions.

## 🔐 Security

- **Authentication**: Firebase Auth with JWT tokens
- **Authorization**: Role-based access control
- **API Security**: Rate limiting, CORS, trusted hosts
- **Data Protection**: Encrypted sensitive data, secure headers
- **Infrastructure**: VPC isolation, security groups, WAF

## 📈 Performance

- **API**: FastAPI with async/await, connection pooling
- **Database**: PostgreSQL with read replicas (production)
- **Cache**: Redis for session storage and query caching
- **CDN**: CloudFront for static assets
- **Monitoring**: Real-time performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

See [Contributing Guidelines](docs/development/contributing.md) for detailed instructions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourorg/quote-of-the-day/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/yourorg/quote-of-the-day/discussions)

## 📋 Roadmap

- [ ] Advanced quote personalization with ML
- [ ] Social features (sharing, favorites)
- [ ] Offline mode support
- [ ] Widget support for mobile home screens
- [ ] Integration with calendar apps
- [ ] Multi-language support

---

Built with ❤️ by the Quote of the Day Team