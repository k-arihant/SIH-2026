# MetroScan Codebase — Comprehensive File & Architecture Guide

This document provides a complete, detailed walkthrough of every folder, file, and code module in the **MetroScan** repository, explaining its purpose, how it functions, and how the entire pipeline fits together.

---

## High-Level System Architecture

MetroScan is an automated compliance verification engine for the **Legal Metrology (Packaged Commodities) Rules, 2011**.

`
[Raw Package Image / OCR Output]
              |
              v
[sampleinput.json] (Stage 2 & 3: Bounding boxes, OCR text, barcode reference)
              |
              v
[backend/extractors/] (Stage 4: Gemini 3.6 Flash Semantic Normalization)
              |
              v
[sampleout.json] (Structured declaration fields + source detection IDs)
              |
              v
[backend/legal_engine/] (Stage 5: Deterministic Legal Rule Validation)
              |-- 10 Pure-Python Rule Evaluators (Zero LLM Hallucinations)
              |-- Physical Barcode Calibration (GS1 EAN-13 37.29mm scale)
              \-- Unit / Tax / Address / Expiry Regex & Logic Engine
              |
              v
[compliance_result.json] (10-rule PASS/FAIL/UNCERTAIN/NOT_APPLICABLE report)
              |
              v
[congigation_data.json] (Unified Dossier: Input + Extraction + Legal Verification)
`

---

## Detailed Directory & File Breakdown

### 1. Root Level (Working Directory & Data Contracts)

| File | Purpose & Code Operation |
| :--- | :--- |
| **sampleinput.json** | **Active Input Contract**: Contains raw OCR detections, bounding boxes (x, y, width, height), image metadata, and reference objects (e.g. EAN-13 barcodes). Paste any product dataset here to test. |
| **sampleout.json** | **Extraction Output Contract**: Stores structured JSON output produced by Stage 4 (Gemini 3.6 Flash). Maps raw OCR text into standardized fields with confidence scores. |
| **compliance_result.json** | **Legal Validation Output**: Full evaluation report produced by Stage 5. Contains individual PASS, FAIL, UNCERTAIN, NOT_APPLICABLE statuses, rationale, and exact evidence pointers for all 10 statutory rules. |
| **congigation_data.json** | **Consolidated Product Dossier**: Single unified JSON file containing the original input OCR, semantic extraction output, and final legal compliance evaluation together with execution timestamps. |
| **data_config.json** | **Active File Registry**: Maps the input and output filenames currently used by the test runners. |
| **.gitignore** | **Security & Cleanliness**: Ensures virtual environments, Python bytecode (__pycache__), temporary uploads, and crucially .env files containing private API keys are never committed to version control. |
| **SIH_COMPREHENSIVE_GUIDE.md** | **Hackathon / Project Guide**: Original comprehensive specification covering legal context, SIH problem statements, and system objectives. |

---

### 2. ackend/ (Core Application & API Layer)

| File | Purpose & Code Operation |
| :--- | :--- |
| **ackend/.env** | **Local Environment Secrets**: Contains environment configuration: HOST, PORT, and private GEMINI_API_KEY. Gitignored for security. |
| **ackend/config.py** | **Settings Configuration**: Loads environment variables, sets upload directories, default model names, and server port constants. |
| **ackend/requirements.txt** | **Dependency Manifest**: Python package dependencies (astapi, uvicorn, pydantic, google-genai, python-dotenv, etc.). |
| **ackend/main.py** | **FastAPI Server**: Web backend application exposing endpoints: GET /api/health, POST /api/upload (handling image uploads), and mounts static frontend files for the web UI. |
| **ackend/run_sample.py** | **Main Interactive Runner**: Orchestrates the live end-to-end pipeline. Loads sampleinput.json, calls Gemini 3.6 Flash once for extraction, executes the Stage 5 Legal Engine, writes sampleout.json and compliance_result.json, and prints the terminal report. Includes --test-connection flag for health checks. |
| **ackend/run_stage5.py** | **Offline Legal Engine Runner**: Runs Stage 5 deterministic legal checks without making any external network or API calls. Directly takes sampleout.json + sampleinput.json and outputs compliance_result.json. |
| **ackend/test_connection.py** | **Diagnostic Tool**: Minimal script to verify Gemini Developer API connectivity (GEMINI_OK) and .env loading without exposing the raw API key. |

---

### 3. ackend/extractors/ (Stage 4: AI Semantic Extraction)

| File | Purpose & Code Operation |
| :--- | :--- |
| **prompt.py** | **AI Instructions & Schemas**: Defines EXTRACTION_SYSTEM_INSTRUCTION and uild_user_prompt(). Instructs Gemini 3.6 Flash to parse messy OCR text into standard fields (manufacturer, net quantity, MRP, etc.) while mapping back to exact detection IDs. Strictly forbids the LLM from making compliance judgments. |
| **gemini_extractor.py** | **LLM Client Wrapper**: Implements GeminiSemanticExtractor. Configures genai.Client for Developer API with model="gemini-3.6-flash", zero temperature, and strict JSON response mode. Emits zero retries on 429 RESOURCE_EXHAUSTED to protect API quotas. |

---

### 4. ackend/legal_engine/ (Stage 5: Deterministic Legal Engine)

> **Core Principle**: Pure deterministic Python logic. Gemini does not make PASS/FAIL legal decisions.

