
-- 1. Row counts for all core tables
SELECT 'fund_master' AS table_name, COUNT(*) AS row_count
FROM fund_master
UNION ALL
SELECT 'nav_history', COUNT(*) FROM nav_history
UNION ALL
SELECT 'aum_by_fund_house', COUNT(*) FROM aum_by_fund_house
UNION ALL
SELECT 'monthly_sip_inflows', COUNT(*) FROM monthly_sip_inflows
UNION ALL
SELECT 'category_inflows', COUNT(*) FROM category_inflows
UNION ALL
SELECT 'industry_folio_count', COUNT(*) FROM industry_folio_count
UNION ALL
SELECT 'scheme_performance', COUNT(*) FROM scheme_performance
UNION ALL
SELECT 'investor_transactions', COUNT(*) FROM investor_transactions
UNION ALL
SELECT 'portfolio_holdings', COUNT(*) FROM portfolio_holdings
UNION ALL
SELECT 'benchmark_indices', COUNT(*) FROM benchmark_indices;

-- 2. Schemes without NAV records
SELECT f.amfi_code, f.scheme_name
FROM fund_master f
LEFT JOIN nav_history n ON f.amfi_code = n.amfi_code
WHERE n.amfi_code IS NULL;

-- 3. Transaction totals by type
SELECT transaction_type,
       COUNT(*) AS transaction_count,
       ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM investor_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;

-- 4. Top 10 schemes by reported three-year return
SELECT scheme_name, category, return_3yr_pct, sharpe_ratio, risk_grade
FROM scheme_performance
WHERE return_3yr_pct IS NOT NULL
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- 5. Monthly SIP inflow trend
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM monthly_sip_inflows
ORDER BY month;
