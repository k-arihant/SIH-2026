class DashboardStats {
  final int totalScans;
  final int todayScans;
  final int violationsDetected;
  final double complianceRate;
  final int pendingNotices;

  const DashboardStats({
    required this.totalScans,
    required this.todayScans,
    required this.violationsDetected,
    required this.complianceRate,
    required this.pendingNotices,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalScans: json['total_scans'] as int? ?? 0,
      todayScans: json['today_scans'] as int? ?? 0,
      violationsDetected: json['violations_detected'] as int? ?? 0,
      complianceRate: json['compliance_rate'] != null
          ? (json['compliance_rate'] as num).toDouble()
          : 0.0,
      pendingNotices: json['pending_notices'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
    'total_scans': totalScans,
    'today_scans': todayScans,
    'violations_detected': violationsDetected,
    'compliance_rate': complianceRate,
    'pending_notices': pendingNotices,
  };
}
