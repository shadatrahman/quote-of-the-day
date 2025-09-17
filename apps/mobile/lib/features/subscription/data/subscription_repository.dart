/// Subscription repository for API calls.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/models/shared_types.dart';

import '../../../core/config/api_config.dart';
import '../../../core/auth/auth_service.dart';

class SubscriptionRepository {
  final http.Client _httpClient;
  final ApiConfig _apiConfig;
  final AuthService _authService;

  SubscriptionRepository({
    required http.Client httpClient,
    required ApiConfig apiConfig,
    required AuthService authService,
  }) : _httpClient = httpClient,
       _apiConfig = apiConfig,
       _authService = authService;

  /// Get current user's subscription status
  Future<SubscriptionStatusResponse> getSubscriptionStatus() async {
    final token = await _authService.getAccessToken();
    if (token == null) {
      throw Exception('User not authenticated');
    }

    final response = await _httpClient.get(
      Uri.parse('${_apiConfig.baseUrl}/api/v1/subscription/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return SubscriptionStatusResponse.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get subscription status');
    }
  }

  /// Upgrade user to premium subscription
  Future<Subscription> upgradeSubscription(
    SubscriptionUpgradeRequest request,
  ) async {
    final token = await _authService.getAccessToken();
    if (token == null) {
      throw Exception('User not authenticated');
    }

    final response = await _httpClient.post(
      Uri.parse('${_apiConfig.baseUrl}/api/v1/subscription/upgrade'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode(request.toJson()),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Subscription.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to upgrade subscription');
    }
  }

  /// Cancel user's premium subscription
  Future<Map<String, dynamic>> cancelSubscription(
    SubscriptionCancelRequest request,
  ) async {
    final token = await _authService.getAccessToken();
    if (token == null) {
      throw Exception('User not authenticated');
    }

    final response = await _httpClient.post(
      Uri.parse('${_apiConfig.baseUrl}/api/v1/subscription/cancel'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode(request.toJson()),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to cancel subscription');
    }
  }

  /// Get available features for current user
  Future<Map<String, bool>> getAvailableFeatures() async {
    final token = await _authService.getAccessToken();
    if (token == null) {
      throw Exception('User not authenticated');
    }

    final response = await _httpClient.get(
      Uri.parse('${_apiConfig.baseUrl}/api/v1/subscription/features'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Map<String, bool>.from(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get available features');
    }
  }

  /// Check if user has access to a specific feature
  Future<bool> checkFeatureAccess(String feature) async {
    final token = await _authService.getAccessToken();
    if (token == null) {
      throw Exception('User not authenticated');
    }

    final response = await _httpClient.get(
      Uri.parse('${_apiConfig.baseUrl}/api/v1/subscription/check/$feature'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['has_access'] ?? false;
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to check feature access');
    }
  }

  /// Get Stripe configuration for client-side integration
  Future<StripeConfig> getStripeConfig() async {
    final response = await _httpClient.get(
      Uri.parse('${_apiConfig.baseUrl}/webhooks/stripe/config'),
      headers: {
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return StripeConfig.fromJson(data);
    } else {
      final error = json.decode(response.body);
      throw Exception(error['detail'] ?? 'Failed to get Stripe configuration');
    }
  }
}
