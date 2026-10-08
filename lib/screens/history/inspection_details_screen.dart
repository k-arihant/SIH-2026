import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../models/scan_response.dart';
import '../../providers/scan_provider.dart';
import '../../services/share_service.dart';
import '../../widgets/gov_app_bar.dart';
import '../../widgets/verdict_badge.dart';
import '../../widgets/declaration_card.dart';
import '../../widgets/bottom_distribution_bar.dart';

final scanDetailFutureProvider =
    FutureProvider.family<ScanResponse, String>((ref, scanId) async {
  final service = ref.watch(scanServiceProvider);
  return service.getScanDetails(scanId);
});

class InspectionDetailsScreen extends ConsumerWidget {
  final String scanId;

  const InspectionDetailsScreen({
    super.key,
    required this.scanId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(scanDetailFutureProvider(scanId));
    final scan = detailAsync.valueOrNull;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: GovAppBar(
        title: 'Inspection Dossier',
        subtitle: 'Memo ID #${scanId.length > 8 ? scanId.substring(0, 8) : scanId}',
        actions: [
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_outlined, color: Colors.white),
            tooltip: 'View Official Notice',
            onPressed: () => context.push('/pdf-preview/$scanId'),
          ),
        ],
      ),
      bottomNavigationBar: scan != null
          ? BottomDistributionBar(
              onDownload: () async {
                final res = await ShareService.downloadPdf(
                  scanId: scan.scanId,
                  productName: scan.productName,
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res.message)),
                  );
                }
              },
              onWhatsApp: () async {
                final res = await ShareService.shareViaWhatsApp(
                  scanId: scan.scanId,
                  productName: scan.productName,
                  score: scan.complianceScore,
                  overallStatus: scan.overallStatus,
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res.message)),
                  );
                }
              },
              onEmail: () async {
                final res = await ShareService.sendViaEmail(
                  scanId: scan.scanId,
                  recipientEmail: 'officer@gov.in',
                  productName: scan.productName,
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(res.message)),
                  );
                }
              },
              onPreviewPdf: () => context.push('/pdf-preview/$scanId'),
            )
          : null,
      body: detailAsync.when(
        data: (scan) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                VerdictBadge(scan: scan),
                const SizedBox(height: 16),

                // Inspection Meta Card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.cardBorder),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AUDIT PARTICULARS',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textSecondary,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const Divider(height: 16),
                      _buildMetaRow('Audit Memo ID', scan.scanId),
                      _buildMetaRow('Inspected Facility', 'Reliance Smart Supermarket, Sector 62'),
                      _buildMetaRow('Geo-Coordinates', '28.6139° N, 77.2090° E (Verified Point of Audit)'),
                      _buildMetaRow('Inspecting Officer', 'Inspector Amit Verma (Badge: LM-DEL-8492)'),
                    ],
                  ),
                ),
                const SizedBox(height: 18),

                const Text(
                  '10-POINT MANDATORY STATUTORY DECLARATIONS',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textSecondary,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 8),

                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: scan.declarations.length,
                  itemBuilder: (context, index) {
                    final decl = scan.declarations[index];
                    return DeclarationCard(declaration: decl);
                  },
                ),
                const SizedBox(height: 16),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
      ),
    );
  }

  Widget _buildMetaRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
