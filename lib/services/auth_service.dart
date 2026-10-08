import '../models/user_profile.dart';
import '../models/user_role.dart';

abstract class AuthService {
  Future<UserProfile?> getCurrentUser();
  Future<UserProfile> login({required String email, required String password});
  Future<UserProfile> loginAsDemo(UserRole role);
  Future<void> logout();
}
