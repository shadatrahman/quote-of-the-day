# Frontend Architecture

## Component Architecture

Flutter component organization following clean architecture principles with feature-based directory structure optimized for the premium quote delivery experience.

### Component Organization
```
apps/mobile/lib/
├── core/
│   ├── constants/         # App-wide constants and enums
│   ├── theme/            # Material 3 theme configuration
│   ├── utils/            # Shared utility functions
│   └── error/            # Global error handling
├── features/
│   ├── auth/
│   │   ├── data/         # Auth repository implementations
│   │   ├── domain/       # Auth entities and use cases
│   │   └── presentation/ # Auth screens and widgets
│   ├── quotes/
│   │   ├── data/         # Quote repository and models
│   │   ├── domain/       # Quote business logic
│   │   └── presentation/ # Quote display screens
│   ├── subscription/
│   │   ├── data/         # Stripe integration
│   │   ├── domain/       # Subscription logic
│   │   └── presentation/ # Premium upgrade screens
│   └── settings/
│       ├── data/         # User preferences storage
│       ├── domain/       # Settings entities
│       └── presentation/ # Settings screens
├── shared/
│   ├── widgets/          # Reusable UI components
│   ├── models/           # Shared data models from packages/shared
│   └── services/         # API client and platform services
└── main.dart            # App entry point and routing
```

### Component Template
```dart
// Base stateless widget template for quote-related components
abstract class QuoteWidget extends StatelessWidget {
  const QuoteWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer(
      builder: (context, ref, child) {
        final themeData = Theme.of(context);
        final quote = ref.watch(currentQuoteProvider);

        return quote.when(
          data: (quoteData) => buildQuoteContent(context, quoteData, themeData),
          loading: () => const QuoteShimmer(),
          error: (error, stack) => QuoteErrorWidget(error: error),
        );
      },
    );
  }

  Widget buildQuoteContent(BuildContext context, Quote quote, ThemeData theme);
}

// Example implementation for daily quote display
class DailyQuoteCard extends QuoteWidget {
  const DailyQuoteCard({super.key});

  @override
  Widget buildQuoteContent(BuildContext context, Quote quote, ThemeData theme) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              quote.content,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w400,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    '— ${quote.author}',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontStyle: FontStyle.italic,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                QuoteActionButtons(quote: quote),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

## State Management Architecture

Riverpod-based reactive state management with clear separation between UI state, business logic, and data access.

### State Structure
```dart
// Core providers structure
final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider));
});

final currentUserProvider = Provider<AsyncValue<User?>>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.user;
});

final subscriptionProvider = FutureProvider<Subscription>((ref) async {
  final authRepo = ref.watch(authRepositoryProvider);
  final user = await ref.watch(currentUserProvider.future);
  if (user == null) throw UnauthorizedException();
  return ref.watch(subscriptionRepositoryProvider).getCurrentSubscription();
});

// Quote-specific state management
final currentQuoteProvider = FutureProvider<Quote>((ref) async {
  final quoteRepo = ref.watch(quoteRepositoryProvider);
  return quoteRepo.getTodaysQuote();
});

final starredQuotesProvider = FutureProvider<List<Quote>>((ref) async {
  final quoteRepo = ref.watch(quoteRepositoryProvider);
  return quoteRepo.getStarredQuotes();
});

final quoteSearchProvider = StateNotifierProvider.family<QuoteSearchNotifier,
    AsyncValue<List<Quote>>, String>((ref, query) {
  return QuoteSearchNotifier(
    ref.watch(quoteRepositoryProvider),
    ref.watch(subscriptionProvider),
  );
});

