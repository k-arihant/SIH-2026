import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:metroscan/main.dart';
import 'package:metroscan/widgets/stat_card.dart';

void main() {
  testWidgets('MetroScanApp smoke test - boots cleanly into splash screen',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MetroScanApp(),
      ),
    );

    // Initial frame displays METRO and SCAN headers
    expect(find.text('METRO'), findsOneWidget);
    expect(find.text('SCAN'), findsOneWidget);

    // Advance past splash transition timer
    await tester.pump(const Duration(milliseconds: 1500));
    await tester.pumpAndSettle();
  });

  testWidgets('StatCard onTap callback is triggered on user tap',
      (WidgetTester tester) async {
    bool tapped = false;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StatCard(
            title: 'Violations Flagged',
            value: '12',
            icon: Icons.gavel,
            accentColor: Colors.red,
            onTap: () {
              tapped = true;
            },
          ),
        ),
      ),
    );

    expect(find.text('Violations Flagged'), findsOneWidget);
    expect(find.text('12'), findsOneWidget);

    await tester.tap(find.text('Violations Flagged'));
    await tester.pump();

    expect(tapped, isTrue);
  });
}
