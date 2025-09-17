# Coding Standards

## Critical Fullstack Rules

- **Type Sharing:** Always define shared types in packages/shared-types and import consistently across Flutter and Python codebases
- **API Error Handling:** All API responses must use standardized error format with code, message, timestamp, and request_id
- **Premium Feature Gates:** Never bypass subscription checks - always validate tier through middleware or route guards
- **Database Transactions:** Use database transactions for all multi-step operations, especially subscription and quote delivery workflows
- **Async Operations:** All I/O operations must be async/await in both Flutter (Future) and Python (async/await)
- **Environment Configuration:** Never hardcode URLs or API keys - use environment-specific configuration files
- **Authentication Flow:** JWT tokens must include user_id, email, subscription_tier, and expiration for proper authorization

## Naming Conventions

| Element | Frontend (Flutter) | Backend (FastAPI) | Example |
|---------|-------------------|-------------------|---------|
| Models | PascalCase | PascalCase (Pydantic) | `UserProfile`, `QuoteModel` |
| Services | PascalCase with Service suffix | snake_case with _service suffix | `AuthService`, `auth_service.py` |
| API Routes | - | snake_case with descriptive verbs | `/api/v1/quotes/search` |
| Database Tables | - | snake_case with plural nouns | `user_quote_history` |
| Constants | SCREAMING_SNAKE_CASE | SCREAMING_SNAKE_CASE | `MAX_SEARCH_RESULTS` |
