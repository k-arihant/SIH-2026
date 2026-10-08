import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';

class CaptureTray extends StatelessWidget {
  final List<String> capturedImages;
  final int activeIndex;
  final void Function(int index)? onSlotTapped;
  final void Function(int index)? onDeleteImage;
  final VoidCallback? onAddSlot;

  static const List<String> slotLabels = [
    'Front Panel (PDP)',
    'Info / Packer',
    'MRP & Dates',
    'Side 1',
    'Side 2',
    'Reference / Base',
  ];

  const CaptureTray({
    super.key,
    required this.capturedImages,
    this.activeIndex = 0,
    this.onSlotTapped,
    this.onDeleteImage,
    this.onAddSlot,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'EVIDENCE TRAY (${capturedImages.length}/6 PHOTOS)',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textSecondary,
                  letterSpacing: 0.5,
                ),
              ),
              if (capturedImages.isNotEmpty)
                Text(
                  '${slotLabels[capturedImages.length.clamp(0, 5)]} next',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryBlue,
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 86,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: 6,
            separatorBuilder: (_, __) => const SizedBox(width: 8),
            itemBuilder: (context, index) {
              final hasImage = index < capturedImages.length;
              final isCurrent = index == activeIndex;
              final label = slotLabels[index];

              return GestureDetector(
                onTap: () => onSlotTapped?.call(index),
                child: Container(
                  width: 76,
                  decoration: BoxDecoration(
                    color: hasImage ? AppColors.blueSurface : Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: isCurrent
                          ? AppColors.saffron
                          : (hasImage ? AppColors.primaryBlue.withOpacity(0.4) : AppColors.cardBorder),
                      width: isCurrent ? 2 : 1,
                    ),
                  ),
                  child: Stack(
                    children: [
                      Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            if (hasImage) ...[
                              const Icon(Icons.check_circle_rounded,
                                  color: AppColors.compliantGreen, size: 24),
                              const SizedBox(height: 4),
                              Text(
                                'Photo ${index + 1}',
                                style: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.primaryBlue,
                                ),
                              ),
                            ] else ...[
                              Icon(
                                Icons.camera_alt_outlined,
                                color: isCurrent ? AppColors.saffron : AppColors.textMuted,
                                size: 22,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Slot ${index + 1}',
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w600,
                                  color: isCurrent ? AppColors.saffron : AppColors.textMuted,
                                ),
                              ),
                            ],
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 2),
                              child: Text(
                                label.split(' ').first,
                                style: const TextStyle(
                                  fontSize: 8,
                                  color: AppColors.textSecondary,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                      ),
                      if (hasImage && onDeleteImage != null)
                        Positioned(
                          top: 2,
                          right: 2,
                          child: GestureDetector(
                            onTap: () => onDeleteImage?.call(index),
                            child: Container(
                              padding: const EdgeInsets.all(2),
                              decoration: const BoxDecoration(
                                color: AppColors.violationRed,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.close, size: 12, color: Colors.white),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
