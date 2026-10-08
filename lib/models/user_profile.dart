import 'user_role.dart';

class UserProfile {
  final String id;
  final String email;
  final String fullName;
  final UserRole role;
  final String? badgeId;
  final String? department;
  final String? designation;
  final String? phone;

  const UserProfile({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.badgeId,
    this.department,
    this.designation,
    this.phone,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String? ?? json['user_id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      fullName: json['full_name'] as String? ?? 'User',
      role: UserRole.fromString(json['role'] as String?),
      badgeId: json['badge_id'] as String?,
      department: json['department'] as String?,
      designation: json['designation'] as String?,
      phone: json['phone'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'full_name': fullName,
    'role': role.name,
    'badge_id': badgeId,
    'department': department,
    'designation': designation,
    'phone': phone,
  };
}
