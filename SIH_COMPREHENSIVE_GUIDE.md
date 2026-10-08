# 🏆 METROSCAN: End-to-End Execution Guide & System Architecture
## Smart India Hackathon (SIH) — Automated Compliance System for Legal Metrology (Packaged Commodities) Rules, 2011

---

## Executive Summary & Problem-Solution Matrix

### 1. The Problem Statement (In Short)
Under the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011**, every packaged commodity manufactured, packed, imported, or distributed in India is legally mandated to display clear, legible, and conspicuous declarations:
- Name and complete address of the manufacturer, packer, or importer
- Common or generic name of the packaged commodity
- Net quantity in standard SI metric units (weight, volume, measure, or count)
- Maximum Retail Price (MRP), strictly inclusive of all applicable taxes
- Month and year of manufacture, packing, or import
- Complete consumer care contact details (name/designation, postal address, telephone, and email)
- Country of origin (mandatory for all imported commodities)
- Best before or use-by date (for perishables and commodities subject to deterioration)
- Unit Sale Price (USP) in standard metric denominators for transparent price comparison

**The Real-World Enforcement Bottleneck:**
Millions of distinct packaged products are sold across brick-and-mortar retail stores, wholesale mandis, supermarkets, and e-commerce fulfillment hubs. Today, inspection by State Legal Metrology officers is entirely manual. Inspectors physically visit shops, examine packages with magnifying glasses, manually measure text heights using millimeter gauges, verify calculations with pocket calculators, and handwrite legal inspection notices. As a result, an inspector can realistically audit only 15 to 25 packages in a workday. Widespread consumer deception—such as altered MRPs, missing customer care details, deceptive unit quantities, and microscopic font sizes—goes undetected.

---

### 2. Our Proposed Solution: **MetroScan** (In Short)
**MetroScan** is an offline-first, dual-surface software ecosystem (Native Mobile Inspection Application + Centralized Web Command Portal) built on a unified **Flutter + Supabase** architecture:
- **At the Retail Front:** An enforcement inspector or consumer uses their smartphone camera to capture multi-angle images of any package.
- **Sub-Second Extraction:** An on-device optical character recognition engine extracts all printed text blocks and spatial coordinates in under 800 milliseconds without requiring active internet connectivity.
- **Intelligent Semantic Mapping:** A specialized generative AI classifier categorizes raw text lines into statutory declaration fields and flags missing elements.
- **Statutory Rule Engine:** A deterministic verification engine evaluates the extracted data against the exact clauses of the 2011 Rules (including syntax verification, unit checks, and millimeter font-size estimation).
- **Instant Official Action:** In under 30 seconds from shutter click, the system generates a tamper-evident digital inspection report (PDF) complete with geo-coordinates, timestamp, and photographic evidence. The report can be **downloaded directly**, **dispatched via WhatsApp**, or **sent via email** — all through the native device share mechanism at zero API cost.
- **At the Central Command:** All inspection audits sync in real time to a central dashboard displaying regional violation heatmaps, repeat offender analytics, and enforcement tracking.

---

## Analysis of the Reference Video & Key Takeaways

The provided reference video (`https://www.youtube.com/watch?v=3DOWuYKxDHs`) demonstrates real-time optical scanning workflows for physical product packaging and text recognition. Analyzing this implementation reveals four critical architectural lessons that directly shape the MetroScan product strategy:

1. **Active Camera Viewfinder vs. Passive Photo Taking:**
   Instead of forcing users to take a photo, wait 5 seconds, realize it was blurry, and retake it, the application must provide an interactive viewfinder guide with real-time text density feedback. The interface visually indicates whether the packaging label is properly framed, illuminated, and focused before analysis begins.
2. **Edge Computing Over Cloud Offloading:**
   Uploading uncompressed 12-megapixel smartphone photos to cloud servers introduces significant latency (3 to 7 seconds per round-trip) and causes failures in basement supermarkets, wholesale warehouses, and rural markets where cellular signals are weak. Running text recognition directly on the mobile device's Neural Processing Unit (NPU) guarantees instant, reliable performance.
3. **Multi-Stage Processing Pipeline:**
   Accurate compliance checking cannot be done in a single raw step. The pipeline must separate physical text extraction from semantic legal validation:
   - Stage 1: Optical Detection (identifying character boundaries and bounding boxes)
   - Stage 2: Structural Assembly (grouping lines into logical paragraphs and labels)
   - Stage 3: Semantic Parsing (understanding what each text segment represents)
   - Stage 4: Legal Rule Validation (testing against statutory mandates)
4. **Visual Scorecard Over Dense Logs:**
   Enforcement officers on field duty do not have time to read raw terminal outputs or multi-page text logs. The user interface must present an immediate, color-coded visual scorecard (Green for compliant, Red for non-compliant, Amber for warnings) mapped directly against statutory rules.

---

## Mobile App vs. Website — What Should You Build?

### The Strategic Recommendation: **Build BOTH from a Single Codebase**

To score maximum marks in SIH evaluation, building only a mobile app or only a website leaves an incomplete solution:
- If you build **only a website**, field enforcement is impractical. Inspectors cannot carry laptops through store aisles or hold a laptop webcam up to a bag of flour.
- If you build **only a mobile app**, senior administrators, legal directors, and ministry officials have no centralized oversight, bulk reporting, or regional analytics.

### How Flutter Solves This Without Doubling Work
By selecting **Flutter & Dart**, your team writes **one single codebase** that compiles natively into:
1. **The Mobile Application (Android / iOS):** Optimized for field inspectors and everyday consumers. Focuses on high-speed multi-angle camera capture, on-device OCR, offline caching, GPS tagging, and direct WhatsApp sharing.
2. **The Web Management Portal (Desktop Chrome / Edge / Safari):** Optimized for district controllers and ministry directors. Focuses on high-density data tables, interactive India geographic maps, violation trends, administrative user management, and bulk PDF notice downloads.

Both surfaces connect to the exact same database, share the exact same data models, and use identical business logic.

---

## What is OCR? — A Beginner's Guide

### The Foundational Concept
**OCR stands for Optical Character Recognition.** In everyday terms, cameras capture images as grids of colored dots called pixels. A computer looking at an image of a soap wrapper does not see words like "MRP" or "₹45.00"; it only sees millions of red, blue, and green numbers. 

OCR is the artificial intelligence technology that analyzes those pixel arrangements, recognizes geometric character patterns (such as curves, intersecting strokes, and vertical lines), and translates them into editable, searchable digital characters that a computer can read, store, and process.

### The 5 Steps of Modern OCR Processing

```
[ Step 1: Raw Image Capture ]
   A photo of packaging with shadows, reflections, and varied angles.
            │
            ▼
[ Step 2: Computer Vision Preprocessing ]
   - Grayscale conversion: Removes distracting colors.
   - Contrast enhancement & thresholding: Separates dark ink from light backgrounds.
   - Deskewing & rotation: Straightens tilted text lines.
            │
            ▼
[ Step 3: Text Detection (Locating) ]
   The neural network scans the image and draws invisible rectangular coordinates
   around text blocks, lines, and words. These are called Bounding Boxes.
            │
            ▼
[ Step 4: Character Recognition (Reading) ]
   Inside each bounding box, a trained convolutional and recurrent neural network
   determines the exact letter, numeral, or punctuation mark.
            │
            ▼
[ Step 5: Structured Output Generation ]
   The OCR engine outputs clean text alongside metadata:
   - The detected string (e.g., "Net Qty: 500 g")
   - The bounding box coordinates: (X, Y, Width, Height)
   - The algorithmic confidence level (e.g., 98.4%)
```

