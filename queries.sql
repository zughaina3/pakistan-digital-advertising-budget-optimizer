-- ==============================================================================
-- 🇵🇰 Pakistan Digital Advertising Budget Optimizer & Campaign Analytics
-- SQL Query Suite (ANSI SQL / BigQuery / Snowflake / PostgreSQL / SQLite)
-- ==============================================================================
-- Table Schema Assumption:
--   campaign_data (
--     date DATE / VARCHAR,
--     campaign VARCHAR,
--     platform VARCHAR,
--     impressions INTEGER,
--     clicks INTEGER,
--     spend NUMERIC,
--     conversions INTEGER,
--     revenue NUMERIC,
--     age VARCHAR,
--     gender VARCHAR,
--     city VARCHAR,
--     device VARCHAR
--   )
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Query 1: Platform-Level Acquisition Cost (CPA / CAC) and ROAS Performance
-- Purpose: Identify which advertising channels acquire customers most cost-effectively
-- ------------------------------------------------------------------------------
SELECT
    platform,
    ROUND(SUM(spend), 2) AS total_spend_rs,
    ROUND(SUM(revenue), 2) AS total_revenue_rs,
    SUM(conversions) AS total_conversions,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS avg_cpa_rs,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS avg_roas,
    ROUND(SUM(spend) / NULLIF(SUM(clicks), 0), 2) AS avg_cpc_rs
FROM campaign_data
GROUP BY platform
ORDER BY avg_cpa_rs ASC;


-- ------------------------------------------------------------------------------
-- Query 2: Monthly Blended Performance & Marketing Efficiency Trends
-- Purpose: Track blended ROAS, CPA, and revenue trajectory month over month
-- ------------------------------------------------------------------------------
SELECT
    SUBSTR(date, 1, 7) AS month,
    ROUND(SUM(spend), 2) AS total_spend_rs,
    ROUND(SUM(revenue), 2) AS total_revenue_rs,
    ROUND(SUM(revenue) - SUM(spend), 2) AS net_profit_rs,
    SUM(conversions) AS total_conversions,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS blended_roas,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS blended_cpa_rs
FROM campaign_data
GROUP BY SUBSTR(date, 1, 7)
ORDER BY month ASC;


-- ------------------------------------------------------------------------------
-- Query 3: Multi-Metric Channel Efficiency Dual-Ranking via Window Functions
-- Purpose: Rank advertising channels simultaneously by ROAS (profitability) and CPA (efficiency)
-- ------------------------------------------------------------------------------
SELECT
    platform,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS avg_roas,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS avg_cpa_rs,
    ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0), 2) AS avg_ctr_pct,
    ROUND(SUM(conversions) * 100.0 / NULLIF(SUM(clicks), 0), 2) AS avg_cvr_pct,
    DENSE_RANK() OVER (ORDER BY SUM(revenue) / NULLIF(SUM(spend), 0) DESC) AS roas_rank,
    DENSE_RANK() OVER (ORDER BY SUM(spend) / NULLIF(SUM(conversions), 0) ASC) AS cpa_efficiency_rank
FROM campaign_data
GROUP BY platform
ORDER BY avg_roas DESC;


-- ------------------------------------------------------------------------------
-- Query 4: Multi-Stage Conversion Funnel Efficiency by Platform
-- Purpose: Measure drop-off at every funnel stage (Impression -> Click -> Conversion)
-- ------------------------------------------------------------------------------
SELECT
    platform,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks,
    SUM(conversions) AS total_conversions,
    ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impressions), 0), 2) AS impression_to_click_pct,
    ROUND(SUM(conversions) * 100.0 / NULLIF(SUM(clicks), 0), 2) AS click_to_conversion_pct,
    ROUND(SUM(conversions) * 100.0 / NULLIF(SUM(impressions), 0), 3) AS overall_conversion_pct
FROM campaign_data
GROUP BY platform
ORDER BY overall_conversion_pct DESC;


-- ------------------------------------------------------------------------------
-- Query 5: Channel ROAS vs. Blended Benchmark Comparison with CTEs
-- Purpose: Compare individual platform performance against the blended portfolio average
-- ------------------------------------------------------------------------------
WITH channel_totals AS (
    SELECT
        platform,
        SUM(spend) AS platform_spend,
        SUM(revenue) AS platform_revenue,
        SUM(conversions) AS platform_conversions
    FROM campaign_data
    GROUP BY platform
),
portfolio_total AS (
    SELECT
        SUM(spend) AS grand_spend,
        SUM(revenue) AS grand_revenue
    FROM campaign_data
)
SELECT
    ct.platform,
    ROUND(ct.platform_revenue / NULLIF(ct.platform_spend, 0), 2) AS platform_roas,
    ROUND(ct.platform_spend / NULLIF(ct.platform_conversions, 0), 2) AS platform_cpa_rs,
    ROUND(ct.platform_spend * 100.0 / NULLIF(pt.grand_spend, 0), 1) AS spend_share_pct,
    ROUND(ct.platform_revenue * 100.0 / NULLIF(pt.grand_revenue, 0), 1) AS revenue_share_pct,
    ROUND(
        (ct.platform_revenue / NULLIF(ct.platform_spend, 0)) -
        (pt.grand_revenue / NULLIF(pt.grand_spend, 0)),
        2
    ) AS roas_vs_blended_benchmark
