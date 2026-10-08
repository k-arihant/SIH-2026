"""
Package export for all 10 Legal Metrology rule evaluators.
"""

from backend.legal_engine.rules.rule_6_1_a import evaluate_rule_6_1_a
from backend.legal_engine.rules.rule_6_1_b import evaluate_rule_6_1_b
from backend.legal_engine.rules.rule_6_1_c import evaluate_rule_6_1_c
from backend.legal_engine.rules.rule_6_1_d import evaluate_rule_6_1_d
from backend.legal_engine.rules.rule_6_1_e import evaluate_rule_6_1_e
from backend.legal_engine.rules.rule_6_1_f import evaluate_rule_6_1_f
from backend.legal_engine.rules.rule_6_1_g import evaluate_rule_6_1_g
from backend.legal_engine.rules.rule_6_1_h import evaluate_rule_6_1_h
from backend.legal_engine.rules.rule_6_1_i import evaluate_rule_6_1_i
from backend.legal_engine.rules.rule_6_3 import evaluate_rule_6_3

ALL_RULE_EVALUATORS = [
    evaluate_rule_6_1_a,
    evaluate_rule_6_1_b,
    evaluate_rule_6_1_c,
    evaluate_rule_6_1_d,
    evaluate_rule_6_1_e,
    evaluate_rule_6_1_f,
    evaluate_rule_6_1_g,
    evaluate_rule_6_1_h,
    evaluate_rule_6_1_i,
    evaluate_rule_6_3,
]