### Why Bounding Boxes Are Critical for Legal Metrology
Under Legal Metrology Rule 6(3), text cannot just be present; it must meet minimum physical font heights (such as 1.0 mm, 2.0 mm, or 4.0 mm depending on the package surface area). Because modern on-device OCR provides exact bounding box heights in pixels, MetroScan can calculate the physical millimeter height of letters when calibrated against a reference object or packaging scale.

---

## Complete Legal Metrology Rules Checklist

The system must validate packaging against the specific provisions of the **Legal Metrology (Packaged Commodities) Rules, 2011**. The following 10 statutory declarations form the core rule validation matrix:

| Statutory Rule | Declaration Name | Mandatory Format & Statutory Requirements | Common Violations Detected |
| :--- | :--- | :--- | :--- |
| **Rule 6(1)(a)** | Manufacturer / Packer / Importer Details | Complete legal name and full physical address (flat/survey number, street, city, state, postal PIN code). For imported goods, the importer's full details must appear. | Using vague names, missing physical address, mentioning only a website or city name without street address. |
| **Rule 6(1)(b)** | Generic / Common Commodity Name | The common or generic identity of the commodity contained inside (e.g., "Refined Sunflower Oil", "Wheat Flour"). | Concealing generic name under aggressive marketing brand names (e.g., only writing "Crunchy Bliss" without stating "Biscuits"). |
| **Rule 6(1)(c)** | Net Quantity | Stated strictly in standard SI metric units: mass (g, kg), volume (ml, L), length (cm, m), area (sq. m), or numerical count (N or U). Must be on the Principal Display Panel. | Using non-standard units (e.g., "gms", "kilos", "litres" spelled incorrectly, or imperial ounces/pounds), placing net qty on back folds. |
| **Rule 6(1)(d)** | Manufacturing / Packing Date | Month and year of manufacture, packing, or import (e.g., "07/2024", "July 2024", "Mfg Date: 08/24"). | Missing date completely, ambiguous batch codes without explicit month/year identifiers, illegible stamping. |
| **Rule 6(1)(e)** | Maximum Retail Price (MRP) | Must be clearly declared with the mandatory phrase *"Inclusive of all taxes"* or *"Incl. of all taxes"*. Format: *"MRP ₹ ...... (inclusive of all taxes)"*. | Omitting the tax inclusion clause, altering or overwriting prices with stickers, charging above declared MRP. |
| **Rule 6(1)(f)** | Best Before / Expiry Date | Mandatory for perishable commodities or items liable to deteriorate over time. Must state month/year or duration from packing date. | Missing on food items, cosmetics, or chemical commodities; contradictory date markings. |
| **Rule 6(1)(g)** | Consumer Care Details | Complete contact information of the designated consumer grievance officer: Name/Designation, Physical Address, Telephone Number, and Email Address. | Declaring only an email without a contact telephone number, or listing an inactive phone number. |
| **Rule 6(1)(h)** | Country of Origin | Mandatory for all imported goods. Must explicitly name the country of origin/manufacture (e.g., "Country of Origin: Vietnam"). | Concealing imported status, omitting country of origin on cross-border e-commerce consignments. |
| **Rule 6(1)(i)** | Unit Sale Price (USP) | Mandatory declaration of price per standard unit (e.g., "₹0.40 per g" or "₹40.00 per 100g", "₹120.00 per L"). | Omitting USP on multi-pack or non-standard package volumes, preventing fair consumer comparison. |
| **Rule 6(3)** | Minimum Font & Numeral Height | Minimum character height based on Principal Display Panel (PDP) area: $\le 100\text{ cm}^2 \rightarrow \ge 1\text{ mm}$; $100\text{ to }500\text{ cm}^2 \rightarrow \ge 2\text{ mm}$; $500\text{ to }2500\text{ cm}^2 \rightarrow \ge 4\text{ mm}$; $> 2500\text{ cm}^2 \rightarrow \ge 6\text{ mm}$. | Printing critical warnings and declarations in tiny, unreadable fine print under 1 mm height to mislead buyers. |

---

## Complete Product Features

### Mobile Inspection Application (Android — Primary Target)
1. **Dual-Role Login System:** Two separate entry points — **Consumer Login** (email/Google, lightweight scan summary) and **Official/Inspector Login** (email/Google, full legal certificate with badge and department credentials). New accounts default to Consumer; inspector access requires admin approval or invite code.
2. **Guided Multi-Image Shutter:** A dynamic capture tray allowing between 1 and 6 photographs per inspection (front display panel, information panel, barcode/MRP panel, side folds).
3. **On-Device Edge OCR Engine:** Instant offline text recognition executing within 800 milliseconds via neural models embedded inside the application package.
4. **Reference-Based Font Calibration:** Primarily uses detected EAN-13 barcode dimensions (standard 37.29 mm width) for automated pixels-per-millimeter calculation. Optional coin placement (₹1 coin, 25 mm diameter) as a secondary calibration method.
5. **Interactive Verification Scorecard:** A real-time summary card presenting categorized findings: Passed declarations (Green), Missing declarations (Red), and Non-compliant syntax/size issues (Amber).
6. **Human-in-the-Loop Field Editor:** Allows inspectors to tap and manually adjust any extracted text line if optical distortion or reflective plastic wrapping lowered confidence scores.
7. **Dual Report Generation (PDF):**
   - **Official Inspection Certificate** (Inspector login): Full legal document with inspector credentials, badge ID, department, GPS coordinates, timestamp, compliance matrix, evidence photographs, and QR code linking to the web portal.
   - **Consumer Scan Summary** (Consumer login): Simplified report without legal authority branding — shows product details, compliance result, and evidence.
8. **Triple Distribution System:**
   - **📥 Download PDF** — Save directly to device Downloads folder.
   - **📱 Send via WhatsApp** — Opens native share sheet with PDF pre-attached; user selects WhatsApp.
   - **📧 Send via Email** — Opens native share sheet with PDF pre-attached; user selects Gmail/Outlook/any email app.
   All three options use `share_plus` native OS share intents — **zero API cost, zero configuration, works offline**.
9. **Offline Synchronization Buffer:** Automatically saves inspection data in encrypted local storage when operating in basement stores or remote rural mandis, syncing seamlessly once network connectivity resumes.
10. **Barcode / QR Code Auto-Fetch:** Scans EAN-13, UPC, and DataMatrix codes to cross-reference known product master catalogs, accelerating audits for known brands.

### Centralized Web Management Command Portal
1. **National & Regional Executive Dashboard:** Displays macro compliance metrics, inspection volume trends, and percentage compliance ratios across districts and states.
2. **Interactive Geographic Inspection Heatmap:** Uses OpenStreetMap layers to plot geo-tagged inspection locations, identifying localized clusters of non-compliant retail centers.
3. **Repeat Offender & Brand Risk Analytics:** Aggregates violation data by brand name, manufacturer, and distributor, highlighting repeat violators for targeted regulatory audits.
4. **Comprehensive Scanned Product Repository:** Searchable archive of all historic inspections filterable by date, location, compliance status, category, and inspector ID.
5. **Role-Based Access Control (RBAC):** Tiered security access separating Central Administrators, Regional Controllers, Field Inspectors, and Consumer Public Users.
6. **Bulk Legal Notice Generation:** Tools to batch-export formal compliance inquiry notices, violation records, and court-admissible audit trails in PDF and spreadsheet formats.

---

## End-to-End System Workflow

