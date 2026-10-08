-- ============================================================
-- MetroScan Database Schema for Supabase PostgreSQL
-- Run this ENTIRE script in Supabase SQL Editor (one shot)
-- ============================================================

-- 1. User Profiles (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK (role IN ('consumer', 'inspector', 'admin', 'super_admin')) DEFAULT 'consumer',
    badge_id TEXT,
    department TEXT,
    designation TEXT,
    phone TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Product Catalog
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode TEXT UNIQUE,
    brand_name TEXT,
    product_name TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    total_scans INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Inspection Scans
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id),
    product_id UUID REFERENCES products(id),
    store_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    overall_status TEXT CHECK (overall_status IN ('COMPLIANT', 'NON_COMPLIANT', 'WARNING')),
    compliance_score NUMERIC(5, 2),
    raw_text TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Scan Images (Cloudinary URLs)
CREATE TABLE IF NOT EXISTS scan_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    annotated_url TEXT,
    panel_type TEXT CHECK (panel_type IN ('front', 'back', 'mrp_panel', 'side', 'other')),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Statutory Declaration Results
CREATE TABLE IF NOT EXISTS declarations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    rule_code TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    extracted_value TEXT,
    is_present BOOLEAN DEFAULT FALSE,
    status TEXT CHECK (status IN ('PASS', 'FAIL', 'WARNING')),
    measured_font_height_mm NUMERIC(4, 2),
    confidence_score NUMERIC(4, 2),
    violation_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Generated Reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    report_type TEXT CHECK (report_type IN ('certificate', 'summary')),
    pdf_url TEXT NOT NULL,
    distribution_method TEXT,
    sha256_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(overall_status);
CREATE INDEX IF NOT EXISTS idx_declarations_scan_id ON declarations(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_images_scan_id ON scan_images(scan_id);
CREATE INDEX IF NOT EXISTS idx_reports_scan_id ON reports(scan_id);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);

-- ============================================================
-- Row Level Security (RLS) — Enable on all tables
-- ============================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE declarations ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Allow service role (backend) full access to all tables
CREATE POLICY "Service role full access" ON profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON products FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON scans FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON scan_images FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON declarations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON reports FOR ALL USING (true) WITH CHECK (true);

-- Users can read their own profile
CREATE POLICY "Users read own profile" ON profiles FOR SELECT USING (auth.uid() = id);

-- Users can read all products (public catalog)
CREATE POLICY "Public product read" ON products FOR SELECT USING (true);

-- Consumers can only see their own scans; inspectors/admins see all
CREATE POLICY "Users read own scans" ON scans FOR SELECT
    USING (
        user_id = auth.uid()
        OR EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('inspector', 'admin', 'super_admin'))
    );
