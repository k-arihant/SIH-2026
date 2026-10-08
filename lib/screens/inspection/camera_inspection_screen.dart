import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/scan_provider.dart';

// ============================================================================
// BACKEND DEVELOPER INTEGRATION POINT:
// ============================================================================
// Hey backend developer! This screen handles:
// 1. Capturing/Selecting the package image from camera or gallery.
// 2. Displaying the captured photo preview.
// 3. The "Find Details" button triggers the OCR & Legal Metrology analysis.
//
// To connect your FastAPI / PyTorch / Gemini OCR endpoint:
// See the `_onFindDetailsPressed()` method below.
// ============================================================================

class CameraInspectionScreen extends ConsumerStatefulWidget {
  const CameraInspectionScreen({super.key});

  @override
  ConsumerState<CameraInspectionScreen> createState() => _CameraInspectionScreenState();
}

class _CameraInspectionScreenState extends ConsumerState<CameraInspectionScreen> {
  final ImagePicker _picker = ImagePicker();
  String? _capturedImagePath;

  Future<void> _captureFromCamera() async {
    if (!kIsWeb && Platform.isAndroid) {
      final status = await Permission.camera.request();
      if (!status.isGranted) {
        _loadDemoSample();
        return;
      }
    }

    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 88,
      );

      if (photo != null) {
        setState(() {
          _capturedImagePath = photo.path;
        });
      }
    } catch (e) {
      debugPrint('[Camera] Camera capture error: $e');
      _loadDemoSample();
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 88,
      );

      if (photo != null) {
        setState(() {
          _capturedImagePath = photo.path;
        });
      }
    } catch (e) {
      debugPrint('[Gallery] Pick error: $e');
      _loadDemoSample();
    }
  }

  void _loadDemoSample() {
    setState(() {
      _capturedImagePath = 'demo_aashirvaad_package.jpg';
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Sample package photo loaded for testing'),
        duration: Duration(seconds: 2),
        backgroundColor: AppColors.primaryBlue,
      ),
    );
  }

  void _clearImage() {
    setState(() {
      _capturedImagePath = null;
    });
  }

  void _onFindDetailsPressed() {
    if (_capturedImagePath == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please capture or select an image first'),
          backgroundColor: AppColors.violationRed,
        ),
      );
      return;
    }

    // ========================================================================
    // BACKEND DEVELOPER INTEGRATION:
    // Pass `_capturedImagePath` to your OCR / Gemini / FastAPI backend here.
    // Example:
    //   final bytes = await File(_capturedImagePath!).readAsBytes();
    //   final response = await http.post(
    //     Uri.parse('${ApiConstants.baseUrl}/api/v1/ocr/detect'),
    //     body: bytes,
    //   );
    //
    // Currently, it stores the captured image in the provider and
    // navigates to `/processing` which displays the legal compliance analysis.
    // ========================================================================
    ref.read(capturedImagesProvider.notifier).state = [_capturedImagePath!];
    context.push('/processing');
  }

  @override
  Widget build(BuildContext context) {
    final bool hasImage = _capturedImagePath != null;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: SafeArea(
        child: Column(
          children: [
            // 1. Top Header Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              color: const Color(0xFF0B1120),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
                    tooltip: 'Back',
                    onPressed: () {
                      if (context.canPop()) {
                        context.pop();
                      } else {
                        context.go('/dashboard');
                      }
                    },
                  ),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Package Inspection',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        Text(
                          'Legal Metrology Compliance Check',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Image Status Badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: hasImage ? AppColors.compliantGreen : const Color(0xFF334155),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          hasImage ? Icons.check_circle_rounded : Icons.camera_alt_rounded,
                          color: Colors.white,
                          size: 13,
                        ),
                        const SizedBox(width: 5),
                        Text(
                          hasImage ? 'Captured' : 'No Photo',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // 2. Central Viewfinder / Captured Photo Display
            Expanded(
              child: Container(
                margin: const EdgeInsets.fromLTRB(16, 12, 16, 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: hasImage ? AppColors.compliantGreen : Colors.white24,
                    width: 2.2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.4),
                      blurRadius: 16,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                clipBehavior: Clip.antiAlias,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // A. If image is captured, show the photo preview!
                    if (hasImage)
                      Positioned.fill(
                        child: _buildCapturedImagePreview(_capturedImagePath!),
                      )
                    // B. If no image captured yet, show framing viewfinder
                    else
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.06),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.camera_alt_rounded,
                              color: Colors.white.withOpacity(0.4),
                              size: 64,
                            ),
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            'Click Shutter to Take Photo',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Align MRP, Net Qty & Expiry details within frame',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.6),
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),

                    // C. Framing Corner Reticles
                    if (!hasImage) ...[
                      Positioned(top: 24, left: 24, child: _bracketCorner(0)),
                      Positioned(top: 24, right: 24, child: _bracketCorner(1)),
                      Positioned(bottom: 24, left: 24, child: _bracketCorner(2)),
                      Positioned(bottom: 24, right: 24, child: _bracketCorner(3)),
                    ],

                    // D. Top Overlay Badge when image is captured
                    if (hasImage)
                      Positioned(
                        top: 14,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.8),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: AppColors.compliantGreen, width: 1.5),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.check_circle_rounded, color: AppColors.compliantGreen, size: 16),
                              SizedBox(width: 6),
                              Text(
                                'Image Captured Successfully',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),

            // 3. Quick Controls Bar (Camera / Gallery / Retake)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Pick from Gallery
                  InkWell(
                    onTap: _pickFromGallery,
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white24),
                      ),
                      child: const Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.photo_library_rounded, color: Colors.white, size: 22),
                          SizedBox(height: 4),
                          Text(
                            'Gallery',
                            style: TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.w700),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Main Shutter Button
                  GestureDetector(
                    onTap: _captureFromCamera,
                    child: Container(
                      width: 76,
                      height: 76,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white,
                        border: Border.all(color: AppColors.saffron, width: 4),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.saffron.withOpacity(0.4),
                            blurRadius: 18,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.camera_alt_rounded,
                          color: AppColors.sovereignDark,
                          size: 34,
                        ),
                      ),
                    ),
                  ),

                  // Quick Demo Sample
                  InkWell(
                    onTap: hasImage ? _clearImage : _loadDemoSample,
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white24),
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            hasImage ? Icons.delete_outline_rounded : Icons.auto_fix_high_rounded,
                            color: hasImage ? AppColors.violationRed : AppColors.saffronLight,
                            size: 22,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            hasImage ? 'Clear' : 'Sample',
                            style: TextStyle(
                              color: hasImage ? AppColors.violationRed : Colors.white70,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // 4. ONLY BUTTON: "Find Details" (As Requested)
            Container(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: hasImage ? _onFindDetailsPressed : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.compliantGreen,
                    disabledBackgroundColor: const Color(0xFF334155),
                    elevation: hasImage ? 4 : 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.search_rounded,
                        color: hasImage ? Colors.white : Colors.white38,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Find Details',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w900,
                          color: hasImage ? Colors.white : Colors.white38,
                          letterSpacing: 0.3,
                        ),
                      ),
                      if (hasImage) ...[
                        const SizedBox(width: 8),
                        const Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 18),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCapturedImagePreview(String path) {
    if (File(path).existsSync()) {
      return Image.file(
        File(path),
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => _buildDemoPlaceholder(),
      );
    }
    return _buildDemoPlaceholder();
  }

  Widget _buildDemoPlaceholder() {
    return Container(
      color: const Color(0xFF1E293B),
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: const BoxDecoration(
              color: AppColors.compliantGreenLight,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.inventory_2_rounded,
              color: AppColors.compliantGreen,
              size: 52,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Package Photo Ready',
            style: TextStyle(
              color: Colors.white,
              fontSize: 17,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            _capturedImagePath ?? 'Ready for verification',
            style: const TextStyle(
              color: Colors.white60,
              fontSize: 12,
              fontFamily: 'monospace',
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Text(
              'Tap "Find Details" to run compliance check',
              style: TextStyle(color: AppColors.saffronLight, fontSize: 11, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }

  Widget _bracketCorner(int corner) {
    // 0: top-left, 1: top-right, 2: bottom-left, 3: bottom-right
    return Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        border: Border(
          top: (corner == 0 || corner == 1)
              ? const BorderSide(color: AppColors.saffronLight, width: 3)
              : BorderSide.none,
          bottom: (corner == 2 || corner == 3)
              ? const BorderSide(color: AppColors.saffronLight, width: 3)
              : BorderSide.none,
          left: (corner == 0 || corner == 2)
              ? const BorderSide(color: AppColors.saffronLight, width: 3)
              : BorderSide.none,
          right: (corner == 1 || corner == 3)
              ? const BorderSide(color: AppColors.saffronLight, width: 3)
              : BorderSide.none,
        ),
      ),
    );
  }
}