### Stage 1: Authentication & Access Control
- Users choose between **Consumer Login** or **Official Login** from the dual-tab login screen.
- **Consumer Login:** Email/Password or Google OAuth. Minimal profile (name, email). Routed to Consumer Dashboard.
- **Official Login:** Email/Password or Google OAuth. First-time officials complete a profile setup screen (badge ID, department, designation, division). Routed to Inspector Dashboard.
- The system checks the user's role (`consumer`, `inspector`, `admin`, `super_admin`) from the `profiles` table and tailors available actions accordingly.

### Stage 2: Packaging Image Acquisition
- The inspector selects "New Inspection" and selects the product category (Food, Cosmetic, Electronic, or General Commodity).
- The camera interface guides the inspector to capture:
  - Photograph 1: Principal Display Panel (Product Name, Brand, Net Quantity)
  - Photograph 2: Information Panel (Manufacturer, Address, Consumer Care)
  - Photograph 3: MRP & Date Stamping Panel (MRP, Batch, Mfg Date, Expiry)
  - Photographs 4 to 6 (Optional): Sides, barcodes, or reference calibration view.

### Stage 3: Image Optimization & On-Device OCR
- The captured images undergo client-side image processing: converting to grayscale, normalizing local contrast, and correcting skewed angles.
- Google ML Kit processes the optimized bitmaps locally on the smartphone, returning an array of recognized text blocks along with 2D bounding boxes and confidence metrics.

### Stage 4: Semantic Classification via Generative AI
- The extracted text blocks are transmitted to Google Gemini 2.0 Flash in lightweight JSON structure.
- The language model performs semantic entity recognition:
  - It maps unstructured lines to legal categories (e.g., identifying that "Pkd by: XYZ Ent." corresponds to Manufacturer/Packer).
  - It handles common typographical variations and multilingual headers (English and Hindi).
  - It explicitly identifies which mandatory fields are entirely absent from the text.

### Stage 5: Deterministic Legal Rule Validation
- The structured entities are evaluated against programmatic rules:
  - Net Quantity Rule: Validates standard SI unit formatting (`g`, `kg`, `ml`, `l`).
  - MRP Rule: Verifies the exact presence of *"inclusive of all taxes"*.
  - Consumer Care Rule: Checks that both a telephone number and an email address exist.
  - Font Size Calculation: Calculates physical millimeter letter heights from bounding box coordinates and compares them against package area thresholds.

### Stage 6: Review, Reporting & Distribution
- The user reviews the live scorecard on screen.
- Upon confirmation, the application generates a role-appropriate PDF:
  - **Inspector/Admin:** Official Inspection Certificate with inspector credentials, badge ID, department branding, GPS coordinates, timestamp, compliance matrix, evidence photos, and QR code.
  - **Consumer:** Simplified Scan Summary with product details, compliance result, and evidence (no legal authority branding).
- The user chooses from **three distribution options:**
  - **📥 Download** — saves PDF to device Downloads folder.
  - **📱 WhatsApp** — opens native share sheet with PDF pre-attached.
  - **📧 Email** — opens native share sheet; user selects email app.
- The certificate/summary and images are saved to Supabase Storage.
- The inspection data syncs to the central database for immediate display on the administrative web dashboard.

---

## Indian Government UI/UX Design & Architecture

### Design Philosophy & National Standards
To instill trust and authority, MetroScan strictly adheres to:
- **GIGW (Guidelines for Indian Government Websites and Apps):** Ensuring high contrast, clear visual hierarchy, accessible touch targets, and bilingual support.
- **UX4G (Government Design System 3.0):** Standardized typography, component spacing, and clean layouts consistent with national digital infrastructure like DigiLocker and UMANG.

### The Authority Color Palette
- **Primary Sovereign Blue (`#1A5276` / `#0B3C5D`):** Represents legal authority, institutional trust, and digital governance. Used on app bars, primary action buttons, and official report headers.
- **Tiranga Saffron Accent (`#F39C12` / `#E67E22`):** Used sparingly on active tab indicators, primary capture triggers, and national header accents.
- **Statutory Compliant Green (`#27AE60`):** Indicates fully compliant declarations and verified packages.
- **Statutory Violation Red (`#C0392B`):** Highlights missing mandatory declarations, altered prices, or illegal packaging.
- **Regulatory Warning Amber (`#F1C40F`):** Marks borderline font sizes, missing tax sub-clauses, or unverified date formats.
- **Clean Neutral Canvas (`#F8F9FA`):** High-readability light background with elevated white cards (`#FFFFFF`) to prevent eye fatigue during lengthy outdoor field inspections.

### Screen Layout Descriptions

#### 1. Inspector Dashboard Screen
- **Header:** Government emblem and departmental branding, active inspector name, enforcement division, and online/offline status pill.
- **Quick Statistics Carousel:** Four clean KPI cards showing Today's Audits, Violations Identified, Pending Notices, and Overall District Compliance Percentage.
- **Primary Floating Action Button:** Prominent, centered button with a camera icon labeled "Start Inspection" positioned comfortably within the one-handed thumb zone.
- **Recent Audit Activity Feed:** A scrollable list of recently scanned products showing brand name, timestamp, compliance pill (Pass/Fail/Warning), and quick-action buttons to view or share the report.

#### 2. Multi-Image Capture Screen
- **Top Bar:** Step indicator showing capture progress (e.g., "Image 2 of 4 — Capture Information Panel").
- **Camera Frame:** Live preview with semi-transparent framing brackets to help align label edges.
- **Bottom Tray:** A horizontal carousel showing real-time thumbnails of captured images with checkmarks, a retake button, and an "Add Side Panel" button.
- **Action Buttons:** Large circular shutter trigger alongside a gallery import option for auditing pre-existing evidence photos.

#### 3. Compliance Scorecard Screen
- **Overall Verdict Card:** Large compliance badge displaying overall status: "COMPLIANT", "NON-COMPLIANT", or "PARTIAL COMPLIANCE" with an overall percentage score.
- **Categorized Checklist Accordion:** Nine expandable declaration rows. Each row displays:
  - Status Icon (Green Check, Red Cross, Amber Warning)
  - Declaration Category Title (e.g., "Maximum Retail Price — Rule 6(1)(e)")
  - Extracted Text Value in quotes
  - Statutory Reference Citation
  - Action link to manually edit or verify against original image crop
- **Bottom Action Bar:** Three equal-width action buttons: **\"📥 Download PDF\"**, **\"📱 Send via WhatsApp\"**, and **\"📧 Send via Email\"**.

#### 4. Web Command Center (Desktop)
- **Persistent Left Navigation Sidebar:** Direct links to Overview, Real-Time Heatmap, Product Catalog, Violation Registry, Inspector Management, and System Settings.
- **Main Command Canvas:** Top row features macro KPI cards; middle section features an interactive OpenStreetMap of India with clustering pins; bottom section contains high-density, searchable audit tables with sorting and CSV/PDF export buttons.

---

## Complete Technology Analysis & Tech Stack Justification

### Layer-by-Layer Architectural Matrix

