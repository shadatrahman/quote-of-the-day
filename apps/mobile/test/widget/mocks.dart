/// Mock classes for widget tests.

import 'package:quote_of_the_day_mobile/features/auth/presentation/auth_notifier.dart';
import 'package:quote_of_the_day_mobile/features/auth/domain/auth_entities.dart';

class MockAuthNotifier extends AuthNotifier {
  AuthState _state = const AuthState();
  String? _token;

  @override
  AuthState build() {
    return _state;
  }

  @override
  AuthState get state => _state;

  @override
  String? get token => _token;

  // Mock methods
  Future<void> login(LoginRequest request) async {
    // Mock implementation
  }

  Future<void> register(RegisterRequest request) async {
    // Mock implementation
  }

  Future<void> logout() async {
    _state = const AuthState();
    _token = null;
  }

  Future<void> verifyEmail(String token) async {
    // Mock implementation
  }

  Future<void> resendVerificationEmail(String email) async {
    // Mock implementation
  }

  Future<void> forgotPassword(String email) async {
    // Mock implementation
  }

  Future<void> resetPassword(String token, String newPassword, String passwordConfirm) async {
    // Mock implementation
  }

  Future<void> getCurrentUser() async {
    // Mock implementation
  }

  Future<void> updateProfile(Map<String, dynamic> updates) async {
    // Mock implementation
  }

  Future<void> changePassword(String currentPassword, String newPassword, String passwordConfirm) async {
    // Mock implementation
  }

  Future<void> deactivateAccount() async {
    // Mock implementation
  }

  void clearError() {
    // Mock implementation
  }

  // Helper methods for testing
  void setState(AuthState newState) {
    _state = newState;
  }

  void setToken(String? token) {
    _token = token;
  }
}
