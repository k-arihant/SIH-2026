import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class ScoreIndicator extends StatelessWidget {
  final double score;
  final double size;

  const ScoreIndicator({
    super.key,
    required this.score,
    this.size = 76,
  });

  @override
  Widget build(BuildContext context) {
    Color scoreColor;
    if (score >= 90) {
      scoreColor = AppColors.compliantGreen;
    } else if (score >= 60) {
      scoreColor = AppColors.warningAmber;
    } else {
      scoreColor = AppColors.violationRed;
    }

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: (score / 100).clamp(0.0, 1.0),
              strokeWidth: 6,
              backgroundColor: AppColors.canvas,
              valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${score.toInt()}%',
                style: TextStyle(
                  fontSize: size * 0.28,
                  fontWeight: FontWeight.w900,
                  color: AppColors.textPrimary,
                  height: 1.1,
                ),
              ),
              Text(
                'COMPLIANCE',
                style: TextStyle(
                  fontSize: size * 0.11,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
