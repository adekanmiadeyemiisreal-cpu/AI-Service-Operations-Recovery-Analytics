-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 09: Smoothed Symptom Risk Score
-- ============================================================

DROP VIEW IF EXISTS symptom_risk_score;

CREATE VIEW symptom_risk_score AS

WITH overall AS (

    SELECT
        SUM(incident_count)::numeric AS total_incidents,
        SUM(prolonged_incidents)::numeric AS total_prolonged,

        SUM(prolonged_incidents)::numeric
        / NULLIF(SUM(incident_count), 0) AS overall_rate

    FROM symptom_risk_profile
),

scored AS (

    SELECT
        s.u_symptom,
        s.incident_count,
        s.prolonged_incidents,
        s.prolonged_rate_pct,
        s.avg_complexity_score,
        s.avg_reassignments,
        s.avg_reopens,

        o.overall_rate,

        50.0 AS prior_strength,

        (
            s.prolonged_incidents
            + (50.0 * o.overall_rate)
        )
        /
        (
            s.incident_count
            + 50.0
        ) AS smoothed_rate

    FROM symptom_risk_profile s
    CROSS JOIN overall o
)

SELECT
    u_symptom,
    incident_count,
    prolonged_incidents,
    prolonged_rate_pct,

    ROUND(
        100.0 * smoothed_rate,
        2
    ) AS smoothed_prolonged_rate_pct,

    ROUND(
        100.0 * (smoothed_rate - overall_rate),
        2
    ) AS risk_lift_pct_points,

    ROUND(
        avg_complexity_score::numeric,
        2
    ) AS avg_complexity_score,

    ROUND(
        avg_reassignments::numeric,
        2
    ) AS avg_reassignments,

    ROUND(
        avg_reopens::numeric,
        2
    ) AS avg_reopens

FROM scored;