FROM channel_totals ct
CROSS JOIN portfolio_total pt
ORDER BY platform_roas DESC;


-- ------------------------------------------------------------------------------
-- Query 6: Month-over-Month (MoM) Growth Rates using Window LAG()
-- Purpose: Calculate month-over-month percentage growth in spend, revenue, and orders
-- ------------------------------------------------------------------------------
WITH monthly_data AS (
    SELECT
        SUBSTR(date, 1, 7) AS month,
        SUM(spend) AS total_spend,
        SUM(revenue) AS total_revenue,
        SUM(conversions) AS total_conversions
    FROM campaign_data
    GROUP BY SUBSTR(date, 1, 7)
)
SELECT
    month,
    ROUND(total_spend, 2) AS total_spend_rs,
    ROUND(total_revenue, 2) AS total_revenue_rs,
    total_conversions,
    ROUND(
        (total_spend - LAG(total_spend) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(total_spend) OVER (ORDER BY month), 0),
        1
    ) AS spend_mom_growth_pct,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(total_revenue) OVER (ORDER BY month), 0),
        1
    ) AS revenue_mom_growth_pct,
    ROUND(
        (total_conversions - LAG(total_conversions) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(total_conversions) OVER (ORDER BY month), 0),
        1
    ) AS conversions_mom_growth_pct
FROM monthly_data
ORDER BY month ASC;


-- ------------------------------------------------------------------------------
-- Query 7: Automated Pure-SQL Budget Reallocation Engine (Target: Rs. 1M Spend)
-- Purpose: Algorithmic decision logic allocating budget shifts based on ROAS & CPA
-- ------------------------------------------------------------------------------
WITH channel_perf AS (
    SELECT
        platform,
        SUM(spend) AS current_spend,
        SUM(revenue) AS current_revenue,
        ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS roas,
        ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS cpa
    FROM campaign_data
    GROUP BY platform
),
blended_bench AS (
    SELECT
        ROUND(SUM(current_revenue) / NULLIF(SUM(current_spend), 0), 2) AS blended_roas
    FROM channel_perf
)
SELECT
    cp.platform,
    ROUND(cp.current_spend, 2) AS historical_spend_rs,
    cp.roas AS historical_roas,
    cp.cpa AS historical_cpa_rs,
    b.blended_roas AS benchmark_roas,
    CASE
        WHEN cp.roas >= b.blended_roas * 1.15 THEN 'INCREASE BUDGET (+15% to +35%) - HIGH EFFICIENCY'
        WHEN cp.roas >= b.blended_roas THEN 'MAINTAIN / OPTIMIZE - MEETS BENCHMARK'
        WHEN cp.roas >= 2.50 THEN 'SOFT SCALE - TEST CREATIVE / NARROW TARGETING'
        ELSE 'REDUCE BUDGET (-30% to -50%) - UNDERPERFORMING'
    END AS budget_recommendation,
    CASE
        WHEN cp.platform = 'Google' THEN 'Allocate 35% of Rs. 1M (Rs. 350,000)'
        WHEN cp.platform = 'Instagram' THEN 'Allocate 30% of Rs. 1M (Rs. 300,000)'
        WHEN cp.platform = 'Facebook' THEN 'Allocate 20% of Rs. 1M (Rs. 200,000)'
        WHEN cp.platform = 'TikTok' THEN 'Allocate 10% of Rs. 1M (Rs. 100,000)'
        WHEN cp.platform = 'YouTube' THEN 'Allocate 5% of Rs. 1M (Rs. 50,000)'
        ELSE 'Review'
    END AS target_rs_1m_allocation
FROM channel_perf cp
CROSS JOIN blended_bench b
ORDER BY cp.roas DESC;


-- ------------------------------------------------------------------------------
-- Query 8: Regional Pakistan City & Demographic High-Yield Matrix
-- Purpose: Identify the most lucrative geographic and demographic segments in Pakistan
-- ------------------------------------------------------------------------------
SELECT
    city,
    age,
    gender,
    ROUND(SUM(revenue), 2) AS total_revenue_rs,
    SUM(conversions) AS total_conversions,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS segment_roas,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS segment_cpa_rs
FROM campaign_data
GROUP BY city, age, gender
HAVING SUM(conversions) >= 50
ORDER BY total_revenue_rs DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- Query 9: Campaign Creative & Promotional Theme Effectiveness
-- Purpose: Evaluate lawn pret, university tote bags, and clearance campaign returns
-- ------------------------------------------------------------------------------
SELECT
    campaign,
    ROUND(SUM(spend), 2) AS campaign_spend_rs,
    ROUND(SUM(revenue), 2) AS campaign_revenue_rs,
    ROUND(SUM(revenue) - SUM(spend), 2) AS net_profit_rs,
    SUM(conversions) AS orders_generated,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS campaign_roas,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS campaign_cpa_rs
FROM campaign_data
GROUP BY campaign
ORDER BY campaign_revenue_rs DESC;
