class GisMapPin {
  final String id;
  final String storeName;
  final String address;
  final String city;
  final double latitude;
  final double longitude;
  final String status; // COMPLIANT, NON_COMPLIANT, WARNING
  final double complianceScore;
  final String lastAuditedProduct;
  final DateTime auditedAt;
  final String inspectorName;

  const GisMapPin({
    required this.id,
    required this.storeName,
    required this.address,
    required this.city,
    required this.latitude,
    required this.longitude,
    required this.status,
    required this.complianceScore,
    required this.lastAuditedProduct,
    required this.auditedAt,
    required this.inspectorName,
  });
}
