# Getting Started - Quote of the Day Development Guide

This guide will walk you through setting up the Quote of the Day development environment from scratch.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Node.js** | 18.0+ | Package management and tooling |
| **Python** | 3.13+ | Backend API development |
| **Flutter** | 3.32.8+ | Mobile app development |
| **Docker** | 24.0+ | Local development services |
| **Git** | 2.0+ | Version control |

### Optional Tools

- **AWS CLI** v2 - For deployment and infrastructure management
- **VS Code** - Recommended IDE with Flutter and Python extensions
- **Android Studio** - For Android development and emulator
- **Xcode** - For iOS development (macOS only)

## 🔧 System Setup

### 1. Install Node.js

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or download from https://nodejs.org/
```

### 2. Install Python

```bash
# macOS (using Homebrew)
brew install python@3.13

# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-pip

# Windows (using Chocolatey)
choco install python --version=3.13.0
```

### 3. Install Flutter

```bash
# macOS (using Homebrew)
brew install flutter

# Or download from https://flutter.dev/docs/get-started/install

# Verify installation
flutter doctor
```

### 4. Install Docker

```bash
# macOS (using Homebrew)
brew install docker docker-compose

# Or download Docker Desktop from https://docker.com/
```

### 5. Configure Flutter

```bash
# Accept Android licenses
flutter doctor --android-licenses

# Configure development settings
flutter config --enable-web
flutter config --enable-macos-desktop
flutter config --enable-linux-desktop
flutter config --enable-windows-desktop
```

## 📁 Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/quote-of-the-day.git
cd quote-of-the-day
```

### 2. Install Dependencies

```bash
# Install all project dependencies
npm run install:all

# This runs:
# - npm install (root dependencies)
# - cd apps/api && pip install -r requirements.txt
# - cd apps/mobile && flutter pub get
# - cd packages/* && npm install
# - cd infrastructure/aws && npm install
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file
nano .env  # or your preferred editor
```

#### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://quote_user:quote_password@localhost:5432/quote_of_the_day_dev
REDIS_URL=redis://localhost:6379/0

# API
SECRET_KEY=your-super-secret-development-key-change-this
DEBUG=true
ENVIRONMENT=development

# Firebase (create a Firebase project first)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_ADMIN_CREDENTIALS_PATH=./secrets/firebase-admin-credentials.json

# Optional: Monitoring (for production-like setup)
SENTRY_DSN=your-sentry-dsn-optional
```

### 4. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication and Firestore
3. Download the service account key
4. Place it at `apps/api/secrets/firebase-admin-credentials.json`
5. Update the Firebase configuration in `.env`

### 5. Mobile App Configuration

Create mobile environment file:

```bash
cd apps/mobile
cp .env.example .env.local

# Edit mobile-specific settings
nano .env.local
```

```bash
# Mobile app environment
FLUTTER_APP_ENV=development
API_BASE_URL=http://localhost:8000
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_API_KEY=your-firebase-api-key
```

## 🚀 Running the Application

### 1. Start Development Services

```bash
# Start PostgreSQL and Redis containers
npm run dev:services

# Wait for services to start (check logs)
npm run logs
```

### 2. Initialize Database

```bash
# Run database migrations
npm run db:migrate

# Seed with development data
npm run db:seed
```

### 3. Start the API Server

```bash
# Start FastAPI development server
npm run dev:api

# The API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Start the Mobile App

```bash
# In a new terminal
npm run dev:mobile

# Or run directly
cd apps/mobile
flutter run
```

## 🧪 Verify Installation

### 1. Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 2. Check Mobile App

The Flutter app should launch and display the Quote of the Day interface.

### 3. Run Tests

```bash
# Run all tests
npm run test

# Run specific test suites
npm run test:api
npm run test:mobile
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Services Won't Start

```bash
# Check Docker is running
docker ps

# Reset Docker containers
npm run stop
docker-compose down -v
npm run dev:services
```

#### 2. Database Connection Issues

```bash
# Check database is running
docker-compose logs postgres

# Reset database
npm run db:reset
```

#### 3. Flutter Build Issues

```bash
# Clean Flutter cache
cd apps/mobile
flutter clean
flutter pub get

# Check Flutter doctor
flutter doctor -v
```

#### 4. Python Dependencies Issues

```bash
cd apps/api

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 5. Node.js Dependencies Issues

```bash
# Clear npm cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Platform-Specific Setup

#### macOS

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install additional dependencies
brew install postgresql redis
```

#### Windows

```bash
# Enable WSL2 for Docker
wsl --install

# Install Windows Terminal for better CLI experience
winget install Microsoft.WindowsTerminal
```

#### Linux (Ubuntu/Debian)

```bash
# Install additional dependencies
sudo apt install postgresql-client redis-tools build-essential

# Install Flutter dependencies
sudo apt install clang cmake ninja-build pkg-config libgtk-3-dev
```

## 🔧 IDE Setup

### VS Code Extensions

Install these recommended extensions:

```bash
# Flutter and Dart
code --install-extension Dart-Code.dart-code
code --install-extension Dart-Code.flutter

# Python
code --install-extension ms-python.python
code --install-extension ms-python.pylint

# General development
code --install-extension ms-vscode.vscode-typescript-next
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-json
```

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./apps/api/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "flutter.sdkPath": "/path/to/flutter",
  "dart.debugExternalLibraries": false,
  "dart.debugSdkLibraries": false
}
```

## 📚 Next Steps

Now that you have the development environment set up:

1. **Explore the codebase** - Familiarize yourself with the project structure
2. **Read the architecture docs** - Understand the system design
3. **Run the test suites** - Ensure everything works correctly
4. **Make a small change** - Try modifying something and see the hot reload
5. **Check the API docs** - Visit http://localhost:8000/docs

## 📖 Additional Resources

- [Architecture Overview](../architecture/README.md)
- [API Development Guide](api-development.md)
- [Mobile Development Guide](mobile-development.md)
- [Testing Guide](testing.md)
- [Deployment Guide](../deployment/README.md)

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Search existing [GitHub Issues](https://github.com/yourorg/quote-of-the-day/issues)
3. Join our [Discussions](https://github.com/yourorg/quote-of-the-day/discussions)
4. Contact the development team

---

**Happy Coding!** 🎉