# Data Models

## User

**Purpose:** Represents registered users with authentication and subscription status for personalized quote delivery

**Key Attributes:**
- id: UUID - Primary key for user identification
- email: str - User's email address for authentication and communication
- password_hash: str - Securely hashed password for authentication
- created_at: datetime - Account creation timestamp
- is_active: bool - Account status (supports account suspension)
- subscription_tier: SubscriptionTier - Current subscription level (FREE/PREMIUM)
- notification_settings: NotificationSettings - Personalized delivery preferences
- timezone: str - User's timezone for accurate notification timing
- last_quote_delivered: datetime - Tracking for daily delivery logic

### TypeScript Interface
```typescript
interface User {
  id: string;
  email: string;
  created_at: string;
  is_active: boolean;
  subscription_tier: 'FREE' | 'PREMIUM';
  notification_settings: NotificationSettings;
  timezone: string;
  last_quote_delivered: string | null;
}

interface NotificationSettings {
  enabled: boolean;
  delivery_time: string; // HH:MM format
  weekdays_only: boolean;
  pause_until: string | null;
}
```

### Relationships
- One-to-many with Quote interactions (stars, views)
- One-to-many with Subscription history
- One-to-many with UserQuoteHistory

## Quote

**Purpose:** Core content entity representing curated quotes with metadata for intelligent professional targeting

**Key Attributes:**
- id: UUID - Primary key for quote identification
- content: str - The actual quote text
- author: str - Quote attribution/author name
- source: str - Book, speech, or context where quote originated
- category: QuoteCategory - Thematic classification for targeting
- difficulty_level: int - Sophistication level (1-5) for audience matching
- created_at: datetime - When quote was added to system
- is_active: bool - Publication status
- curator_notes: str - Internal notes for content quality
- copyright_status: str - Legal status and attribution requirements

### TypeScript Interface
```typescript
interface Quote {
  id: string;
  content: string;
  author: string;
  source: string | null;
  category: QuoteCategory;
  difficulty_level: number; // 1-5 scale
  created_at: string;
  is_active: boolean;
  curator_notes: string | null;
}

type QuoteCategory = 'LEADERSHIP' | 'PHILOSOPHY' | 'BUSINESS' | 'CREATIVITY' | 'WISDOM' | 'DECISION_MAKING';
```

### Relationships
- One-to-many with UserQuoteHistory (delivery tracking)
- One-to-many with QuoteStar (user favorites)
- Many-to-many with User through interactions

## UserQuoteHistory

**Purpose:** Tracks quote delivery and user engagement for analytics and preventing duplicate delivery

**Key Attributes:**
- id: UUID - Primary key
- user_id: UUID - Foreign key to User
- quote_id: UUID - Foreign key to Quote
- delivered_at: datetime - When quote was sent to user
- viewed_at: datetime - When user opened/viewed quote
- starred_at: datetime - When user starred quote (nullable)
- engagement_score: float - Calculated engagement metric for personalization

### TypeScript Interface
```typescript
interface UserQuoteHistory {
  id: string;
  user_id: string;
  quote_id: string;
  delivered_at: string;
  viewed_at: string | null;
  starred_at: string | null;
  engagement_score: number;
}
```

### Relationships
- Many-to-one with User
- Many-to-one with Quote
- Used for analytics and personalization algorithms

## Subscription

**Purpose:** Manages premium subscription lifecycle, payment tracking, and feature access control

**Key Attributes:**
- id: UUID - Primary key
- user_id: UUID - Foreign key to User
- tier: SubscriptionTier - Current subscription level
- status: SubscriptionStatus - Payment and lifecycle status
- stripe_customer_id: str - Stripe customer reference
- stripe_subscription_id: str - Stripe subscription reference
- current_period_start: datetime - Billing cycle start
- current_period_end: datetime - Billing cycle end
- created_at: datetime - Subscription creation
- cancelled_at: datetime - Cancellation timestamp (nullable)

### TypeScript Interface
```typescript
interface Subscription {
  id: string;
  user_id: string;
  tier: 'FREE' | 'PREMIUM';
  status: 'ACTIVE' | 'CANCELLED' | 'PAST_DUE' | 'INCOMPLETE';
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  current_period_start: string;
  current_period_end: string;
  created_at: string;
  cancelled_at: string | null;
}
```

### Relationships
- One-to-one with User (current subscription)
- Historical tracking through status changes
