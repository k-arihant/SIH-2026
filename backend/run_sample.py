"""
Interactive Sample Runner for MetroScan:
Step 1: Minimal Connection Test ('GEMINI_OK')
Step 2: Structured Semantic Extraction on sample_input.json (Gemini 3.6 Flash)
Step 3: Stage 5 Deterministic Legal Rule Validation (10 Rules) -> ComplianceResult

Usage:
    python backend/run_sample.py [path_to_input.json] [gemini_api_key]
"""

import os
import sys
import json
from dotenv import load_dotenv

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

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from google import genai
from backend.extractors.gemini_extractor import GeminiSemanticExtractor
from backend.legal_engine.engine import MetroScanLegalEngine

MODEL_NAME = "gemini-3.6-flash"


def handle_quota_error():
    print("\n" + "=" * 80)
    print("Gemini API quota exhausted.")
    print("Please wait for the quota window to reset or check your Google AI Studio quota.")
    print("=" * 80 + "\n")


def test_connection(clean_key: str):
    print("\n" + "=" * 80)
    print(f"Testing Gemini Developer API connection with '{MODEL_NAME}'...")
    print("=" * 80)
    try:
        client = genai.Client(api_key=clean_key)
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents="Reply with exactly: GEMINI_OK"
        )
        print(f"[+] Output from {MODEL_NAME}: {resp.text.strip()}")
        print("[OK] AUTHENTICATION VERIFIED: GEMINI_OK\n")
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            handle_quota_error()
        else:
            print(f"\n[!] Connection test failed: {e}\n")


def main():
    test_connection_mode = "--test-connection" in sys.argv
    cli_args = [arg for arg in sys.argv[1:] if arg != "--test-connection"]

    # Detect default input file (prefer sampleinput.json, fallback to sample_input.json)
    if os.path.exists("sampleinput.json"):
        input_file = "sampleinput.json"
    elif os.path.exists("sample_input.json"):
        input_file = "sample_input.json"
    else:
        input_file = "sampleinput.json"

    raw_key = os.getenv("GEMINI_API_KEY", "")

    # Flexible CLI arguments
    if len(cli_args) == 1:
        if cli_args[0].endswith(".json") or os.path.exists(cli_args[0]):
            input_file = cli_args[0]
        else:
            raw_key = cli_args[0]
    elif len(cli_args) >= 2:
        input_file = cli_args[0]
        raw_key = cli_args[1]

    clean_key = raw_key.strip().strip('"').strip("'") if raw_key else ""

    if not clean_key:
        print("\n" + "=" * 70)
        print("[!] GEMINI_API_KEY NOT DETECTED")
        print("=" * 70)
        print(f"Usage: python backend/run_sample.py {input_file} YOUR_GEMINI_API_KEY")
        print("Or set GEMINI_API_KEY in backend/.env")
        print("=" * 70 + "\n")
        return

    # If user explicitly requested --test-connection, run only the connection test
    if test_connection_mode:
        test_connection(clean_key)
        return

    # 1. LOAD SAMPLE INPUT
    if not os.path.exists(input_file):
        print(f"\n[!] Error: Input file '{input_file}' not found.")
        print(f"Please create '{input_file}' or pass path to your JSON.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"\n[!] Error reading JSON from '{input_file}': {e}\n")
        return

    # 2. RUN STRUCTURED SEMANTIC EXTRACTION (EXACTLY ONE GEMINI REQUEST)
    print("\n" + "=" * 80)
    print(f"Extracting Structured Declarations from '{input_file}' using {MODEL_NAME}...")
    print("=" * 80)

    try:
        extractor = GeminiSemanticExtractor(api_key=clean_key)
        result = extractor.extract(raw_data)

        # Save semantic output to sampleout.json and sample_output.json
        for fname in ["sampleout.json", "sample_output.json"]:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[OK] Semantic extraction complete. Saved to: sampleout.json")

    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            handle_quota_error()
        else:
            print(f"\n[!] Extraction failed: {e}\n")
        return

    # 3. RUN STAGE 5 DETERMINISTIC LEGAL RULE ENGINE (10 RULES) - ZERO API CALLS
    print("\n" + "=" * 80)
    print(f"Stage 5 Deterministic Legal Metrology Validation (10 Rules)...")
    print("=" * 80)

    try:
        engine = MetroScanLegalEngine()
        compliance = engine.evaluate(semantic_data=result, ocr_data=raw_data)
        compliance_dict = compliance.model_dump()

        compliance_output_file = "compliance_result.json"
        with open(compliance_output_file, "w", encoding="utf-8") as f:
            json.dump(compliance_dict, f, indent=2, ensure_ascii=False)

        # 5. CONSOLIDATION / CONJUGATION OF ALL DATA
        import datetime
        congigation_record = {
            "package_id": raw_data.get("package_id", "unknown_package"),
            "processed_at": datetime.datetime.now().isoformat(),
            "config": {
                "input_file": input_file,
                "semantic_output_file": "sampleout.json",
                "compliance_output_file": compliance_output_file,
                "model": MODEL_NAME
            },
            "input_ocr_data": raw_data,
            "extracted_semantic_data": result,
            "legal_compliance_evaluation": compliance_dict
        }

        # Save congregation/consolidation data file
        for cong_file in ["congigation_data.json", "consolidated_data.json"]:
            with open(cong_file, "w", encoding="utf-8") as f:
                json.dump(congigation_record, f, indent=2, ensure_ascii=False)

        # Save data configuration file
        data_config = {
            "input_file": input_file,
            "output_file": "sampleout.json",
            "compliance_file": "compliance_result.json",
            "congigation_file": "congigation_data.json",
            "consolidated_file": "consolidated_data.json"
        }
        with open("data_config.json", "w", encoding="utf-8") as f:
            json.dump(data_config, f, indent=2)

        status_icons = {
            "PASS": "[PASS]          ",
            "FAIL": "[FAIL]          ",
            "UNCERTAIN": "[UNCERTAIN]     ",
            "NOT_APPLICABLE": "[NOT APPLICABLE]"
        }

        print(f"OVERALL STATUS  : {compliance.overall_status}")
        print(f"COMPLIANCE SCORE : {compliance.overall_score} / 100.0")
        print(f"SUMMARY         : Total: {compliance.summary.total_rules} | Passed: {compliance.summary.passed} | Failed: {compliance.summary.failed} | Uncertain: {compliance.summary.uncertain} | N/A: {compliance.summary.not_applicable}\n")
        print("-" * 80)
        print(f"{'RULE':<9} | {'STATUS':<16} | {'DESCRIPTION / REASON'}")
        print("-" * 80)

        for rule in compliance.rule_evaluations:
            status_label = status_icons.get(rule.status, rule.status)
            print(f"{rule.rule_id:<9} | {status_label:<16} | {rule.reason}")
            if rule.extracted_value:
                print(f"          Value: \"{rule.extracted_value}\"")
            for ev in rule.evidence:
                det_id = f"[{ev.detection_id}] " if ev.detection_id else ""
                print(f"          Evidence: {det_id}\"{ev.source_text}\"")
            print()

        print("=" * 80)
        print(f"Semantic Output (Stage 4)      : {os.path.abspath('sampleout.json')}")
        print(f"Compliance Evaluation (Stage 5): {os.path.abspath(compliance_output_file)}")
        print(f"Congigated / Consolidated Data : {os.path.abspath('congigation_data.json')}")
        print(f"Data Configuration             : {os.path.abspath('data_config.json')}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n[!] Legal engine validation failed: {e}\n")


if __name__ == "__main__":
    main()
