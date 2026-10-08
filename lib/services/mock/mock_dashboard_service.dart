import '../dashboard_service.dart';
import '../../models/dashboard_stats.dart';
import '../../models/recent_scan.dart';
import 'mock_data.dart';

class MockDashboardService implements DashboardService {
  @override
  Future<DashboardStats> getStats() async {
    await Future.delayed(const Duration(milliseconds: 350));
    return MockData.stats;
  }

  @override
  Future<List<RecentScan>> getRecentScans({String? query, String? status}) async {
    await Future.delayed(const Duration(milliseconds: 350));
    var list = List<RecentScan>.from(MockData.recentScans);

    if (status != null && status.toUpperCase() != 'ALL') {
      list = list
          .where((s) => s.overallStatus.toUpperCase() == status.toUpperCase())
          .toList();
    }

    if (query != null && query.trim().isNotEmpty) {
      final q = query.trim().toLowerCase();
      list = list.where((s) {
        return s.productName.toLowerCase().contains(q) ||
            s.brandName.toLowerCase().contains(q) ||
            (s.storeName?.toLowerCase().contains(q) ?? false);
      }).toList();
    }

    return list;
  }
}
