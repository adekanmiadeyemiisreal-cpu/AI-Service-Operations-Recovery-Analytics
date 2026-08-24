-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 07: Risk Baseline Evaluation
-- ============================================================

DROP VIEW IF EXISTS risk_baseline_evaluation;

CREATE VIEW risk_baseline_evaluation AS

WITH metrics AS (

    SELECT
        COUNT(*) FILTER (
            WHERE complexity_risk_flag
              AND prolonged_resolution
        ) AS true_positive,

        COUNT(*) FILTER (
            WHERE complexity_risk_flag
              AND NOT prolonged_resolution
        ) AS false_positive,

        COUNT(*) FILTER (
            WHERE NOT complexity_risk_flag
              AND prolonged_resolution
        ) AS false_negative,

        COUNT(*) FILTER (
            WHERE NOT complexity_risk_flag
              AND NOT prolonged_resolution
        ) AS true_negative

    FROM incident_risk_features
)

SELECT
    true_positive,
    false_positive,
    false_negative,
    true_negative,

    ROUND(
        100.0 * true_positive
        / NULLIF(true_positive + false_positive, 0),
        2
    ) AS precision_pct,

    ROUND(
        100.0 * true_positive
        / NULLIF(true_positive + false_negative, 0),
        2
    ) AS recall_pct,

    ROUND(
        100.0 * true_negative
        / NULLIF(true_negative + false_positive, 0),
        2
    ) AS specificity_pct

FROM metrics;