import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/gov_app_bar.dart';

class ConsumerRightsScreen extends StatelessWidget {
  const ConsumerRightsScreen({super.key});

  static const List<Map<String, dynamic>> _rightsList = [
    {
      'num': '01',
      'rule': 'Rule 6(1)(e)',
      'title': 'Right to True MRP (Inclusive of All Taxes)',
      'summary': 'No retailer can legally charge even 1 paisa above the printed Maximum Retail Price.',
      'detail':
          'Under Rule 6(1)(e) of the Legal Metrology (Packaged Commodities) Rules, 2011, every retail price must explicitly include the statement "inclusive of all taxes". Adding extra GST, cooling charges, or surcharges at billing is a punishable offence under Section 36 with fines up to ₹25,000.',
      'icon': Icons.currency_rupee_rounded,
      'color': AppColors.primaryBlue,
      'penalty': 'Penalty: Up to ₹25,000 fine under Sec 36',
    },
    {
      'num': '02',
      'rule': 'Rule 6(1)(c)',
      'title': 'Right to Exact Net Quantity in SI Metric Units',
      'summary': 'Weights and volumes must be declared strictly in grams (g), kilograms (kg), or litres (L).',
      'detail':
          'Under Rule 6(1)(c), net contents must declare the true measure without packaging weight. Non-standard expressions such as "approximate", "when packed", or non-metric imperial units are strictly illegal. Packages must adhere to Maximum Permissible Error (MPE) tolerances.',
      'icon': Icons.scale_rounded,
      'color': AppColors.compliantGreen,
      'penalty': 'Penalty: Goods seizure & prosecution under Sec 30',
    },
    {
      'num': '03',
      'rule': 'Rule 6(1)(f)',
      'title': 'Right to Unit Sale Price (USP)',
      'summary': 'Mandatory price per gram or per millilitre so you can compare real costs across brands.',
      'detail':
          'Enforced under the 2022 statutory amendments, all pre-packaged commodities exceeding 1 kg or 1 L must state the Unit Sale Price (e.g. ₹0.45 per gram or ₹0.12 per ml). This empowers consumers to detect hidden shrinkflation and compare value accurately.',
      'icon': Icons.calculate_rounded,
      'color': AppColors.saffron,
      'penalty': 'Statutory requirement for all packaged goods',
    },
    {
      'num': '04',
      'rule': 'Rule 6(1)(d)',
      'title': 'Right to Date of Manufacture / Best Before',
      'summary': 'Clear Month and Year of packing or manufacturing must be legibly printed on every pack.',
      'detail':
          'Under Rule 6(1)(d), every package must clearly state the month and year of manufacture or pre-packing. For food, cosmetics, and pharmaceuticals, the "Best Before" or "Expiry Date" must be prominently declared on the Principal Display Panel.',
      'icon': Icons.event_available_rounded,
      'color': Color(0xFF8B5CF6),
      'penalty': 'Prohibits sale of outdated or expired items',
    },
    {
      'num': '05',
      'rule': 'Rule 6(1)(a)',
      'title': 'Right to Manufacturer & Country of Origin Transparency',
      'summary': 'Complete factory address, manufacturer identity, and country of origin must be declared.',
      'detail':
          'Consumers have the statutory right to know who produced the commodity. The package must state the complete registered name and address of the manufacturer, packer, or importer. For imported items, the Country of Origin must be explicitly declared.',
      'icon': Icons.factory_rounded,
      'color': Color(0xFF0EA5E9),
      'penalty': 'Ensures legal accountability & traceability',
    },
    {
      'num': '06',
      'rule': 'Rule 6(1)(b)',
      'title': 'Right to Common Generic Commodity Name',
      'summary': 'Packages must state the true generic identity, preventing misleading marketing claims.',
      'detail':
          'Under Rule 6(1)(b), the common or generic name of the commodity (e.g. "Refined Sunflower Oil", "Instant Noodles", "Wheat Flour") must be printed on the PDP in clear terms, prohibiting brands from using confusing marketing jargon to deceive buyers.',
      'icon': Icons.label_important_rounded,
      'color': Color(0xFF10B981),
      'penalty': 'Protects against deceptive commercial labelling',
    },
    {
      'num': '07',
      'rule': 'Rule 6(1)(h)',
      'title': 'Right to Consumer Care Contact Details',
      'summary': 'Mandatory phone helpline, email ID, and postal address for swift grievance redressal.',
      'detail':
          'Every packaged commodity must provide name/designation, official telephone helpline, active email address, and postal contact of the person or office to contact in case of consumer complaints. Failure to respond within statutory timelines is punishable.',
      'icon': Icons.support_agent_rounded,
      'color': Color(0xFFEC4899),
      'penalty': 'Statutory 48-hour response protocol',
    },
    {
      'num': '08',
      'rule': 'Rule 7 & 8',
      'title': 'Right to Legible Text & Minimum Font Heights',
      'summary': 'Declarations cannot be hidden in microscopic print or low-contrast backgrounds.',
      'detail':
          'The Legal Metrology Schedule mandates minimum letter and numeral heights (ranging from 1mm up to 6mm depending on package surface area). Printing declarations in faint or low-contrast colors constitutes statutory non-compliance.',
      'icon': Icons.format_size_rounded,
      'color': Color(0xFFF59E0B),
      'penalty': 'Strict millimeter font guidelines enforced',
    },
    {
      'num': '09',
      'rule': 'Rule 6(1)(g)',
      'title': 'Right to True Dimensions for Non-Weight Goods',
      'summary': 'Goods sold by length or area must state exact width, length, and dimensions.',
      'detail':
          'Items such as bedsheets, fabrics, paper, electronic displays, cords, and hardware must declare true measurements (length × width × thickness) in meters, centimeters, or millimeters. Selling undersized goods is a punishable offence.',
      'icon': Icons.straighten_rounded,
      'color': Color(0xFF6366F1),
      'penalty': 'Measurement audit verification under Sec 30',
    },
    {
      'num': '10',
      'rule': 'Rule 18(2) & Sec 36',
      'title': 'Right Against Dual Pricing & Sticker Overwriting',
      'summary': 'No dual MRPs or price sticker pasting is permitted at airports, cinema halls, or restaurants.',
      'detail':
          'Supreme Court of India rulings and Rule 18(2) prohibit manufacturers from printing different MRPs for identical products sold in different locations (such as airports, multiplexes, or luxury hotels). Smudging, tampering, or sticking price tags over printed MRP is illegal.',
      'icon': Icons.block_rounded,
      'color': AppColors.violationRed,
      'penalty': 'Criminal prosecution & fines under Sec 36(2)',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: GovAppBar(
        title: '10 Consumer Rights',
        subtitle: 'Legal Metrology Act, 2009 & PCR 2011',
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
            // 1. Hero Educational Banner
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.sovereignDark, AppColors.primaryBlue],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: AppColors.heroShadow,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.saffron,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'STATUTORY PROTECTION',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                      const Spacer(),
                      const Icon(Icons.shield_rounded, color: AppColors.saffronLight, size: 24),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Know Your 10 Legal Rights',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Every packaged product sold in India is legally obligated to declare these 10 mandatory disclosures under the Legal Metrology (Packaged Commodities) Rules, 2011.',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.88),
                      fontSize: 12,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.phone_in_talk_rounded, color: AppColors.saffronLight, size: 16),
                        SizedBox(width: 8),
                        Text(
                          'National Consumer Helpline: 1915 (Toll-Free)',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 2. Section Heading
            const Text(
              '10 Mandatory Declarations Under Law',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w900,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 12),

            // 3. List of 10 Rights Cards
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _rightsList.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (ctx, index) {
                final right = _rightsList[index];
                final Color cardColor = right['color'] as Color;

                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.cardBorderSubtle),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 10,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header Row: Number + Rule + Icon
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                            decoration: BoxDecoration(
                              color: cardColor.withOpacity(0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'RIGHT #${right['num']}',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w900,
                                color: cardColor,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF1F5F9),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              right['rule'] as String,
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textSecondary,
                                fontFamily: 'monospace',
                              ),
                            ),
                          ),
                          const Spacer(),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: cardColor.withOpacity(0.1),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              right['icon'] as IconData,
                              color: cardColor,
                              size: 20,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),

                      // Title
                      Text(
                        right['title'] as String,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w900,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 4),

                      // Summary
                      Text(
                        right['summary'] as String,
                        style: const TextStyle(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w700,
                          color: AppColors.sovereignDark,
                        ),
                      ),
                      const SizedBox(height: 8),

                      // Detail
                      Text(
                        right['detail'] as String,
                        style: const TextStyle(
                          fontSize: 11.5,
                          color: AppColors.textSecondary,
                          height: 1.45,
                        ),
                      ),
                      const SizedBox(height: 10),

                      // Penalty Tag
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade200),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.gavel_rounded, size: 13, color: AppColors.violationRed),
                            const SizedBox(width: 6),
                            Text(
                              right['penalty'] as String,
                              style: const TextStyle(
                                fontSize: 10.5,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 20),

            // 4. Return to Dashboard Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  if (context.canPop()) {
                    context.pop();
                  } else {
                    context.go('/dashboard');
                  }
                },
                icon: const Icon(Icons.arrow_back_rounded, size: 18),
                label: const Text(
                  'Return to Consumer Portal',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryBlue,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