| File | Purpose & Code Operation |
| :--- | :--- |
| **models.py** | **Pydantic Data Models**: Defines EvidenceItem (linking bounding boxes and source text), RuleEvaluation (status, reason, value, details), ComplianceSummary (total, passed, failed, uncertain counts), and ComplianceResult. |
| **
ormalization.py** | **Legal Normalizers & Regex**: Reusable standardizers for SI units (g, kg, ml, l, pcs), currency values, tax inclusive clauses, date formats, contact details (phone, email), and import origin indicators. |
| **engine.py** | **MetroScanLegalEngine Orchestrator**: Coordinates all 10 rule evaluators, calculates total compliance score (passed / applicable_rules * 100), determines overall status (PASS, FAIL, or UNCERTAIN), and aggregates unified evidence. |
| **ules/__init__.py** | **Rule Registry**: Collects and exposes the list of all active statutory rule evaluators. |

#### Specific Statutory Rule Modules (ackend/legal_engine/rules/)

- **ule_6_1_a.py (Manufacturer / Packer / Importer)**:
  Validates legal name and physical address (flat/survey number, street, city, state, PIN code). Flags incomplete entries under 15 characters as UNCERTAIN and missing entries as FAIL.
- **ule_6_1_b.py (Generic Commodity Name)**:
  Checks that the true generic identity is declared (e.g. "Biscuits", "Sunflower Oil"). Rejects standalone aggressive marketing brand names.
- **ule_6_1_c.py (Net Quantity)**:
  Validates standard SI metric units (g, kg, ml, l, L, cm, m, sq. m, N, U). Catches non-standard or misspelled units (gms, kilos, non-metric pounds/oz) and rejects non-quantities.
- **ule_6_1_d.py (Manufacturing / Packing Date)**:
  Validates month and year format. Rejects ambiguous batch codes without explicit month/year and flags illegible stamping as UNCERTAIN.
- **ule_6_1_e.py (Maximum Retail Price - MRP)**:
  Validates numerical retail price and enforces the statutory phrase *"inclusive of all taxes"* / *"incl. of all taxes"*. Flags FAIL if tax inclusion is omitted.
- **ule_6_1_f.py (Best Before / Expiry Date)**:
  Category-aware evaluator. Mandatory for perishable food, beverage, or cosmetic goods (FAIL if absent). Returns NOT_APPLICABLE for durable consumer electronics and apparel.
- **ule_6_1_g.py (Consumer Care Details)**:
  Validates presence of a designated grievance redressal mechanism with contact telephone/toll-free number or email address.
- **ule_6_1_h.py (Country of Origin)**:
  Mandatory for imported commodities. Flags FAIL if product is declared as imported but country of origin is omitted. Returns NOT_APPLICABLE for domestic Indian products.
- **ule_6_1_i.py (Unit Sale Price - USP)**:
  Validates price per standard unit (₹ X per g, ₹ X per ml, ₹ X per piece). Mandatory for multi-piece combo packs (FAIL if omitted). Returns NOT_APPLICABLE for single items.
- **ule_6_3.py (Minimum Font & Numeral Height)**:
  Evaluates physical numeral height against statutory Table 1 thresholds based on Principal Display Panel area ($<= 100 cm^2 -> 1mm$, -500 cm^2 -> 2mm$, etc.). Uses GS1 standard EAN-13 barcode dimensions (37.29mm width) for real-world pixel-to-millimeter scaling.

---

### 5. ackend/tests/ (Test Automation)

| File | Purpose & Code Operation |
| :--- | :--- |
| **	est_legal_engine.py** | **Automated Test Suite**: 33 unit tests validating PASS, FAIL, UNCERTAIN, and NOT_APPLICABLE edge cases for all 10 statutory rules. Runs 100% offline in 0.004s with zero external dependencies. |

---

### 6. 	est_samples/ (Benchmark Dataset Library)

Contains 10 ready-to-use real-world Indian packaged commodity test datasets:
1. sample_02_maggi_noodles.json: Food item with net quantity, dates, and expiry.
2. sample_03_tata_salt_noisy.json: Low-confidence noisy OCR test.
3. sample_04_ferrero_imported.json: Imported confectionery testing Country of Origin.
4. sample_05_parle_g_missing_tax.json: Tests MRP missing *"inclusive of all taxes"*.
5. sample_06_local_bread_missing_care.json: Tests missing consumer care grievance details.
6. sample_07_colgate_combo.json: Multi-pack combo testing Unit Sale Price (USP).
7. sample_08_boat_earphones.json: Consumer electronic non-perishable testing.
8. sample_09_haldiram_bilingual.json: Bilingual Hindi/English packaging test.
9. sample_10_corrupted_snack.json: Heavy OCR degradation and corrupted numeral testing.

---

### 7. rontend/ (Web Testing Dashboard)

| File | Purpose & Code Operation |
| :--- | :--- |
| **index.html** | Single-page UI for uploading product photos, viewing extracted declarations, checking compliance badges, and reviewing raw JSON outputs. |
| **style.css** | Clean styling for cards, badges (PASS, FAIL, WARNING), and responsive inspection layout. |
| **pp.js** | Vanilla JavaScript handling drag-and-drop file uploads, calling /api/upload, and rendering compliance cards dynamically. |
