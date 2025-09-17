/// API configuration for HTTP requests.

import 'app_config.dart';

class ApiConfig {
  final String baseUrl;
  final int timeoutSeconds;

  const ApiConfig({
    required this.baseUrl,
    this.timeoutSeconds = 30,
  });

  /// Default API configuration
  factory ApiConfig.defaultConfig() {
    return ApiConfig(
      baseUrl: AppConfig.apiBaseUrl,
      timeoutSeconds: AppConfig.requestTimeoutSeconds,
    );
  }

  /// Get full API URL
  String get apiUrl => '$baseUrl/api/${AppConfig.apiVersion}';

  /// Subscription endpoints
  String get subscriptionUrl => '$apiUrl/subscription';
  String get subscriptionUpgradeUrl => '$apiUrl/subscription/upgrade';
  String get subscriptionCancelUrl => '$apiUrl/subscription/cancel';
  String get subscriptionFeaturesUrl => '$apiUrl/subscription/features';
  String get subscriptionCheckUrl => '$apiUrl/subscription/check';
  String get stripeConfigUrl => '$baseUrl/webhooks/stripe/config';
}
