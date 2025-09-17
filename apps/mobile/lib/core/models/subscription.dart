/**
 * Subscription model and related types for Quote of the Day application.
 */

import 'user.dart';

enum SubscriptionStatus {
  active('ACTIVE'),
  cancelled('CANCELLED'),
  pastDue('PAST_DUE'),
  incomplete('INCOMPLETE');

  const SubscriptionStatus(this.value);
  final String value;

  static SubscriptionStatus fromString(String value) {
    return SubscriptionStatus.values.firstWhere(
      (status) => status.value == value,
      orElse: () => SubscriptionStatus.incomplete,
    );
  }
}

class Subscription {
  final String id; // UUID primary key
  final String userId; // Foreign key to User
  final SubscriptionTier tier; // Subscription level
  final SubscriptionStatus status; // Payment status
  final String? stripeCustomerId; // Stripe customer reference
  final String? stripeSubscriptionId; // Stripe subscription reference
  final String? currentPeriodStart; // Billing cycle start (ISO date)
  final String? currentPeriodEnd; // Billing cycle end (ISO date)
  final String? cancelledAt; // Cancellation timestamp (ISO date)
  final String createdAt; // Subscription creation (ISO date)
  final String updatedAt; // Last update (ISO date)

  const Subscription({
    required this.id,
    required this.userId,
    required this.tier,
    required this.status,
    this.stripeCustomerId,
    this.stripeSubscriptionId,
    this.currentPeriodStart,
    this.currentPeriodEnd,
    this.cancelledAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      tier: SubscriptionTier.fromString(json['tier'] as String),
      status: SubscriptionStatus.fromString(json['status'] as String),
      stripeCustomerId: json['stripe_customer_id'] as String?,
      stripeSubscriptionId: json['stripe_subscription_id'] as String?,
      currentPeriodStart: json['current_period_start'] as String?,
      currentPeriodEnd: json['current_period_end'] as String?,
      cancelledAt: json['cancelled_at'] as String?,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'tier': tier.value,
      'status': status.value,
      'stripe_customer_id': stripeCustomerId,
      'stripe_subscription_id': stripeSubscriptionId,
      'current_period_start': currentPeriodStart,
      'current_period_end': currentPeriodEnd,
      'cancelled_at': cancelledAt,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }
}

class SubscriptionCreate {
  final SubscriptionTier tier;
  final String? stripeCustomerId;
  final String? stripeSubscriptionId;
  final String? currentPeriodStart;
  final String? currentPeriodEnd;

  const SubscriptionCreate({
    required this.tier,
    this.stripeCustomerId,
    this.stripeSubscriptionId,
    this.currentPeriodStart,
    this.currentPeriodEnd,
  });

  Map<String, dynamic> toJson() {
    return {
      'tier': tier.value,
      if (stripeCustomerId != null) 'stripe_customer_id': stripeCustomerId,
      if (stripeSubscriptionId != null) 'stripe_subscription_id': stripeSubscriptionId,
      if (currentPeriodStart != null) 'current_period_start': currentPeriodStart,
      if (currentPeriodEnd != null) 'current_period_end': currentPeriodEnd,
    };
  }
}

class SubscriptionUpdate {
  final SubscriptionStatus? status;
  final String? stripeCustomerId;
  final String? stripeSubscriptionId;
  final String? currentPeriodStart;
  final String? currentPeriodEnd;
  final String? cancelledAt;

  const SubscriptionUpdate({
    this.status,
    this.stripeCustomerId,
    this.stripeSubscriptionId,
    this.currentPeriodStart,
    this.currentPeriodEnd,
    this.cancelledAt,
  });

  Map<String, dynamic> toJson() {
    return {
      if (status != null) 'status': status!.value,
      if (stripeCustomerId != null) 'stripe_customer_id': stripeCustomerId,
      if (stripeSubscriptionId != null) 'stripe_subscription_id': stripeSubscriptionId,
      if (currentPeriodStart != null) 'current_period_start': currentPeriodStart,
      if (currentPeriodEnd != null) 'current_period_end': currentPeriodEnd,
      if (cancelledAt != null) 'cancelled_at': cancelledAt,
    };
  }
}

class SubscriptionUpgradeRequest {
  final String paymentMethodId;

  const SubscriptionUpgradeRequest({required this.paymentMethodId});

  Map<String, dynamic> toJson() {
    return {'payment_method_id': paymentMethodId};
  }
}

class SubscriptionCancelRequest {
  final String? reason;

  const SubscriptionCancelRequest({this.reason});

  Map<String, dynamic> toJson() {
    return {
      if (reason != null) 'reason': reason,
    };
  }
}

class SubscriptionFeatures {
  final bool dailyQuotes;
  final bool basicNotifications;
  final bool quoteStarring;
  final bool unlimitedStarredQuotes;
  final bool quoteSearch;
  final bool advancedNotifications;
  final bool quoteHistory;
  final bool prioritySupport;
  final bool exportQuotes;
  final bool customQuoteCategories;

