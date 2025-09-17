# Testing Strategy

## Testing Pyramid

```
     E2E Tests (10%)
    /              \
   Integration Tests (30%)
  /                    \
Frontend Unit (30%)  Backend Unit (30%)
```

## Test Organization

**Frontend Tests:**
```
apps/mobile/test/
├── unit/                    # Isolated unit tests
│   ├── models/             # Data model tests
│   ├── services/           # API service tests
│   └── utils/              # Utility function tests
├── widget/                 # Flutter widget tests
│   ├── quote_card_test.dart
│   ├── auth_screens_test.dart
│   └── subscription_flows_test.dart
└── integration/            # Integration tests
    ├── quote_flow_test.dart
    ├── auth_flow_test.dart
    └── subscription_flow_test.dart
```

**Backend Tests:**
```
apps/api/tests/
├── unit/                   # Isolated unit tests
│   ├── test_services/      # Business logic tests
│   ├── test_repositories/  # Data access tests
│   └── test_utils/         # Utility tests
├── integration/            # API integration tests
│   ├── test_auth_api.py    # Authentication endpoint tests
│   ├── test_quotes_api.py  # Quote management tests
│   └── test_webhooks.py    # External service integration tests
└── e2e/                    # End-to-end API tests
    └── test_user_journeys.py
```

**E2E Tests:**
```
integration_test/
├── quote_delivery_test.dart    # Daily quote notification flow
├── subscription_upgrade_test.dart # Premium conversion flow
└── search_functionality_test.dart # Premium search features
```

## Test Examples

**Frontend Component Test:**
```dart
void main() {
  group('QuoteCard Widget Tests', () {
    testWidgets('displays quote content and author', (tester) async {
      final mockQuote = Quote(
        id: '1',
        content: 'Test quote content',
        author: 'Test Author',
        category: QuoteCategory.wisdom,
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: QuoteCard(quote: mockQuote),
          ),
        ),
      );

      expect(find.text('Test quote content'), findsOneWidget);
      expect(find.text('— Test Author'), findsOneWidget);
    });

    testWidgets('shows premium upgrade for search when free tier', (tester) async {
      // Test premium feature gating
    });
  });
}
```

**Backend API Test:**
```python
def test_get_todays_quote_requires_authentication(client):
    response = client.get("/api/v1/quotes/today")
    assert response.status_code == 401

def test_get_todays_quote_returns_quote_for_authenticated_user(
    client, authenticated_user
):
    response = client.get(
        "/api/v1/quotes/today",
        headers={"Authorization": f"Bearer {authenticated_user.access_token}"}
    )
    assert response.status_code == 200
    assert "content" in response.json()
    assert "author" in response.json()

def test_search_quotes_requires_premium_subscription(client, free_user):
    response = client.get(
        "/api/v1/quotes/search?q=leadership",
        headers={"Authorization": f"Bearer {free_user.access_token}"}
    )
    assert response.status_code == 403
    assert "premium" in response.json()["error"]["message"].lower()
```

**E2E Test:**
```dart
void main() {
  group('Quote Delivery E2E', () {
    patrolTest('complete daily quote flow', (PatrolTester $) async {
      // Launch app and authenticate
      await $.pumpWidgetAndSettle(MyApp());
      await $.tap(find.text('Login'));
      await $.enterText(find.byType(TextField).first, 'test@example.com');
      await $.enterText(find.byType(TextField).last, 'password123');
      await $.tap(find.text('Sign In'));

      // Verify today's quote is displayed
      await $.waitUntilVisible(find.text('Today\'s Quote'));
      expect($, findsOneWidget(find.byType(QuoteCard)));

      // Test starring functionality
      await $.tap(find.byIcon(Icons.star_outline));
      await $.waitUntilVisible(find.byIcon(Icons.star));

      // Navigate to starred quotes
      await $.tap(find.text('Starred'));
      expect($, findsAtLeastNWidgets(find.byType(QuoteCard), 1));
    });
  });
}
```
