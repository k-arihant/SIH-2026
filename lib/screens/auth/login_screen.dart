import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/api_constants.dart';
import '../../core/constants/app_colors.dart';
import '../../models/user_role.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';
import '../../widgets/app_text_field.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController(text: 'inspector.verma@gov.in');
  final _passwordController = TextEditingController(text: 'pass123');
  final _badgeController = TextEditingController(text: 'LM-DEL-8492');
  final _deptController = TextEditingController(text: 'Delhi State Legal Metrology Division');

  UserRole _selectedRole = UserRole.inspector;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _badgeController.dispose();
    _deptController.dispose();
    super.dispose();
  }

  void _switchRole(UserRole role) {
    setState(() {
      _selectedRole = role;
      if (role == UserRole.inspector) {
        _emailController.text = 'inspector.verma@gov.in';
        _passwordController.text = 'pass123';
        _badgeController.text = 'LM-DEL-8492';
        _deptController.text = 'Delhi State Legal Metrology Division';
      } else {
        _emailController.text = 'citizen.rahul@example.com';
        _passwordController.text = 'pass123';
      }
    });
  }

  Future<void> _handleLogin() async {
    final notifier = ref.read(authStateProvider.notifier);
    final email = _emailController.text.trim();
    final pass = _passwordController.text.trim();

    if (email.isEmpty) {
      await notifier.loginAsDemo(_selectedRole);
    } else {
      await notifier.login(email: email, password: pass.isEmpty ? 'pass123' : pass);
    }

    if (mounted) {
      context.go('/dashboard');
    }
  }

  void _showServerConfigDialog() {
    final hostController = TextEditingController(text: ApiConstants.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.dns_rounded, color: AppColors.primaryBlue),
            SizedBox(width: 8),
            Text('Server Endpoint', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 17)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Specify the backend FastAPI server URL for mobile/web syncing:',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: hostController,
              decoration: InputDecoration(
                labelText: 'Server Base URL',
                labelStyle: const TextStyle(fontSize: 13),
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
                hintText: 'http://192.168.1.x:8000',
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: [
                ActionChip(
                  label: const Text('Localhost (8000)', style: TextStyle(fontSize: 11)),
                  onPressed: () => hostController.text = 'http://localhost:8000',
                ),
                ActionChip(
                  label: const Text('Android 10.0.2.2', style: TextStyle(fontSize: 11)),
                  onPressed: () => hostController.text = 'http://10.0.2.2:8000',
                ),
              ],
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
              ApiConstants.setCustomHost(hostController.text);
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Backend host set to ${ApiConstants.baseUrl}')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryBlue,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text('Save & Apply', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FA),
      body: SafeArea(
        child: Stack(
          children: [
            // Background Subtle Watermark Pattern
            Positioned(
              top: -60,
              right: -60,
              child: Container(
                width: 220,
                height: 220,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.primaryBlue.withOpacity(0.04),
                ),
              ),
            ),
            Positioned(
              bottom: -40,
              left: -40,
              child: Container(
                width: 180,
                height: 180,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.saffron.withOpacity(0.04),
                ),
              ),
            ),

            // Top Server Endpoint Config
            Positioned(
              top: 10,
              right: 12,
              child: InkWell(
                onTap: _showServerConfigDialog,
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.cardBorderSubtle),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 6,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.settings_ethernet_rounded, size: 16, color: AppColors.primaryBlue),
                      SizedBox(width: 5),
                      Text(
                        'Server',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryBlue,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 12),

                      // Government Official Emblem Badge
                      Center(
                        child: Container(
                          width: 74,
                          height: 74,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [AppColors.sovereignDark, AppColors.primaryBlue],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            shape: BoxShape.circle,
                            border: Border.all(color: AppColors.saffronLight, width: 2.5),
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.primaryBlue.withOpacity(0.28),
                                blurRadius: 16,
                                offset: const Offset(0, 6),
                              ),
                            ],
                          ),
                          child: const Center(
                            child: Icon(
                              Icons.balance_rounded,
                              size: 38,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // National Portal Branding
                      const Center(
                        child: Text(
                          'METROSCAN',
                          style: TextStyle(
                            fontSize: 26,
                            fontWeight: FontWeight.w900,
                            color: AppColors.sovereignDark,
                            letterSpacing: 1.2,
                          ),
                        ),
                      ),
                      const SizedBox(height: 3),
                      Center(
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                          decoration: BoxDecoration(
                            color: AppColors.blueSurface,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: AppColors.primaryBlue.withOpacity(0.18)),
                          ),
                          child: const Text(
                            'Legal Metrology Enforcement System',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primaryBlue,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 5),
                      const Center(
                        child: Text(
                          'Ministry of Consumer Affairs, Food & Public Distribution • Govt. of India',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 10.5,
                            color: AppColors.textSecondary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Dual Role Segmented Selector (Inspector vs Consumer)
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE2E8F0),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: _buildRoleTab(
                                title: 'Official Inspector',
                                icon: Icons.badge_rounded,
                                role: UserRole.inspector,
                              ),
                            ),
                            Expanded(
                              child: _buildRoleTab(
                                title: 'Citizen Consumer',
                                icon: Icons.person_rounded,
                                role: UserRole.consumer,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),

                      // Form Container Card
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(color: AppColors.cardBorderSubtle),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 14,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              _selectedRole == UserRole.inspector
                                  ? 'Enforcement Officer Authentication'
                                  : 'Consumer Access Credentials',
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 14),

                            AppTextField(
                              controller: _emailController,
                              label: _selectedRole == UserRole.inspector
                                  ? 'Official Department Email'
                                  : 'Registered Email Address',
                              hint: _selectedRole == UserRole.inspector
                                  ? 'officer.name@gov.in'
                                  : 'name@example.com',
                              prefixIcon: Icons.email_rounded,
                              keyboardType: TextInputType.emailAddress,
                            ),
                            const SizedBox(height: 14),

                            AppTextField(
                              controller: _passwordController,
                              label: 'Passcode / Password',
                              hint: 'Enter login passcode',
                              prefixIcon: Icons.lock_rounded,
                              obscureText: true,
                            ),

                            if (_selectedRole == UserRole.inspector) ...[
                              const SizedBox(height: 14),
                              AppTextField(
                                controller: _badgeController,
                                label: 'Inspector Badge ID',
                                hint: 'e.g. LM-DEL-8492',
                                prefixIcon: Icons.verified_user_rounded,
                              ),
                              const SizedBox(height: 14),
                              AppTextField(
                                controller: _deptController,
                                label: 'Enforcement Division',
                                hint: 'State Legal Metrology Division',
                                prefixIcon: Icons.apartment_rounded,
                              ),
                            ],

                            const SizedBox(height: 20),

                            // Submit Button
                            AppButton(
                              text: _selectedRole == UserRole.inspector
                                  ? 'Authorize & Enter Command Center'
                                  : 'Continue as Citizen Consumer',
                              icon: Icons.login_rounded,
                              isLoading: authState.isLoading,
                              onPressed: _handleLogin,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 18),

                      // Quick Fill Demo Chips
                      Center(
                        child: Column(
                          children: [
                            const Text(
                              'QUICK FILL DEMO CREDENTIALS',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textMuted,
                                letterSpacing: 0.8,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 10,
                              runSpacing: 8,
                              alignment: WrapAlignment.center,
                              children: [
                                ActionChip(
                                  avatar: const Icon(Icons.security_rounded, size: 15, color: AppColors.primaryBlue),
                                  label: const Text('Inspector Demo', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700)),
                                  backgroundColor: AppColors.blueSurface,
                                  side: BorderSide(color: AppColors.primaryBlue.withOpacity(0.2)),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  onPressed: () => _switchRole(UserRole.inspector),
                                ),
                                ActionChip(
                                  avatar: const Icon(Icons.shopping_bag_outlined, size: 15, color: AppColors.compliantGreenDark),
                                  label: const Text('Citizen Demo', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700)),
                                  backgroundColor: AppColors.compliantGreenLight,
                                  side: BorderSide(color: AppColors.compliantGreen.withOpacity(0.2)),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  onPressed: () => _switchRole(UserRole.consumer),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Legal Disclaimer / Statutory Authority
                      const Center(
                        child: Text(
                          'Enforcing The Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011\nOfficial Enforcement Portal — All Actions Are Logged',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 9.5,
                            color: AppColors.textMuted,
                            height: 1.4,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoleTab({
    required String title,
    required IconData icon,
    required UserRole role,
  }) {
    final isSelected = _selectedRole == role;

    return GestureDetector(
      onTap: () => _switchRole(role),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 17,
              color: isSelected ? AppColors.primaryBlue : AppColors.textSecondary,
            ),
            const SizedBox(width: 6),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                color: isSelected ? AppColors.primaryBlue : AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