| Architecture Layer | Recommended Technology | Why This Specific Choice? | Technical Alternatives Rejected |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | **Flutter 3.x (Dart)** | Single codebase compiling natively to Android and Web. Delivers 60 FPS performance, rich camera access, and unified state logic across mobile and desktop. **Targets Android + Web only** for the hackathon (no iOS/Mac dependency). | React Native (inferior web rendering and bridge latency); native Kotlin/Swift (requires writing code twice). |
| **State Management** | **Riverpod 2.x** | Compile-safe, testable, and completely independent of the Flutter UI widget tree. Handles asynchronous states (camera, OCR, API calls) without race conditions. | Provider (lacks modern compile-time safety); BLoC (excessive boilerplate for a fast-paced hackathon). |
| **On-Device OCR** | **Google ML Kit Text Recognition v2** | Runs entirely on-device with zero network latency (<800ms). Supports Latin and Devanagari scripts. Completely free with no monthly API billing caps. | Tesseract OCR (significantly slower, higher CPU usage, lower accuracy on complex mobile labels); Cloud Vision (fails when offline, introduces network lag). |
| **Semantic AI Engine** | **Google Gemini 2.0 Flash API** | Industry-leading speed and reasoning for structured JSON extraction. Capable of understanding messy, multi-line OCR text and categorizing declarations with pinpoint accuracy. Free tier: 15 RPM, 1500 RPD, 1M TPM. | Gemini 1.5 Pro / GPT-4o (slower response latency, higher token cost); Custom BERT models (requires extensive training data and GPU hosting). |
| **Backend & Database** | **Supabase (PostgreSQL)** | Combines enterprise-grade relational PostgreSQL with managed authentication (Email/Password + Google OAuth), instant REST/GraphQL endpoints, built-in S3-compatible file storage, and Row Level Security (RLS). | Firebase Firestore (NoSQL document model makes complex multi-table SQL queries and regulatory violation analytics difficult); Custom Node.js/Express (requires building authentication, file storage, and server hosting from scratch). |
| **Mapping & GIS** | **Flutter Map + OpenStreetMap** | Completely free and open-source map visualization. Displays geo-tagged inspection coordinates and violation heatmaps without Google Maps API credit card requirements or billing quotas. | Google Maps Platform (strict billing quotas, credit card requirement, potential cutoff during live demo). |
| **Document Engine** | **Dart `pdf` & `printing`** | Generates pixel-perfect, vector-based PDF inspection certificates directly on the mobile device or browser client without requiring server rendering. | Server-side Puppeteer / HTML-to-PDF (heavy backend overhead, requires network connectivity, adds 3–5 seconds delay). |
| **Report Distribution** | **`share_plus` (Native OS Share Sheet)** | Single unified mechanism for all three distribution channels (Download, WhatsApp, Email). 100% free, zero-config, works offline. User selects target app from native share sheet. | Meta Cloud API (requires Business verification, template approval — impossible in 36 hours); Commercial SMS/Email Gateways (expensive per-message charges). |

---

## Smoothness, Efficiency & Latency Optimization (<30-Second SLA)

To ensure the product runs smoothly during live hackathon judging and field testing, the architecture implements five specific performance safeguards:

1. **Hardware-Accelerated On-Device OCR:**
   By processing images on-device via Google ML Kit, we eliminate the step of uploading 10MB camera bitmaps to the cloud. Raw text extraction finishes in 600 to 800 milliseconds.
2. **Text-Only Cloud Transmission:**
   When communicating with the Gemini AI semantic classifier, the application transmits **only the extracted text strings (approx. 2 to 4 Kilobytes)** rather than full-resolution images. This payload uploads and receives a response in under 2 seconds even over constrained 3G mobile connections.
3. **Multithreaded Background Workers (Dart Isolates):**
   Heavy computer vision tasks—such as image downsampling, contrast stretching, and PDF compilation—are executed inside separate Dart background isolates. This keeps the user interface thread completely unblocked, ensuring smooth 60 FPS animations with zero stutter.
4. **Client-Side Image Downsampling:**
   Smartphone cameras frequently capture 4000x3000 pixel images. Before running OCR, the client downsamples images to an optimal resolution of 1920x1080. This preserves full character sharpness while cutting memory consumption and image processing time by more than 60%.
5. **Local-First Caching (Offline Database):**
   Every scan record is written immediately to a high-speed local key-value store (Hive DB) before any network call is initiated. If the device is offline, the user experiences zero blocking spinners; the inspection is saved instantly and synchronized in the background once internet connectivity is restored.

---

## Multi-Image Capture Strategy for 3D Packaging

Packaged commodities are three-dimensional objects (cylinders, cardboard cartons, flexible pouches). Mandatory declarations are rarely printed on a single visible surface:
- The **Principal Display Panel** contains the brand name, product name, and net quantity.
- The **Back or Side Information Panel** contains the manufacturer address, batch details, and customer care details.
- The **Top Flap or Bottom Base** contains the stamped MRP, packing date, and expiry date.

### How MetroScan Handles Multi-Image Analysis
1. **The Visual Capture Tray:** The user interface presents a structured capture workflow prompting the user to photograph up to 6 angles of the package.
2. **Composite Text Assembly:** The on-device OCR runs on each captured photo individually. The system tags each extracted text block with its image origin (e.g., `[Image_1_Front]`, `[Image_2_Back]`, `[Image_3_MRP_Base]`).
3. **Unified Semantic Consolidation:** All text streams are merged into a single multi-panel context and passed to the AI classifier. This allows the system to cross-reference declarations across faces—for example, validating that a net quantity stated on the front panel correctly corresponds to the unit sale price stated on the back panel.

---

## Unique Selling Propositions (USPs) to Win SIH

To stand out from competitors who build basic camera-and-OCR prototypes, MetroScan incorporates five high-impact USPs:

1. **The 30-Second Enforcement SLA:**
   While competing systems take minutes uploading files and running slow cloud models, MetroScan executes image preprocessing, on-device OCR, semantic classification, rule checking, and PDF notice generation in under 30 seconds.
2. **True Offline-First Capability:**
   Designed for India's operational ground reality. An inspector can scan products in underground basements, remote rural grain markets, or steel godowns with zero cellular reception. Everything runs locally, storing audit trails that sync automatically upon returning to network coverage.
3. **Hybrid Verification Architecture (AI + Statutory Rules):**
   Pure AI models can hallucinate numbers. Pure regular expressions break on real-world label layout variations. MetroScan uses generative AI exclusively for flexible semantic classification, and feeds that structured output into an immutable, deterministic rule engine that verifies exact statutory syntax and legal limits.
4. **Physical Millimeter Font-Size Measurement:**
   MetroScan does not merely check if text exists; it estimates physical character height in millimeters using bounding-box scaling against reference objects, directly validating compliance with Rule 6(3) font-size mandates.
5. **Zero-Cost Triple Report Distribution:**
   Eliminates expensive SMS gateways and third-party email SaaS. Reports can be **downloaded**, **sent via WhatsApp**, or **sent via email** — all through the native OS share sheet using `share_plus` at zero API cost. No server-side infrastructure required.
6. **Live GIS Violation Heatmapping:**
   Every inspection automatically captures GPS coordinates. The central web command portal visualizes regional violation densities across districts, empowering authorities to shift from random inspections to intelligence-driven enforcement.
7. **Dual-Role Architecture with Role-Appropriate Output:**
   Separate Consumer and Official login paths ensure the right experience for each user. Officials get legally-branded inspection certificates with credentials and QR codes; consumers get clean, shareable scan summaries. Both feed into the same compliance engine.

---

## 4-Person Team Workload Division & 36-Hour Hackathon Schedule

