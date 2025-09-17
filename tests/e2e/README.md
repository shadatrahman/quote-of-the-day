# End-to-End Smoke Tests

This directory contains end-to-end smoke tests for the Quote of the Day application, validating the complete application flow from frontend to backend to infrastructure components.

## Test Categories

### Application Smoke Tests (`test_application_smoke.py`)

- Application startup sequence validation
- API endpoints functionality testing
- Database operations testing
- Redis operations testing
- Flutter app integration testing
- CI/CD pipeline integration testing
- Infrastructure configuration testing
- Monitoring and logging testing
- Security configuration testing
- Complete application flow testing
- Deployment smoke test simulation

## Test Coverage

### Backend Testing

- ✅ API server startup and health checks
- ✅ Database connectivity and operations
- ✅ Redis caching operations
- ✅ API endpoint functionality
- ✅ Security configuration validation
- ✅ Monitoring and logging setup

### Frontend Testing

- ✅ Flutter app compilation
- ✅ Widget structure validation
- ✅ API service integration
- ✅ App lifecycle testing

### Infrastructure Testing

- ✅ CDK configuration validation
- ✅ AWS service integration
- ✅ Environment configuration
- ✅ Security best practices

### CI/CD Testing

- ✅ GitHub workflow validation
- ✅ Deployment pipeline testing
- ✅ Smoke test simulation
- ✅ Integration testing

## Running the Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt

# Ensure you have the project dependencies
cd /path/to/quote-of-the-day
pip install -r apps/api/requirements.txt
```

### Run All E2E Tests

```bash
pytest tests/e2e/ -v
```

### Run Specific Test Categories

```bash
# Application smoke tests
pytest tests/e2e/test_application_smoke.py -v

# Slow tests only
pytest tests/e2e/ -m slow -v

# API tests only
pytest tests/e2e/ -m api -v

# Frontend tests only
pytest tests/e2e/ -m frontend -v

# Infrastructure tests only
pytest tests/e2e/ -m infrastructure -v

# Security tests only
pytest tests/e2e/ -m security -v
```

### Run with Coverage

```bash
pytest tests/e2e/ --cov=. --cov-report=html
```

### Run in Parallel

```bash
pytest tests/e2e/ -n auto
```

## Test Configuration

The tests use the following configuration files:

- `pytest.ini`: Pytest configuration with markers and options
- `conftest.py`: Shared fixtures and configuration
- `requirements.txt`: Test dependencies

## Test Markers

- `e2e`: End-to-end tests
- `smoke`: Smoke tests
- `slow`: Slow running tests (use `-m "not slow"` to skip)
- `integration`: Integration tests
- `api`: API tests
- `frontend`: Frontend tests
- `infrastructure`: Infrastructure tests
- `security`: Security tests
- `performance`: Performance tests

## Mocking Strategy

The tests use extensive mocking to avoid requiring actual external services:

- AWS credentials and services are mocked
- HTTP requests are mocked with realistic responses
- Database operations are mocked
- Redis operations are mocked
- External API calls are mocked

## Test Data

The tests use the following test data:

- Mock environment configurations
- Mock HTTP responses
- Mock AWS service responses
- Mock database operations
- Mock Redis operations

## Continuous Integration

These tests are designed to run in CI/CD pipelines and validate:

- Complete application functionality
- End-to-end user workflows
- System integration
- Deployment readiness
- Performance characteristics
- Security compliance

## Test Scenarios

### 1. Application Startup Sequence

- Database initialization
- Redis connectivity
- API server startup
- Flutter app compilation

### 2. API Functionality

- Health check endpoints
- Metrics endpoints
- API v1 router
- Error handling

### 3. Database Operations

- Connection establishment
- Schema validation
- Data operations
- Migration testing

### 4. Redis Operations

- Connection establishment
- Cache operations
- Data serialization
- Error handling

### 5. Flutter Integration

- App compilation
- Widget structure
- API communication
- State management

### 6. Infrastructure Validation

- CDK configuration
- AWS service integration
- Environment setup
- Security configuration

### 7. Monitoring and Logging

- Log configuration
- Metrics collection
- CloudWatch integration
- Error tracking

### 8. Security Testing

- Environment variable validation
- API security middleware
- Authentication setup
- Authorization checks

### 9. Complete Application Flow

- End-to-end user journey
- System integration
- Error handling
- Performance validation

### 10. Deployment Smoke Test

- Deployment readiness
- Service availability
- Health checks
- Performance validation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Path Issues**: Run tests from the project root directory
3. **Mock Issues**: Check that mocks are properly configured
4. **File Not Found**: Ensure all required files exist in the project
5. **Environment Issues**: Check that test environment variables are set

### Debug Mode

```bash
pytest tests/e2e/ -v -s --tb=long
```

### Verbose Output

```bash
pytest tests/e2e/ -vvv
```

### Run Specific Test

```bash
pytest tests/e2e/test_application_smoke.py::TestApplicationSmoke::test_application_startup_sequence -v
```

## Performance Considerations

- Tests are designed to run quickly with extensive mocking
- Slow tests are marked with `@pytest.mark.slow`
- Use `-m "not slow"` to skip slow tests in development
- Parallel execution is supported with `pytest-xdist`

## Best Practices

1. **Mock External Dependencies**: Always mock external services
2. **Use Fixtures**: Leverage pytest fixtures for setup and teardown
3. **Test Isolation**: Ensure tests don't depend on each other
4. **Clear Test Names**: Use descriptive test names
5. **Proper Assertions**: Use specific assertions with clear error messages
6. **Error Handling**: Test both success and failure scenarios
7. **Documentation**: Keep test documentation up to date
