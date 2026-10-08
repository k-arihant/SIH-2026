"""
Stage 5 Runner: Deterministic Legal Rule Validation.
Evaluates structured semantic JSON (from Stage 2) against the 10 target Legal Metrology rules.
No Gemini call needed — executes 100% deterministic Python logic.

Usage:
    python backend/run_stage5.py [path_to_semantic_output.json] [path_to_ocr_input.json]
"""

import os
import sys
import json

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.legal_engine.engine import MetroScanLegalEngine


def main():
    semantic_file = "sampleout.json" if os.path.exists("sampleout.json") else "sample_output.json"
    ocr_file = "sampleinput.json" if os.path.exists("sampleinput.json") else "sample_input.json"

    if len(sys.argv) > 1:
        semantic_file = sys.argv[1]
    if len(sys.argv) > 2:
        ocr_file = sys.argv[2]

    if not os.path.exists(semantic_file):
        print(f"\n[!] Error: Semantic input file '{semantic_file}' not found.")
        print("Please run Stage 2 first or provide path to structured semantic JSON:")
        print("    python backend/run_stage5.py path/to/sample_output.json\n")
        return

    try:
        with open(semantic_file, "r", encoding="utf-8") as f:
            semantic_data = json.load(f)
    except Exception as e:
        print(f"[!] Error loading semantic JSON: {e}")
        return

    ocr_data = None
    if os.path.exists(ocr_file):
        try:
            with open(ocr_file, "r", encoding="utf-8") as f:
                ocr_data = json.load(f)
        except Exception:
            pass

    print("\n" + "=" * 80)
    print(f"METROSCAN STAGE 5: Deterministic Legal Metrology Validation")
    print(f"Package: {semantic_data.get('package_id', 'unknown')}")
    print("=" * 80)

    engine = MetroScanLegalEngine()
    result = engine.evaluate(semantic_data, ocr_data)
    res_dict = result.model_dump()

    # Save to compliance_result.json
    output_path = "compliance_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(res_dict, f, indent=2, ensure_ascii=False)

    # Display clean table
    status_icons = {
        "PASS": "[PASS]          ",
        "FAIL": "[FAIL]          ",
        "UNCERTAIN": "[UNCERTAIN]     ",
        "NOT_APPLICABLE": "[NOT APPLICABLE]"
    }

    print(f"\nOVERALL STATUS  : {result.overall_status}")
    print(f"COMPLIANCE SCORE : {result.overall_score} / 100.0")
    print(f"SUMMARY         : Total: {result.summary.total_rules} | Passed: {result.summary.passed} | Failed: {result.summary.failed} | Uncertain: {result.summary.uncertain} | N/A: {result.summary.not_applicable}\n")
    print("-" * 80)
    print(f"{'RULE':<9} | {'STATUS':<16} | {'DESCRIPTION / REASON'}")
    print("-" * 80)

    for rule in result.rule_evaluations:
        status_label = status_icons.get(rule.status, rule.status)
        print(f"{rule.rule_id:<9} | {status_label:<16} | {rule.reason}")
        if rule.extracted_value:
            print(f"          Value: \"{rule.extracted_value}\"")
        for ev in rule.evidence:
            det_id = f"[{ev.detection_id}] " if ev.detection_id else ""
            print(f"          Evidence: {det_id}\"{ev.source_text}\"")
        print()

    print("=" * 80)
    print(f"Complete ComplianceResult JSON written to: {os.path.abspath(output_path)}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
