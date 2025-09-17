# Technical Assumptions

## Repository Structure: Monorepo
Single repository containing Flutter mobile app, backend services, and shared configuration - enables consistent deployment and version management across platforms.

## Service Architecture
**Hybrid Architecture**: Monolith backend API with serverless functions for notification delivery and content curation tasks. This provides:
- Reliable core service for user management, subscription, and quote storage (monolith)
- Scalable, redundant notification delivery (serverless functions)
- Cost-effective content curation workflows (serverless functions)

## Testing Requirements
**Unit + Integration Testing**: Given the critical nature of notification delivery and subscription management, comprehensive testing is essential. Manual testing convenience methods needed for quote curation quality assurance.

## Additional Technical Assumptions and Requests

**Mobile Development Stack:**
- **Cross-Platform**: Flutter with Dart for unified iOS and Android development
- **Rationale**: Single codebase reduces development complexity while maintaining native notification integration capabilities and performance

**Backend Technology:**
- **API Framework**: Node.js with Express or FastAPI with Python for rapid development
- **Database**: PostgreSQL for reliable subscription/user management with Redis for notification queuing
- **Rationale**: Mature ecosystem supporting payment integration and notification services

**Infrastructure & Deployment:**
- **Cloud Provider**: AWS (free tier optimization per Brief's cost consciousness)
- **Notification Services**: Firebase Cloud Messaging (FCM) for cross-platform push notifications
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Rationale**: Proven reliability for mobile notification delivery with cost-effective scaling

**Key Technical Constraints:**
- Must support A/B testing infrastructure for conversion optimization
- Payment processing integration (Stripe recommended for subscription management)
- Content management system for quote curation workflow
- Analytics integration for user engagement tracking and freemium optimization
