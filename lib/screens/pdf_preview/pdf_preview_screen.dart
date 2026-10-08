import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../services/share_service.dart';
import '../../widgets/gov_app_bar.dart';

class PdfPreviewScreen extends ConsumerWidget {
  final String scanId;

  const PdfPreviewScreen({
    super.key,
    required this.scanId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: const Color(0xFF525659), // Standard PDF reader canvas
      appBar: GovAppBar(
        title: 'Form 1 Statutory Certificate',
        subtitle: 'Digital Court-Admissible Inspection Report',
        actions: [
          IconButton(
            icon: const Icon(Icons.open_in_browser_rounded, color: Colors.white),
            tooltip: 'Open Live Stream PDF',
            onPressed: () async {
              final url = Uri.parse(ApiConstants.scanCertificatePdfUrl(scanId));
              try {
                await launchUrl(url, mode: LaunchMode.externalApplication);
              } catch (_) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Could not launch: $url')),
                  );
                }
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.download_rounded, color: Colors.white),
            tooltip: 'Download PDF',
            onPressed: () async {
              final res = await ShareService.downloadPdf(
                scanId: scanId,
                productName: 'Packaged Commodity',
              );
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(res.message)),
                );
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.share_rounded, color: Colors.white),
            tooltip: 'Native Share',
            onPressed: () async {
              final res = await ShareService.shareViaWhatsApp(
                scanId: scanId,
                productName: 'Packaged Commodity',
                score: 72.5,
                overallStatus: 'NON_COMPLIANT',
              );
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(res.message)),
                );
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 580),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(4),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Government Header
                const Center(
                  child: Text(
                    'GOVERNMENT OF INDIA',
                    style: TextStyle(
                      fontFamily: 'serif',
                      fontSize: 14,
                      fontWeight: FontWeight.w900,
                      color: AppColors.sovereignDark,
                      letterSpacing: 1.2,
                    ),
                  ),
                ),
                const SizedBox(height: 2),
                const Center(
                  child: Text(
                    'MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF566573),
                    ),
                  ),
                ),
                const Center(
                  child: Text(
                    'DELHI STATE LEGAL METROLOGY ENFORCEMENT DIVISION',
                    style: TextStyle(
                      fontSize: 9,
                      color: Color(0xFF566573),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                const Divider(color: AppColors.primaryBlue, thickness: 1.5),
                const SizedBox(height: 6),

                const Center(
                  child: Text(
                    'FORM 1: STATUTORY PACKAGING INSPECTION REPORT & NOTICE',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w900,
                      color: AppColors.warningAmber,
                      letterSpacing: 0.3,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const Center(
                  child: Text(
                    'Issued under Section 18 & 36, Legal Metrology Act, 2009 read with 2011 Rules',
                    style: TextStyle(
                      fontSize: 8,
                      fontStyle: FontStyle.italic,
                      color: Color(0xFF7F8C8D),
                    ),
                  ),
                ),
                const SizedBox(height: 14),

                // Meta table box
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppColors.canvas,
                    border: Border.all(color: const Color(0xFFBDC3C7)),
                  ),
                  child: Column(
                    children: [
                      _buildRow('Inspection Memo ID:', scanId),
                      _buildRow('Audit Timestamp:', '08-Sep-2026 07:45:12 PM IST'),
                      _buildRow('Inspecting Authority:', 'Inspector Amit Verma (LM-DEL-8492)'),
                      _buildRow('Mandi / Store Location:', 'Reliance Smart Supermarket, Sector 62'),
                      _buildRow('Geo-Coordinates:', '28.6139° N, 77.2090° E'),
                      _buildRow('Commodity Verified:', 'Aashirvaad Whole Wheat Atta 5kg (ITC Limited)'),
                      _buildRow('Statutory Verdict:', 'NON_COMPLIANT (Score: 72.5%)'),
                      _buildRow('Enforcement Action:', 'LEGAL NOTICE ISSUED U/S 36'),
                    ],
                  ),
                ),
                const SizedBox(height: 14),

                // 10-Rule Audit Matrix
                const Text(
                  '10-POINT MANDATORY STATUTORY DECLARATION AUDIT MATRIX',
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.w900,
                    color: AppColors.primaryBlue,
                  ),
                ),
                const SizedBox(height: 6),

                Table(
                  border: TableBorder.all(color: const Color(0xFFD5DBDB), width: 0.8),
                  columnWidths: const {
                    0: FlexColumnWidth(1.2),
                    1: FlexColumnWidth(2.5),
                    2: FlexColumnWidth(1.0),
                  },
                  children: [
                    _buildTableHeader(),
                    _buildTableRow('Rule 6(1)(a)', 'Manufacturer & Address', 'PASS (2.4 mm)'),
                    _buildTableRow('Rule 6(1)(b)', 'Generic Commodity Name', 'PASS (3.8 mm)'),
                    _buildTableRow('Rule 6(1)(c)', 'Net Quantity SI Units', 'PASS (4.2 mm)'),
                    _buildTableRow('Rule 6(1)(d)', 'Mfg & Packing Date', 'PASS (1.8 mm)'),
                    _buildTableRow('Rule 6(1)(e)', 'MRP Tax Inclusion Clause', 'FAIL (Missing Taxes)'),
                    _buildTableRow('Rule 6(1)(f)', 'Best Before / Expiry Date', 'PASS (1.5 mm)'),
                    _buildTableRow('Rule 6(1)(g)', 'Consumer Care Contact', 'WARN (Phone Missing)'),
                    _buildTableRow('Rule 6(1)(h)', 'Country of Origin', 'PASS (Domestic)'),
                    _buildTableRow('Rule 6(1)(i)', 'Unit Sale Price (USP)', 'FAIL (Omitted)'),
                    _buildTableRow('Rule 6(3)', 'Minimum Font Height', 'WARN (1.2 mm < 2.0 mm)'),
                  ],
                ),
                const SizedBox(height: 18),

                // Tamper Proof Verification Footer
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF2F4F4),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: const Color(0xFFE5E7E9)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text(
                        'DIGITAL EVIDENCE SHA-256 TAMPER-PROOF HASH:',
                        style: TextStyle(
                          fontSize: 8,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF2C3E50),
                        ),
                      ),
                      SizedBox(height: 2),
                      Text(
                        'cb2a694ce8e6a1b50a332409d84e6d8e54a79be4551b558ccd7220e49b09d3d1',
                        style: TextStyle(
                          fontSize: 7.5,
                          fontFamily: 'monospace',
                          color: Color(0xFF566573),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Stamp & Seal Representation
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.compliantGreen, width: 1.5),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'VERIFIED DIGITAL MEMO\nOFFICIAL EVIDENCE RECORD',
                        style: TextStyle(
                          fontSize: 8,
                          fontWeight: FontWeight.w900,
                          color: AppColors.compliantGreen,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: const [
                        Text(
                          'Shri Amit Verma',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                        Text(
                          'Senior Enforcement Officer\nBadge ID: LM-DEL-8492',
                          style: TextStyle(fontSize: 8, color: Color(0xFF7F8C8D)),
                          textAlign: TextAlign.right,
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1C2833),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 9,
                color: Color(0xFF2C3E50),
              ),
            ),
          ),
        ],
      ),
    );
  }

  TableRow _buildTableHeader() {
    return TableRow(
      decoration: const BoxDecoration(color: AppColors.primaryBlue),
      children: const [
        Padding(
          padding: EdgeInsets.all(5),
          child: Text('RULE', style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
        ),
        Padding(
          padding: EdgeInsets.all(5),
          child: Text('STATUTORY DECLARATION', style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
        ),
        Padding(
          padding: EdgeInsets.all(5),
          child: Text('VERDICT', style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  TableRow _buildTableRow(String rule, String name, String status) {
    final isPass = status.contains('PASS');
    final isFail = status.contains('FAIL');
    final color = isPass
        ? AppColors.compliantGreen
        : (isFail ? AppColors.violationRed : AppColors.warningAmber);

    return TableRow(
      children: [
        Padding(
          padding: const EdgeInsets.all(4),
          child: Text(rule, style: const TextStyle(fontSize: 8, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
        ),
        Padding(
          padding: const EdgeInsets.all(4),
          child: Text(name, style: const TextStyle(fontSize: 8)),
        ),
        Padding(
          padding: const EdgeInsets.all(4),
          child: Text(status, style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: color)),
        ),
      ],
    );
  }
}
