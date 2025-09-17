import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:quote_of_the_day_mobile/main.dart';

void main() {
  group('HomePage Unit Tests', () {
    testWidgets('HomePage constructor', (WidgetTester tester) async {
      // Test that HomePage can be instantiated
      const homePage = HomePage();
      expect(homePage, isA<StatelessWidget>());
      expect(homePage.key, isNull);
    });

    testWidgets('HomePage with custom key', (WidgetTester tester) async {
      // Test HomePage with a custom key
      const key = Key('home_page_test_key');
      const homePage = HomePage(key: key);
      expect(homePage.key, key);
    });

    testWidgets('HomePage build method returns Scaffold', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify that build method returns a Scaffold
      final scaffold = find.byType(Scaffold);
      expect(scaffold, findsOneWidget);
    });

    testWidgets('HomePage AppBar configuration', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Find the AppBar widget
      final appBarFinder = find.byType(AppBar);
      expect(appBarFinder, findsOneWidget);

      final AppBar appBar = tester.widget(appBarFinder);

      // Verify AppBar title
      expect(appBar.title, isA<Text>());
      final Text titleWidget = appBar.title as Text;
      expect(titleWidget.data, 'Quote of the Day');
    });

    testWidgets('HomePage body structure', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Verify body structure
      expect(find.byType(Center), findsOneWidget);

      // Find the text widget inside the Center
      final textFinder = find.descendant(of: find.byType(Center), matching: find.byType(Text));
      expect(textFinder, findsOneWidget);

      final Text textWidget = tester.widget(textFinder);
      expect(textWidget.data, 'Welcome to Quote of the Day!');
      expect(textWidget.style?.fontSize, 24);
    });

    testWidgets('HomePage text styling', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: MaterialApp(home: HomePage())));

      // Find the welcome text
      final textFinder = find.text('Welcome to Quote of the Day!');
      expect(textFinder, findsOneWidget);

      final Text textWidget = tester.widget(textFinder);
      expect(textWidget.style, isNotNull);
      expect(textWidget.style?.fontSize, 24);
    });

    testWidgets('HomePage responds to BuildContext', (WidgetTester tester) async {
      late BuildContext capturedContext;

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Builder(
              builder: (context) {
                capturedContext = context;
                return const HomePage();
              },
            ),
          ),
        ),
      );

      // Verify that HomePage can access theme from context
      final theme = Theme.of(capturedContext);
      expect(theme, isNotNull);
      expect(theme.colorScheme, isNotNull);
    });
  });

  group('QuoteOfTheDayApp Unit Tests', () {
    testWidgets('QuoteOfTheDayApp constructor', (WidgetTester tester) async {
      // Test that QuoteOfTheDayApp can be instantiated
      const app = QuoteOfTheDayApp();
      expect(app, isA<StatelessWidget>());
      expect(app.key, isNull);
    });

    testWidgets('QuoteOfTheDayApp with custom key', (WidgetTester tester) async {
      // Test QuoteOfTheDayApp with a custom key
      const key = Key('app_test_key');
      const app = QuoteOfTheDayApp(key: key);
      expect(app.key, key);
    });

    testWidgets('QuoteOfTheDayApp build method returns MaterialApp', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      // Verify that build method returns a MaterialApp
      final materialApp = find.byType(MaterialApp);
      expect(materialApp, findsOneWidget);
    });

    testWidgets('QuoteOfTheDayApp MaterialApp configuration', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      final MaterialApp app = tester.widget(find.byType(MaterialApp));

      // Verify MaterialApp configuration
      expect(app.title, 'Quote of the Day');
      expect(app.theme, isNotNull);
      expect(app.theme?.useMaterial3, true);
      expect(app.theme?.colorScheme, isNotNull);
      expect(app.home, isA<HomePage>());
    });

    testWidgets('QuoteOfTheDayApp theme configuration', (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: QuoteOfTheDayApp()));

      final MaterialApp app = tester.widget(find.byType(MaterialApp));
      final theme = app.theme;

      expect(theme, isNotNull);
      expect(theme?.useMaterial3, true);
      expect(theme?.colorScheme, isNotNull);

      // Verify color scheme is based on deep purple
      final colorScheme = theme?.colorScheme;
      expect(colorScheme?.primary, isNotNull);
    });
  });

  group('Widget Properties Tests', () {
    test('HomePage is StatelessWidget', () {
      const homePage = HomePage();
      expect(homePage, isA<StatelessWidget>());
    });

    test('QuoteOfTheDayApp is StatelessWidget', () {
      const app = QuoteOfTheDayApp();
      expect(app, isA<StatelessWidget>());
    });

    testWidgets('Widgets handle null keys gracefully', (WidgetTester tester) async {
      // Test that widgets work with null keys
      const homePage = HomePage(key: null);

      await tester.pumpWidget(ProviderScope(child: MaterialApp(home: homePage)));

      expect(find.byType(HomePage), findsOneWidget);
      expect(find.byWidget(homePage), findsOneWidget);
    });

    testWidgets('Widgets maintain identity with keys', (WidgetTester tester) async {
      const key1 = Key('test_key_1');
      const key2 = Key('test_key_2');

      const homePage1 = HomePage(key: key1);
      const homePage2 = HomePage(key: key2);

      // Test that widgets with different keys are different
      expect(homePage1.key, isNot(equals(homePage2.key)));
      expect(homePage1, isNot(same(homePage2)));
    });
  });
}
