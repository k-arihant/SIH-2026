"""
Benchmark Evaluation Runner.
Compares Gemini Semantic Extraction against Human-Verified Ground Truth across 16 test packages.
Computes Precision, Recall, F1, Exact Value Match Rate, and common failure modes.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.schemas.structured_product import StructuredProductInformation
from backend.extractors.gemini_extractor import GeminiSemanticExtractor

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TARGET_FIELDS = [
    "manufacturer_packer_importer",
    "generic_commodity_name",
    "net_quantity",
    "manufacturing_packing_import_date",
    "mrp",
    "best_before_expiry",
    "consumer_care",
    "country_of_origin",
    "unit_sale_price"
]


def load_json(filepath: str) -> Any:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_package(
    pkg_id: str, 
    extracted: StructuredProductInformation, 
    ground_truth: Dict[str, Any]
) -> Dict[str, Any]:
    """Evaluates a single package extraction against its ground truth."""
    extracted_dict = extracted.model_dump()
    pkg_results = {}

    for field in TARGET_FIELDS:
        gt = ground_truth.get(field, {"found": False})
        pred = extracted_dict.get(field, {"found": False})
        
        gt_found = gt.get("found", False)
        pred_found = pred.get("found", False)
        
        match = False
        value_correct = False
        details_correct = True
        error_type = None

        if gt_found and pred_found:
            match = True
            # Check value match
            pred_val = (pred.get("normalized_value") or "").lower()
            expected_contains = [c.lower() for c in gt.get("contains", [])]
            if expected_contains:
                value_correct = any(token in pred_val for token in expected_contains)
            else:
                value_correct = True

            # Check details match
            gt_details = gt.get("details", {})
            pred_details = pred.get("details", {})
            for k, expected_v in gt_details.items():
                actual_v = pred_details.get(k)
                if actual_v is None and expected_v is not None:
                    # If detail was not extracted
                    details_correct = False
                elif isinstance(expected_v, str) and isinstance(actual_v, str):
                    if expected_v.lower() != actual_v.lower():
                        details_correct = False
                elif isinstance(expected_v, (int, float)) and isinstance(actual_v, (int, float)):
                    if abs(float(expected_v) - float(actual_v)) > 0.01:
                        details_correct = False
                elif expected_v != actual_v:
                    details_correct = False
            
            if not value_correct or not details_correct:
                error_type = "VALUE_OR_DETAILS_MISMATCH"

        elif not gt_found and not pred_found:
            match = True
            value_correct = True
        elif gt_found and not pred_found:
            match = False
            error_type = "FALSE_NEGATIVE"  # Field existed, but model missed it
        elif not gt_found and pred_found:
            match = False
            error_type = "FALSE_POSITIVE"  # Field didn't exist, model hallucinated

        # Check uncertainty accuracy
        expected_uncertain = gt.get("uncertain", False)
        pred_uncertain = pred.get("uncertain", False)
        uncertainty_match = (expected_uncertain == pred_uncertain)

        pkg_results[field] = {
            "gt_found": gt_found,
            "pred_found": pred_found,
            "detection_match": (gt_found == pred_found),
            "value_correct": value_correct,
            "details_correct": details_correct,
            "overall_field_success": (match and value_correct and details_correct),
            "error_type": error_type,
            "pred_value": pred.get("normalized_value"),
            "expected_contains": gt.get("contains", []),
            "pred_details": pred.get("details"),
            "expected_details": gt.get("details"),
            "uncertainty_match": uncertainty_match
        }

    return pkg_results


def run_benchmark(api_key: str = None, cached_outputs_path: str = None):
    eval_dir = os.path.dirname(__file__)
    benchmark_file = os.path.join(eval_dir, "benchmark_dataset.json")
    ground_truth_file = os.path.join(eval_dir, "ground_truth.json")

    packages = load_json(benchmark_file)
    ground_truths = load_json(ground_truth_file)

    outputs_cache_file = cached_outputs_path or os.path.join(eval_dir, "gemini_outputs.json")
    cached_outputs = {}
    if os.path.exists(outputs_cache_file):
        try:
            cached_outputs = load_json(outputs_cache_file)
        except Exception:
            cached_outputs = {}

    extractor = None
    if api_key or os.getenv("GEMINI_API_KEY"):
        extractor = GeminiSemanticExtractor(api_key=api_key)

    total_fields = 0
    total_detection_matches = 0
    total_field_successes = 0
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    errors_log = []

    all_extractions = {}

    print("=" * 80)
    print("METROSCAN GEMINI SEMANTIC EXTRACTION BENCHMARK")
    print(f"Evaluating {len(packages)} packages across {len(TARGET_FIELDS)} statutory fields ({len(packages) * len(TARGET_FIELDS)} evaluations)")
    print("=" * 80)

    for i, pkg in enumerate(packages, 1):
        pkg_id = pkg["package_id"]
        gt = ground_truths.get(pkg_id, {})
        print(f"[{i:02d}/{len(packages):02d}] Testing: {pkg_id} ...", end=" ", flush=True)

        extracted = None
        if pkg_id in cached_outputs:
            extracted = StructuredProductInformation(**cached_outputs[pkg_id])
            print("(cached)", end=" ", flush=True)
        elif extractor is not None:
            try:
                extracted = extractor.extract(pkg)
                cached_outputs[pkg_id] = extracted.model_dump()
                print("(live Gemini)", end=" ", flush=True)
            except Exception as e:
                print(f"FAILED: {e}")
                continue
        else:
            print("SKIPPED (No API key and no cache)")
            continue

        all_extractions[pkg_id] = extracted.model_dump()
        pkg_eval = evaluate_package(pkg_id, extracted, gt)

        # Aggregate metrics
        pkg_successes = 0
        for f, res in pkg_eval.items():
            total_fields += 1
            if res["detection_match"]:
                total_detection_matches += 1
            if res["overall_field_success"]:
                total_field_successes += 1
                pkg_successes += 1
            else:
                errors_log.append({
                    "package_id": pkg_id,
                    "field": f,
                    "error_type": res["error_type"],
                    "pred_value": res["pred_value"],
                    "expected": res["expected_contains"] or res["expected_details"],
                    "actual_details": res["pred_details"]
                })

            if res["gt_found"] and res["pred_found"]:
                tp += 1
            elif not res["gt_found"] and not res["pred_found"]:
                tn += 1
            elif not res["gt_found"] and res["pred_found"]:
                fp += 1
            elif res["gt_found"] and not res["pred_found"]:
                fn += 1

        print(f"-> {pkg_successes}/{len(TARGET_FIELDS)} fields verified correct")

    # Save cache
    if cached_outputs:
        with open(outputs_cache_file, "w", encoding="utf-8") as f:
            json.dump(cached_outputs, f, indent=2, ensure_ascii=False)

    if total_fields == 0:
        print("\nNo evaluations completed. Provide a GEMINI_API_KEY to run live evaluations.")
        return

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    field_accuracy = (total_field_successes / total_fields) * 100
    presence_accuracy = (total_detection_matches / total_fields) * 100

    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Evaluated Fields:          {total_fields}")
    print(f"Field Presence Detection Rate:   {presence_accuracy:.2f}% ({total_detection_matches}/{total_fields})")
    print(f"Overall Exact Value Match Rate:  {field_accuracy:.2f}% ({total_field_successes}/{total_fields})")
    print(f"Precision:                       {precision * 100:.2f}%")
    print(f"Recall:                          {recall * 100:.2f}%")
    print(f"F1 Score:                        {f1 * 100:.2f}%")
    print(f"Confusion Matrix:                TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print("=" * 80)

    if errors_log:
        print(f"\nDETAILED DISCREPANCY LOG ({len(errors_log)} items):")
        for err in errors_log:
            print(f"- [{err['package_id']}] Field: {err['field']}")
            print(f"    Type: {err['error_type']}")
            pred_str = str(err['pred_value']).encode('ascii', 'replace').decode('ascii')
            print(f"    Predicted: {pred_str} (Details: {err['actual_details']})")
            print(f"    Expected : {err['expected']}")
    else:
        print("\nPERFECT EXTRACTION! 0 discrepancies detected against ground truth.")

    return {
        "total_fields": total_fields,
        "presence_accuracy": presence_accuracy,
        "field_accuracy": field_accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "errors": errors_log
    }


if __name__ == "__main__":
    api_key_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_benchmark(api_key=api_key_arg)
