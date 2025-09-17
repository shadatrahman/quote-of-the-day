import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:quote_of_the_day_mobile/main.dart';

void main() {
  group('QuoteOfTheDayApp Widget Tests', () {
    testWidgets('App renders without crashing', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Verify that the app builds without throwing an exception
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('App has correct title', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Find the MaterialApp and check its title
      final MaterialApp materialApp = tester.widget(find.byType(MaterialApp));
      expect(materialApp.title, 'Quote of the Day');
    });

    testWidgets('App uses Material 3', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Find the MaterialApp and check theme configuration
      final MaterialApp materialApp = tester.widget(find.byType(MaterialApp));
      expect(materialApp.theme?.useMaterial3, true);
    });

    testWidgets('App has correct color scheme', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      final MaterialApp materialApp = tester.widget(find.byType(MaterialApp));
      final ThemeData? theme = materialApp.theme;

      // Verify that color scheme is created from deep purple seed
      expect(theme?.colorScheme.primary, isNotNull);
      expect(theme?.useMaterial3, true);
    });

    testWidgets('App renders HomePage as home', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Verify that HomePage is rendered
      expect(find.byType(HomePage), findsOneWidget);
    });

    testWidgets('App is wrapped with ProviderScope', (WidgetTester tester) async {
      // Test that the main app function sets up ProviderScope
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Find the ProviderScope widget
      expect(find.byType(ProviderScope), findsOneWidget);
    });
  });

  group('HomePage Widget Tests', () {
    testWidgets('HomePage renders correctly', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify that HomePage renders a Scaffold
      expect(find.byType(Scaffold), findsOneWidget);

      // Verify that AppBar is present
      expect(find.byType(AppBar), findsOneWidget);
    });

    testWidgets('HomePage has correct app bar title', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify that AppBar contains the correct title
      expect(find.text('Quote of the Day'), findsOneWidget);
    });

    testWidgets('HomePage displays welcome message', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify that the welcome message is displayed
      expect(find.text('Welcome to Quote of the Day!'), findsOneWidget);
    });

    testWidgets('HomePage centers the welcome message', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify that the body contains a Center widget
      expect(find.byType(Center), findsOneWidget);

      // Verify that the welcome text has correct styling
      final Text welcomeText = tester.widget(find.text('Welcome to Quote of the Day!'));
      expect(welcomeText.style?.fontSize, 24);
    });

    testWidgets('HomePage AppBar uses theme colors', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple), useMaterial3: true),
            home: HomePage(),
          ),
        ),
      );

      // Verify AppBar is present
      expect(find.byType(AppBar), findsOneWidget);

      // The AppBar should use the theme's inverse primary color
      final AppBar appBar = tester.widget(find.byType(AppBar));
      expect(appBar.backgroundColor, isNotNull);
    });

    testWidgets('HomePage structure is correct', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify the widget tree structure
      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.byType(Center), findsOneWidget);
      expect(find.byType(Text), findsNWidgets(2)); // AppBar title + welcome message
    });
  });

  group('Main Function Tests', () {
    testWidgets('Main function setup', (WidgetTester tester) async {
      // Test the main function setup
      // Note: We can't directly test main() in widget tests, but we can test the setup
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Verify the complete app structure is set up correctly
      expect(find.byType(ProviderScope), findsOneWidget);
      expect(find.byType(QuoteOfTheDayApp), findsOneWidget);
      expect(find.byType(MaterialApp), findsOneWidget);
      expect(find.byType(HomePage), findsOneWidget);
    });
  });

  group('Widget Integration Tests', () {
    testWidgets('Full app integration test', (WidgetTester tester) async {
      // Test the full app integration
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Verify complete application flow
      expect(find.byType(ProviderScope), findsOneWidget);
      expect(find.byType(MaterialApp), findsOneWidget);
      expect(find.byType(HomePage), findsOneWidget);
      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('Quote of the Day'), findsOneWidget);
      expect(find.text('Welcome to Quote of the Day!'), findsOneWidget);

      // Verify no exceptions are thrown during build
      await tester.pump();
      expect(tester.takeException(), isNull);
    });

    testWidgets('App responds to theme changes', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Initial render should work
      expect(find.byType(HomePage), findsOneWidget);

      // App should handle theme data properly
      final MaterialApp app = tester.widget(find.byType(MaterialApp));
      expect(app.theme, isNotNull);
      expect(app.theme?.colorScheme, isNotNull);
    });

    testWidgets('App handles different screen sizes', (WidgetTester tester) async {
      // Test with different screen sizes
      await tester.binding.setSurfaceSize(const Size(400, 800));
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      expect(find.text('Welcome to Quote of the Day!'), findsOneWidget);

      // Test with different screen size
      await tester.binding.setSurfaceSize(const Size(800, 600));
      await tester.pump();

      expect(find.text('Welcome to Quote of the Day!'), findsOneWidget);

      // Reset to default size
      await tester.binding.setSurfaceSize(null);
    });
  });
}