  const SubscriptionFeatures({
    required this.dailyQuotes,
    required this.basicNotifications,
    required this.quoteStarring,
    required this.unlimitedStarredQuotes,
    required this.quoteSearch,
    required this.advancedNotifications,
    required this.quoteHistory,
    required this.prioritySupport,
    required this.exportQuotes,
    required this.customQuoteCategories,
  });

  factory SubscriptionFeatures.fromJson(Map<String, dynamic> json) {
    return SubscriptionFeatures(
      dailyQuotes: json['daily_quotes'] as bool,
      basicNotifications: json['basic_notifications'] as bool,
      quoteStarring: json['quote_starring'] as bool,
      unlimitedStarredQuotes: json['unlimited_starred_quotes'] as bool,
      quoteSearch: json['quote_search'] as bool,
      advancedNotifications: json['advanced_notifications'] as bool,
      quoteHistory: json['quote_history'] as bool,
      prioritySupport: json['priority_support'] as bool,
      exportQuotes: json['export_quotes'] as bool,
      customQuoteCategories: json['custom_quote_categories'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'daily_quotes': dailyQuotes,
      'basic_notifications': basicNotifications,
      'quote_starring': quoteStarring,
      'unlimited_starred_quotes': unlimitedStarredQuotes,
      'quote_search': quoteSearch,
      'advanced_notifications': advancedNotifications,
      'quote_history': quoteHistory,
      'priority_support': prioritySupport,
      'export_quotes': exportQuotes,
      'custom_quote_categories': customQuoteCategories,
    };
  }
}

class SubscriptionStatusResponse {
  final Subscription? subscription;
  final bool isPremium;
  final SubscriptionFeatures features;

  const SubscriptionStatusResponse({
    this.subscription,
    required this.isPremium,
    required this.features,
  });

  factory SubscriptionStatusResponse.fromJson(Map<String, dynamic> json) {
    return SubscriptionStatusResponse(
      subscription: json['subscription'] != null ? Subscription.fromJson(json['subscription'] as Map<String, dynamic>) : null,
      isPremium: json['is_premium'] as bool,
      features: SubscriptionFeatures.fromJson(json['features'] as Map<String, dynamic>),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (subscription != null) 'subscription': subscription!.toJson(),
      'is_premium': isPremium,
      'features': features.toJson(),
    };
  }
}

class StripeConfig {
  final String publishableKey;
  final String premiumPriceId;

  const StripeConfig({
    required this.publishableKey,
    required this.premiumPriceId,
  });

  factory StripeConfig.fromJson(Map<String, dynamic> json) {
    return StripeConfig(
      publishableKey: json['publishable_key'] as String,
      premiumPriceId: json['premium_price_id'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'publishable_key': publishableKey,
      'premium_price_id': premiumPriceId,
    };
  }
}

class StripeWebhookEvent {
  final String id;
  final String type;
  final Map<String, dynamic> data;
  final int created;

  const StripeWebhookEvent({
    required this.id,
    required this.type,
    required this.data,
    required this.created,
  });

  factory StripeWebhookEvent.fromJson(Map<String, dynamic> json) {
    return StripeWebhookEvent(
      id: json['id'] as String,
      type: json['type'] as String,
      data: json['data'] as Map<String, dynamic>,
      created: json['created'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'data': data,
      'created': created,
    };
  }
}

// Common API response types
class ApiResponse<T> {
  final T? data;
  final ApiError? error;
  final Map<String, dynamic>? meta;

  const ApiResponse({
    this.data,
    this.error,
    this.meta,
  });

  factory ApiResponse.fromJson(Map<String, dynamic> json, T Function(Map<String, dynamic>) fromJsonT) {
    return ApiResponse(
      data: json['data'] != null ? fromJsonT(json['data'] as Map<String, dynamic>) : null,
      error: json['error'] != null ? ApiError.fromJson(json['error'] as Map<String, dynamic>) : null,
      meta: json['meta'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson(Map<String, dynamic> Function(T) toJsonT) {
    return {
      if (data != null) 'data': toJsonT(data as T),
      if (error != null) 'error': error!.toJson(),
      if (meta != null) 'meta': meta,
    };
  }
}

class PaginatedResponse<T> extends ApiResponse<List<T>> {
  final int total;
  final int page;
  final int limit;
  final int totalPages;

  const PaginatedResponse({
    required this.total,
    required this.page,
    required this.limit,
    required this.totalPages,
    super.data,
    super.error,
  });

  factory PaginatedResponse.fromJson(Map<String, dynamic> json, T Function(Map<String, dynamic>) fromJsonT) {
    final meta = json['meta'] as Map<String, dynamic>;
    return PaginatedResponse(
      total: meta['total'] as int,
      page: meta['page'] as int,
      limit: meta['limit'] as int,
      totalPages: meta['total_pages'] as int,
      data: json['data'] != null ? (json['data'] as List).map((item) => fromJsonT(item as Map<String, dynamic>)).toList() : null,
      error: json['error'] != null ? ApiError.fromJson(json['error'] as Map<String, dynamic>) : null,
    );
  }
}
