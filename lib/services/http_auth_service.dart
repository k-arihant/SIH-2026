import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants/api_constants.dart';
import '../models/user_profile.dart';
import '../models/user_role.dart';
import 'auth_service.dart';
import 'mock/mock_data.dart';

class HttpAuthService implements AuthService {
  UserProfile? _currentUser;
  String? _token;

  String? get token => _token;

  @override
  Future<UserProfile?> getCurrentUser() async {
    if (_currentUser != null) return _currentUser;

    if (_token != null) {
      try {
        final res = await http.get(
          Uri.parse(ApiConstants.meUrl),
          headers: {'Authorization': 'Bearer $_token'},
        ).timeout(const Duration(seconds: 4));

        if (res.statusCode == 200) {
          final data = jsonDecode(res.body) as Map<String, dynamic>;
          if (data['authenticated'] == true) {
            _currentUser = UserProfile.fromJson(data);
            return _currentUser;
          }
        }
      } catch (_) {
        // Fallback silently if offline
      }
    }
    return _currentUser;
  }

  @override
  Future<UserProfile> login({
    required String email,
    required String password,
  }) async {
    try {
      final res = await http.post(
        Uri.parse(ApiConstants.loginUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        _token = data['access_token'] as String?;
        _currentUser = UserProfile.fromJson(data);
        return _currentUser!;
      }
    } catch (e) {
      // Graceful fallback to demo mode when server is unreachable
      // so user experience is not blocked
    }

    // Offline / Demo Fallback
    final isOfficial = email.toLowerCase().contains('inspector') ||
        email.toLowerCase().contains('gov') ||
        email.toLowerCase().contains('officer');
    _currentUser = isOfficial ? MockData.inspectorProfile : MockData.consumerProfile;
    return _currentUser!;
  }

  @override
  Future<UserProfile> loginAsDemo(UserRole role) async {
    if (role == UserRole.inspector || role == UserRole.admin) {
      return login(email: 'inspector.verma@gov.in', password: 'pass');
    } else {
      return login(email: 'citizen.rahul@example.com', password: 'pass');
    }
  }

  @override
  Future<void> logout() async {
    _currentUser = null;
    _token = null;
  }
}
