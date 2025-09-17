# External APIs

## Firebase Cloud Messaging API

- **Purpose:** Cross-platform push notification delivery for daily quote notifications and user engagement
- **Documentation:** https://firebase.google.com/docs/cloud-messaging
- **Base URL(s):** https://fcm.googleapis.com/fcm/send (legacy), https://fcm.googleapis.com/v1/projects/{project_id}/messages:send (HTTP v1)
- **Authentication:** Firebase Admin SDK with service account JSON key
- **Rate Limits:** 600,000 downstream messages per minute per project

**Key Endpoints Used:**
- `POST /v1/projects/{project_id}/messages:send` - Send individual notification to device token
- `POST /v1/projects/{project_id}/messages:sendMulticast` - Send notifications to multiple devices
- `POST /fcm/send` - Legacy endpoint for batch notifications (fallback)

**Integration Notes:** Critical for 99.9% notification reliability requirement. Requires device token management, message payload optimization for mobile platforms, and retry logic for failed deliveries.

## Stripe Payments API

- **Purpose:** Premium subscription management, payment processing, and billing lifecycle for $1/month freemium conversion
- **Documentation:** https://stripe.com/docs/api
- **Base URL(s):** https://api.stripe.com/v1
- **Authentication:** Bearer token with secret key (server-side) and publishable key (client-side)
- **Rate Limits:** 100 requests per second in live mode, 25 requests per second in test mode

**Key Endpoints Used:**
- `POST /v1/customers` - Create customer for user subscription
- `POST /v1/subscriptions` - Create premium subscription
- `POST /v1/payment_methods` - Attach payment method to customer
- `GET /v1/subscriptions/{subscription_id}` - Check subscription status
- `POST /v1/subscriptions/{subscription_id}` - Update or cancel subscription
- `POST /v1/billing_portal/sessions` - Generate customer portal session

**Integration Notes:** Webhook handling required for subscription status changes. Must implement idempotency keys for payment operations and handle failed payment scenarios gracefully.

## Firebase Authentication API

- **Purpose:** Mobile-optimized user authentication with email/password and social login options
- **Documentation:** https://firebase.google.com/docs/auth
- **Base URL(s):** https://identitytoolkit.googleapis.com/v1, SDK handles most direct API calls
- **Authentication:** Firebase Admin SDK with service account credentials
- **Rate Limits:** 500 requests per 10 minutes per IP address for authentication endpoints

**Key Endpoints Used:**
- `POST /v1/accounts:signUp` - Create new user account
- `POST /v1/accounts:signInWithPassword` - Authenticate user
- `POST /v1/accounts:sendOobCode` - Send password reset email
- `POST /v1/accounts:verifyPassword` - Verify user credentials
- `POST /v1/projects/{project_id}:verifyCustomToken` - Verify custom JWT tokens

**Integration Notes:** Custom JWT token generation required for backend API authentication. Email verification workflow must integrate with app onboarding flow.

## AWS Simple Email Service (SES)

- **Purpose:** Transactional email delivery for user verification, password resets, and subscription notifications
- **Documentation:** https://docs.aws.amazon.com/ses/
- **Base URL(s):** https://email.{region}.amazonaws.com
- **Authentication:** AWS SDK with IAM credentials (access key/secret key)
- **Rate Limits:** 200 emails per 24-hour period (sandbox), increased limits available upon request

**Key Endpoints Used:**
- `POST /` with Action=SendEmail - Send individual transactional emails
- `POST /` with Action=SendTemplatedEmail - Send emails using SES templates
- `POST /` with Action=GetSendQuota - Check sending limits and usage

**Integration Notes:** Email templates required for consistent branding. Bounce and complaint handling needed for deliverability. Domain verification required for production use.
