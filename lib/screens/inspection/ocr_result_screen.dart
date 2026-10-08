import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:share_plus/share_plus.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/gov_app_bar.dart';

class OcrResultScreen extends StatefulWidget {
  final Map<String, dynamic> ocrJson;
  final String imagePath;
  final String localSavedJsonPath;

  const OcrResultScreen({
    super.key,
    required this.ocrJson,
    required this.imagePath,
    required this.localSavedJsonPath,
  });

  @override
  State<OcrResultScreen> createState() => _OcrResultScreenState();
}

class _OcrResultScreenState extends State<OcrResultScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  String get _prettyJson {
    return const JsonEncoder.withIndent('  ').convert(widget.ocrJson);
  }

  List<dynamic> get _detections {
    if (widget.ocrJson['detections'] is List) {
      return widget.ocrJson['detections'] as List;
    }
    if (widget.ocrJson['ocr'] is List) {
      return widget.ocrJson['ocr'] as List;
    }
    return [];
  }

  @override
  Widget build(BuildContext context) {
    final detections = _detections;
    final totalDetections = detections.length;
    final packageId = widget.ocrJson['package_id'] as String? ?? 'pkg_001';
    final imagesList = (widget.ocrJson['images'] as List?) ?? [];
    final imgMeta = imagesList.isNotEmpty ? (imagesList.first as Map<String, dynamic>) : <String, dynamic>{};

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: GovAppBar(
        title: 'Step 2: Image Converted to JSON',
        subtitle: 'Package ID: $packageId • $totalDetections Detections',
        actions: [
          IconButton(
            icon: const Icon(Icons.copy_rounded, color: Colors.white),
            tooltip: 'Copy JSON to Clipboard',
            onPressed: () {
              Clipboard.setData(ClipboardData(text: _prettyJson));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Step 2 JSON copied to clipboard.'),
                  backgroundColor: AppColors.compliantGreen,
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.share_rounded, color: Colors.white),
            tooltip: 'Share JSON File',
            onPressed: () {
              if (File(widget.localSavedJsonPath).existsSync()) {
                Share.shareXFiles(
                  [XFile(widget.localSavedJsonPath)],
                  text: 'MetroScan Step 2 Output JSON',
                );
              } else {
                Share.share(_prettyJson, subject: 'MetroScan Step 2 JSON');
              }
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Status & Image Info Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              color: Colors.white,
              child: Row(
                children: [
                  if (File(widget.imagePath).existsSync())
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(
                        File(widget.imagePath),
                        width: 60,
                        height: 60,
                        fit: BoxFit.cover,
                      ),
                    ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: AppColors.compliantGreen.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: AppColors.compliantGreen, width: 1.2),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.check_circle_rounded, size: 14, color: AppColors.compliantGreen),
                                  SizedBox(width: 4),
                                  Text(
                                    'STEP 2 COMPLETED',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w800,
                                      color: AppColors.compliantGreen,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Spacer(),
                            Text(
                              '$totalDetections Items',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: AppColors.primaryBlue,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Package ID: $packageId',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          'Image: ${imgMeta['image_id'] ?? 'img_001'} (${imgMeta['width'] ?? '?'}x${imgMeta['height'] ?? '?'} px) • Side: ${imgMeta['label_side'] ?? 'back'}',
                          style: const TextStyle(fontSize: 10, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Tab Bar
            Container(
              color: Colors.white,
              child: TabBar(
                controller: _tabController,
                indicatorColor: AppColors.primaryBlue,
                indicatorWeight: 3,
                labelColor: AppColors.primaryBlue,
                unselectedLabelColor: AppColors.textSecondary,
                labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                tabs: const [
                  Tab(icon: Icon(Icons.code_rounded, size: 18), text: 'Exact Output JSON'),
                  Tab(icon: Icon(Icons.list_alt_rounded, size: 18), text: 'Detections List'),
                ],
              ),
            ),
            const Divider(height: 1),

            // Tab Views
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  // Tab 1: Monospace JSON Viewer
                  Container(
                    width: double.infinity,
                    margin: const EdgeInsets.all(12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E1E),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.cardBorder),
                    ),
                    child: SingleChildScrollView(
                      child: SelectableText(
                        _prettyJson,
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 11.5,
                          color: Color(0xFFD4D4D4),
                          height: 1.45,
                        ),
                      ),
                    ),
                  ),

                  // Tab 2: Detected Text Items
                  detections.isEmpty
                      ? const Center(child: Text('No detections found.'))
                      : ListView.builder(
                          padding: const EdgeInsets.all(12),
                          itemCount: detections.length,
                          itemBuilder: (ctx, idx) {
                            final item = detections[idx] as Map<String, dynamic>;
                            final detId = item['detection_id'] ?? 'det_${idx + 1}';
                            final txt = item['text'] ?? '';
                            final conf = (item['confidence'] as num?)?.toDouble() ?? 0.0;
                            final bbox = item['bounding_box'] ?? item['bbox'];

                            return Card(
                              elevation: 1,
                              margin: const EdgeInsets.only(bottom: 8),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: AppColors.blueSurface,
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            detId,
                                            style: const TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.bold,
                                              color: AppColors.primaryBlue,
                                            ),
                                          ),
                                        ),
                                        const Spacer(),
                                        Text(
                                          'Conf: ${(conf * 100).toStringAsFixed(0)}%',
                                          style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.bold,
                                            color: conf >= 0.5 ? AppColors.compliantGreen : AppColors.warningAmber,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    SelectableText(
                                      txt,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w700,
                                        color: AppColors.textPrimary,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'bounding_box: $bbox',
                                      style: const TextStyle(
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                        color: AppColors.textSecondary,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ],
              ),
            ),

            // Bottom Action Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: Colors.white,
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        if (context.canPop()) {
                          context.pop();
                        } else {
                          context.go('/dashboard');
                        }
                      },
                      icon: const Icon(Icons.camera_alt_outlined, size: 18),
                      label: const Text('Retake Photo'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        side: const BorderSide(color: AppColors.primaryBlue),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: _prettyJson));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Saved to ocr_output.json & copied to clipboard!'),
                            backgroundColor: AppColors.compliantGreen,
                          ),
                        );
                      },
                      icon: const Icon(Icons.copy_rounded, size: 18),
                      label: const Text('Copy JSON'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primaryBlue,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
