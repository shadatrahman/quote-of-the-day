# Troubleshooting Guide

This guide helps you resolve common issues when developing the Quote of the Day application.

## 🔍 Quick Diagnostics

### Health Check Commands

```bash
# Check all services
npm run test:health

# Check API health
curl http://localhost:8000/health

# Check database connection
npm run db:shell
# In psql: \l (list databases)

# Check Redis connection
npm run redis:cli
# In redis: ping (should return PONG)

# Check Docker services
docker-compose ps
```

### Service Status Check

```bash
# Check what's running on ports
lsof -i :8000  # API server
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Check Docker containers
docker ps

# Check logs
npm run logs
docker-compose logs -f
```

## 🐳 Docker Issues

### Docker Services Won't Start

**Problem**: `npm run dev:services` fails or containers exit immediately.

**Solutions**:

```bash
# Check Docker daemon is running
docker version
docker info

# Reset Docker state
docker-compose down -v  # Warning: removes all data
docker system prune -f
npm run dev:services

# Check Docker resources (memory/disk)
docker system df
```

### PostgreSQL Container Issues

**Problem**: Database container keeps restarting.

**Symptoms**:
- `Connection refused` errors
- Container exits with code 1
- `initdb: error` in logs

**Solutions**:

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Common fixes
docker-compose down
docker volume rm quote-of-the-day_postgres_data
npm run dev:services

# Check permissions (Linux/macOS)
ls -la /var/lib/docker/volumes/

# Alternative: use different PostgreSQL version
# Edit docker-compose.yml: postgres:15 instead of postgres:17
```

### Redis Container Issues

**Problem**: Redis connection fails or container won't start.

**Solutions**:

```bash
# Check Redis logs
docker-compose logs redis

# Reset Redis data
docker-compose down
docker volume rm quote-of-the-day_redis_data
npm run dev:services

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Port Conflicts

**Problem**: "Port already in use" errors.

**Solutions**:

```bash
# Find what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # API

# Kill processes using ports
kill -9 $(lsof -ti:5432)
kill -9 $(lsof -ti:6379)
kill -9 $(lsof -ti:8000)

# Or change ports in docker-compose.yml
```

## 🐍 Python/API Issues

### Dependencies Installation Problems

**Problem**: `pip install -r requirements.txt` fails.

**Solutions**:

```bash
# Check Python version
python --version  # Should be 3.13+

# Recreate virtual environment
cd apps/api
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Update pip and install
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Platform-specific issues
# macOS: Install Xcode Command Line Tools
xcode-select --install

# Linux: Install build dependencies
sudo apt install build-essential python3-dev libpq-dev

# Windows: Install Microsoft C++ Build Tools
```

### Database Migration Issues

**Problem**: Alembic migrations fail.

**Symptoms**:
- `sqlalchemy.exc.OperationalError`
- `Target database is not up to date`
- Migration conflicts

**Solutions**:

```bash
cd apps/api

# Check database connection
python -c "from src.core.database import db_manager; print('DB OK')"

# Check current migration status
alembic current
alembic history

# Reset migrations (destructive!)
alembic downgrade base
alembic upgrade head

# Fix migration conflicts
alembic merge heads  # If multiple heads exist
alembic upgrade head

# Recreate database (nuclear option)
npm run db:reset
```

### Import/Module Errors

**Problem**: `ModuleNotFoundError` or import issues.

**Solutions**:

```bash
# Check Python path
cd apps/api
python -c "import sys; print('\n'.join(sys.path))"

# Ensure src is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Check virtual environment
which python  # Should point to venv/bin/python
pip list  # Check installed packages

# Reinstall in development mode
pip install -e .
```

### API Server Won't Start

**Problem**: FastAPI server crashes or won't start.

**Symptoms**:
- `Address already in use`
- Configuration errors
- Module import failures

**Solutions**:

```bash
# Check if port is in use
lsof -i :8000
kill -9 $(lsof -ti:8000)

# Check configuration
cd apps/api
python -c "from src.core.config import settings; print(settings.dict())"

# Run with debug info
python -m uvicorn src.main:app --reload --log-level debug

# Check environment variables
env | grep -E "(DATABASE|REDIS|SECRET)"
```

## 📱 Flutter/Mobile Issues

### Flutter Installation Problems

**Problem**: Flutter doctor shows issues.

**Solutions**:

```bash
# Run comprehensive check
flutter doctor -v

# Common fixes
flutter upgrade
flutter config --clear-ios-signing-cert
flutter clean

# Android issues
flutter doctor --android-licenses  # Accept all licenses
$ANDROID_HOME/tools/bin/sdkmanager --licenses

# iOS issues (macOS only)
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

### Build Failures

**Problem**: `flutter build` or `flutter run` fails.

**Solutions**:

```bash
cd apps/mobile

# Clean everything
flutter clean
rm -rf .dart_tool
flutter pub get

# Platform-specific clean
# Android
cd android && ./gradlew clean && cd ..

# iOS
cd ios && rm -rf build && cd ..

# Fix common issues
flutter pub deps
flutter analyze
flutter test

# Update dependencies
flutter pub upgrade --major-versions
```

### Dependency Conflicts

**Problem**: Package conflicts or version issues.

**Solutions**:

```bash
cd apps/mobile

