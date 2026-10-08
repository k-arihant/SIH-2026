class DeclarationResult {
  final String ruleCode;
  final String ruleName;
  final String? extractedValue;
  final bool isPresent;
  final String status; // "PASS" | "FAIL" | "WARNING"
  final String statutoryCitation;
  final double? measuredFontHeightMm;
  final double confidenceScore;
  final String? violationReason;

  const DeclarationResult({
    required this.ruleCode,
    required this.ruleName,
    this.extractedValue,
    this.isPresent = false,
    this.status = 'FAIL',
    this.statutoryCitation = '',
    this.measuredFontHeightMm,
    this.confidenceScore = 0.0,
    this.violationReason,
  });

  bool get isPass => status.toUpperCase() == 'PASS';
  bool get isFail => status.toUpperCase() == 'FAIL';
  bool get isWarning => status.toUpperCase() == 'WARNING';

  factory DeclarationResult.fromJson(Map<String, dynamic> json) {
    return DeclarationResult(
      ruleCode: json['rule_code'] as String? ?? '',
      ruleName: json['rule_name'] as String? ?? '',
      extractedValue: json['extracted_value'] as String?,
      isPresent: json['is_present'] as bool? ?? false,
      status: json['status'] as String? ?? 'FAIL',
      statutoryCitation: json['statutory_citation'] as String? ?? '',
      measuredFontHeightMm: json['measured_font_height_mm'] != null
          ? (json['measured_font_height_mm'] as num).toDouble()
          : null,
      confidenceScore: json['confidence_score'] != null
          ? (json['confidence_score'] as num).toDouble()
          : 0.0,
      violationReason: json['violation_reason'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'rule_code': ruleCode,
    'rule_name': ruleName,
    'extracted_value': extractedValue,
    'is_present': isPresent,
    'status': status,
    'statutory_citation': statutoryCitation,
    'measured_font_height_mm': measuredFontHeightMm,
    'confidence_score': confidenceScore,
    'violation_reason': violationReason,
  };

  DeclarationResult copyWith({
    String? ruleCode,
    String? ruleName,
    String? extractedValue,
    bool? isPresent,
    String? status,
    String? statutoryCitation,
    double? measuredFontHeightMm,
    double? confidenceScore,
    String? violationReason,
  }) {
    return DeclarationResult(
      ruleCode: ruleCode ?? this.ruleCode,
      ruleName: ruleName ?? this.ruleName,
      extractedValue: extractedValue ?? this.extractedValue,
      isPresent: isPresent ?? this.isPresent,
      status: status ?? this.status,
      statutoryCitation: statutoryCitation ?? this.statutoryCitation,
      measuredFontHeightMm: measuredFontHeightMm ?? this.measuredFontHeightMm,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      violationReason: violationReason ?? this.violationReason,
    );
  }
}
