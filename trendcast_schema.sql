-- ============================================
-- TrendCast PostgreSQL Schema
-- Member 02: SQL & Financial Data
-- Managing Data · Spring 2026
-- ============================================

-- Table: companies
CREATE TABLE companies (
    company_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL,
    ticker_symbol   VARCHAR(10) UNIQUE NOT NULL,
    industry        VARCHAR(100),
    sector          VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: filings
CREATE TABLE filings (
    filing_id         SERIAL PRIMARY KEY,
    company_id        INT REFERENCES companies(company_id),
    filing_type       VARCHAR(10) NOT NULL,
    filing_date       DATE NOT NULL,
    period_of_report  DATE,
    accession_number  VARCHAR(25) UNIQUE
);

-- Table: financials
CREATE TABLE financials (
    financial_id   SERIAL PRIMARY KEY,
    filing_id      INT REFERENCES filings(filing_id),
    company_id     INT REFERENCES companies(company_id),
    revenue        NUMERIC(20, 2),
    net_income     NUMERIC(20, 2),
    eps            NUMERIC(10, 4),
    rd_spend       NUMERIC(20, 2),
    fiscal_year    INT NOT NULL,
    fiscal_quarter INT CHECK (fiscal_quarter BETWEEN 1 AND 4)
);

-- Table: trend_scores
CREATE TABLE trend_scores (
    score_id     SERIAL PRIMARY KEY,
    company_id   INT REFERENCES companies(company_id),
    score_date   DATE NOT NULL,
    trend_score  NUMERIC(5, 2),
    keyword      VARCHAR(100),
    source       VARCHAR(50)
);

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX idx_filings_company      ON filings(company_id);
CREATE INDEX idx_financials_company   ON financials(company_id);
CREATE INDEX idx_financials_year      ON financials(fiscal_year);
CREATE INDEX idx_trend_scores_date    ON trend_scores(score_date);
CREATE INDEX idx_trend_scores_keyword ON trend_scores(keyword);

-- ============================================
-- Pre-loaded Companies
-- ============================================
INSERT INTO companies (company_name, ticker_symbol, industry, sector) VALUES
    ('Apple Inc.',        'AAPL', 'Consumer Electronics', 'Technology'),
    ('Sony Group',        'SONY', 'Consumer Electronics', 'Technology'),
    ('Dell Technologies', 'DELL', 'Computer Hardware',    'Technology'),
    ('HP Inc.',           'HPQ',  'Computer Hardware',    'Technology'),
    ('Garmin Ltd.',       'GRMN', 'Wearables & GPS',      'Technology'),
    ('NVIDIA Corp.',      'NVDA', 'Semiconductors',       'Technology');

-- ============================================
-- Dashboard View (for Member 05 Flask UI)
-- Single query, no joins needed in Flask
-- NULL placeholders for Member 04 PySpark output
-- ============================================
CREATE OR REPLACE VIEW dashboard_view AS
SELECT
    ts.keyword,
    CASE
        WHEN ts.keyword IN ('Apple', 'NVIDIA', 'Samsung', 'Logitech', 'Sony', 'Dell', 'HP', 'Garmin') THEN 'company'
        WHEN ts.keyword IN ('smartphone', 'laptop', 'smartwatch', 'tablet') THEN 'categorical'
        ELSE 'feature'
    END AS keyword_group,
    ts.trend_score,
    ts.score_date AS updated_at,
    ts.source,

    -- Financial fields (populated for company keywords only)
    f.revenue,
    f.eps,
    f.net_income,

    -- Placeholders for Member 04 PySpark output
    NULL::NUMERIC AS sentiment_score,
    NULL::INT     AS news_count,
    NULL::NUMERIC AS google_trends_score

FROM trend_scores ts
LEFT JOIN companies c
    ON LOWER(ts.keyword) = LOWER(c.ticker_symbol)
    OR LOWER(ts.keyword) = LOWER(c.company_name)
LEFT JOIN financials f
    ON f.company_id = c.company_id
LEFT JOIN filings fi
    ON fi.filing_id = f.filing_id
    AND fi.filing_type = '10-K'
ORDER BY ts.score_date DESC;
