enum UserRole {
  inspector,
  consumer,
  admin;

  static UserRole fromString(String? role) {
    if (role == null) return UserRole.consumer;
    switch (role.toLowerCase()) {
      case 'inspector':
      case 'officer':
        return UserRole.inspector;
      case 'admin':
      case 'super_admin':
        return UserRole.admin;
      default:
        return UserRole.consumer;
    }
  }

  String get displayName {
    switch (this) {
      case UserRole.inspector:
        return 'Official Inspector';
      case UserRole.consumer:
        return 'Citizen Consumer';
      case UserRole.admin:
        return 'Enforcement Controller';
    }
  }

  bool get isOfficial => this == UserRole.inspector || this == UserRole.admin;
}
