# Monitoring and Observability

## Monitoring Stack
- **Frontend Monitoring:** Sentry for Flutter crash reporting and performance monitoring
- **Backend Monitoring:** AWS CloudWatch for infrastructure metrics, Sentry for application errors
- **Error Tracking:** Centralized error tracking with user context and subscription tier information
- **Performance Monitoring:** APM with request tracing, database query monitoring, and notification delivery tracking

## Key Metrics

**Frontend Metrics:**
- App startup time and crash rates
- Quote loading performance and user engagement
- Premium feature interaction rates
- Subscription conversion funnel metrics

**Backend Metrics:**
- API response times (95th percentile <500ms)
- Database connection pool utilization
- Notification delivery success rates (target 99.9%)
- Subscription webhook processing reliability
