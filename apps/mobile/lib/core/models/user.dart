/**
 * User model and related types for Quote of the Day application.
 */

class NotificationSettings {
  final bool enabled;
  final String deliveryTime; // HH:MM format
  final bool weekdaysOnly;
  final String? pauseUntil; // ISO date string

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
      pauseUntil: json['pause_until'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'delivery_time': deliveryTime,
      'weekdays_only': weekdaysOnly,
      'pause_until': pauseUntil,
    };
  }
}

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

class User {
  final String id; // UUID primary key
  final String email; // Email for authentication
  final bool isActive; // Account status
  final bool isVerified; // Email verification status
  final SubscriptionTier subscriptionTier; // Default to FREE
  final String timezone; // User's timezone
  final NotificationSettings notificationSettings;
  final String createdAt; // ISO date string
  final String updatedAt; // ISO date string
  final String? lastLoginAt; // ISO date string
  final String? lastQuoteDelivered; // ISO date string

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
      notificationSettings: NotificationSettings.fromJson(json['notification_settings'] as Map<String, dynamic>),
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      lastLoginAt: json['last_login_at'] as String?,
      lastQuoteDelivered: json['last_quote_delivered'] as String?,
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
      'created_at': createdAt,
      'updated_at': updatedAt,
      'last_login_at': lastLoginAt,
      'last_quote_delivered': lastQuoteDelivered,
    };
  }
}

class UserCreate {
  final String email;
  final String password;
  final String passwordConfirm;
  final String timezone;
  final NotificationSettings notificationSettings;

  const UserCreate({
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

class UserUpdate {
  final String? timezone;
  final NotificationSettings? notificationSettings;

  const UserUpdate({
    this.timezone,
    this.notificationSettings,
  });

  Map<String, dynamic> toJson() {
    return {
      if (timezone != null) 'timezone': timezone,
      if (notificationSettings != null) 'notification_settings': notificationSettings!.toJson(),
    };
  }
}

class UserLogin {
  final String email;
  final String password;

  const UserLogin({
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

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
    };
  }
}

class EmailVerificationRequest {
  final String token;

  const EmailVerificationRequest({required this.token});

  Map<String, dynamic> toJson() {
    return {'token': token};
  }
}

class ForgotPasswordRequest {
  final String email;

  const ForgotPasswordRequest({required this.email});

  Map<String, dynamic> toJson() {
    return {'email': email};
  }
}

class ResetPasswordRequest {
  final String token;
  final String newPassword;
  final String passwordConfirm;

  const ResetPasswordRequest({
    required this.token,
    required this.newPassword,
    required this.passwordConfirm,
  });

  Map<String, dynamic> toJson() {
    return {
      'token': token,
      'new_password': newPassword,
      'password_confirm': passwordConfirm,
    };
  }
}

class ChangePasswordRequest {
  final String currentPassword;
  final String newPassword;
  final String passwordConfirm;

  const ChangePasswordRequest({
    required this.currentPassword,
    required this.newPassword,
    required this.passwordConfirm,
  });

  Map<String, dynamic> toJson() {
    return {
      'current_password': currentPassword,
      'new_password': newPassword,
      'password_confirm': passwordConfirm,
    };
  }
}

class ApiError {
  final String code;
  final String message;
  final String timestamp;
  final String? requestId;

  const ApiError({
    required this.code,
    required this.message,
    required this.timestamp,
    this.requestId,
  });

  factory ApiError.fromJson(Map<String, dynamic> json) {
    return ApiError(
      code: json['code'] as String,
      message: json['message'] as String,
      timestamp: json['timestamp'] as String,
      requestId: json['request_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'code': code,
      'message': message,
      'timestamp': timestamp,
      if (requestId != null) 'request_id': requestId,
    };
  }
}
