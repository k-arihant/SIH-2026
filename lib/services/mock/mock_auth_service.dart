import '../auth_service.dart';
import '../../models/user_profile.dart';
import '../../models/user_role.dart';
import 'mock_data.dart';

class MockAuthService implements AuthService {
  UserProfile? _currentUser;

  @override
  Future<UserProfile?> getCurrentUser() async {
    await Future.delayed(const Duration(milliseconds: 300));
    return _currentUser;
  }

  @override
  Future<UserProfile> login({required String email, required String password}) async {
    await Future.delayed(const Duration(milliseconds: 600));
    final isOfficial = email.toLowerCase().contains('inspector') ||
        email.toLowerCase().contains('gov') ||
        email.toLowerCase().contains('officer');

    if (isOfficial) {
      _currentUser = MockData.inspectorProfile;
    } else {
      _currentUser = MockData.consumerProfile;
    }
    return _currentUser!;
  }

  @override
  Future<UserProfile> loginAsDemo(UserRole role) async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (role == UserRole.inspector || role == UserRole.admin) {
      _currentUser = MockData.inspectorProfile;
    } else {
      _currentUser = MockData.consumerProfile;
    }
    return _currentUser!;
  }

  @override
  Future<void> logout() async {
    await Future.delayed(const Duration(milliseconds: 200));
    _currentUser = null;
  }
}
