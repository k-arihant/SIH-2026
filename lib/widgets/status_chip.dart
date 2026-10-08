import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class StatusChip extends StatelessWidget {
  final String status;
  final bool compact;

  const StatusChip({
    super.key,
    required this.status,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    IconData icon;
    String label = status.toUpperCase();

    switch (label) {
      case 'PASS':
      case 'COMPLIANT':
        bg = AppColors.compliantGreenLight;
        fg = AppColors.compliantGreen;
        icon = Icons.check_circle_rounded;
        break;
      case 'FAIL':
      case 'NON_COMPLIANT':
        bg = AppColors.violationRedLight;
        fg = AppColors.violationRed;
        icon = Icons.cancel_rounded;
        break;
      case 'WARNING':
      case 'PARTIAL':
        bg = AppColors.warningAmberLight;
        fg = AppColors.warningAmber;
        icon = Icons.warning_amber_rounded;
        break;
      default:
        bg = AppColors.canvas;
        fg = AppColors.textSecondary;
        icon = Icons.info_outline_rounded;
        break;
    }

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 8 : 12,
        vertical: compact ? 4 : 6,
      ),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: fg.withOpacity(0.35), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: compact ? 13 : 16, color: fg),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: compact ? 11 : 12,
              fontWeight: FontWeight.w800,
              color: fg,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }
}
