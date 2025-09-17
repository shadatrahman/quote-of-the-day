/// Subscription domain entities for Quote of the Day app.

import '../../../core/models/shared_types.dart';

/// Subscription state for state management
class SubscriptionState {
  final bool isLoading;
  final Subscription? subscription;
  final bool isPremium;
  final Map<String, bool> features;
  final String? error;

  const SubscriptionState({
    this.isLoading = false,
    this.subscription,
    this.isPremium = false,
    this.features = const {},
    this.error,
  });

  SubscriptionState copyWith({
    bool? isLoading,
    Subscription? subscription,
    bool? isPremium,
    Map<String, bool>? features,
    String? error,
  }) {
    return SubscriptionState(
      isLoading: isLoading ?? this.isLoading,
      subscription: subscription ?? this.subscription,
      isPremium: isPremium ?? this.isPremium,
      features: features ?? this.features,
      error: error ?? this.error,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is SubscriptionState && other.isLoading == isLoading && other.subscription == subscription && other.isPremium == isPremium && other.features == features && other.error == error;
  }

  @override
  int get hashCode {
    return isLoading.hashCode ^ subscription.hashCode ^ isPremium.hashCode ^ features.hashCode ^ error.hashCode;
  }
}

/// Subscription feature access helper
class SubscriptionFeatureAccess {
  static const String dailyQuotes = 'daily_quotes';
  static const String basicNotifications = 'basic_notifications';
  static const String quoteStarring = 'quote_starring';
  static const String unlimitedStarredQuotes = 'unlimited_starred_quotes';
  static const String quoteSearch = 'quote_search';
  static const String advancedNotifications = 'advanced_notifications';
  static const String quoteHistory = 'quote_history';
  static const String prioritySupport = 'priority_support';
  static const String exportQuotes = 'export_quotes';
  static const String customQuoteCategories = 'custom_quote_categories';

  /// Check if user has access to a specific feature
  static bool hasAccess(Map<String, bool> features, String feature) {
    return features[feature] ?? false;
  }

  /// Get all available features for a subscription tier
  static Map<String, bool> getFeaturesForTier(SubscriptionTier tier) {
    switch (tier) {
      case SubscriptionTier.premium:
        return {
          dailyQuotes: true,
          basicNotifications: true,
          quoteStarring: true,
          unlimitedStarredQuotes: true,
          quoteSearch: true,
          advancedNotifications: true,
          quoteHistory: true,
          prioritySupport: true,
          exportQuotes: true,
          customQuoteCategories: true,
        };
      case SubscriptionTier.free:
        return {
          dailyQuotes: true,
          basicNotifications: true,
          quoteStarring: true,
          unlimitedStarredQuotes: false,
          quoteSearch: false,
          advancedNotifications: false,
          quoteHistory: false,
          prioritySupport: false,
          exportQuotes: false,
          customQuoteCategories: false,
        };
    }
  }
}