// Settings and preferences
final notificationSettingsProvider = StateNotifierProvider<NotificationSettingsNotifier,
    NotificationSettings>((ref) {
  return NotificationSettingsNotifier(
    ref.watch(userRepositoryProvider),
    ref.watch(currentUserProvider),
  );
});
```

### State Management Patterns
- **Repository Pattern with Riverpod**: Data access abstraction with provider dependency injection
- **StateNotifier for Complex State**: User interactions, search queries, settings modifications
- **FutureProvider for Async Data**: API calls, database queries, external service integration
- **Family Providers for Parameterized State**: Search queries, paginated lists, dynamic filters
- **AsyncValue Error Handling**: Consistent error boundaries across all async operations
- **Provider Composition**: Dependent providers for subscription-gated features

## Routing Architecture

Flutter auto_route-based navigation with authentication guards and premium feature gates.

### Route Organization
```
/                          # Root route - redirects based on auth state
├── /onboarding           # First-time user setup flow
├── /auth/                # Authentication screens
│   ├── /auth/login       # Sign in screen
│   ├── /auth/register    # Sign up screen
│   └── /auth/forgot      # Password reset screen
├── /home                 # Main quote display (authenticated)
├── /quotes/              # Quote-related screens
│   ├── /quotes/starred   # Starred quotes collection
│   ├── /quotes/history   # Historical archive
│   └── /quotes/search    # Premium search (with paywall)
├── /subscription/        # Premium subscription management
│   ├── /subscription/upgrade    # Premium upgrade flow
│   └── /subscription/manage     # Current subscription settings
└── /settings             # User preferences and account settings
```

### Protected Route Pattern
```dart
@AutoRouterConfig()
class AppRouter extends _$AppRouter {
  @override
  List<AutoRoute> get routes => [
    // Redirect root based on auth state
    AutoRoute(
      page: SplashRoute.page,
      path: '/',
      initial: true,
    ),

    // Auth flow
    AutoRoute(
      page: AuthWrapperRoute.page,
      path: '/auth',
      children: [
        AutoRoute(page: LoginRoute.page, path: '/login'),
        AutoRoute(page: RegisterRoute.page, path: '/register'),
      ],
    ),

    // Protected app routes
    AutoRoute(
      page: AppWrapperRoute.page,
      path: '/app',
      guards: [AuthGuard],
      children: [
        AutoRoute(page: HomeRoute.page, path: '/home', initial: true),
        AutoRoute(
          page: SearchRoute.page,
          path: '/search',
          guards: [PremiumGuard], // Premium feature protection
        ),
        AutoRoute(page: StarredRoute.page, path: '/starred'),
        AutoRoute(page: SettingsRoute.page, path: '/settings'),
      ],
    ),

    // Premium subscription flow
    AutoRoute(
      page: SubscriptionWrapperRoute.page,
      path: '/subscription',
      guards: [AuthGuard],
      children: [
        AutoRoute(page: UpgradeRoute.page, path: '/upgrade'),
        AutoRoute(page: ManageRoute.page, path: '/manage'),
      ],
    ),
  ];
}

// Authentication guard implementation
class AuthGuard extends AutoRouteGuard {
  @override
  void onNavigation(NavigationResolver resolver, StackRouter router) {
    final container = ProviderScope.containerOf(router.navigatorKey.currentContext!);
    final authState = container.read(authStateProvider);

    if (authState.isAuthenticated) {
      resolver.next();
    } else {
      router.pushAndClearStack(const AuthWrapperRoute());
    }
  }
}

// Premium feature guard with elegant paywall
class PremiumGuard extends AutoRouteGuard {
  @override
  void onNavigation(NavigationResolver resolver, StackRouter router) async {
    final container = ProviderScope.containerOf(router.navigatorKey.currentContext!);
    final subscription = await container.read(subscriptionProvider.future);

    if (subscription.tier == SubscriptionTier.premium) {
      resolver.next();
    } else {
      // Show premium upgrade modal instead of blocking navigation
      showDialog(
        context: router.navigatorKey.currentContext!,
        builder: (context) => PremiumUpgradeModal(
          feature: 'Advanced Search',
          onUpgrade: () => router.pushPath('/subscription/upgrade'),
        ),
      );
    }
  }
}
```

## Frontend Services Layer

API client setup with authentication, error handling, and offline-first capabilities for quote caching.

### API Client Setup
```dart
// HTTP client with authentication and retry logic
final httpClientProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
  ));

  // Add authentication interceptor
  dio.interceptors.add(AuthInterceptor(ref));

  // Add retry logic for network failures
  dio.interceptors.add(RetryInterceptor(
    dio: dio,
    logPrint: (message) => logger.d(message),
    retries: 3,
    retryDelays: const [
      Duration(seconds: 1),
      Duration(seconds: 2),
      Duration(seconds: 3),
    ],
  ));

  // Add response/error logging
  if (kDebugMode) {
    dio.interceptors.add(PrettyDioLogger(
      requestHeader: true,
      requestBody: true,
      responseHeader: false,
      responseBody: true,
      error: true,
    ));
  }

  return dio;
});

