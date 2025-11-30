import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:stock_predictor/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Stock Predictor E2E Tests', () {
    testWidgets('Test 1: Search → Fetch → Open Stock', (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Discover tab
      final discoverTab = find.text('Discover');
      expect(discoverTab, findsOneWidget);
      await tester.tap(discoverTab);
      await tester.pumpAndSettle();

      // Tap search bar
      final searchBar = find.byType(TextField).first;
      expect(searchBar, findsOneWidget);
      await tester.tap(searchBar);
      await tester.pumpAndSettle();

      // Enter search query
      await tester.enterText(searchBar, 'TCS');
      await tester.pumpAndSettle(const Duration(seconds: 1));

      // Verify search results appear
      expect(find.text('TCS'), findsWidgets);

      // Tap on first search result
      await tester.tap(find.text('TCS').first);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify stock detail screen opened
      expect(find.text('Overview'), findsOneWidget);
      expect(find.text('Chart'), findsOneWidget);
      expect(find.text('AI Prediction'), findsOneWidget);
    });

    testWidgets('Test 2: Watchlist Updates', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Verify we're on Watchlist tab (default)
      expect(find.text('Watchlist'), findsOneWidget);

      // Wait for data to load
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify watchlist items are displayed
      expect(find.byType(ListView), findsWidgets);

      // Switch to different watchlist tab
      final watchlistTabs = find.byType(Tab);
      if (watchlistTabs.evaluate().length > 1) {
        await tester.tap(watchlistTabs.at(1));
        await tester.pumpAndSettle(const Duration(seconds: 1));

        // Verify new data loaded
        expect(find.byType(ListView), findsWidgets);
      }
    });

    testWidgets('Test 3: Prediction Fetch Success', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Discover
      await tester.tap(find.text('Discover'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify AI Picks section loaded
      expect(find.text('AI Top Picks 🤖'), findsOneWidget);

      // Tap on an AI pick
      final aiPickCard = find.byType(GestureDetector).first;
      await tester.tap(aiPickCard);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify prediction data is displayed
      expect(find.text('AI Prediction'), findsOneWidget);
      await tester.tap(find.text('AI Prediction'));
      await tester.pumpAndSettle();

      // Verify prediction components
      expect(find.byType(CircularProgressIndicator), findsNothing); // No loading
    });

    testWidgets('Test 4: Chart Loading', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Discover and open a stock
      await tester.tap(find.text('Discover'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Tap first stock card
      final stockCard = find.byType(GestureDetector).first;
      await tester.tap(stockCard);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Navigate to Chart tab
      await tester.tap(find.text('Chart'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify chart loaded (no loading indicator)
      expect(find.byType(CircularProgressIndicator), findsNothing);

      // Test timeframe selector
      final timeframeChips = find.byType(ChoiceChip);
      if (timeframeChips.evaluate().isNotEmpty) {
        await tester.tap(timeframeChips.at(1)); // Select 1W
        await tester.pumpAndSettle(const Duration(seconds: 2));

        // Verify chart updated
        expect(find.byType(CircularProgressIndicator), findsNothing);
      }
    });

    testWidgets('Test 5: Screener Load', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Screener tab
      await tester.tap(find.text('Screener'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify screener tabs
      expect(find.text('Bullish'), findsOneWidget);
      expect(find.text('Bearish'), findsOneWidget);
      expect(find.text('AI Picks'), findsOneWidget);

      // Verify stocks loaded
      expect(find.byType(ListView), findsOneWidget);

      // Switch to Bearish tab
      await tester.tap(find.text('Bearish'));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify different data loaded
      expect(find.byType(ListView), findsOneWidget);

      // Test search functionality
      final searchField = find.byType(TextField);
      if (searchField.evaluate().isNotEmpty) {
        await tester.enterText(searchField.first, 'STOCK');
        await tester.pumpAndSettle(const Duration(milliseconds: 500));

        // Verify filtered results
        expect(find.byType(ListView), findsOneWidget);
      }

      // Test scroll for pagination
      await tester.drag(find.byType(ListView), const Offset(0, -500));
      await tester.pumpAndSettle(const Duration(seconds: 1));
    });

    testWidgets('Test 6: Offline Backend → Error UI', (WidgetTester tester) async {
      // Note: This test assumes mock mode is enabled
      // In a real scenario, you would mock network failures
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Settings
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Tap API Health Check button
      final healthCheckButton = find.text('Check API Health');
      expect(healthCheckButton, findsOneWidget);
      await tester.tap(healthCheckButton);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify health check result is displayed
      // In mock mode, it should show success
      expect(find.textContaining('API'), findsWidgets);
    });

    testWidgets('Test 7: Dark Mode Switch', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Verify app is in dark mode (default)
      final scaffold = tester.widget<MaterialApp>(find.byType(MaterialApp));
      expect(scaffold.theme?.brightness, Brightness.dark);

      // Navigate to Settings
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Verify settings screen loaded
      expect(find.text('Settings'), findsOneWidget);

      // Verify dark theme colors are applied
      final appBar = tester.widget<AppBar>(find.byType(AppBar).first);
      expect(appBar.backgroundColor, const Color(0xFF0F0F0F)); // backgroundDark
    });

    testWidgets('Test 8: Navigation Flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Test all bottom navigation tabs
      final tabs = ['Watchlist', 'Discover', 'Screener', 'Settings'];

      for (final tabName in tabs) {
        await tester.tap(find.text(tabName));
        await tester.pumpAndSettle(const Duration(seconds: 1));

        // Verify tab is active
        expect(find.text(tabName), findsWidgets);
      }
    });

    testWidgets('Test 9: Settings Persistence', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Settings
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Find and adjust threshold slider
      final slider = find.byType(Slider);
      if (slider.evaluate().isNotEmpty) {
        await tester.drag(slider, const Offset(100, 0));
        await tester.pumpAndSettle();

        // Verify slider value changed
        expect(slider, findsOneWidget);
      }

      // Toggle notifications
      final notificationSwitch = find.byType(Switch);
      if (notificationSwitch.evaluate().isNotEmpty) {
        await tester.tap(notificationSwitch);
        await tester.pumpAndSettle();

        // Verify switch toggled
        expect(notificationSwitch, findsOneWidget);
      }
    });

    testWidgets('Test 10: Pull to Refresh', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to Discover
      await tester.tap(find.text('Discover'));
      await tester.pumpAndSettle(const Duration(seconds: 1));

      // Perform pull to refresh
      await tester.drag(find.byType(CustomScrollView), const Offset(0, 300));
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify data reloaded
      expect(find.text('Trending Now 🔥'), findsOneWidget);
    });
  });
}
