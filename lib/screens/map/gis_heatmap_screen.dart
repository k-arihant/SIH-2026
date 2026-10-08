import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../models/gis_map_pin.dart';
import '../../services/mock/mock_data.dart';
import '../../widgets/floating_nav_bar.dart';
import '../../widgets/gov_app_bar.dart';

class GisHeatmapScreen extends StatefulWidget {
  const GisHeatmapScreen({super.key});

  @override
  State<GisHeatmapScreen> createState() => _GisHeatmapScreenState();
}

class _GisHeatmapScreenState extends State<GisHeatmapScreen> {
  String _selectedCity = 'All Regions';
  String _searchQuery = '';

  final List<String> _cities = [
    'All Regions',
    'Delhi',
    'Bengaluru',
    'Mumbai',
    'Kolkata',
    'Hyderabad',
  ];

  List<GisMapPin> get _filteredPins {
    return MockData.mockMapPins.where((pin) {
      if (_selectedCity != 'All Regions' && pin.city != _selectedCity) return false;
      if (_searchQuery.isNotEmpty) {
        final q = _searchQuery.toLowerCase();
        final matchName = pin.storeName.toLowerCase().contains(q);
        final matchAddr = pin.address.toLowerCase().contains(q);
        final matchProd = pin.lastAuditedProduct.toLowerCase().contains(q);
        if (!matchName && !matchAddr && !matchProd) return false;
      }
      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final pins = _filteredPins;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: GovAppBar(
        title: 'Geotagged Store Registry',
        subtitle: 'Retail Stores & Inspection Records',
        showBackButton: true,
        onBackPressed: () {
          if (context.canPop()) {
            context.pop();
          } else {
            context.go('/dashboard');
          }
        },
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Macro Summary Cards
            Row(
              children: [
                Expanded(
                  child: _buildSummaryPill(
                    title: 'Audited Stores',
                    value: '${MockData.mockMapPins.length}',
                    icon: Icons.storefront_rounded,
                    color: AppColors.primaryBlue,
                    bgColor: AppColors.blueSurface,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildSummaryPill(
                    title: 'Violations Found',
                    value: '${MockData.mockMapPins.where((p) => p.status == "NON_COMPLIANT").length}',
                    icon: Icons.warning_rounded,
                    color: AppColors.violationRed,
                    bgColor: AppColors.violationRedLight,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildSummaryPill(
                    title: 'Compliance Rate',
                    value: '74.4%',
                    icon: Icons.verified_rounded,
                    color: AppColors.compliantGreen,
                    bgColor: AppColors.compliantGreenLight,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // 2. Search & City Filters
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppColors.cardBorderSubtle),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.03),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Search Bar
                  TextField(
                    onChanged: (val) => setState(() => _searchQuery = val.trim()),
                    decoration: InputDecoration(
                      hintText: 'Search store name, address, or product...',
                      hintStyle: const TextStyle(fontSize: 12.5, color: AppColors.textMuted),
                      prefixIcon: const Icon(Icons.search_rounded, color: AppColors.textSecondary, size: 20),
                      isDense: true,
                      filled: true,
                      fillColor: const Color(0xFFF8FAFC),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey.shade200),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),

                  // City Filter Chips
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _cities.map((city) {
                        final isSel = _selectedCity == city;
                        return Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: ChoiceChip(
                            label: Text(city),
                            selected: isSel,
                            showCheckmark: false,
                            onSelected: (_) => setState(() => _selectedCity = city),
                            labelStyle: TextStyle(
                              fontSize: 11,
                              fontWeight: isSel ? FontWeight.w800 : FontWeight.w600,
                              color: isSel ? Colors.white : AppColors.textPrimary,
                            ),
                            selectedColor: AppColors.primaryBlue,
                            backgroundColor: const Color(0xFFF1F5F9),
                            visualDensity: VisualDensity.compact,
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                              side: BorderSide(
                                color: isSel ? AppColors.primaryBlue : Colors.transparent,
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // 3. Section Title
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Geotagged Retail Audits',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  '${pins.length} Locations',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primaryBlue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),

            // 4. List of Geotagged Stores
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: pins.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (ctx, index) {
                final pin = pins[index];
                final isViolated = pin.status == 'NON_COMPLIANT';

                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(
                      color: isViolated
                          ? AppColors.violationRed.withOpacity(0.3)
                          : AppColors.cardBorderSubtle,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: 42,
                            height: 42,
                            decoration: BoxDecoration(
                              color: isViolated
                                  ? AppColors.violationRedLight
                                  : AppColors.compliantGreenLight,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              isViolated
                                  ? Icons.warning_amber_rounded
                                  : Icons.verified_rounded,
                              color: isViolated
                                  ? AppColors.violationRed
                                  : AppColors.compliantGreen,
                              size: 22,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  pin.storeName,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w900,
                                    color: AppColors.textPrimary,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  '${pin.address}, ${pin.city}',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: isViolated
                                  ? AppColors.violationRedLight
                                  : AppColors.compliantGreenLight,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              '${pin.complianceScore.toInt()}%',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w900,
                                color: isViolated
                                    ? AppColors.violationRed
                                    : AppColors.compliantGreenDark,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Region & Status Badges
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.location_city_rounded, size: 14, color: AppColors.primaryBlue),
                                const SizedBox(width: 6),
                                Text(
                                  'Region: ${pin.city}',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w800,
                                    color: AppColors.primaryBlue,
                                  ),
                                ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: isViolated ? AppColors.violationRedLight : AppColors.compliantGreenLight,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                isViolated ? 'NON-COMPLIANT' : 'COMPLIANT',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w900,
                                  color: isViolated ? AppColors.violationRed : AppColors.compliantGreenDark,
                                  letterSpacing: 0.3,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 10),

                      // Audited Product & Officer
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Audited: ${pin.lastAuditedProduct}',
                            style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                          ),
                          Text(
                            'Officer: ${pin.inspectorName}',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
      bottomNavigationBar: FloatingNavBar(
        currentIndex: 2,
        onTap: (index) {
          if (index == 0) context.go('/dashboard');
          if (index == 1) context.push('/history');
          if (index == 3) context.push('/profile');
        },
      ),
    );
  }

  Widget _buildSummaryPill({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required Color bgColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.cardBorderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: color),
          ),
          Text(
            title,
            style: const TextStyle(fontSize: 10, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}
