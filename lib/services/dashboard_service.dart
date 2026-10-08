import '../models/dashboard_stats.dart';
import '../models/recent_scan.dart';

abstract class DashboardService {
  Future<DashboardStats> getStats();
  Future<List<RecentScan>> getRecentScans({String? query, String? status});
}
