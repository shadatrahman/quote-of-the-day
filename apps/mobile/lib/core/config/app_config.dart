/// Application configuration management.

class AppConfig {
  static const String _defaultApiBaseUrl = 'http://localhost:8000';
  static const String _defaultApiVersion = 'v1';

  /// API base URL
  static String get apiBaseUrl {
    // In production, this would come from environment variables or build configuration
    // For now, we'll use a simple approach that can be overridden
    return const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: _defaultApiBaseUrl,
    );
  }

  /// API version
  static String get apiVersion => _defaultApiVersion;

  /// Full API URL
  static String get apiUrl => '$apiBaseUrl/api/$apiVersion';

  /// Authentication endpoints
  static String get authRegisterUrl => '$apiUrl/auth/register';
  static String get authLoginUrl => '$apiUrl/auth/login';
  static String get authVerifyEmailUrl => '$apiUrl/auth/verify-email';
  static String get authResendVerificationUrl => '$apiUrl/auth/resend-verification';
  static String get authForgotPasswordUrl => '$apiUrl/auth/forgot-password';
  static String get authResetPasswordUrl => '$apiUrl/auth/reset-password';
  static String get authMeUrl => '$apiUrl/auth/me';
  static String get authChangePasswordUrl => '$apiUrl/auth/change-password';
  static String get authLogoutUrl => '$apiUrl/auth/logout';
  static String get authDeactivateUrl => '$apiUrl/auth/deactivate';

  /// Request timeout in seconds
  static const int requestTimeoutSeconds = 30;

  /// Token storage key
  static const String tokenStorageKey = 'auth_token';

  /// User data storage key
  static const String userDataStorageKey = 'user_data';

  /// App version
  static const String appVersion = '1.0.0';

  /// Debug mode
  static const bool debugMode = bool.fromEnvironment('DEBUG', defaultValue: true);

  /// Environment
  static const String environment = String.fromEnvironment('ENVIRONMENT', defaultValue: 'development');

  /// Is production environment
  static bool get isProduction => environment == 'production';

  /// Is development environment
  static bool get isDevelopment => environment == 'development';
}
