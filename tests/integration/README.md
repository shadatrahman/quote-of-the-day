# Integration Tests

This directory contains integration tests for the Quote of the Day application, focusing on CI/CD pipeline validation and infrastructure testing.

## Test Categories

### CI/CD Pipeline Tests (`test_ci_pipeline.py`)

- Workflow file syntax validation
- Environment variable consistency
- Docker configuration validation
- Package dependency validation
- Security scanning configuration
- Coverage reporting validation

### Deployment Pipeline Tests (`test_deployment_pipeline.py`)

- Docker build configuration
- ECR image build workflow
- ECS deployment configuration
- CDK deployment workflow
- Smoke tests configuration
- Health check endpoint validation
- Environment-specific configurations
- Deployment artifacts handling
- Notification configuration

### Infrastructure Validation Tests (`test_infrastructure_validation.py`)

- CDK configuration files
- CDK package dependencies
- Stack file validation
- Database stack configuration
- API stack configuration
- Lambda stack configuration
- Monitoring stack configuration
- Security configurations
- Scaling configurations
- Networking configurations

## Running the Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt

# Ensure you have the project dependencies
cd /path/to/quote-of-the-day
pip install -r apps/api/requirements.txt
```

### Run All Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test Categories

```bash
# CI/CD pipeline tests
pytest tests/integration/test_ci_pipeline.py -v

# Deployment pipeline tests
pytest tests/integration/test_deployment_pipeline.py -v

# Infrastructure validation tests
pytest tests/integration/test_infrastructure_validation.py -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=. --cov-report=html
```

## Test Configuration

The tests use the following configuration files:

- `pytest.ini`: Pytest configuration
- `conftest.py`: Shared fixtures and configuration
- `requirements.txt`: Test dependencies

## Mocking

The tests use extensive mocking to avoid requiring actual AWS credentials or external services:

- AWS credentials are mocked
- HTTP requests are mocked
- CDK synthesis is mocked
- External API calls are mocked

## Test Data

The tests use the following test data:

- Mock GitHub workflow configurations
- Mock CDK outputs
- Mock AWS responses
- Temporary project directories

## Continuous Integration

These tests are designed to run in CI/CD pipelines and validate:

- Workflow syntax and structure
- Configuration consistency
- Deployment readiness
- Infrastructure configuration validity

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Path Issues**: Run tests from the project root directory
3. **Mock Issues**: Check that mocks are properly configured
4. **File Not Found**: Ensure all required files exist in the project

### Debug Mode

```bash
pytest tests/integration/ -v -s --tb=long
```

### Verbose Output

```bash
pytest tests/integration/ -vvv
```