# Check dependency tree
flutter pub deps

# Resolve conflicts
flutter pub upgrade --major-versions
flutter pub get

# Manual resolution in pubspec.yaml
dependency_overrides:
  package_name: ^version
```

### Device/Emulator Issues

**Problem**: App won't run on device or emulator.

**Solutions**:

```bash
# Check available devices
flutter devices

# Android emulator
$ANDROID_HOME/emulator/emulator -list-avds
$ANDROID_HOME/emulator/emulator -avd Pixel_4_API_30

# iOS Simulator (macOS only)
open -a Simulator

# Physical device debugging
flutter run -v  # Verbose output

# Reset device/emulator
flutter clean
flutter run --hot
```

## 🛠️ Development Tools Issues

### VS Code Problems

**Problem**: Extensions not working or IDE issues.

**Solutions**:

```bash
# Reload VS Code window
Cmd+Shift+P → "Developer: Reload Window"

# Check extensions
code --list-extensions
code --install-extension Dart-Code.flutter

# Reset VS Code settings
rm -rf .vscode/settings.json
# Recreate from template
```

### Git Issues

**Problem**: Git operations fail or conflicts.

**Solutions**:

```bash
# Check git status
git status
git log --oneline -10

# Fix common issues
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Resolve conflicts
git pull --rebase origin main
# Fix conflicts in editor
git add .
git rebase --continue

# Nuclear option (lose local changes)
git reset --hard origin/main
```

## 🔧 Environment Issues

### Environment Variables Not Loading

**Problem**: App doesn't recognize environment variables.

**Solutions**:

```bash
# Check .env file exists and format
ls -la .env
cat .env

# Verify environment loading
python -c "import os; print(os.getenv('DATABASE_URL'))"

# Common format issues
# ❌ Wrong: DATABASE_URL = "postgresql://..."
# ✅ Correct: DATABASE_URL=postgresql://...

# Restart services after changing .env
npm run stop
npm run dev:services
npm run dev:api
```

### Firebase Configuration Issues

**Problem**: Firebase authentication fails.

**Solutions**:

```bash
# Check Firebase config
cd apps/api
ls -la secrets/firebase-admin-credentials.json

# Verify Firebase project
# Visit https://console.firebase.google.com/
# Check project ID matches FIREBASE_PROJECT_ID

# Test Firebase connection
python -c "
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate('secrets/firebase-admin-credentials.json')
firebase_admin.initialize_app(cred)
print('Firebase OK')
"
```

## 📊 Performance Issues

### Slow API Responses

**Problem**: API endpoints are slow.

**Debug Steps**:

```bash
# Check database performance
npm run db:shell
# In psql: EXPLAIN ANALYZE SELECT * FROM quotes LIMIT 10;

# Check Redis performance
npm run redis:cli
# In redis: INFO stats

# Monitor API logs
tail -f apps/api/logs/app.log

# Profile API endpoints
curl -w "@curl-format.txt" http://localhost:8000/api/v1/quotes
```

### High Memory Usage

**Problem**: Application uses too much memory.

**Debug Steps**:

```bash
# Check Docker memory usage
docker stats

# Check Python memory
pip install memory-profiler
python -m memory_profiler your_script.py

# Monitor system resources
top -p $(pgrep -f python)
htop
```

## 🔍 Testing Issues

### Tests Failing

**Problem**: Tests fail unexpectedly.

**Solutions**:

```bash
# Run tests with verbose output
cd apps/api
pytest -v -s tests/

cd apps/mobile
flutter test -v

# Run specific test
pytest tests/test_quotes.py::test_get_quotes -v

# Clear test cache
pytest --cache-clear
rm -rf .pytest_cache

# Check test database
TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5432/quote_test_db pytest
```

## 🚨 Emergency Procedures

### Complete Reset

When everything is broken:

```bash
# Stop all services
npm run stop:all
docker-compose down -v

# Clean everything
docker system prune -f
rm -rf node_modules
rm -rf apps/api/venv
rm -rf apps/mobile/.dart_tool

# Reinstall everything
npm run install:all
npm run dev:services
npm run db:migrate
npm run db:seed
```

### Backup Important Data

Before destructive operations:

```bash
# Backup database
docker-compose exec postgres pg_dump -U quote_user quote_of_the_day_dev > backup.sql

# Backup Redis data
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb redis_backup.rdb

# Backup configuration
cp .env .env.backup
cp apps/mobile/.env.local apps/mobile/.env.local.backup
```

## 📞 Getting Help

### Information to Gather

When reporting issues, include:

```bash
# System information
uname -a
docker --version
node --version
python --version
flutter --version

# Service status
docker-compose ps
npm run logs | tail -50

# Error messages
# Copy exact error messages and stack traces
```

### Where to Get Help

1. **Documentation**: Check relevant docs in `docs/`
2. **GitHub Issues**: Search existing issues
3. **Discussions**: Join GitHub Discussions
4. **Logs**: Always include relevant log outputs

### Creating Good Bug Reports

Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Log outputs
- Configuration (sanitized)

---

Still stuck? Create an issue with the template and we'll help! 🚀