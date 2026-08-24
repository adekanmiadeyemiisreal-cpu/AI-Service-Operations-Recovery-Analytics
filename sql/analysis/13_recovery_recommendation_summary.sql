-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Step 85 - Recovery Recommendation Summary
-- ============================================================

DROP VIEW IF EXISTS recovery_recommendation_summary;

CREATE VIEW recovery_recommendation_summary AS

SELECT
    combined_risk_band,
    recommended_priority,

    COUNT(*) AS incident_count,

    COUNT(*) FILTER (
        WHERE prolonged_resolution
    ) AS prolonged_incidents,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE prolonged_resolution
        ) / COUNT(*),
        2
    ) AS prolonged_rate_pct,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_all_incidents,

    MAX(primary_recommendation) AS primary_recommendation,

    MAX(recommendation_reason) AS recommendation_reason

FROM service_recovery_recommendations

GROUP BY
    combined_risk_band,
    recommended_priority;