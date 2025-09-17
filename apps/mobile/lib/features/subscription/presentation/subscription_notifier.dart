/// Subscription notifier for state management using Riverpod.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/shared_types.dart';
import 'package:http/http.dart' as http;

import '../../../core/config/api_config.dart';
import '../../../core/auth/auth_service.dart';
import '../data/subscription_repository.dart';
import '../domain/subscription_entities.dart';

/// API configuration provider
final apiConfigProvider = Provider<ApiConfig>((ref) {
  return ApiConfig.defaultConfig();
});

/// HTTP client provider
final httpClientProvider = Provider<http.Client>((ref) {
  return http.Client();
});

/// Auth service provider
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService();
});

/// Subscription repository provider
final subscriptionRepositoryProvider = Provider<SubscriptionRepository>((ref) {
  final apiConfig = ref.watch(apiConfigProvider);
  final httpClient = ref.watch(httpClientProvider);
  final authService = ref.watch(authServiceProvider);

  return SubscriptionRepository(
    httpClient: httpClient,
    apiConfig: apiConfig,
    authService: authService,
  );
});

/// Subscription state notifier
class SubscriptionNotifier extends Notifier<SubscriptionState> {
  late final SubscriptionRepository _repository;

  @override
  SubscriptionState build() {
    _repository = ref.watch(subscriptionRepositoryProvider);
    return const SubscriptionState();
  }

  /// Load subscription status
  Future<void> loadSubscriptionStatus() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final statusResponse = await _repository.getSubscriptionStatus();
      state = state.copyWith(
        isLoading: false,
        subscription: statusResponse.subscription,
        isPremium: statusResponse.isPremium,
        features: statusResponse.features.toJson().map((key, value) => MapEntry(key, value as bool)),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Upgrade to premium subscription
  Future<void> upgradeToPremium(String paymentMethodId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final request = SubscriptionUpgradeRequest(
        paymentMethodId: paymentMethodId,
      );
      await _repository.upgradeSubscription(request);

      // Reload subscription status to get updated features
      await loadSubscriptionStatus();
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Cancel subscription
  Future<void> cancelSubscription({String? reason}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final request = SubscriptionCancelRequest(reason: reason);
      await _repository.cancelSubscription(request);

      // Reload subscription status to get updated state
      await loadSubscriptionStatus();
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Check feature access
  Future<bool> checkFeatureAccess(String feature) async {
    try {
      return await _repository.checkFeatureAccess(feature);
    } catch (e) {
      // If check fails, return false for safety
      return false;
    }
  }

  /// Get available features
  Future<Map<String, bool>> getAvailableFeatures() async {
    try {
      return await _repository.getAvailableFeatures();
    } catch (e) {
      // Return free tier features if request fails
      return SubscriptionFeatureAccess.getFeaturesForTier(SubscriptionTier.free);
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Refresh subscription status
  Future<void> refresh() async {
    await loadSubscriptionStatus();
  }
}

/// Subscription state provider
final subscriptionStateProvider = NotifierProvider<SubscriptionNotifier, SubscriptionState>(() {
  return SubscriptionNotifier();
});

/// Current subscription provider
final currentSubscriptionProvider = Provider<Subscription?>((ref) {
  final subscriptionState = ref.watch(subscriptionStateProvider);
  return subscriptionState.subscription;
});

/// Is premium provider
final isPremiumProvider = Provider<bool>((ref) {
  final subscriptionState = ref.watch(subscriptionStateProvider);
  return subscriptionState.isPremium;
});

/// Available features provider
final availableFeaturesProvider = Provider<Map<String, bool>>((ref) {
  final subscriptionState = ref.watch(subscriptionStateProvider);
  return subscriptionState.features;
});

/// Feature access provider
final featureAccessProvider = Provider.family<bool, String>((ref, feature) {
  final features = ref.watch(availableFeaturesProvider);
  return SubscriptionFeatureAccess.hasAccess(features, feature);
});
