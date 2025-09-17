/// Authentication repository for API communication.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/app_config.dart';
import '../domain/auth_entities.dart';

class AuthRepository {
  final String baseUrl;
  final http.Client _client;

  AuthRepository({
    String? baseUrl,
    http.Client? client,
  }) : baseUrl = baseUrl ?? AppConfig.apiUrl,
       _client = client ?? http.Client();

  /// Register a new user
  Future<User> register(RegisterRequest request) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authRegisterUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return User.fromJson(data);
    } else {
      throw _handleError(response);
    }
  }

  /// Login user
  Future<TokenResponse> login(LoginRequest request) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authLoginUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return TokenResponse.fromJson(data);
    } else {
      throw _handleError(response);
    }
  }

  /// Verify email with token
  Future<void> verifyEmail(String token) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authVerifyEmailUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'token': token}),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Resend verification email
  Future<void> resendVerificationEmail(String email) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authResendVerificationUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'email': email}),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Forgot password
  Future<void> forgotPassword(String email) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authForgotPasswordUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'email': email}),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Reset password with token
  Future<void> resetPassword(String token, String newPassword, String passwordConfirm) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authResetPasswordUrl),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'token': token,
        'new_password': newPassword,
        'password_confirm': passwordConfirm,
      }),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Get current user info
  Future<User> getCurrentUser(String token) async {
    final response = await _client.get(
      Uri.parse(AppConfig.authMeUrl),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return User.fromJson(data);
    } else {
      throw _handleError(response);
    }
  }

  /// Update user profile
  Future<User> updateProfile(String token, Map<String, dynamic> updates) async {
    final response = await _client.put(
      Uri.parse(AppConfig.authMeUrl),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(updates),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return User.fromJson(data);
    } else {
      throw _handleError(response);
    }
  }

  /// Change password
  Future<void> changePassword(
    String token,
    String currentPassword,
    String newPassword,
    String passwordConfirm,
  ) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authChangePasswordUrl),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'current_password': currentPassword,
        'new_password': newPassword,
        'password_confirm': passwordConfirm,
      }),
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Logout (client-side token removal)
  Future<void> logout() async {
    // This is handled client-side by removing the token
    // No API call needed
  }

  /// Deactivate account
  Future<void> deactivateAccount(String token) async {
    final response = await _client.post(
      Uri.parse(AppConfig.authDeactivateUrl),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw _handleError(response);
    }
  }

  /// Handle API errors
  Exception _handleError(http.Response response) {
    try {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final message = data['detail'] as String? ?? 'An error occurred';
      return Exception(message);
    } catch (e) {
      return Exception('An error occurred: ${response.statusCode}');
    }
  }

  void dispose() {
    _client.close();
  }
}
