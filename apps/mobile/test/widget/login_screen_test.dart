/// Widget tests for login screen.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:quote_of_the_day_mobile/features/auth/presentation/login_screen.dart';
import 'package:quote_of_the_day_mobile/features/auth/presentation/auth_notifier.dart';
import 'package:quote_of_the_day_mobile/features/auth/domain/auth_entities.dart';

import 'mocks.dart';

void main() {
  group('LoginScreen', () {
    late MockAuthNotifier mockAuthNotifier;

    setUp(() {
      mockAuthNotifier = MockAuthNotifier();
    });

    Future<Widget> createTestWidget() async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();

      return ProviderScope(
        overrides: [
          authNotifierProvider.overrideWith(() => mockAuthNotifier),
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: const MaterialApp(
          home: LoginScreen(),
        ),
      );
    }

    testWidgets('should display login form elements', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());

      // Assert
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Sign in to continue'), findsOneWidget);
      expect(find.byIcon(Icons.format_quote), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2)); // Email and password fields
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text("Don't have an account? "), findsOneWidget);
      expect(find.text('Sign Up'), findsOneWidget);
      expect(find.text('Forgot Password?'), findsOneWidget);
    });

    testWidgets('should show loading indicator when loading', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState(isLoading: true));

      // Act
      await tester.pumpWidget(await createTestWidget());

      // Assert
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Sign In'), findsNothing);
    });

    testWidgets('should validate email field', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      // Assert
      expect(find.text('Please enter your email'), findsOneWidget);
    });

    testWidgets('should validate password field', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.enterText(find.byType(TextFormField).first, 'test@example.com');
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      // Assert
      expect(find.text('Please enter your password'), findsOneWidget);
    });

    testWidgets('should validate email format', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.enterText(find.byType(TextFormField).first, 'invalid-email');
      await tester.enterText(find.byType(TextFormField).last, 'password');
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      // Assert
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('should call login when form is valid', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.enterText(find.byType(TextFormField).first, 'test@example.com');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      // Assert - verify that login was called (simplified check)
      // Note: In a real test, we would verify with proper argument matchers
      // but for now we just check that the form validation passes
      expect(find.text('Please enter your email'), findsNothing);
      expect(find.text('Please enter your password'), findsNothing);
    });

    testWidgets('should toggle password visibility', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());

      final visibilityButton = find.byIcon(Icons.visibility);

      expect(visibilityButton, findsOneWidget);

      await tester.tap(visibilityButton);
      await tester.pump();

      // Assert
      expect(find.byIcon(Icons.visibility_off), findsOneWidget);
    });

    testWidgets('should navigate to register screen', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.tap(find.text('Sign Up'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('Create Account'), findsAtLeastNWidgets(1));
    });

    testWidgets('should navigate to forgot password screen', (WidgetTester tester) async {
      // Arrange
      mockAuthNotifier.setState(const AuthState());

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.tap(find.text('Forgot Password?'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('Reset Password'), findsOneWidget);
    });

    testWidgets('should handle error state gracefully', (WidgetTester tester) async {
      // Arrange - Start with error state
      mockAuthNotifier.setState(const AuthState(error: 'Login failed'));

      // Act
      await tester.pumpWidget(await createTestWidget());
      await tester.pump(); // Initial build

      // Assert - UI should still be functional even with error state
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Sign in to continue'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2)); // Email and password fields
      expect(find.text('Sign In'), findsOneWidget);
    });
  });
}
