import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';
import '../models/declaration_result.dart';
import 'status_chip.dart';

class DeclarationCard extends StatefulWidget {
  final DeclarationResult declaration;
  final VoidCallback? onEdit;

  const DeclarationCard({
    super.key,
    required this.declaration,
    this.onEdit,
  });

  @override
  State<DeclarationCard> createState() => _DeclarationCardState();
}

class _DeclarationCardState extends State<DeclarationCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final d = widget.declaration;
    Color statusBorderColor;
    if (d.isPass) {
      statusBorderColor = AppColors.compliantGreen.withOpacity(0.4);
    } else if (d.isFail) {
      statusBorderColor = AppColors.violationRed.withOpacity(0.5);
    } else {
      statusBorderColor = AppColors.warningAmber.withOpacity(0.5);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: _isExpanded ? statusBorderColor : AppColors.cardBorder,
          width: _isExpanded ? 1.5 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header row (always visible)
          InkWell(
            onTap: () => setState(() => _isExpanded = !_isExpanded),
            borderRadius: BorderRadius.circular(14),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Statutory Citation Tag
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                    decoration: BoxDecoration(
                      color: AppColors.blueSurface,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: AppColors.primaryBlue.withOpacity(0.2)),
                    ),
                    child: Text(
                      d.statutoryCitation.isNotEmpty ? d.statutoryCitation : 'Rule 6',
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AppColors.primaryBlue,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),

                  // Rule Name & snippet
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          d.ruleName,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        if (d.extractedValue != null && !_isExpanded) ...[
                          const SizedBox(height: 3),
                          Text(
                            '"${d.extractedValue!}"',
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                              fontStyle: FontStyle.italic,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),

                  // Status Chip & Accordion Arrow
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      StatusChip(status: d.status, compact: true),
                      const SizedBox(width: 4),
                      Icon(
                        _isExpanded
                            ? Icons.keyboard_arrow_up_rounded
                            : Icons.keyboard_arrow_down_rounded,
                        color: AppColors.textMuted,
                        size: 20,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Expandable Details
          if (_isExpanded)
            Container(
              padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: AppColors.cardBorder, width: 0.8)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 10),

                  // Extracted Value Section
                  const Text(
                    'EXTRACTED DECLARATION:',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppColors.canvas,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppColors.cardBorder),
                    ),
                    child: SelectableText(
                      d.extractedValue != null && d.extractedValue!.isNotEmpty
                          ? d.extractedValue!
                          : 'Declaration is completely missing from scanned package.',
                      style: TextStyle(
                        fontSize: 13,
                        color: d.extractedValue != null ? AppColors.textPrimary : AppColors.violationRed,
                        fontStyle: d.extractedValue != null ? FontStyle.normal : FontStyle.italic,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),

                  // Violation Reason Box (if any)
                  if (d.violationReason != null && d.violationReason!.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.violationRedLight,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.violationRed.withOpacity(0.3)),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.error_outline_rounded,
                              size: 16, color: AppColors.violationRed),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              d.violationReason!,
                              style: const TextStyle(
                                fontSize: 12,
                                color: AppColors.violationRed,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 10),

                  // Measurement & Confidence Metadata
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (d.measuredFontHeightMm != null)
                        Row(
                          children: [
                            const Icon(Icons.straighten_rounded,
                                size: 14, color: AppColors.primaryBlue),
                            const SizedBox(width: 4),
                            Text(
                              'Font: ${d.measuredFontHeightMm} mm',
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: AppColors.primaryBlue,
                              ),
                            ),
                          ],
                        )
                      else
                        const SizedBox.shrink(),
                      Row(
                        children: [
                          const Icon(Icons.verified_outlined,
                              size: 14, color: AppColors.textSecondary),
                          const SizedBox(width: 4),
                          Text(
                            'Confidence: ${(d.confidenceScore * 100).toInt()}%',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),

                  // Human-in-the-loop Edit Button
                  if (widget.onEdit != null) ...[
                    const SizedBox(height: 10),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton.icon(
                        onPressed: widget.onEdit,
                        icon: const Icon(Icons.edit_outlined, size: 14),
                        label: const Text(
                          'Edit Extracted Value',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                        style: TextButton.styleFrom(
                          foregroundColor: AppColors.primaryBlue,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          minimumSize: Size.zero,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
        ],
      ),
    );
  }
}
