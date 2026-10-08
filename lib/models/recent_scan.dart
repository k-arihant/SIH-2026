class RecentScan {
  final String scanId;
  final String productName;
  final String brandName;
  final String overallStatus; // "COMPLIANT" | "NON_COMPLIANT" | "WARNING"
  final double complianceScore;
  final String? storeName;
  final DateTime createdAt;

  const RecentScan({
    required this.scanId,
    required this.productName,
    required this.brandName,
    required this.overallStatus,
    required this.complianceScore,
    this.storeName,
    required this.createdAt,
  });

  bool get isCompliant => overallStatus.toUpperCase() == 'COMPLIANT';
  bool get isNonCompliant => overallStatus.toUpperCase() == 'NON_COMPLIANT';
  bool get isWarning => overallStatus.toUpperCase() == 'WARNING';

  factory RecentScan.fromJson(Map<String, dynamic> json) {
    return RecentScan(
      scanId: json['scan_id'] as String? ?? '',
      productName: json['product_name'] as String? ?? 'Product',
      brandName: json['brand_name'] as String? ?? 'Brand',
      overallStatus: json['overall_status'] as String? ?? 'WARNING',
      complianceScore: json['compliance_score'] != null
          ? (json['compliance_score'] as num).toDouble()
          : 0.0,
      storeName: json['store_name'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
    'scan_id': scanId,
    'product_name': productName,
    'brand_name': brandName,
    'overall_status': overallStatus,
    'compliance_score': complianceScore,
    'store_name': storeName,
    'created_at': createdAt.toIso8601String(),
  };
}
