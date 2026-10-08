import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class BottomDistributionBar extends StatelessWidget {
  final VoidCallback onDownload;
  final VoidCallback onWhatsApp;
  final VoidCallback onEmail;
  final VoidCallback? onPreviewPdf;
  final bool isLoading;

  const BottomDistributionBar({
    super.key,
    required this.onDownload,
    required this.onWhatsApp,
    required this.onEmail,
    this.onPreviewPdf,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        border: const Border(
          top: BorderSide(color: AppColors.cardBorder, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 10,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (onPreviewPdf != null) ...[
              GestureDetector(
                onTap: onPreviewPdf,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.visibility_outlined, size: 15, color: AppColors.primaryBlue),
                      SizedBox(width: 5),
                      Text(
                        'Preview Official Form 1 Certificate (PDF)',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryBlue,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            Row(
              children: [
                // 1. Download Button
                Expanded(
                  child: _buildActionBtn(
                    label: 'Download',
                    icon: Icons.download_rounded,
                    color: AppColors.primaryBlue,
                    onTap: onDownload,
                  ),
                ),
                const SizedBox(width: 8),

                // 2. WhatsApp Button
                Expanded(
                  child: _buildActionBtn(
                    label: 'WhatsApp',
                    icon: Icons.chat_bubble_outline_rounded,
                    color: const Color(0xFF25D366),
                    onTap: onWhatsApp,
                  ),
                ),
                const SizedBox(width: 8),

                // 3. Email Button
                Expanded(
                  child: _buildActionBtn(
                    label: 'Email',
                    icon: Icons.mail_outline_rounded,
                    color: AppColors.saffron,
                    onTap: onEmail,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionBtn({
    required String label,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return SizedBox(
      height: 44,
      child: ElevatedButton(
        onPressed: isLoading ? null : onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 6),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 16, color: Colors.white),
            const SizedBox(width: 5),
            Flexible(
              child: Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