### Team Roles, Service Ownership & Key Packages

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           4-PERSON TEAM ALLOCATION                             │
├───────────────────┬────────────────────────────────────────────────────────────┤
│ PERSON 1          │ 📱 Frontend Lead & Mobile/Web UI Specialist                │
│ (Frontend Lead)   │ • Implements ALL Flutter screens (mobile + web responsive) │
│                   │ • Builds dual-tab login screen (Consumer / Official)       │
│                   │ • Builds multi-image camera tray & viewfinder overlay      │
│                   │ • Builds compliance scorecard with 3 action buttons        │
│                   │ • Integrates UX4G / GIGW color themes & typography         │
│                   │ • Builds web portal dashboard, heatmap, analytics          │
│                   │                                                            │
│                   │ 🔧 Owns: All files in screens/, widgets/, theme/           │
│                   │ 📦 Packages: flutter, go_router, flutter_riverpod,         │
│                   │    fl_chart, flutter_map, shimmer, camera (UI only)        │
├───────────────────┼────────────────────────────────────────────────────────────┤
│ PERSON 2          │ 🧠 AI / Computer Vision & Core Engine Specialist           │
│ (AI / CV Lead)    │ • Integrates Google ML Kit on-device OCR + barcode scan    │
│                   │ • Implements image preprocessing in Dart Isolates          │
│                   │ • Crafts Gemini 2.0 Flash classification prompts           │
│                   │ • Programs the deterministic Legal Metrology rule engine   │
│                   │ • Implements font size estimation (barcode-based px/mm)    │
│                   │ • Builds multi-image text consolidation logic              │
│                   │ • Implements confidence scoring algorithm                  │
│                   │                                                            │
│                   │ 🔧 Owns: ocr_service.dart, image_preprocessor.dart,        │
│                   │    gemini_classifier.dart, compliance_engine.dart,          │
│                   │    font_size_calculator.dart, confidence_scorer.dart        │
│                   │ 📦 Packages: google_mlkit_text_recognition,                │
│                   │    google_mlkit_barcode_scanning, google_generative_ai,     │
│                   │    image, dart:isolate                                     │
├───────────────────┼────────────────────────────────────────────────────────────┤
│ PERSON 3          │ ☁️ Backend, Cloud & Security Specialist                    │
│ (Backend Lead)    │ • Sets up Supabase project, PostgreSQL schema, indexes     │
│                   │ • Configures Row-Level Security (RLS) policies             │
│                   │ • Implements Email/Password + Google OAuth dual-login      │
│                   │ • Builds Supabase Storage buckets for images & PDFs        │
│                   │ • Implements offline sync (Hive local cache → Supabase)    │
│                   │ • Sets up Supabase Realtime for web portal live updates    │
│                   │ • Handles web deployment (Vercel/Firebase Hosting)         │
│                   │                                                            │
│                   │ 🔧 Owns: auth_service.dart, profile_service.dart,          │
│                   │    scan_service.dart, product_service.dart,                 │
│                   │    storage_service.dart, sync_service.dart                  │
│                   │ 📦 Packages: supabase_flutter, hive_flutter,               │
│                   │    connectivity_plus, path_provider                        │
├───────────────────┼────────────────────────────────────────────────────────────┤
│ PERSON 4          │ 📄 Report Engine, QA, Pitch & Demo Specialist              │
│ (Integration Lead)│ • Builds PDF certificate (official) + summary (consumer)  │
│                   │ • Implements triple distribution (Download/WhatsApp/Email) │
│                   │ • Runs end-to-end QA testing across full pipeline          │
│                   │ • Collects physical product packaging for demo props       │
│                   │ • Creates presentation slides & architecture diagrams      │
│                   │ • Rehearses and leads the 5-minute live demo               │
│                   │                                                            │
│                   │ 🔧 Owns: pdf_generator.dart, share_service.dart            │
│                   │ 📦 Packages: pdf, printing, share_plus, path_provider,     │
│                   │    crypto, uuid                                            │
└───────────────────┴────────────────────────────────────────────────────────────┘
```

### Priority Tiers (Critical Path)

> 🔴 **MUST HAVE (Hours 0–16):** Without these, there is no product to demo.
> 🟡 **SHOULD HAVE (Hours 16–28):** These make the difference between "works" and "wins."
> 🟢 **NICE TO HAVE (Hours 28–34):** Bonus scoring; skip if behind schedule.
> 🔵 **DEMO PREP (Hours 34–36):** Lockdown. No new features. Rehearse only.

### 36-Hour Hackathon Hour-by-Hour Roadmap

| Timeframe | Person 1 (Frontend) | Person 2 (AI / CV) | Person 3 (Backend) | Person 4 (Reports & Pitch) |
| :--- | :--- | :--- | :--- | :--- |
| **🔴 Hours 00 — 04** | Set up Flutter repo, add all deps to `pubspec.yaml`, create `lib/` folder structure, implement theme (colors, typography), set up `GoRouter` routes, build splash screen. | Add ML Kit OCR + barcode scanning deps, write `OcrService` class: image file path → `List<TextBlock>` with bounding boxes. Verify basic OCR on a test image. | Create Supabase project, execute all 6 `CREATE TABLE` SQL statements, enable Auth providers (Email/Password + Google OAuth), configure redirect URLs. | Design the PDF certificate layout on paper/Figma: header, inspector info, product info, evidence photos, 10-rule compliance table, verdict, GPS, QR code, footer. |
| **🔴 Hours 04 — 08** | Build dual-tab login screen (Consumer / Official), email+password forms, Google OAuth button, input validation. Build profile setup screen for officials (badge ID, department, designation). | Write `ImagePreprocessor` using Dart `image` package: resize to 1920×1080, grayscale, contrast, auto-rotate via EXIF. Run in `Isolate`. | Write `AuthService` (sign up, login, Google OAuth, session, logout) and `ProfileService` (create/update profile, check role). Write RLS policies on all 6 tables. | Write `PdfGenerator` class using `pdf` package: build official inspection certificate with all sections. Accept `ComplianceResult` + `ScanData` + image bytes → return PDF bytes. |
| **🔴 Hours 08 — 12** | Build camera capture screen: multi-image tray (1–6 photos), guided step indicator ("Photo 1: Front Panel"), live camera preview with framing brackets, retake/gallery buttons. | Write `GeminiClassifier` service: craft prompt, call Gemini 2.0 Flash, parse structured JSON response mapping OCR text to Rule 6(1)(a)–(i). Handle errors, timeouts, offline fallback. | Write `ScanService` (CRUD for scans), `ProductService` (upsert products, barcode lookup), `DeclarationService` (batch insert rule results), `ReportService` (save PDF metadata). | Write `ShareService`: (1) Save PDF to Downloads via `path_provider`, (2) Share via `share_plus` for WhatsApp/Email, (3) Print preview via `printing`. Wire up 3 buttons. |
| **🔴 Hours 12 — 16** | Build compliance scorecard screen: overall verdict badge, 10-rule accordion with green/red/amber chips, extracted text display, 3 action buttons (📥 Download / 📱 WhatsApp / 📧 Email). | Write `ComplianceEngine` class: validate 10 rules deterministically — SI units (regex), MRP "inclusive of all taxes" (string match), phone+email presence, date format. Emit `ComplianceResult`. | Configure Supabase Storage buckets: `scan-images` (public read), `reports` (private). Write `StorageService`: upload image, upload PDF, get signed URL. | Build consumer "Scan Summary" PDF variant (no inspector credentials). Detect user role → generate appropriate report type. Test both PDF variants. |
| **🟡 Hours 16 — 20** | Build web portal responsive layout: sidebar nav (desktop), bottom nav (mobile). Dashboard with 4 KPI stat cards, inspection history table with search/filter. | Write `FontSizeCalculator`: barcode bounding box → px/mm ratio → font height mm → compare against Rule 6(3) thresholds. | Write `SyncService` using `hive_flutter` + `connectivity_plus`: offline local save → detect network → batch sync → mark synced. | Test FULL end-to-end flow: Login → Camera → OCR → AI → Scorecard → PDF → Share. Document every bug. Test with 4+ real products. |
| **🟡 Hours 20 — 24** | Integrate `flutter_map` with OpenStreetMap pins. Add `fl_chart` analytics (bar/pie for violations). | Write `MultiImageConsolidator`: tag OCR by image source → merge → deduplicate → single Gemini context. Write `ConfidenceScorer`. | Set up Supabase Realtime for live web portal updates. Write dashboard stat query helpers. | Collect 4 real products: (A) compliant FMCG, (B) MRP violation, (C) missing consumer care, (D) microscopic font. |
| **🟡 Hours 24 — 28** | Polish: loading shimmers, error states, empty states, smooth transitions, responsive consistency. | Test edge cases: wrinkled packaging, foil, Hindi text, partial labels. Tune Gemini prompts. Add regex fallback classifier. | Build Flutter web → deploy to Vercel/Firebase Hosting. Build Android release APK. Test on 2 physical phones. | Create 8–10 presentation slides: Problem → Solution → Live Demo → Architecture → USPs → Impact. Time the 5-minute pitch. |
| **🟢 Hours 28 — 32** | Fix UI bugs, conduct UX walkthroughs on mobile + web. Add visual bounding-box overlay on images (optional wow factor). | Final accuracy tuning and error handling for camera capture failures. Verify font size estimation produces reasonable mm values. | Verify RLS policies correct. Test offline→online sync. Verify cloud backup of all photos and PDFs. | Rehearse live demo 3+ times with physical packaging. Practice airplane mode test. Ensure WhatsApp + Email share works. |
| **🔵 Hours 32 — 36** | **DEMO LOCKDOWN** — Final visual tweaks only. Prepare demo device. | **DEMO LOCKDOWN** — Final accuracy verification with demo products. | **DEMO LOCKDOWN** — Verify cloud services. Prepare backup APK. | **DEMO LOCKDOWN** — Final rehearsal. Charge devices. Test projector. |

### Integration Contracts (Who Passes Data to Whom)

All 4 people must agree on the data models in `lib/models/` by **Hour 2**:
- **Person 2 → Person 1:** Returns a `ComplianceResult` object containing per-rule results + overall verdict.
- **Person 3 → Person 1:** Returns database model objects (`Profile`, `Scan`, `Product`, etc.) via service classes.
- **Person 4 ← Person 2:** Accepts `ComplianceResult` + captured image bytes → returns PDF bytes.
- **Person 1:** Wires everything into the UI using Riverpod providers.

---

## Interconnection Architecture: Frontend, Backend, AI & Pipelines

```
 ┌─────────────────────────────────────────────────────────────┐
 │                FLUTTER CLIENT APPLICATION                   │
 │           (Android Mobile + Desktop Web)                │
 └──────┬───────────────────────┬───────────────────────┬──────┘
        │                       │                       │
        │ 1. Local Processing   │ 2. Semantic Query     │ 3. Data Sync
        ▼                       ▼                       ▼
 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
 │ ON-DEVICE CV │        │ GOOGLE AI    │        │ SUPABASE     │
 │ & OCR ENGINE │        │ CLOUD API    │        │ POSTGRESQL   │
 ├──────────────┤        ├──────────────┤        ├──────────────┤
 │ • Image Prep │        │ • Gemini 2.0 │        │ • Auth & JWT │
 │ • ML Kit OCR │        │   Flash      │        │ • Profiles   │
 │ • BoundingBox│        │ • JSON Schema│        │ • Scans & DB │
 │ • Font Calc  │        │   Extraction │        │ • S3 Storage │
 │ • Rule Engine│        │ • Missing Flg│        │ • Realtime   │
 └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
        │                       │                       │
        └───────────────┬───────┴───────────────────────┘
                        ▼
        ┌────────────────────────────────┐
        │  COMPILED INSPECTION AUDIT     │
        ├────────────────────────────────┤
        │ • Structured Legal Scorecard   │
        │ • Official Signed PDF Document │
        │ • Real-Time Web Map Update     │
        │ • Download / WhatsApp / Email  │
        └────────────────────────────────┘
