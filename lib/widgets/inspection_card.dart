import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/constants/app_colors.dart';
import '../models/recent_scan.dart';
import 'status_chip.dart';

class InspectionCard extends StatelessWidget {
  final RecentScan scan;
  final VoidCallback? onTap;

  const InspectionCard({
    super.key,
    required this.scan,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd MMM, hh:mm a');
    final dateStr = dateFormat.format(scan.createdAt);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(13),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Left Circular Score Pill
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: scan.isCompliant
                      ? AppColors.compliantGreenLight
                      : (scan.isNonCompliant
                          ? AppColors.violationRedLight
                          : AppColors.warningAmberLight),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: scan.isCompliant
                        ? AppColors.compliantGreen.withOpacity(0.3)
                        : (scan.isNonCompliant
                            ? AppColors.violationRed.withOpacity(0.3)
                            : AppColors.warningAmber.withOpacity(0.3)),
                  ),
                ),
                child: Center(
                  child: Text(
                    '${scan.complianceScore.toInt()}%',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w900,
                      color: scan.isCompliant
                          ? AppColors.compliantGreen
                          : (scan.isNonCompliant
                              ? AppColors.violationRed
                              : AppColors.warningAmber),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Middle details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      scan.productName,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textPrimary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      scan.brandName,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryBlue,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 5),
                    Row(
                      children: [
                        if (scan.storeName != null) ...[
                          const Icon(Icons.storefront_outlined,
                              size: 12, color: AppColors.textSecondary),
                          const SizedBox(width: 3),
                          Flexible(
                            child: Text(
                              scan.storeName!,
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppColors.textSecondary,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 8),
                        ],
                        Text(
                          dateStr,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),

              // Right Status Chip & Arrow
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  StatusChip(status: scan.overallStatus, compact: true),
                  const SizedBox(height: 8),
                  const Icon(Icons.chevron_right_rounded,
                      color: AppColors.textMuted, size: 20),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
