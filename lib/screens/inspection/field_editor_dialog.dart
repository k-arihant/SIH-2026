import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../models/declaration_result.dart';
import '../../widgets/app_button.dart';
import '../../widgets/app_text_field.dart';

class FieldEditorDialog extends StatefulWidget {
  final DeclarationResult declaration;
  final void Function(String newValue) onSave;

  const FieldEditorDialog({
    super.key,
    required this.declaration,
    required this.onSave,
  });

  static Future<void> show({
    required BuildContext context,
    required DeclarationResult declaration,
    required void Function(String newValue) onSave,
  }) {
    return showDialog(
      context: context,
      builder: (ctx) => FieldEditorDialog(
        declaration: declaration,
        onSave: onSave,
      ),
    );
  }

  @override
  State<FieldEditorDialog> createState() => _FieldEditorDialogState();
}

class _FieldEditorDialogState extends State<FieldEditorDialog> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: widget.declaration.extractedValue ?? '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final d = widget.declaration;

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AppColors.blueSurface,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.edit_note_rounded,
                      color: AppColors.primaryBlue, size: 20),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        d.ruleName,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      Text(
                        d.statutoryCitation,
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppColors.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            const Text(
              'Human-in-the-Loop Field Correction:',
              style: TextStyle(
                fontSize: 12,
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),

            AppTextField(
              controller: _controller,
              label: 'Verified Value',
              hint: 'Enter corrected statutory declaration',
              maxLines: 3,
            ),
            const SizedBox(height: 18),

            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.textSecondary,
                      side: const BorderSide(color: AppColors.cardBorder),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    child: const Text('Cancel'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: AppButton(
                    text: 'Save & Verify',
                    height: 44,
                    onPressed: () {
                      final val = _controller.text.trim();
                      if (val.isNotEmpty) {
                        widget.onSave(val);
                        Navigator.of(context).pop();
                      }
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
