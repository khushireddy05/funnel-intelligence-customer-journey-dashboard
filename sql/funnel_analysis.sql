-- Example SQL for a database loaded with the processed CSV tables.
-- Overall stage counts and conversion from the preceding acquisition stage.
WITH stage_counts AS (
    SELECT stage, stage_order, COUNT(DISTINCT customer_id) AS customers
    FROM FactFunnelEvents
    WHERE stage <> 'Repeat Purchase'
    GROUP BY stage, stage_order
)
SELECT
    stage,
    customers,
    ROUND(100.0 * customers / LAG(customers) OVER (ORDER BY stage_order), 1) AS stage_conversion_pct,
    ROUND(100.0 * (1 - customers * 1.0 / LAG(customers) OVER (ORDER BY stage_order)), 1) AS drop_off_pct
FROM stage_counts
ORDER BY stage_order;

-- Marketing channel quality: initial customers, leads, and purchasers.
SELECT
    marketing_channel,
    COUNT(DISTINCT CASE WHEN stage = 'Initial Interaction' THEN customer_id END) AS prospects,
    COUNT(DISTINCT CASE WHEN stage = 'Lead' THEN customer_id END) AS leads,
    COUNT(DISTINCT CASE WHEN stage = 'Purchase' THEN customer_id END) AS purchasers
FROM FactFunnelEvents
GROUP BY marketing_channel
ORDER BY purchasers DESC;
