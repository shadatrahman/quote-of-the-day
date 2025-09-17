/// Unit tests for authentication repository.

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:quote_of_the_day_mobile/features/auth/data/auth_repository.dart';
import 'package:quote_of_the_day_mobile/features/auth/domain/auth_entities.dart';

import 'auth_repository_test.mocks.dart';

@GenerateMocks([http.Client])
void main() {
  group('AuthRepository', () {
    late AuthRepository repository;
    late MockClient mockClient;

    setUp(() {
      mockClient = MockClient();
      repository = AuthRepository(
        baseUrl: 'http://test-server:8000', // Use test server URL
        client: mockClient,
      );
    });

    tearDown(() {
      repository.dispose();
    });

    group('register', () {
      test('should return User when registration is successful', () async {
        // Arrange
        final request = RegisterRequest(
          email: 'test@example.com',
          password: 'TestPassword123',
          passwordConfirm: 'TestPassword123',
          timezone: 'UTC',
          notificationSettings: const NotificationSettings(
            enabled: true,
            deliveryTime: '09:00',
            weekdaysOnly: false,
          ),
        );

        final responseBody = '''
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "email": "test@example.com",
          "is_active": true,
          "is_verified": false,
          "subscription_tier": "FREE",
          "timezone": "UTC",
          "notification_settings": {
            "enabled": true,
            "delivery_time": "09:00",
            "weekdays_only": false,
            "pause_until": null
          },
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T00:00:00Z",
          "last_login_at": null,
          "last_quote_delivered": null
        }
        ''';

        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/register'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response(responseBody, 201));

        // Act
        final result = await repository.register(request);

        // Assert
        expect(result.email, equals('test@example.com'));
        expect(result.isActive, equals(true));
        expect(result.isVerified, equals(false));
        expect(result.subscriptionTier, equals(SubscriptionTier.free));
        expect(result.timezone, equals('UTC'));
      });

      test('should throw Exception when registration fails', () async {
        // Arrange
        final request = RegisterRequest(
          email: 'test@example.com',
          password: 'TestPassword123',
          passwordConfirm: 'TestPassword123',
          timezone: 'UTC',
          notificationSettings: const NotificationSettings(
            enabled: true,
            deliveryTime: '09:00',
            weekdaysOnly: false,
          ),
        );

        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/register'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Email already exists"}', 409));

        // Act & Assert
        expect(
          () => repository.register(request),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('login', () {
      test('should return TokenResponse when login is successful', () async {
        // Arrange
        final request = LoginRequest(
          email: 'test@example.com',
          password: 'TestPassword123',
        );

        final responseBody = '''
        {
          "access_token": "test_token",
          "token_type": "bearer",
          "expires_in": 1800,
          "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "is_active": true,
            "is_verified": true,
            "subscription_tier": "FREE",
            "timezone": "UTC",
            "notification_settings": {
              "enabled": true,
              "delivery_time": "09:00",
              "weekdays_only": false,
              "pause_until": null
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "last_login_at": null,
            "last_quote_delivered": null
          }
        }
        ''';

        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/login'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response(responseBody, 200));

        // Act
        final result = await repository.login(request);

        // Assert
        expect(result.accessToken, equals('test_token'));
        expect(result.tokenType, equals('bearer'));
        expect(result.expiresIn, equals(1800));
        expect(result.user.email, equals('test@example.com'));
      });

      test('should throw Exception when login fails', () async {
        // Arrange
        final request = LoginRequest(
          email: 'test@example.com',
          password: 'wrongpassword',
        );

        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/login'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Invalid credentials"}', 401));

        // Act & Assert
        expect(
          () => repository.login(request),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('verifyEmail', () {
      test('should complete successfully when verification is valid', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/verify-email'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"message": "Email verified successfully"}', 200));

        // Act
        await repository.verifyEmail('test_token');

        // Assert
        verify(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/verify-email'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).called(1);
      });

      test('should throw Exception when verification fails', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/verify-email'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Invalid token"}', 400));

        // Act & Assert
        expect(
          () => repository.verifyEmail('invalid_token'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('forgotPassword', () {
      test('should complete successfully when email is valid', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/forgot-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"message": "Reset email sent"}', 200));

        // Act
        await repository.forgotPassword('test@example.com');

        // Assert
        verify(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/forgot-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).called(1);
      });

      test('should throw Exception when request fails', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/forgot-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Email not found"}', 404));

        // Act & Assert
        expect(
          () => repository.forgotPassword('nonexistent@example.com'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('resetPassword', () {
      test('should complete successfully when reset is valid', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/reset-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"message": "Password reset successfully"}', 200));

        // Act
        await repository.resetPassword('test_token', 'NewPassword123', 'NewPassword123');

        // Assert
        verify(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/reset-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).called(1);
      });

      test('should throw Exception when reset fails', () async {
        // Arrange
        when(
          mockClient.post(
            Uri.parse('http://localhost:8000/api/v1/auth/reset-password'),
            headers: anyNamed('headers'),
            body: anyNamed('body'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Invalid token"}', 400));

        // Act & Assert
        expect(
          () => repository.resetPassword('invalid_token', 'NewPassword123', 'NewPassword123'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('getCurrentUser', () {
      test('should return User when request is successful', () async {
        // Arrange
        final responseBody = '''
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "email": "test@example.com",
          "is_active": true,
          "is_verified": true,
          "subscription_tier": "FREE",
          "timezone": "UTC",
          "notification_settings": {
            "enabled": true,
            "delivery_time": "09:00",
            "weekdays_only": false,
            "pause_until": null
          },
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T00:00:00Z",
          "last_login_at": null,
          "last_quote_delivered": null
        }
        ''';

        when(
          mockClient.get(
            Uri.parse('http://localhost:8000/api/v1/auth/me'),
            headers: anyNamed('headers'),
          ),
        ).thenAnswer((_) async => http.Response(responseBody, 200));

        // Act
        final result = await repository.getCurrentUser('test_token');

        // Assert
        expect(result.email, equals('test@example.com'));
        expect(result.isActive, equals(true));
        expect(result.isVerified, equals(true));
        expect(result.subscriptionTier, equals(SubscriptionTier.free));
      });

      test('should throw Exception when request fails', () async {
        // Arrange
        when(
          mockClient.get(
            Uri.parse('http://localhost:8000/api/v1/auth/me'),
            headers: anyNamed('headers'),
          ),
        ).thenAnswer((_) async => http.Response('{"detail": "Unauthorized"}', 401));

        // Act & Assert
        expect(
          () => repository.getCurrentUser('invalid_token'),
          throwsA(isA<Exception>()),
        );
      });
    });
  });
}
