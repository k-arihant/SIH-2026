import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/dashboard_stats.dart';
import '../models/recent_scan.dart';
import 'dashboard_service.dart';
import 'mock/mock_data.dart';

class HttpDashboardService implements DashboardService {
  @override
  Future<DashboardStats> getStats() async {
    try {
      final res = await http.get(
        Uri.parse(ApiConstants.dashboardStatsUrl),
      ).timeout(const Duration(seconds: 4));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        return DashboardStats.fromJson(data);
      }
    } catch (_) {
      // Fallback to sample stats
    }
    return MockData.stats;
  }

  @override
  Future<List<RecentScan>> getRecentScans({String? query, String? status}) async {
    try {
      final queryParams = <String, String>{};
      if (query != null && query.isNotEmpty) queryParams['q'] = query;
      if (status != null && status.isNotEmpty && status != 'ALL') {
        queryParams['status'] = status;
      }

      final uri = Uri.parse(ApiConstants.dashboardRecentScansUrl).replace(
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final res = await http.get(uri).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final list = jsonDecode(res.body) as List<dynamic>;
        return list
            .map((item) => RecentScan.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Fallback
    }

    var list = MockData.recentScans;
    if (status != null && status != 'ALL') {
      list = list.where((s) => s.overallStatus.toUpperCase() == status.toUpperCase()).toList();
    }
    if (query != null && query.isNotEmpty) {
      final q = query.toLowerCase();
      list = list.where((s) =>
          s.productName.toLowerCase().contains(q) ||
          s.brandName.toLowerCase().contains(q) ||
          (s.storeName ?? '').toLowerCase().contains(q)).toList();
    }
    return list;
  }
}
