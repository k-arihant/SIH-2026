import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/gov_app_bar.dart';
import '../../widgets/inspection_card.dart';
import '../../widgets/empty_state_view.dart';
import '../../widgets/error_retry_view.dart';
import '../../widgets/floating_nav_bar.dart';

class ScanHistoryScreen extends ConsumerWidget {
  const ScanHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recentAsync = ref.watch(recentScansProvider);
    final activeStatus = ref.watch(scanFilterStatusProvider);

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: const GovAppBar(
        title: 'Inspection Audit Registry',
        subtitle: 'Digital Section 18/36 Audit Records',
      ),
      body: Column(
        children: [
          // Search & Filter Header
          Container(
            padding: const EdgeInsets.all(14),
            color: Colors.white,
            child: Column(
              children: [
                // Search Input Box
                TextField(
                  onChanged: (val) =>
                      ref.read(scanFilterQueryProvider.notifier).state = val,
                  decoration: InputDecoration(
                    hintText: 'Search by product name, brand, or store...',
                    prefixIcon: const Icon(Icons.search, color: AppColors.primaryBlue),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: const BorderSide(color: AppColors.cardBorder),
                    ),
                  ),
                ),
                const SizedBox(height: 10),

                // Status Filter Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _buildFilterChip(ref, 'All Audits', 'ALL', activeStatus),
                      const SizedBox(width: 8),
                      _buildFilterChip(ref, 'Violations (Fail)', 'NON_COMPLIANT', activeStatus),
                      const SizedBox(width: 8),
                      _buildFilterChip(ref, 'Compliant (Pass)', 'COMPLIANT', activeStatus),
                      const SizedBox(width: 8),
                      _buildFilterChip(ref, 'Warnings', 'WARNING', activeStatus),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Audit List
          Expanded(
            child: recentAsync.when(
              data: (scans) {
                if (scans.isEmpty) {
                  return EmptyStateView(
                    title: 'No Matching Inspections',
                    message: 'No package records match your filter criteria.',
                    actionText: 'Reset Filters',
                    onAction: () {
                      ref.read(scanFilterQueryProvider.notifier).state = '';
                      ref.read(scanFilterStatusProvider.notifier).state = 'ALL';
                    },
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: scans.length,
                  itemBuilder: (context, index) {
                    final scan = scans[index];
                    return InspectionCard(
                      scan: scan,
                      onTap: () => context.push('/inspection-details/${scan.scanId}'),
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => ErrorRetryView(
                errorMessage: err.toString(),
                onRetry: () => ref.invalidate(recentScansProvider),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: FloatingNavBar(
        currentIndex: 1,
        onTap: (index) {
          if (index == 0) context.go('/dashboard');
          if (index == 2) context.push('/gis-map');
          if (index == 3) context.push('/profile');
        },
      ),
    );
  }

  Widget _buildFilterChip(
    WidgetRef ref,
    String label,
    String value,
    String currentStatus,
  ) {
    final isSelected = currentStatus.toUpperCase() == value.toUpperCase();

    return GestureDetector(
      onTap: () =>
          ref.read(scanFilterStatusProvider.notifier).state = value,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primaryBlue : AppColors.canvas,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primaryBlue : AppColors.cardBorder,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
            color: isSelected ? Colors.white : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}
