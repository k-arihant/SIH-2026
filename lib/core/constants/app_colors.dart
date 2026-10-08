import 'package:flutter/material.dart';

/// MetroScan Authority Color Palette (GIGW & UX4G Compliant)
class AppColors {
  // ── Sovereign Authority Blues ───────────────────────────────────────────────
  static const Color sovereignDark = Color(0xFF0B3C5D);
  static const Color primaryBlue = Color(0xFF1A5276);
  static const Color lightBlue = Color(0xFF2980B9);
  static const Color blueSurface = Color(0xFFEBF5FB);

  // ── Tiranga Saffron Accent ──────────────────────────────────────────────────
  static const Color saffron = Color(0xFFE67E22);
  static const Color saffronLight = Color(0xFFF39C12);
  static const Color saffronSurface = Color(0xFFFEF9E7);

  // ── Compliance Status Colors ────────────────────────────────────────────────
  static const Color compliantGreen = Color(0xFF27AE60);
  static const Color compliantGreenLight = Color(0xFFE8F8F5);
  static const Color compliantGreenDark = Color(0xFF1E8449);

  static const Color violationRed = Color(0xFFC0392B);
  static const Color violationRedLight = Color(0xFFFDEDEC);
  static const Color violationRedDark = Color(0xFF922B21);

  static const Color warningAmber = Color(0xFFD35400);
  static const Color warningAmberLight = Color(0xFFFEF5E7);
  static const Color warningAmberAccent = Color(0xFFF1C40F);

  // ── Modern Floating Nav Bar (From Reference Images) ──────────────────────────
  static const Color darkNavBg = Color(0xFF0B192C);
  static const Color darkNavSurface = Color(0xFF1E2E42);
  static const Color darkNavActivePill = Color(0xFF1A5276);
  static const Color darkNavGreenBg = Color(0xFF052117);

  // ── Pastel Accent Tints (From Reference UI Cards) ───────────────────────────
  static const Color pastelMint = Color(0xFFD1F2D9);
  static const Color pastelSky = Color(0xFFD6EAF8);
  static const Color pastelRose = Color(0xFFFADBD8);
  static const Color pastelWarm = Color(0xFFFCF3CF);
  static const Color pastelLavender = Color(0xFFE8DAEF);

  // ── Canvas & Surface ────────────────────────────────────────────────────────
  static const Color canvas = Color(0xFFF8F9FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBorder = Color(0xFFE2E8F0);
  static const Color cardBorderSubtle = Color(0xFFEDF2F7);
  static const Color divider = Color(0xFFCBD5E1);

  // ── High-Contrast Typography (UX4G Standard) ────────────────────────────────
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF475569);
  static const Color textMuted = Color(0xFF94A3B8);
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textOnDark = Color(0xFFF1F5F9);

  // ── Subtle UI Shadows ───────────────────────────────────────────────────────
  static List<BoxShadow> get cardShadow => [
        BoxShadow(
          color: const Color(0xFF0F172A).withOpacity(0.04),
          blurRadius: 16,
          offset: const Offset(0, 4),
        ),
      ];

  static List<BoxShadow> get floatingShadow => [
        BoxShadow(
          color: const Color(0xFF0B192C).withOpacity(0.18),
          blurRadius: 24,
          offset: const Offset(0, 8),
        ),
      ];

  static List<BoxShadow> get heroShadow => [
        BoxShadow(
          color: primaryBlue.withOpacity(0.22),
          blurRadius: 20,
          offset: const Offset(0, 8),
        ),
      ];
}