// Authentication interceptor for JWT token handling
class AuthInterceptor extends Interceptor {
  final Ref ref;

  AuthInterceptor(this.ref);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final authState = ref.read(authStateProvider);
    if (authState.isAuthenticated && authState.token != null) {
      options.headers['Authorization'] = 'Bearer ${authState.token}';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      // Token expired - refresh or logout
      ref.read(authStateProvider.notifier).logout();
    }
    handler.next(err);
  }
}
```

### Service Example
```dart
// Quote service with offline-first caching strategy
abstract class QuoteRepository {
  Future<Quote> getTodaysQuote();
  Future<List<Quote>> getStarredQuotes({int page = 1});
  Future<List<Quote>> searchQuotes(String query, {QuoteCategory? category});
  Future<void> starQuote(String quoteId);
  Future<void> unstarQuote(String quoteId);
}

class ApiQuoteRepository implements QuoteRepository {
  final Dio _httpClient;
  final SharedPreferences _prefs;
  final Database _localDb;

  ApiQuoteRepository(this._httpClient, this._prefs, this._localDb);

  @override
  Future<Quote> getTodaysQuote() async {
    try {
      // Try to get today's quote from API
      final response = await _httpClient.get('/quotes/today');
      final quote = Quote.fromJson(response.data);

      // Cache locally for offline access
      await _cacheQuote(quote);

      return quote;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError) {
        // Fallback to cached quote if offline
        final cachedQuote = await _getCachedTodaysQuote();
        if (cachedQuote != null) return cachedQuote;
      }
      rethrow;
    }
  }

  @override
  Future<List<Quote>> searchQuotes(String query, {QuoteCategory? category}) async {
    // Premium feature - check subscription before API call
    final subscription = await ref.read(subscriptionProvider.future);
    if (subscription.tier != SubscriptionTier.premium) {
      throw PremiumFeatureException('Search requires premium subscription');
    }

    final response = await _httpClient.get('/quotes/search',
      queryParameters: {
        'q': query,
        if (category != null) 'category': category.name,
      },
    );

    return (response.data['quotes'] as List)
        .map((json) => Quote.fromJson(json))
        .toList();
  }

  @override
  Future<void> starQuote(String quoteId) async {
    // Optimistic update - update local state immediately
    await _updateLocalStarStatus(quoteId, true);

    try {
      await _httpClient.post('/quotes/$quoteId/star');
    } catch (e) {
      // Rollback optimistic update on failure
      await _updateLocalStarStatus(quoteId, false);
      rethrow;
    }
  }

  // Private helper methods for caching and offline support
  Future<void> _cacheQuote(Quote quote) async {
    await _localDb.insert('cached_quotes', quote.toJson());
  }

  Future<Quote?> _getCachedTodaysQuote() async {
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final cached = await _localDb.query(
      'cached_quotes',
      where: 'date = ?',
      whereArgs: [today],
      limit: 1,
    );

    return cached.isNotEmpty ? Quote.fromJson(cached.first) : null;
  }
}

// Provider registration for dependency injection
final quoteRepositoryProvider = Provider<QuoteRepository>((ref) {
  return ApiQuoteRepository(
    ref.watch(httpClientProvider),
    ref.watch(sharedPreferencesProvider),
    ref.watch(localDatabaseProvider),
  );
});
```
