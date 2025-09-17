/// Authentication state management with Riverpod.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../domain/auth_entities.dart';
import '../data/auth_repository.dart';

/// Provider for SharedPreferences
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be initialized');
});

/// Provider for AuthRepository
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(); // Uses AppConfig.apiUrl by default
});

/// Provider for AuthNotifier
final authNotifierProvider = NotifierProvider<AuthNotifier, AuthState>(() {
  return AuthNotifier();
});

/// Provider for current user
final currentUserProvider = Provider<User?>((ref) {
  final authState = ref.watch(authNotifierProvider);
  return authState.user;
});

/// Provider for authentication status
final isAuthenticatedProvider = Provider<bool>((ref) {
  final authState = ref.watch(authNotifierProvider);
  return authState.isAuthenticated;
});

/// Authentication notifier
class AuthNotifier extends Notifier<AuthState> {
  late final AuthRepository _repository;
  late final SharedPreferences _prefs;

  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';

  @override
  AuthState build() {
    _repository = ref.watch(authRepositoryProvider);
    _prefs = ref.watch(sharedPreferencesProvider);
    _loadStoredAuth();
    return const AuthState();
  }

  /// Load stored authentication data
  Future<void> _loadStoredAuth() async {
    try {
      final token = _prefs.getString(_tokenKey);
      if (token != null) {
        final userData = _prefs.getString(_userKey);
        if (userData != null) {
          final userJson = jsonDecode(userData) as Map<String, dynamic>;
          final user = User.fromJson(userJson);
          state = state.setUser(user);
        }
      }
    } catch (e) {
      // Clear invalid stored data
      await _clearStoredAuth();
    }
  }

  /// Store authentication data
  Future<void> _storeAuth(String token, User user) async {
    await _prefs.setString(_tokenKey, token);
    await _prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  /// Clear stored authentication data
  Future<void> _clearStoredAuth() async {
    await _prefs.remove(_tokenKey);
    await _prefs.remove(_userKey);
  }

  /// Register a new user
  Future<void> register(RegisterRequest request) async {
    state = state.setLoading(true);
    try {
      final user = await _repository.register(request);
      state = state.setUser(user);
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Login user
  Future<void> login(LoginRequest request) async {
    state = state.setLoading(true);
    try {
      final tokenResponse = await _repository.login(request);
      await _storeAuth(tokenResponse.accessToken, tokenResponse.user);
      state = state.setUser(tokenResponse.user);
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Verify email
  Future<void> verifyEmail(String token) async {
    state = state.setLoading(true);
    try {
      await _repository.verifyEmail(token);
      // Update user verification status
      if (state.user != null) {
        final updatedUser = state.user!.copyWith(isVerified: true);
        state = state.setUser(updatedUser);
        await _storeAuth(_prefs.getString(_tokenKey)!, updatedUser);
      }
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Resend verification email
  Future<void> resendVerificationEmail(String email) async {
    state = state.setLoading(true);
    try {
      await _repository.resendVerificationEmail(email);
      state = state.clearError();
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Forgot password
  Future<void> forgotPassword(String email) async {
    state = state.setLoading(true);
    try {
      await _repository.forgotPassword(email);
      state = state.clearError();
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Reset password
  Future<void> resetPassword(String token, String newPassword, String passwordConfirm) async {
    state = state.setLoading(true);
    try {
      await _repository.resetPassword(token, newPassword, passwordConfirm);
      state = state.clearError();
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Get current user info
  Future<void> getCurrentUser() async {
    final token = _prefs.getString(_tokenKey);
    if (token == null) return;

    state = state.setLoading(true);
    try {
      final user = await _repository.getCurrentUser(token);
      state = state.setUser(user);
      await _storeAuth(token, user);
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Update user profile
  Future<void> updateProfile(Map<String, dynamic> updates) async {
    final token = _prefs.getString(_tokenKey);
    if (token == null) return;

    state = state.setLoading(true);
    try {
      final user = await _repository.updateProfile(token, updates);
      state = state.setUser(user);
      await _storeAuth(token, user);
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Change password
  Future<void> changePassword(String currentPassword, String newPassword, String passwordConfirm) async {
    final token = _prefs.getString(_tokenKey);
    if (token == null) return;

    state = state.setLoading(true);
    try {
      await _repository.changePassword(token, currentPassword, newPassword, passwordConfirm);
      state = state.clearError();
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Logout
  Future<void> logout() async {
    await _clearStoredAuth();
    state = const AuthState();
  }

  /// Deactivate account
  Future<void> deactivateAccount() async {
    final token = _prefs.getString(_tokenKey);
    if (token == null) return;

    state = state.setLoading(true);
    try {
      await _repository.deactivateAccount(token);
      await _clearStoredAuth();
      state = const AuthState();
    } catch (e) {
      state = state.setError(e.toString());
    }
  }

  /// Clear error
  void clearError() {
    state = state.clearError();
  }

  /// Get stored token
  String? get token => _prefs.getString(_tokenKey);
}
