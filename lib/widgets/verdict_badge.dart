import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';
import '../models/scan_response.dart';
import 'score_indicator.dart';

class VerdictBadge extends StatelessWidget {
  final ScanResponse scan;

  const VerdictBadge({
    super.key,
    required this.scan,
  });

  @override
  Widget build(BuildContext context) {
    Color bannerBg;
    Color bannerFg;
    IconData bannerIcon;
    String verdictText;

    if (scan.isCompliant) {
      bannerBg = AppColors.compliantGreen;
      bannerFg = Colors.white;
      bannerIcon = Icons.verified_rounded;
      verdictText = 'COMPLIANT COMMODITY';
    } else if (scan.isNonCompliant) {
      bannerBg = AppColors.violationRed;
      bannerFg = Colors.white;
      bannerIcon = Icons.warning_rounded;
      verdictText = 'NON-COMPLIANT • STATUTORY VIOLATION';
    } else {
      bannerBg = AppColors.warningAmber;
      bannerFg = Colors.white;
      bannerIcon = Icons.report_problem_rounded;
      verdictText = 'REGULATORY WARNING';
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        children: [
          // Top Colored Status Banner
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: bannerBg,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(15),
                topRight: Radius.circular(15),
              ),
            ),
            child: Row(
              children: [
                Icon(bannerIcon, color: bannerFg, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    verdictText,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w900,
                      color: bannerFg,
                      letterSpacing: 0.5,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.25),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Text(
                    'RULE 6',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Main Card Content
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                ScoreIndicator(score: scan.complianceScore, size: 74),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        scan.productName,
                        style: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textPrimary,
                          letterSpacing: -0.2,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 3),
                      Text(
                        scan.brandName,
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryBlue,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 8),
                      // Summary Chips
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: [
                          _buildCountPill(
                            '${scan.passCount} PASS',
                            AppColors.compliantGreen,
                            AppColors.compliantGreenLight,
                          ),
                          if (scan.failCount > 0)
                            _buildCountPill(
                              '${scan.failCount} FAIL',
                              AppColors.violationRed,
                              AppColors.violationRedLight,
                            ),
                          if (scan.warningCount > 0)
                            _buildCountPill(
                              '${scan.warningCount} WARN',
                              AppColors.warningAmber,
                              AppColors.warningAmberLight,
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCountPill(String label, Color fg, Color bg) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: fg.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w800,
          color: fg,
        ),
      ),
    );
  }
}
