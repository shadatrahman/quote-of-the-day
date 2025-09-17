/// Mock classes for testing.

import 'package:mockito/mockito.dart';
import 'package:quote_of_the_day_mobile/features/auth/presentation/auth_notifier.dart';
import 'package:quote_of_the_day_mobile/features/auth/domain/auth_entities.dart';

class MockAuthNotifier extends Mock implements AuthNotifier {
  @override
  AuthState get state => super.noSuchMethod(
    Invocation.getter(#state),
    returnValue: const AuthState(),
  );

  @override
  Future<void> login(LoginRequest request) => super.noSuchMethod(
    Invocation.method(#login, [request]),
    returnValue: Future.value(),
  );

  @override
  Future<void> register(RegisterRequest request) => super.noSuchMethod(
    Invocation.method(#register, [request]),
    returnValue: Future.value(),
  );

  @override
  Future<void> logout() => super.noSuchMethod(
    Invocation.method(#logout, []),
    returnValue: Future.value(),
  );

  @override
  Future<void> verifyEmail(String token) => super.noSuchMethod(
    Invocation.method(#verifyEmail, [token]),
    returnValue: Future.value(),
  );

  @override
  Future<void> resendVerificationEmail(String email) => super.noSuchMethod(
    Invocation.method(#resendVerificationEmail, [email]),
    returnValue: Future.value(),
  );

  @override
  Future<void> forgotPassword(String email) => super.noSuchMethod(
    Invocation.method(#forgotPassword, [email]),
    returnValue: Future.value(),
  );

  @override
  Future<void> resetPassword(String token, String newPassword, String passwordConfirm) => super.noSuchMethod(
    Invocation.method(#resetPassword, [token, newPassword, passwordConfirm]),
    returnValue: Future.value(),
  );

  @override
  Future<void> getCurrentUser() => super.noSuchMethod(
    Invocation.method(#getCurrentUser, []),
    returnValue: Future.value(),
  );

  @override
  Future<void> updateProfile(Map<String, dynamic> updates) => super.noSuchMethod(
    Invocation.method(#updateProfile, [updates]),
    returnValue: Future.value(),
  );

  @override
  Future<void> changePassword(String currentPassword, String newPassword, String passwordConfirm) => super.noSuchMethod(
    Invocation.method(#changePassword, [currentPassword, newPassword, passwordConfirm]),
    returnValue: Future.value(),
  );

  @override
  Future<void> deactivateAccount() => super.noSuchMethod(
    Invocation.method(#deactivateAccount, []),
    returnValue: Future.value(),
  );

  @override
  void clearError() => super.noSuchMethod(
    Invocation.method(#clearError, []),
    returnValue: null,
  );
}
