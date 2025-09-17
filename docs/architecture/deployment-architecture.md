# Deployment Architecture

AWS-based deployment strategy with staging and production environments, emphasizing cost optimization and reliable notification delivery.

## Deployment Strategy

**Frontend Deployment:**
- **Platform:** iOS App Store + Google Play Store for mobile apps (manual deployment)
- **Build Command:** `flutter build apk --release` (Android), `flutter build ios --release` (iOS)
- **Output Directory:** `build/app/outputs/flutter-apk/` (Android), `build/ios/iphoneos/` (iOS)
- **CDN/Edge:** CloudFront for static assets, Firebase Hosting for admin web interface

**Backend Deployment:**
- **Platform:** AWS ECS with Fargate for containerized FastAPI application
- **Build Command:** `docker build -t quote-api:latest -f apps/api/Dockerfile apps/api`
- **Deployment Method:** Blue-green deployment using ECS service updates with health checks

## CI/CD Pipeline

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4

      # Backend tests
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install backend dependencies
        run: |
          cd apps/api
          pip install -r requirements/dev.txt

      - name: Run backend tests
        run: |
          cd apps/api
          pytest --cov=src --cov-report=xml

      # Frontend tests
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'

      - name: Install mobile dependencies
        run: |
          cd apps/mobile
          flutter pub get

      - name: Run mobile tests
        run: |
          cd apps/mobile
          flutter test --coverage

      # Security scanning
      - name: Run security scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: security-scan-results.sarif

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      # Build and push API container
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build and push API image
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t $ECR_REGISTRY/quote-api:$GITHUB_SHA apps/api
          docker push $ECR_REGISTRY/quote-api:$GITHUB_SHA

      # Deploy to ECS
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster quote-of-the-day-prod \
            --service quote-api-service \
            --task-definition quote-api-task:${{ github.sha }} \
            --force-new-deployment

      # Deploy Lambda functions
      - name: Deploy Lambda functions
        run: |
          cd apps/api/lambda_functions
          for dir in */; do
            cd "$dir"
            zip -r "../${dir%/}.zip" .
            aws lambda update-function-code \
              --function-name "quote-${dir%/}" \
              --zip-file "fileb://../${dir%/}.zip"
            cd ..
          done

      # Note: Mobile app deployment is manual to app stores
      - name: Mobile deployment note
        run: |
          echo "Mobile app changes require manual store deployment"
          echo "Run: flutter build apk --release && flutter build ios --release"
```

## Environments

| Environment | Frontend URL | Backend URL | Purpose |
|-------------|-------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:8000 | Local development and testing |
| Staging | https://staging-app.quoteoftheday.com | https://staging-api.quoteoftheday.com | Pre-production testing and QA |
| Production | App Store / Google Play | https://api.quoteoftheday.com | Live user environment |
