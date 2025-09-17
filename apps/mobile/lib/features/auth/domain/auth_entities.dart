/// Authentication domain entities for Quote of the Day app.

enum SubscriptionTier {
  free('FREE'),
  premium('PREMIUM');

  const SubscriptionTier(this.value);
  final String value;

  static SubscriptionTier fromString(String value) {
    return SubscriptionTier.values.firstWhere(
      (tier) => tier.value == value,
      orElse: () => SubscriptionTier.free,
    );
  }
}

class NotificationSettings {
  final bool enabled;
  final String deliveryTime;
  final bool weekdaysOnly;
  final DateTime? pauseUntil;

  const NotificationSettings({
    required this.enabled,
    required this.deliveryTime,
    required this.weekdaysOnly,
    this.pauseUntil,
  });

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      enabled: json['enabled'] as bool,
      deliveryTime: json['delivery_time'] as String,
      weekdaysOnly: json['weekdays_only'] as bool,
      pauseUntil: json['pause_until'] != null ? DateTime.parse(json['pause_until'] as String) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'delivery_time': deliveryTime,
      'weekdays_only': weekdaysOnly,
      'pause_until': pauseUntil?.toIso8601String(),
    };
  }

  NotificationSettings copyWith({
    bool? enabled,
    String? deliveryTime,
    bool? weekdaysOnly,
    DateTime? pauseUntil,
  }) {
    return NotificationSettings(
      enabled: enabled ?? this.enabled,
      deliveryTime: deliveryTime ?? this.deliveryTime,
      weekdaysOnly: weekdaysOnly ?? this.weekdaysOnly,
      pauseUntil: pauseUntil ?? this.pauseUntil,
    );
  }
}

class User {
  final String id;
  final String email;
  final bool isActive;
  final bool isVerified;
  final SubscriptionTier subscriptionTier;
  final String timezone;
  final NotificationSettings notificationSettings;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastLoginAt;
  final DateTime? lastQuoteDelivered;

  const User({
    required this.id,
    required this.email,
    required this.isActive,
    required this.isVerified,
    required this.subscriptionTier,
    required this.timezone,
    required this.notificationSettings,
    required this.createdAt,
    required this.updatedAt,
    this.lastLoginAt,
    this.lastQuoteDelivered,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      isActive: json['is_active'] as bool,
      isVerified: json['is_verified'] as bool,
      subscriptionTier: SubscriptionTier.fromString(json['subscription_tier'] as String),
      timezone: json['timezone'] as String,
      notificationSettings: NotificationSettings.fromJson(
        json['notification_settings'] as Map<String, dynamic>,
      ),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      lastLoginAt: json['last_login_at'] != null ? DateTime.parse(json['last_login_at'] as String) : null,
      lastQuoteDelivered: json['last_quote_delivered'] != null ? DateTime.parse(json['last_quote_delivered'] as String) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'is_active': isActive,
      'is_verified': isVerified,
      'subscription_tier': subscriptionTier.value,
      'timezone': timezone,
      'notification_settings': notificationSettings.toJson(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
      'last_quote_delivered': lastQuoteDelivered?.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    bool? isActive,
    bool? isVerified,
    SubscriptionTier? subscriptionTier,
    String? timezone,
    NotificationSettings? notificationSettings,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLoginAt,
    DateTime? lastQuoteDelivered,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      subscriptionTier: subscriptionTier ?? this.subscriptionTier,
      timezone: timezone ?? this.timezone,
      notificationSettings: notificationSettings ?? this.notificationSettings,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      lastQuoteDelivered: lastQuoteDelivered ?? this.lastQuoteDelivered,
    );
  }

  bool get isPremium => subscriptionTier == SubscriptionTier.premium;
}

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }

  AuthState clearError() {
    return copyWith(error: null);
  }

  AuthState setLoading(bool loading) {
    return copyWith(isLoading: loading);
  }

  AuthState setUser(User? user) {
    return copyWith(
      user: user,
      isAuthenticated: user != null,
      error: null,
    );
  }

  AuthState setError(String error) {
    return copyWith(
      error: error,
      isLoading: false,
    );
  }
}

class LoginRequest {
  final String email;
  final String password;

  const LoginRequest({
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }
}

class RegisterRequest {
  final String email;
  final String password;
  final String passwordConfirm;
  final String timezone;
  final NotificationSettings notificationSettings;

  const RegisterRequest({
    required this.email,
    required this.password,
    required this.passwordConfirm,
    required this.timezone,
    required this.notificationSettings,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'password_confirm': passwordConfirm,
      'timezone': timezone,
      'notification_settings': notificationSettings.toJson(),
    };
  }
}

class TokenResponse {
  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  const TokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> json) {
    return TokenResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}