```

### Data Flow Protocol
1. **Local Pipeline:** Flutter Camera captures frames $\rightarrow$ Dart Image Library normalizes contrast $\rightarrow$ Google ML Kit processes bitmap $\rightarrow$ Text strings and bounding-box coordinates returned.
2. **AI Semantic Pipeline:** Flutter Client sends pure text JSON to Gemini API $\rightarrow$ Gemini returns structured classification schema $\rightarrow$ Client Rule Engine validates against 2011 Rules.
3. **Cloud & Storage Pipeline:** Flutter Client uploads generated PDF and compressed photos to Supabase Storage $\rightarrow$ Saves inspection metadata to PostgreSQL $\rightarrow$ Supabase Realtime notifies the Web Management Portal $\rightarrow$ Map pin appears instantly.
4. **Distribution Pipeline:** Client generates PDF locally $\rightarrow$ User selects distribution method (📥 Download to device / 📱 WhatsApp via share sheet / 📧 Email via share sheet) $\rightarrow$ `share_plus` handles native OS sharing at zero cost.

---

## Flutter Single-Codebase Strategy: Mobile to Web

Because Flutter targets multiple platforms from a single codebase, you do not maintain two separate applications. You maintain **one repository** with responsive layout branching. For the hackathon, we target **Android + Web only** (no iOS build — avoids Mac/Xcode dependency):

### How Platform Adaptability Works
- **Responsive Layout Branching:** When screen width is greater than 800 pixels (Desktop Web), the layout presents a multi-column command center with a permanent left navigation rail and high-density data tables. When screen width is under 800 pixels (Mobile), the layout presents a single-column mobile view with bottom navigation tabs.
- **Hardware Abstraction:**
  - On Android, image input connects directly to the device's native camera hardware via the `camera` package.
  - On Web, image input connects to file pickers via the `image_picker` package (web-compatible).
- **OCR Engine Fallback:**
  - On Android, text extraction runs through on-device Google ML Kit (instant, offline).
  - On Web, the portal is for administrative review only — no live OCR. If image analysis is needed on web, text extraction routes via the Gemini 2.0 Flash Vision API.
- **Unified Backend Connection:** Both Android and web instances communicate with the exact same Supabase database URL and anonymous API keys, sharing identical database tables, security policies, and storage buckets.

---

## Authentication Architecture: Dual-Login with Google OAuth + Email/Password

### Two Separate Login Flows

MetroScan implements **two distinct authentication entry points** tailored to different user types:

#### Consumer Login (Lightweight Access)
- **Auth Methods:** Email + Password (via Supabase Auth) **OR** Google OAuth single sign-on.
- **Profile Requirements:** Full name and email only. No badge, department, or designation fields.
- **Access Level:** Can scan products, view their own scan history, download/share simplified "Scan Summary" reports.
- **Restrictions:** Cannot access the web command portal, cannot generate official legal certificates, cannot see other users' inspection data.

#### Official / Inspector Login (Full Enforcement Access)
- **Auth Methods:** Email + Password **OR** Google OAuth (government/enterprise Google accounts).
- **Profile Requirements:** Full name, badge ID, department name, designation, enforcement division — filled during a mandatory profile setup screen after first login.
- **Access Level:** Full scanning with official inspection certificate generation, GPS tagging, legal authority branding, access to web command portal, view all inspections, generate bulk notices.
- **Role Sub-Types:**
  - `inspector` — Field scanning and certificate generation.
  - `admin` — Web portal analytics, inspector management, bulk operations.
  - `super_admin` — Full system control including user role management.
- **Upgrade Path:** New accounts default to `consumer`. Upgrade to `inspector` or `admin` requires admin approval or a pre-shared invite code.

#### Login Screen Design
```
┌──────────────────────────────┐
│        🏛️ MetroScan          │
│                              │
│   ┌──────────┐ ┌──────────┐  │
│   │ Consumer │ │ Official │  │
│   │  Login   │ │  Login   │  │
│   └──────────┘ └──────────┘  │
│                              │
│   [Consumer selected:]       │
│   ┌─ Email ──────────────┐   │
│   ├─ Password ───────────┤   │
│   ├─ [Login] [Google] ───┤   │
│   └──────────────────────┘   │
│                              │
│   [Official selected:]       │
│   ┌─ Email ──────────────┐   │
│   ├─ Password ───────────┤   │
│   ├─ [Login] [Google] ───┤   │
│   ├─ Badge ID ───────────┤   │
│   ├─ Department ─────────┤   │
│   └──────────────────────┘   │
└──────────────────────────────┘
```

### Why Email/Password Instead of WhatsApp OTP?
WhatsApp OTP authentication requires Meta Business Manager verification (which takes multiple business days), a verified business phone number, and pre-approved message templates. These prerequisites are impossible to satisfy within a 36-hour hackathon window. **Email/Password + Google OAuth** provides instant, zero-cost authentication that is fully functional from minute one. WhatsApp OTP remains a documented production roadmap enhancement.

### Technical Implementation
1. **Supabase Auth** handles both Email/Password sign-up/sign-in and Google OAuth callbacks.
2. After authentication, a `profiles` table record is created/updated with the user's role (`consumer`, `inspector`, `admin`, `super_admin`).
3. The Flutter app checks the `role` column after login and routes to the correct dashboard (Consumer Dashboard vs. Inspector Dashboard).
4. **Row Level Security (RLS)** policies on all database tables enforce that consumers can only read/write their own data, while inspectors and admins have broader access.

---

## Report Distribution System: Download, WhatsApp & Email

MetroScan provides **three distinct report distribution channels**, all powered by the native operating system share mechanism (`share_plus`) at **zero API cost**:

### Option 1: 📥 Download PDF (Direct Save)
- **Use Case:** Inspector or consumer wants to keep a local copy of the inspection report on their device.
- **How It Works:**
  1. The client-side PDF generator compiles the inspection certificate/summary into PDF bytes.
  2. The PDF is saved to the device's Downloads directory via `path_provider`.
  3. A confirmation toast shows the file path.
- **Cost & Configuration:** Zero. Pure local file operation.

### Option 2: 📱 Send via WhatsApp (Native Share)
- **Use Case:** Inspectors sharing reports with shopkeepers on the spot, or consumers sharing with friends.
- **How It Works:**
  1. The client-side PDF is saved to the app's cache directory.
  2. The application triggers `share_plus` with the PDF as an `XFile` attachment and a pre-filled caption:
     > *"Legal Metrology Compliance Report for [Product Name]. Compliance Score: [Score]%. Generated via MetroScan."*
  3. The native OS share sheet opens. The user taps WhatsApp to send the document.
- **Cost & Configuration:** Zero API costs, zero configuration, zero rate limits.

### Option 3: 📧 Send via Email (Native Share)
- **Use Case:** Formal report delivery to department officials, brand compliance officers, or legal counsel.
- **How It Works:**
  1. The same `share_plus` share sheet is triggered with the PDF attachment.
  2. The user selects their preferred email app (Gmail, Outlook, etc.) from the share sheet.
  3. The email client opens with the PDF pre-attached; the user enters recipients and sends.
- **Cost & Configuration:** Zero. Uses the user's own email account.

### UI Implementation
After generating the compliance result, the scorecard screen displays a bottom action bar with three equally-spaced buttons:

```
┌──────────────────────────────────────────┐
│  [📥 Download]  [📱 WhatsApp]  [📧 Email] │
└──────────────────────────────────────────┘
```

All three buttons invoke the same `ShareService` class with different mode parameters.

---

## Font Size Detection & Physical Scaling Methodology

Rule 6(3) sets strict minimum heights for declarations based on packaging area. The technical challenge is that camera images represent sizes in **pixels**, not **millimeters**.

### The MetroScan 3-Tier Measurement Pipeline
1. **Tier 1: Coin / Reference Calibration (High Precision Mode):**
   The inspector can place a standard Indian 1 Rupee coin (officially standardized at exactly $25.0\text{ mm}$ diameter) next to the packaging label. The computer vision algorithm detects the circular contour of the coin, counts its diameter in pixels, and establishes an exact physical scaling ratio:
   $$\text{Pixels-per-Millimeter Ratio} = \frac{\text{Coin Diameter in Pixels}}{25.0\text{ mm}}$$
   Using this ratio, any text bounding box height is converted to true physical millimeters:
   $$\text{Physical Font Height (mm)} = \frac{\text{Bounding Box Height in Pixels}}{\text{Pixels-per-Millimeter Ratio}}$$

2. **Tier 2: Barcode Dimension Scaling (Automated Catalog Mode):**
   Standard retail EAN-13 barcodes have standardized physical dimensions (nominal width of $37.29\text{ mm}$ and height of $25.91\text{ mm}$). When a barcode is present in the frame, the system uses the barcode's pixel dimensions as an automatic reference scale without requiring any coin.

3. **Tier 3: Relative Proportionality Analysis (Default Heuristic Mode):**
   If no reference object is present, the engine evaluates relative prominence. Under the rules, mandatory declarations (like Net Quantity) must appear in fonts at least as prominent as surrounding promotional marketing text. If the ratio of Net Quantity font size to promotional font size falls below statutory guidelines, a warning flag is raised for manual measurement.

---

## Database Architecture (PostgreSQL Schema)

The database structure is organized into **six relational tables** managed inside Supabase:

1. **`profiles` (User & Inspector Registry):**
   Extends Supabase authentication records. Stores full name, mobile phone number, departmental designation, enforcement division, badge ID, and access role (`consumer`, `inspector`, `admin`, `super_admin`). Consumer accounts have minimal fields; inspector/admin accounts include badge ID, department, and designation.
2. **`products` (Standard Commodity Master Catalog):**
   Maintains a persistent record of all scanned products. Stores barcode (EAN/UPC), brand name, registered product name, generic commodity category, and cumulative inspection counts.
3. **`scans` (Inspection Audit Events):**
   Records every individual inspection transaction. Stores foreign keys to the inspector profile and product record, latitude and longitude coordinates, retail store name, overall compliance status (`COMPLIANT`, `NON_COMPLIANT`, `WARNING`), overall percentage score, offline sync flag, and inspector field remarks.
4. **`scan_images` (Photographic Evidence Vault):**
   Stores multiple image URLs for each inspection scan, tagging each photograph by its label side (`front`, `back`, `side`, `mrp_panel`, `reference`) and display order.
5. **`declarations` (Granular Statutory Audit Log):**
   Stores the detailed verification result for each mandatory declaration within an inspection: rule code (e.g., `RULE_6_1_E_MRP`), rule name, extracted text string, presence flag (boolean), compliance status (Pass/Fail/Warning), calculated font size in millimeters, algorithmic confidence score, statutory violation citation, and image source face.
6. **`reports` (Generated Legal Documents):**
   Stores generated PDF file URLs, **report type** (`certificate` for officials, `summary` for consumers), cryptographic SHA-256 hash for tamper verification, **distribution method** (`download`, `whatsapp`, `email`), and generation timestamps.

> **Note:** The `otps` table from the original design has been removed. Authentication now uses Email/Password + Google OAuth via Supabase Auth, eliminating the need for OTP storage.

---

## External Libraries Reference List

| Library / Package | Version | Purpose in MetroScan | Target Platform |
| :--- | :--- | :--- | :--- |
| `flutter_riverpod` | `^2.6.1` | Reactive, compile-safe state management across the entire application | Android & Web |
| `go_router` | `^14.0.0` | Declarative routing with deep linking and role-based redirects | Android & Web |
| `supabase_flutter` | `^2.8.0` | Official client SDK for Supabase authentication (Email/Password + Google OAuth), database, storage, and realtime | Android & Web |
| `google_mlkit_text_recognition` | `^0.14.0` | Standalone on-device OCR engine for offline English and Devanagari text recognition | Android only |
| `google_mlkit_barcode_scanning` | `^0.12.0` | On-device barcode detection (EAN-13/UPC) for product lookup and reference scaling | Android only |
| `google_generative_ai` | `^0.4.6` | Official Google Gemini Dart SDK for semantic entity classification and structured JSON extraction | Android & Web |
| `camera` | `^0.11.0` | Direct access to native camera hardware, real-time preview, and photo capture | Android only |
| `image_picker` | `^1.1.2` | Allows selecting pre-existing packaging photos from device gallery or web file picker | Android & Web |
| `image` | `^4.3.0` | Pure Dart computer vision library for image downsampling, contrast, and grayscale (runs in Isolate) | Android & Web |
| `pdf` | `^3.11.1` | Client-side creation of official legal inspection certificates and consumer scan summaries | Android & Web |
| `printing` | `^5.13.3` | Native print preview and document rendering engine | Android & Web |
| `share_plus` | `^10.1.1` | Native OS share sheet for all three distribution channels: Download PDF, WhatsApp, and Email | Android & Web |
| `path_provider` | `^2.1.4` | Access to device Downloads directory for saving PDF reports locally | Android & Web |
| `url_launcher` | `^6.3.1` | Launches external regulatory links and web URLs | Android & Web |
| `fl_chart` | `^0.69.2` | High-performance interactive charts (bar charts, line graphs, pie breakdowns) for web analytics | Android & Web |
| `flutter_map` | `^7.0.2` | Fast, free OpenStreetMap mapping engine for plotting geo-tagged inspection pins | Android & Web |
| `latlong2` | `^0.9.1` | Geographic latitude and longitude coordinates utility library | Android & Web |
| `geolocator` | `^13.0.1` | Captures precise GPS coordinates during field inspections for legal evidence | Android only |
| `permission_handler` | `^11.3.1` | Manages runtime permissions for camera, storage, and location services | Android only |
| `hive_flutter` | `^1.1.0` | Lightweight, high-speed local key-value database for offline caching and buffering | Android & Web |
| `connectivity_plus` | `^6.1.0` | Real-time network monitoring to trigger background sync when internet returns | Android & Web |
| `shimmer` | `^3.0.0` | Smooth loading skeleton animations adhering to modern UI standards | Android & Web |
| `intl` | `^0.19.0` | Date and number formatting for compliance reports and timestamps | Android & Web |
| `uuid` | `^4.0.0` | Generate unique report IDs for inspection certificates | Android & Web |
| `crypto` | `^3.0.3` | SHA-256 hashing for certificate tamper-proofing and verification | Android & Web |

---

## 5-Minute SIH Winning Presentation & Live Demo Script

| Timing | Presentation Stage | Script & Spoken Narrative | Visual Action on Stage |
| :--- | :--- | :--- | :--- |
| **0:00 — 0:45** | **The Hook & Problem** | *"Respected judges, across India, over 100,000 packaged commodities are sold every second. Yet, Legal Metrology inspectors are forced to audit products manually using rulers and magnifying glasses—checking barely 20 items a day. Non-compliant font sizes, manipulated MRPs, and missing consumer grievance contacts are rampant. Today, we present **MetroScan**."* | Present a compelling slide showing the massive disparity between market scale and manual enforcement capacity. |
| **0:45 — 2:15** | **The Live Unrehearsed Demo** | *"Let's test MetroScan live right now on physical products we purchased from a local market this morning."* | **Physical Action:** Open the Flutter app on an Android phone projected onto the auditorium screen: <br>1. Tap 'Start Inspection'. Point camera at a real biscuit wrapper.<br>2. Snap front and back panels.<br>3. **Within 2 seconds**, the screen displays the complete Legal Metrology Scorecard.<br>4. Point out the live finding: *"Notice, judges: MetroScan instantly flagged that the Net Quantity is missing standard SI units, and the MRP lacks the mandatory 'inclusive of all taxes' clause."* |
| **2:15 — 3:15** | **Triple Report Distribution** | *"With one tap, the inspector generates an official, tamper-evident legal inspection certificate complete with timestamp, GPS coordinates, and embedded evidence photos. And they can distribute it three ways..."* | Tap '📥 Download' — show PDF saved. Tap '📱 WhatsApp' — send the PDF directly to a judge's phone on the spot. Tap '📧 Email' — show email client opens with PDF attached. The judge opens the PDF on their own phone. |
| **3:15 — 4:00** | **The Web Command Portal** | *"Simultaneously, look at our laptop screen. The inspection we just performed on mobile has already updated our centralized Web Management Portal in real time."* | Show the Web Dashboard: The new inspection pin appears on the India map; violation statistics increment automatically. |
| **4:00 — 4:30** | **Technical Superiority & USPs** | *"Unlike standard OCR prototypes, MetroScan operates 100% offline in rural mandis, calculates physical font sizes in millimeters, and distributes reports via Download, WhatsApp, or Email — all at zero API cost."* | Display the system architecture diagram highlighting the on-device ML Kit, Gemini AI, and Supabase integration. |
| **4:30 — 5:00** | **Impact & Conclusion** | *"MetroScan scales enforcement capacity from 20 products a day to over 200 per inspector—protecting consumer rights and ensuring fair trade across India at the speed of AI. Thank you!"* | Display team credits, GitHub repository link, and live deployment URL. |

---

## Deployment, Packaging & QA Strategy

### Building for Demo Day
1. **Android Physical Device Deployment:**
   - Compile a release APK using Flutter build tools.
   - Install the APK directly onto at least two physical demo smartphones to guarantee hardware independence from emulator glitches.
2. **Web Hosting Deployment:**
   - Compile the Flutter web bundle.
   - Deploy the static build to a zero-configuration global hosting provider (such as Firebase Hosting, Vercel, or Cloudflare Pages) connected to your custom domain.
3. **Prepared Inspection Prop Kit:**
   - Prepare a physical demonstration kit containing 4 real commercial packages:
     - **Item A (Fully Compliant):** A standard certified FMCG product (e.g., Parle-G or Amul Milk).
     - **Item B (Violating MRP):** A product with MRP missing "inclusive of all taxes" or overwritten with a price sticker.
     - **Item C (Missing Consumer Care):** A local spice or pulse packet lacking mandatory customer grievance contact details.
     - **Item D (Microscopic Font):** A cosmetic or electronic package where net contents are printed in sub-1mm unreadable text.
4. **Offline Resilience Proof:**
   - During the live demo, switch the phone to Airplane Mode, capture an item, show that the on-device OCR and compliance scorecard work instantly, and then toggle Airplane Mode off to show real-time synchronization with the web dashboard. This single demonstration element consistently secures top marks from technical hackathon judges.

---
*Document compiled and verified for the Smart India Hackathon (SIH) Legal Metrology Compliance Challenge.*
