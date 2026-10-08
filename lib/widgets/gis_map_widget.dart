import 'package:flutter/material.dart';
import '../core/constants/app_colors.dart';
import '../models/gis_map_pin.dart';
import '../services/mock/mock_data.dart';

class GisMapWidget extends StatefulWidget {
  final bool isInteractive;
  final double height;
  final VoidCallback? onExpandTap;

  const GisMapWidget({
    super.key,
    this.isInteractive = true,
    this.height = 320,
    this.onExpandTap,
  });

  @override
  State<GisMapWidget> createState() => _GisMapWidgetState();
}

class _GisMapWidgetState extends State<GisMapWidget> {
  String _selectedCity = 'All Regions';
  String _selectedFilter = 'All';

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
      if (_selectedFilter == 'Violations') return pin.status == 'NON_COMPLIANT';
      if (_selectedFilter == 'Compliant') return pin.status == 'COMPLIANT';
      return true;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final pins = _filteredPins;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppColors.cardBorderSubtle),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 12,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 1. Live GPS Header Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.sovereignDark, AppColors.primaryBlue],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.18),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.my_location_rounded, color: Colors.white, size: 16),
                ),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'GPS Geotagged Locations',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.w800,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.compliantGreen,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.gps_fixed_rounded, color: Colors.white, size: 11),
                      SizedBox(width: 4),
                      Text(
                        'GPS LOCKED',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 9,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 0.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 2. City & Status Filter Selector
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 10, 14, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        'Region',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: SingleChildScrollView(
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
                                backgroundColor: const Color(0xFFF8FAFC),
                                visualDensity: VisualDensity.compact,
                                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: BorderSide(
                                    color: isSel ? AppColors.primaryBlue : AppColors.cardBorderSubtle,
                                  ),
                                ),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        'Status',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: ['All', 'Violations', 'Compliant'].map((status) {
                            final isSel = _selectedFilter == status;
                            Color activeColor = AppColors.primaryBlue;
                            if (status == 'Violations') activeColor = AppColors.violationRed;
                            if (status == 'Compliant') activeColor = AppColors.compliantGreen;

                            return Padding(
                              padding: const EdgeInsets.only(right: 6),
                              child: ChoiceChip(
                                label: Text(status),
                                selected: isSel,
                                showCheckmark: false,
                                onSelected: (_) => setState(() => _selectedFilter = status),
                                labelStyle: TextStyle(
                                  fontSize: 11,
                                  fontWeight: isSel ? FontWeight.w800 : FontWeight.w600,
                                  color: isSel ? Colors.white : AppColors.textPrimary,
                                ),
                                selectedColor: activeColor,
                                backgroundColor: const Color(0xFFF8FAFC),
                                visualDensity: VisualDensity.compact,
                                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: BorderSide(
                                    color: isSel ? activeColor : AppColors.cardBorderSubtle,
                                  ),
                                ),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const Divider(height: 1, color: AppColors.cardBorderSubtle),

          // 3. Geotagged Audited Stores List
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.all(12),
              itemCount: pins.length > 5 ? 5 : pins.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (ctx, index) {
                final pin = pins[index];
                final isViolated = pin.status == 'NON_COMPLIANT';

                return InkWell(
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${pin.storeName} (${pin.city}) • ${pin.status == "NON_COMPLIANT" ? "Violations Detected" : "Compliant"}'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                  borderRadius: BorderRadius.circular(14),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isViolated ? const Color(0xFFFEF2F2) : const Color(0xFFF0FDF4),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: isViolated
                            ? AppColors.violationRed.withOpacity(0.2)
                            : AppColors.compliantGreen.withOpacity(0.2),
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isViolated
                                ? AppColors.violationRedLight
                                : AppColors.compliantGreenLight,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            isViolated ? Icons.report_problem_rounded : Icons.store_rounded,
                            color: isViolated ? AppColors.violationRed : AppColors.compliantGreen,
                            size: 18,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                pin.storeName,
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${pin.address}, ${pin.city}',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: AppColors.textSecondary,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 6),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: AppColors.blueSurface,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        const Icon(Icons.location_city_rounded, size: 11, color: AppColors.primaryBlue),
                                        const SizedBox(width: 3),
                                        Text(
                                          pin.city,
                                          style: const TextStyle(
                                            fontSize: 10,
                                            fontWeight: FontWeight.w700,
                                            color: AppColors.primaryBlue,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: isViolated ? AppColors.violationRedLight : AppColors.compliantGreenLight,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      isViolated ? 'NON-COMPLIANT' : 'COMPLIANT',
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.w800,
                                        color: isViolated ? AppColors.violationRed : AppColors.compliantGreenDark,
                                        letterSpacing: 0.3,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // 4. View All Locations Button
          if (widget.onExpandTap != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              color: const Color(0xFFF8FAFC),
              child: InkWell(
                onTap: widget.onExpandTap,
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'View All Geotagged Locations & Audits',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: AppColors.primaryBlue,
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(Icons.arrow_forward_rounded, size: 14, color: AppColors.primaryBlue),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
