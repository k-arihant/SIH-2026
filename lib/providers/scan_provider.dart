import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/scan_response.dart';
import '../services/scan_service.dart';
import '../services/http_scan_service.dart';

final scanServiceProvider = Provider<ScanService>((ref) {
  return HttpScanService();
});

// Capturing state: list of image paths for the tray (up to 6)
final capturedImagesProvider = StateProvider<List<String>>((ref) => []);
final selectedCategoryProvider = StateProvider<String>((ref) => 'food');
final currentStoreNameProvider = StateProvider<String>((ref) => 'Retail Mandi');

class ScanState {
  final ScanResponse? currentScan;
  final bool isAnalyzing;
  final int analysisStep; // 1 to 4
  final String? error;

  const ScanState({
    this.currentScan,
    this.isAnalyzing = false,
    this.analysisStep = 1,
    this.error,
  });

  ScanState copyWith({
    ScanResponse? currentScan,
    bool? isAnalyzing,
    int? analysisStep,
    String? error,
  }) {
    return ScanState(
      currentScan: currentScan ?? this.currentScan,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      analysisStep: analysisStep ?? this.analysisStep,
      error: error,
    );
  }
}

class ScanNotifier extends StateNotifier<ScanState> {
  final ScanService _scanService;

  ScanNotifier(this._scanService) : super(const ScanState());

  void setStep(int step) {
    state = state.copyWith(analysisStep: step);
  }

  void setScan(ScanResponse scan) {
    state = state.copyWith(currentScan: scan, isAnalyzing: false);
  }

  Future<ScanResponse?> runAnalysis({
    required List<String> images,
    String? storeName,
    String category = 'general',
  }) async {
    state = state.copyWith(isAnalyzing: true, analysisStep: 1, error: null);
    try {
      // Step progression for visual feedback while OCR is working
      Future.delayed(const Duration(milliseconds: 600), () {
        if (state.isAnalyzing) state = state.copyWith(analysisStep: 2);
      });
      Future.delayed(const Duration(milliseconds: 1400), () {
        if (state.isAnalyzing) state = state.copyWith(analysisStep: 3);
      });
      Future.delayed(const Duration(milliseconds: 2200), () {
        if (state.isAnalyzing) state = state.copyWith(analysisStep: 4);
      });

      final result = await _scanService.analyzePackage(
        imagePaths: images,
        storeName: storeName,
        category: category,
      );

      state = state.copyWith(currentScan: result, isAnalyzing: false);
      return result;
    } catch (e) {
      state = state.copyWith(isAnalyzing: false, error: e.toString());
      return null;
    }
  }

  Future<void> updateField({
    required String ruleCode,
    required String newValue,
  }) async {
    final current = state.currentScan;
    if (current == null) return;

    try {
      final updated = await _scanService.updateDeclaration(
        scanId: current.scanId,
        ruleCode: ruleCode,
        newValue: newValue,
      );
      state = state.copyWith(currentScan: updated);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
}

final scanStateProvider = StateNotifierProvider<ScanNotifier, ScanState>((ref) {
  final service = ref.watch(scanServiceProvider);
  return ScanNotifier(service);
});
