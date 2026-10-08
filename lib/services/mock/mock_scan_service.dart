import 'package:uuid/uuid.dart';
import '../scan_service.dart';
import '../../models/scan_response.dart';
import 'mock_data.dart';

class MockScanService implements ScanService {
  final Map<String, ScanResponse> _cache = {
    MockData.sampleAashirvaadScan.scanId: MockData.sampleAashirvaadScan,
    MockData.sampleParleGScan.scanId: MockData.sampleParleGScan,
  };

  @override
  Future<ScanResponse> analyzePackage({
    required List<String> imagePaths,
    String? storeName,
    double? latitude,
    double? longitude,
    String category = 'general',
  }) async {
    // Simulating edge/backend processing time
    await Future.delayed(const Duration(milliseconds: 1800));

    final scanId = const Uuid().v4();
    final newScan = MockData.sampleAashirvaadScan.copyWith(
      scanId: scanId,
      createdAt: DateTime.now(),
      imageUrls: imagePaths.isNotEmpty
          ? imagePaths
          : MockData.sampleAashirvaadScan.imageUrls,
      pdfUrl: '/api/v1/scan/$scanId/certificate.pdf',
    );

    _cache[scanId] = newScan;
    return newScan;
  }

  @override
  Future<ScanResponse> getScanDetails(String scanId) async {
    await Future.delayed(const Duration(milliseconds: 400));
    if (_cache.containsKey(scanId)) {
      return _cache[scanId]!;
    }
    // Fallback: return sample scan with requested ID
    return MockData.sampleAashirvaadScan.copyWith(scanId: scanId);
  }

  @override
  Future<ScanResponse> updateDeclaration({
    required String scanId,
    required String ruleCode,
    required String newValue,
  }) async {
    await Future.delayed(const Duration(milliseconds: 300));
    final current = await getScanDetails(scanId);

    final updatedDeclarations = current.declarations.map((d) {
      if (d.ruleCode == ruleCode) {
        return d.copyWith(
          extractedValue: newValue,
          status: 'PASS',
          isPresent: true,
          violationReason: null,
          confidenceScore: 1.0,
        );
      }
      return d;
    }).toList();

    // Recompute score: 10 pts per PASS, 5 pts per WARNING
    final earned = updatedDeclarations.fold<int>(
      0,
      (acc, d) => acc + (d.isPass ? 10 : (d.isWarning ? 5 : 0)),
    );
    final newScore = ((earned / (updatedDeclarations.length * 10)) * 100)
        .clamp(0.0, 100.0)
        .toDouble();

    final hasFail = updatedDeclarations.any((d) => d.isFail);
    final hasWarning = updatedDeclarations.any((d) => d.isWarning);
    final newStatus = hasFail
        ? 'NON_COMPLIANT'
        : (hasWarning ? 'WARNING' : 'COMPLIANT');

    final updatedScan = current.copyWith(
      declarations: updatedDeclarations,
      complianceScore: double.parse(newScore.toStringAsFixed(1)),
      overallStatus: newStatus,
    );

    _cache[scanId] = updatedScan;
    return updatedScan;
  }
}
