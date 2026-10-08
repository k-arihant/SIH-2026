import '../models/scan_response.dart';

abstract class ScanService {
  Future<ScanResponse> analyzePackage({
    required List<String> imagePaths,
    String? storeName,
    double? latitude,
    double? longitude,
    String category = 'general',
  });

  Future<ScanResponse> getScanDetails(String scanId);
  Future<ScanResponse> updateDeclaration({
    required String scanId,
    required String ruleCode,
    required String newValue,
  });
}
