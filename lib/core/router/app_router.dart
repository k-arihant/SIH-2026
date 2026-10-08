import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../../models/user_role.dart';
import '../../screens/splash/splash_screen.dart';
import '../../screens/auth/login_screen.dart';
import '../../screens/dashboard/inspector_dashboard_screen.dart';
import '../../screens/dashboard/consumer_dashboard_screen.dart';
import '../../screens/inspection/camera_inspection_screen.dart';
import '../../screens/inspection/processing_screen.dart';
import '../../screens/inspection/scorecard_screen.dart';
import '../../screens/history/scan_history_screen.dart';
import '../../screens/history/inspection_details_screen.dart';
import '../../screens/pdf_preview/pdf_preview_screen.dart';
import '../../screens/inspection/ocr_result_screen.dart';
import '../../screens/map/gis_heatmap_screen.dart';
import '../../screens/profile/profile_screen.dart';
import '../../screens/consumer/consumer_rights_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        builder: (context, state) {
          final auth = ref.watch(authStateProvider);
          if (auth.user?.role == UserRole.consumer) {
            return const ConsumerDashboardScreen();
          }
          return const InspectorDashboardScreen();
        },
      ),
      GoRoute(
        path: '/inspect',
        builder: (context, state) => const CameraInspectionScreen(),
      ),
      GoRoute(
        path: '/processing',
        builder: (context, state) => const ProcessingScreen(),
      ),
      GoRoute(
        path: '/scorecard/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? 'sample-scan';
          return ScorecardScreen(scanId: id);
        },
      ),
      GoRoute(
        path: '/history',
        builder: (context, state) => const ScanHistoryScreen(),
      ),
      GoRoute(
        path: '/inspection-details/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return InspectionDetailsScreen(scanId: id);
        },
      ),
      GoRoute(
        path: '/pdf-preview/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return PdfPreviewScreen(scanId: id);
        },
      ),
      GoRoute(
        path: '/gis-map',
        builder: (context, state) => const GisHeatmapScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/report/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return PdfPreviewScreen(scanId: id);
        },
      ),
      GoRoute(
        path: '/inspector-dashboard',
        builder: (context, state) => const InspectorDashboardScreen(),
      ),
      GoRoute(
        path: '/consumer-dashboard',
        builder: (context, state) => const ConsumerDashboardScreen(),
      ),
      GoRoute(
        path: '/ocr-result',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          final ocrJson = extra['ocrJson'] as Map<String, dynamic>? ?? {};
          final imagePath = extra['imagePath'] as String? ?? '';
          final localSavedJsonPath = extra['localSavedJsonPath'] as String? ?? '';
          return OcrResultScreen(
            ocrJson: ocrJson,
            imagePath: imagePath,
            localSavedJsonPath: localSavedJsonPath,
          );
        },
      ),
      GoRoute(
        path: '/consumer-rights',
        builder: (context, state) => const ConsumerRightsScreen(),
      ),
    ],
  );
});
