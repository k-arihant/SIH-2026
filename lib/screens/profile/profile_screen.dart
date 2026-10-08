import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../models/user_role.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/floating_nav_bar.dart';
import '../../widgets/gov_app_bar.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final user = authState.user;
    final isInspector = user?.role == UserRole.inspector;

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: GovAppBar(
        title: isInspector ? 'Officer Profile & System' : 'Consumer Profile & System',
        subtitle: isInspector ? 'Badge: ${user?.badgeId ?? "LM-DEL-8492"} • Enforcement' : 'Verified Citizen Account',
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
            // 1. Officer Credentials Card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.sovereignDark, AppColors.primaryBlue],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(22),
                boxShadow: AppColors.heroShadow,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.18),
                          shape: BoxShape.circle,
                          border: Border.all(color: AppColors.saffronLight, width: 2),
                        ),
                        child: const Center(
                          child: Icon(Icons.shield_rounded, color: Colors.white, size: 28),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user?.fullName ?? (isInspector ? 'Shri Amit Verma' : 'Citizen Rahul Sharma'),
                              style: const TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.w900,
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              isInspector ? 'Senior Legal Metrology Officer' : 'Verified Indian Consumer',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.white.withOpacity(0.85),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.saffron,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                isInspector ? (user?.badgeId ?? 'Badge: LM-DEL-8492') : 'Consumer Account',
                                style: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: Colors.white24, height: 1),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildHeaderStat('Audits Led', '128'),
                      _buildHeaderStat('Notices Issued', '34'),
                      _buildHeaderStat('Compliance', '78.4%'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 2. Demonstration Role Switcher
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.cardBorderSubtle),
                boxShadow: AppColors.cardShadow,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.swap_horiz_rounded, color: AppColors.primaryBlue),
                      SizedBox(width: 8),
                      Text(
                        'Demonstration Role Switcher',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Instantly toggle between Inspector (enforcement authority) and Consumer (citizen summary) workflows for SIH evaluation:',
                    style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            await ref.read(authStateProvider.notifier).loginAsDemo(UserRole.inspector);
                            if (context.mounted) {
                              context.go('/dashboard');
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: isInspector ? AppColors.primaryBlue : Colors.grey.shade200,
                            foregroundColor: isInspector ? Colors.white : AppColors.textPrimary,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: const Text('Inspector View', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () async {
                            await ref.read(authStateProvider.notifier).loginAsDemo(UserRole.consumer);
                            if (context.mounted) {
                              context.go('/dashboard');
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: !isInspector ? AppColors.compliantGreen : Colors.grey.shade200,
                            foregroundColor: !isInspector ? Colors.white : AppColors.textPrimary,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: const Text('Consumer View', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 3. Statutory Standards & Legal Acts Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.cardBorderSubtle),
                boxShadow: AppColors.cardShadow,
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Statutory Standards & Architecture',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                  ),
                  SizedBox(height: 12),
                  _InfoRow(title: 'Governing Legislation', value: 'The Legal Metrology Act, 2009'),
                  _InfoRow(title: 'Rules Applied', value: 'Packaged Commodities Rules, 2011'),
                  _InfoRow(title: 'Design Compliance', value: 'GIGW 3.0 / UX4G Standard'),
                  _InfoRow(title: 'Offline Storage', value: 'Local Encrypted Cache (Active)'),
                  _InfoRow(title: 'App Version', value: 'MetroScan v1.0.0 (SIH 2026 Edition)'),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 4. Server Configuration & Actions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.cardBorderSubtle),
                boxShadow: AppColors.cardShadow,
              ),
              child: Column(
                children: [
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.blueSurface,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.dns_rounded, color: AppColors.primaryBlue),
                    ),
                    title: const Text('Backend Server Endpoint', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
                    subtitle: Text(ApiConstants.baseUrl, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () => _showServerConfigDialog(context),
                  ),
                  const Divider(height: 1),
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppColors.violationRedLight,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.logout_rounded, color: AppColors.violationRed),
                    ),
                    title: const Text('Logout', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.violationRed)),
                    subtitle: const Text('Sign out of active session', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                    trailing: const Icon(Icons.chevron_right_rounded),
                    onTap: () async {
                      await ref.read(authStateProvider.notifier).logout();
                      if (context.mounted) {
                        context.go('/login');
                      }
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
      bottomNavigationBar: FloatingNavBar(
        currentIndex: 3,
        onTap: (index) {
          if (index == 0) context.go('/dashboard');
          if (index == 1) context.push('/history');
          if (index == 2) context.push('/gis-map');
        },
      ),
    );
  }

  static Widget _buildHeaderStat(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Colors.white),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.white.withOpacity(0.8)),
        ),
      ],
    );
  }

  void _showServerConfigDialog(BuildContext context) {
    final controller = TextEditingController(text: ApiConstants.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Server Configuration', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Configured host for real-time mobile API syncing:',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Host Base URL',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              ApiConstants.setCustomHost(controller.text);
              Navigator.pop(ctx);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String title;
  final String value;

  const _InfoRow({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        ],
      ),
    );
  }
}
