# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: Quote of the Day API
  version: 1.0.0
  description: Premium quote delivery service for intelligent professionals with subscription management and personalized content curation
servers:
  - url: https://api.quoteoftheday.com/v1
    description: Production API
  - url: https://staging-api.quoteoftheday.com/v1
    description: Staging API

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        created_at:
          type: string
          format: date-time
        subscription_tier:
          type: string
          enum: [FREE, PREMIUM]
        notification_settings:
          $ref: '#/components/schemas/NotificationSettings'
        timezone:
          type: string
          example: "America/New_York"

    NotificationSettings:
      type: object
      properties:
        enabled:
          type: boolean
        delivery_time:
          type: string
          pattern: '^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
          example: "08:30"
        weekdays_only:
          type: boolean
        pause_until:
          type: string
          format: date-time
          nullable: true

    Quote:
      type: object
      properties:
        id:
          type: string
          format: uuid
        content:
          type: string
        author:
          type: string
        source:
          type: string
          nullable: true
        category:
          type: string
          enum: [LEADERSHIP, PHILOSOPHY, BUSINESS, CREATIVITY, WISDOM, DECISION_MAKING]
        difficulty_level:
          type: integer
          minimum: 1
          maximum: 5
        created_at:
          type: string
          format: date-time
        is_starred:
          type: boolean
          description: Whether current user has starred this quote

    QuoteHistory:
      type: object
      properties:
        id:
          type: string
          format: uuid
        quote:
          $ref: '#/components/schemas/Quote'
        delivered_at:
          type: string
          format: date-time
        viewed_at:
          type: string
          format: date-time
          nullable: true
        starred_at:
          type: string
          format: date-time
          nullable: true

    Subscription:
      type: object
      properties:
        id:
          type: string
          format: uuid
        tier:
          type: string
          enum: [FREE, PREMIUM]
        status:
          type: string
          enum: [ACTIVE, CANCELLED, PAST_DUE, INCOMPLETE]
        current_period_end:
          type: string
          format: date-time
        created_at:
          type: string
          format: date-time

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object
            timestamp:
              type: string
              format: date-time
            request_id:
              type: string

paths:
  # Authentication Endpoints
  /auth/register:
    post:
      summary: Register new user account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                timezone:
                  type: string
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid request data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /auth/login:
    post:
      summary: Authenticate user and return JWT token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
      responses:
        '200':
          description: Authentication successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                    example: bearer
                  user:
                    $ref: '#/components/schemas/User'
        '401':
          description: Invalid credentials

  # Quote Endpoints
  /quotes/today:
    get:
      summary: Get today's quote for authenticated user
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Today's quote
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Quote'
        '404':
          description: No quote available for today

  /quotes/{quote_id}/star:
    post:
      summary: Star a quote for future reference
      security:
        - BearerAuth: []
      parameters:
        - name: quote_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Quote starred successfully
        '404':
          description: Quote not found

    delete:
      summary: Remove star from a quote
      security:
        - BearerAuth: []
      parameters:
        - name: quote_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: Star removed successfully

  /quotes/starred:
    get:
      summary: Get user's starred quotes
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: List of starred quotes
          content:
            application/json:
              schema:
                type: object
                properties:
                  quotes:
                    type: array
                    items:
                      $ref: '#/components/schemas/Quote'
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                      limit:
                        type: integer
                      total:
                        type: integer
                      has_next:
                        type: boolean

  /quotes/search:
    get:
      summary: Search quotes (Premium feature)
      security:
        - BearerAuth: []
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
            minLength: 2
        - name: category
          in: query
          schema:
            type: string
            enum: [LEADERSHIP, PHILOSOPHY, BUSINESS, CREATIVITY, WISDOM, DECISION_MAKING]
        - name: starred_only
          in: query
          schema:
            type: boolean
            default: false
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  quotes:
                    type: array
                    items:
                      $ref: '#/components/schemas/Quote'
                  pagination:
                    type: object
        '403':
          description: Premium feature - upgrade required
        '429':
          description: Search rate limit exceeded

  /quotes/history:
    get:
      summary: Get user's quote delivery history
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Quote delivery history
          content:
            application/json:
              schema:
                type: object
                properties:
                  history:
                    type: array
                    items:
                      $ref: '#/components/schemas/QuoteHistory'
                  pagination:
                    type: object

  # User Management
  /user/profile:
    get:
      summary: Get current user profile
      security:
        - BearerAuth: []
      responses:
        '200':
          description: User profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

    patch:
      summary: Update user profile
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                notification_settings:
                  $ref: '#/components/schemas/NotificationSettings'
                timezone:
                  type: string
      responses:
        '200':
          description: Profile updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  # Subscription Management
  /subscription:
    get:
      summary: Get current subscription status
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Current subscription
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Subscription'

  /subscription/upgrade:
    post:
      summary: Upgrade to premium subscription
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                payment_method_id:
                  type: string
                  description: Stripe payment method ID
      responses:
        '200':
          description: Subscription upgraded successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Subscription'
        '402':
          description: Payment required or failed

  /subscription/cancel:
    post:
      summary: Cancel premium subscription
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Subscription cancelled successfully

  # Health Check
  /health:
    get:
      summary: API health check
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  timestamp:
                    type: string
                    format: date-time
```
