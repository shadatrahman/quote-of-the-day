# Unified Project Structure

Monorepo structure accommodating Flutter mobile app, FastAPI backend, shared types, Lambda functions, and infrastructure-as-code for the Quote of the Day application.

```plaintext
quote-of-the-day/
├── .github/                       # CI/CD workflows and issue templates
│   └── workflows/
│       ├── ci.yaml               # Continuous integration pipeline
│       ├── deploy-staging.yaml   # Staging deployment automation
│       ├── deploy-prod.yaml      # Production deployment automation
│       └── security-scan.yaml    # Security scanning and dependency checks
├── apps/                         # Application packages
│   ├── mobile/                   # Flutter mobile application
│   │   ├── android/              # Android-specific configurations
│   │   ├── ios/                  # iOS-specific configurations
│   │   ├── lib/
│   │   │   ├── core/             # Core utilities and constants
│   │   │   ├── features/         # Feature-based organization
│   │   │   │   ├── auth/         # Authentication screens and logic
│   │   │   │   ├── quotes/       # Quote display and interaction
│   │   │   │   ├── search/       # Premium search functionality
│   │   │   │   ├── subscription/ # Premium upgrade flows
│   │   │   │   └── settings/     # User preferences and profile
│   │   │   ├── shared/           # Shared widgets and providers
│   │   │   └── main.dart         # Application entry point
│   │   ├── test/                 # Flutter unit and widget tests
│   │   ├── integration_test/     # Integration and E2E tests
│   │   ├── assets/               # Images, fonts, and static assets
│   │   ├── pubspec.yaml          # Flutter dependencies
│   │   └── analysis_options.yaml # Dart analyzer configuration
│   └── api/                      # FastAPI backend application
│       ├── src/
│       │   ├── main.py           # FastAPI application entry point
│       │   ├── core/             # Core configuration and utilities
│       │   │   ├── config.py     # Environment and settings management
│       │   │   ├── database.py   # SQLAlchemy setup and connection pooling
│       │   │   ├── security.py   # JWT and authentication utilities
│       │   │   └── middleware.py # CORS, logging, and rate limiting
│       │   ├── api/              # API route definitions
│       │   │   ├── deps.py       # FastAPI dependency injection
│       │   │   └── v1/           # API version 1 endpoints
│       │   │       ├── auth.py   # Authentication routes
│       │   │       ├── quotes.py # Quote management routes
│       │   │       ├── users.py  # User profile routes
│       │   │       ├── subscriptions.py # Premium subscription routes
│       │   │       └── webhooks.py # Stripe webhook handlers
│       │   ├── services/         # Business logic layer
│       │   │   ├── auth_service.py # Authentication business logic
│       │   │   ├── quote_service.py # Quote selection and curation
│       │   │   ├── subscription_service.py # Stripe integration
│       │   │   ├── notification_service.py # FCM integration
│       │   │   └── analytics_service.py # Event tracking and A/B testing
│       │   ├── repositories/     # Data access layer
│       │   │   ├── base.py       # Base repository with common operations
│       │   │   ├── user_repository.py # User data access
│       │   │   ├── quote_repository.py # Quote data access with search
│       │   │   └── subscription_repository.py # Subscription management
│       │   ├── models/           # Data models and schemas
│       │   │   ├── database/     # SQLAlchemy ORM models
│       │   │   │   ├── user.py   # User table model
│       │   │   │   ├── quote.py  # Quote table model
│       │   │   │   ├── subscription.py # Subscription table model
│       │   │   │   └── analytics.py # Analytics and A/B testing models
│       │   │   └── schemas/      # Pydantic request/response schemas
│       │   │       ├── auth.py   # Authentication schemas
│       │   │       ├── quote.py  # Quote schemas
│       │   │       ├── user.py   # User profile schemas
│       │   │       └── subscription.py # Subscription schemas
│       │   ├── utils/            # Utility functions
│       │   │   ├── email.py      # SES email sending utilities
│       │   │   ├── cache.py      # Redis caching helpers
│       │   │   ├── validators.py # Custom validation logic
│       │   │   └── formatters.py # Data formatting utilities
│       │   └── tests/            # Backend tests
│       │       ├── conftest.py   # Pytest configuration and fixtures
│       │       ├── test_auth.py  # Authentication tests
│       │       ├── test_quotes.py # Quote functionality tests
│       │       ├── test_subscriptions.py # Subscription tests
│       │       └── test_integrations.py # External service integration tests
│       ├── lambda_functions/     # Serverless function implementations
│       │   ├── notification_delivery/ # Daily quote delivery Lambda
│       │   │   ├── handler.py    # Lambda handler for notifications
│       │   │   ├── requirements.txt # Lambda dependencies
│       │   │   └── deployment.yaml # SAM deployment template
│       │   ├── webhook_processor/ # Stripe webhook processing Lambda
│       │   │   ├── handler.py    # Webhook validation and processing
│       │   │   ├── requirements.txt
│       │   │   └── deployment.yaml
│       │   └── analytics_processor/ # Batch analytics processing Lambda
│       │       ├── handler.py    # Analytics data processing
│       │       ├── requirements.txt
│       │       └── deployment.yaml
│       ├── alembic/              # Database migrations
│       │   ├── versions/         # Migration scripts
│       │   ├── alembic.ini       # Alembic configuration
│       │   └── env.py            # Migration environment setup
│       ├── requirements/         # Python dependencies
│       │   ├── base.txt          # Core dependencies
│       │   ├── dev.txt           # Development dependencies
│       │   └── prod.txt          # Production dependencies
│       ├── Dockerfile            # Container image definition
│       └── docker-compose.yml    # Local development environment
├── packages/                     # Shared packages and utilities
│   ├── shared-types/            # Shared TypeScript/Dart type definitions
│   │   ├── lib/                 # Dart type definitions for Flutter
│   │   │   ├── models/          # Shared data models
│   │   │   │   ├── user.dart    # User model definitions
│   │   │   │   ├── quote.dart   # Quote model definitions
│   │   │   │   ├── subscription.dart # Subscription model definitions
│   │   │   │   └── api_response.dart # API response wrappers
│   │   │   ├── enums/           # Shared enumerations
│   │   │   │   ├── subscription_tier.dart
│   │   │   │   ├── quote_category.dart
│   │   │   │   └── user_status.dart
│   │   │   └── constants/       # Shared constants
│   │   │       ├── api_endpoints.dart
│   │   │       └── app_constants.dart
│   │   ├── python/              # Python type definitions for FastAPI
│   │   │   ├── models/          # Pydantic model definitions
│   │   │   ├── enums/           # Python enum definitions
│   │   │   └── constants/       # Shared constants
│   │   └── pubspec.yaml         # Package dependencies
│   ├── ui-components/           # Shared UI components library
│   │   ├── lib/
│   │   │   ├── widgets/         # Reusable Flutter widgets
│   │   │   │   ├── quote_card.dart # Quote display component
│   │   │   │   ├── premium_upgrade_modal.dart # Upgrade prompts
│   │   │   │   ├── loading_states.dart # Loading indicators
│   │   │   │   └── error_widgets.dart # Error display components
│   │   │   ├── themes/          # Shared theme definitions
│   │   │   │   ├── app_theme.dart # Material 3 theme configuration
│   │   │   │   ├── colors.dart   # Brand color palette
│   │   │   │   └── typography.dart # Text styles and fonts
│   │   │   └── utils/           # UI utility functions
│   │   │       ├── responsive.dart # Screen size utilities
│   │   │       └── animations.dart # Shared animations
│   │   └── pubspec.yaml
│   └── config/                  # Shared configuration files
│       ├── eslint/              # JavaScript/TypeScript linting rules
│       │   └── .eslintrc.js
│       ├── prettier/            # Code formatting configuration
│       │   └── .prettierrc.json
│       ├── typescript/          # TypeScript compiler configuration
│       │   └── tsconfig.json
│       └── dart/                # Dart analyzer configuration
│           └── analysis_options.yaml
├── infrastructure/              # Infrastructure as Code definitions
│   ├── aws/                     # AWS CDK infrastructure definitions
│   │   ├── lib/                 # CDK stack definitions
│   │   │   ├── app-stack.ts     # Main application stack
│   │   │   ├── database-stack.ts # RDS and Redis infrastructure
│   │   │   ├── lambda-stack.ts  # Lambda functions and triggers
│   │   │   ├── api-stack.ts     # ECS and ALB configuration
│   │   │   └── monitoring-stack.ts # CloudWatch and alerting
│   │   ├── bin/                 # CDK application entry points
│   │   │   └── infrastructure.ts
│   │   ├── cdk.json             # CDK configuration
│   │   └── package.json         # CDK dependencies
│   ├── terraform/               # Alternative Terraform configurations
│   │   ├── modules/             # Reusable Terraform modules
│   │   ├── environments/        # Environment-specific configurations
│   │   │   ├── dev/             # Development environment
│   │   │   ├── staging/         # Staging environment
│   │   │   └── prod/            # Production environment
│   │   └── main.tf              # Main Terraform configuration
│   └── docker/                  # Docker configuration files
│       ├── api/                 # API container configuration
│       │   ├── Dockerfile       # Production API image
│       │   └── Dockerfile.dev   # Development API image
│       └── nginx/               # Reverse proxy configuration
│           ├── Dockerfile
│           └── nginx.conf
├── scripts/                     # Build, deployment, and utility scripts
│   ├── build/                   # Build automation scripts
│   │   ├── build-mobile.sh      # Flutter mobile build script
│   │   ├── build-api.sh         # API container build script
│   │   └── build-all.sh         # Full project build script
│   ├── deploy/                  # Deployment automation scripts
│   │   ├── deploy-staging.sh    # Staging deployment script
│   │   ├── deploy-prod.sh       # Production deployment script
│   │   └── rollback.sh          # Rollback script for failed deployments
│   ├── database/                # Database management scripts
│   │   ├── migrate.sh           # Database migration script
│   │   ├── seed.sh              # Test data seeding script
│   │   └── backup.sh            # Database backup script
│   └── setup/                   # Development environment setup
│       ├── setup-dev.sh         # Local development environment setup
│       ├── install-deps.sh      # Dependency installation script
│       └── configure-env.sh     # Environment configuration script
├── docs/                        # Project documentation
│   ├── api/                     # API documentation
│   │   ├── openapi.yaml         # OpenAPI specification
│   │   └── postman/             # Postman collection for API testing
│   ├── architecture/            # Architecture documentation
│   │   ├── adr/                 # Architectural Decision Records
│   │   ├── diagrams/            # System architecture diagrams
│   │   └── specifications/      # Technical specifications
│   ├── deployment/              # Deployment guides
│   │   ├── aws-setup.md         # AWS infrastructure setup guide
│   │   ├── ci-cd-setup.md       # CI/CD pipeline configuration
│   │   └── monitoring-setup.md  # Monitoring and alerting setup
│   └── development/             # Development documentation
│       ├── getting-started.md   # Developer onboarding guide
│       ├── coding-standards.md  # Code style and conventions
│       ├── testing-guide.md     # Testing strategy and guidelines
│       └── troubleshooting.md   # Common issues and solutions
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── .dockerignore               # Docker ignore rules
├── package.json                 # Root package.json for npm workspaces
├── melos.yaml                   # Dart/Flutter monorepo management
├── README.md                    # Project overview and setup instructions
└── LICENSE                      # Project license
```
