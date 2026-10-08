"""
Unit Tests for Stage 5: Deterministic Legal Rule Validation.
Covers Positive (PASS), Negative (FAIL), Ambiguous (UNCERTAIN), and NOT_APPLICABLE cases
across all 10 target Legal Metrology rules.
"""

import unittest
from backend.legal_engine.engine import MetroScanLegalEngine
from backend.legal_engine.rules import (
    evaluate_rule_6_1_a,
    evaluate_rule_6_1_b,
    evaluate_rule_6_1_c,
    evaluate_rule_6_1_d,
    evaluate_rule_6_1_e,
    evaluate_rule_6_1_f,
    evaluate_rule_6_1_g,
    evaluate_rule_6_1_h,
    evaluate_rule_6_1_i,
    evaluate_rule_6_3
)


class TestLegalEngineRules(unittest.TestCase):

    # -------------------------------------------------------------
    # Rule 6(1)(a): Manufacturer / Packer / Importer
    # -------------------------------------------------------------
    def test_rule_6_1_a_pass(self):
        data = {
            "fields": {
                "manufacturer_packer_importer": "Mfd. by Britannia Industries Ltd., 5/1A Hungerford St., Kolkata - 700017"
            }
        }
        res = evaluate_rule_6_1_a(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_a_fail_missing(self):
        data = {"fields": {"manufacturer_packer_importer": None}}
        res = evaluate_rule_6_1_a(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_a_uncertain_truncated(self):
        data = {
            "fields": {
                "manufacturer_packer_importer": "Mfd by: ...Ind. Estate, Guj"
            }
        }
        res = evaluate_rule_6_1_a(data)
        self.assertEqual(res.status, "UNCERTAIN")

    # -------------------------------------------------------------
    # Rule 6(1)(b): Generic Commodity Name
    # -------------------------------------------------------------
    def test_rule_6_1_b_pass(self):
        data = {"fields": {"generic_common_name": "Glucose Biscuits"}}
        res = evaluate_rule_6_1_b(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_b_fail_missing(self):
        data = {"fields": {"generic_common_name": None}}
        res = evaluate_rule_6_1_b(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_b_fail_standalone_brand(self):
        data = {"fields": {"generic_common_name": "Britannia"}}
        res = evaluate_rule_6_1_b(data)
        self.assertEqual(res.status, "FAIL")

    # -------------------------------------------------------------
    # Rule 6(1)(c): Net Quantity
    # -------------------------------------------------------------
    def test_rule_6_1_c_pass_weight(self):
        data = {"fields": {"net_quantity": "Net Qty: 250 g"}}
        res = evaluate_rule_6_1_c(data)
        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.extracted_value, "250 g")

    def test_rule_6_1_c_pass_volume(self):
        data = {"fields": {"net_quantity": "750 ml"}}
        res = evaluate_rule_6_1_c(data)
        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.extracted_value, "750 ml")

    def test_rule_6_1_c_pass_count(self):
        data = {"fields": {"net_quantity": "1 Unit"}}
        res = evaluate_rule_6_1_c(data)
        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.extracted_value, "1 Unit")

    def test_rule_6_1_c_fail_missing(self):
        data = {"fields": {"net_quantity": None}}
        res = evaluate_rule_6_1_c(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_c_fail_batch_number_rejected(self):
        data = {"fields": {"net_quantity": "Batch No: 250"}}
        res = evaluate_rule_6_1_c(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_c_uncertain_corrupted_unit(self):
        data = {"fields": {"net_quantity": "Net W+: 45g"}}
        res = evaluate_rule_6_1_c(data)
        self.assertIn(res.status, ["PASS", "UNCERTAIN"])

    # -------------------------------------------------------------
    # Rule 6(1)(d): Date of Manufacture / Packing
    # -------------------------------------------------------------
    def test_rule_6_1_d_pass_pkd(self):
        data = {"fields": {"manufacturing_packing_import_date": "PKD: 08/2026"}}
        res = evaluate_rule_6_1_d(data)
        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.extracted_value, "08/2026")

    def test_rule_6_1_d_fail_missing(self):
        data = {"fields": {"manufacturing_packing_import_date": None}}
        res = evaluate_rule_6_1_d(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_d_uncertain_unreadable_digits(self):
        data = {"fields": {"manufacturing_packing_import_date": "PKD: ??/26"}}
        res = evaluate_rule_6_1_d(data)
        self.assertEqual(res.status, "UNCERTAIN")

    # -------------------------------------------------------------
    # Rule 6(1)(e): Maximum Retail Price (MRP)
    # -------------------------------------------------------------
    def test_rule_6_1_e_pass_with_tax(self):
        data = {
            "fields": {"mrp": "MRP Rs. 25.00 (incl. of all taxes)"},
            "field_details": {"mrp": {"numeric_value": 25.0, "tax_inclusive_mentioned": True}}
        }
        res = evaluate_rule_6_1_e(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_e_fail_missing_tax_wording(self):
        data = {
            "fields": {"mrp": "MRP Rs. 10.00"},
            "field_details": {"mrp": {"numeric_value": 10.0, "tax_inclusive_mentioned": False}}
        }
        res = evaluate_rule_6_1_e(data)
        self.assertEqual(res.status, "FAIL")
        self.assertIn("mandatory 'inclusive of all taxes'", res.reason)

    def test_rule_6_1_e_fail_completely_missing(self):
        data = {"fields": {"mrp": None}}
        res = evaluate_rule_6_1_e(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_e_uncertain_corrupted_characters(self):
        data = {"fields": {"mrp": "M.R.P Rs 2O.OO (inc|. of a|| taxes)"}}
        res = evaluate_rule_6_1_e(data)
        self.assertEqual(res.status, "UNCERTAIN")

    # -------------------------------------------------------------
    # Rule 6(1)(f): Best Before / Expiry
    # -------------------------------------------------------------
    def test_rule_6_1_f_pass_consumable(self):
        data = {
            "fields": {
                "generic_common_name": "Biscuits",
                "best_before_expiry": "Best Before 6 Months from Packaging"
            }
        }
        res = evaluate_rule_6_1_f(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_f_fail_missing_on_consumable(self):
        data = {
            "fields": {
                "generic_common_name": "Brown Bread",
                "best_before_expiry": None
            }
        }
        res = evaluate_rule_6_1_f(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_f_not_applicable_on_electronics(self):
        data = {
            "fields": {
                "generic_common_name": "Bluetooth Wireless Earphones",
                "best_before_expiry": None
            }
        }
        res = evaluate_rule_6_1_f(data)
        self.assertEqual(res.status, "NOT_APPLICABLE")

    # -------------------------------------------------------------
    # Rule 6(1)(g): Consumer Care Details
    # -------------------------------------------------------------
    def test_rule_6_1_g_pass_phone_and_email(self):
        data = {
            "fields": {
                "consumer_care": "Call 1800-425-4449 or email care@britannia.co.in"
            }
        }
        res = evaluate_rule_6_1_g(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_g_fail_missing(self):
        data = {"fields": {"consumer_care": None}}
        res = evaluate_rule_6_1_g(data)
        self.assertEqual(res.status, "FAIL")

    # -------------------------------------------------------------
    # Rule 6(1)(h): Country of Origin (Imported Goods)
    # -------------------------------------------------------------
    def test_rule_6_1_h_pass_declared(self):
        data = {
            "fields": {
                "country_of_origin": "Italy",
                "manufacturer_packer_importer": "Imported by Ferrero India Pune"
            }
        }
        res = evaluate_rule_6_1_h(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_h_fail_imported_missing_country(self):
        data = {
            "fields": {
                "country_of_origin": None,
                "manufacturer_packer_importer": "Imported and Marketed by ABC Impex Mumbai"
            }
        }
        res = evaluate_rule_6_1_h(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_h_not_applicable_domestic(self):
        data = {
            "fields": {
                "country_of_origin": None,
                "manufacturer_packer_importer": "Mfd by Britannia Industries Ltd, Kolkata, India"
            }
        }
        res = evaluate_rule_6_1_h(data)
        self.assertEqual(res.status, "NOT_APPLICABLE")

    # -------------------------------------------------------------
    # Rule 6(1)(i): Unit Sale Price
    # -------------------------------------------------------------
    def test_rule_6_1_i_pass_valid_rate(self):
        data = {
            "fields": {
                "unit_sale_price": "Unit Sale Price: Rs. 0.10/g",
                "net_quantity": "250 g"
            }
        }
        res = evaluate_rule_6_1_i(data)
        self.assertEqual(res.status, "PASS")

    def test_rule_6_1_i_fail_multi_pack_missing_usp(self):
        data = {
            "fields": {
                "unit_sale_price": None,
                "net_quantity": "300 g (2 x 150 g Save Pack)"
            }
        }
        res = evaluate_rule_6_1_i(data)
        self.assertEqual(res.status, "FAIL")

    def test_rule_6_1_i_not_applicable_single_pack(self):
        data = {
            "fields": {
                "unit_sale_price": None,
                "net_quantity": "100 g"
            }
        }
        res = evaluate_rule_6_1_i(data)
        self.assertEqual(res.status, "NOT_APPLICABLE")

    # -------------------------------------------------------------
    # Rule 6(3): Minimum Font / Numeral Height
    # -------------------------------------------------------------
    def test_rule_6_3_pass_calibrated_barcode(self):
        semantic = {
            "evidence": {
                "net_quantity": {
                    "raw_source_text": "Net Qty: 250 g",
                    "detection_id": "det_002",
                    "bounding_box": {"x": 300, "y": 900, "width": 240, "height": 45}  # 45px
                }
            }
        }
        ocr_data = {
            "reference_objects": [
                {
                    "type": "ean_13_barcode",
                    "bounding_box": {"x": 1200, "y": 800, "width": 373, "height": 259}  # 373px / 37.29mm = 10 px/mm -> 45px / 10 = 4.5 mm
                }
            ]
        }
        res = evaluate_rule_6_3(semantic, ocr_data)
        self.assertEqual(res.status, "PASS")
        self.assertIn("satisfies minimum threshold", res.reason)

    def test_rule_6_3_uncertain_no_reference(self):
        semantic = {"evidence": {}}
        ocr_data = {"reference_objects": []}
        res = evaluate_rule_6_3(semantic, ocr_data)
        self.assertEqual(res.status, "UNCERTAIN")

    # -------------------------------------------------------------
    # Overall Engine Orchestration & Scoring
    # -------------------------------------------------------------
    def test_overall_engine_fail_dominance(self):
        engine = MetroScanLegalEngine()
        # Missing MRP -> should result in overall FAIL
        data = {
            "package_id": "test_pkg",
            "fields": {
                "manufacturer_packer_importer": "Britannia Industries Kolkata",
                "generic_common_name": "Biscuits",
                "net_quantity": "250 g",
                "manufacturing_packing_import_date": "08/2026",
                "mrp": None,  # Causes FAIL
                "best_before_expiry": "6 Months",
                "consumer_care": "1800-425-4449",
                "country_of_origin": None,
                "unit_sale_price": "Rs. 0.10/g"
            }
        }
        res = engine.evaluate(data)
        self.assertEqual(res.overall_status, "FAIL")
        self.assertTrue(res.summary.failed > 0)


if __name__ == "__main__":
    unittest.main()
