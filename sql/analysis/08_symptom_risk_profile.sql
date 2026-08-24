-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 08: Symptom Risk Profile
-- ============================================================

DROP VIEW IF EXISTS symptom_risk_profile;

CREATE VIEW symptom_risk_profile AS

SELECT
    i.u_symptom,

    COUNT(*) AS incident_count,

    COUNT(*) FILTER (
        WHERE r.prolonged_resolution
    ) AS prolonged_incidents,

    ROUND(
        100.0
        * COUNT(*) FILTER (WHERE r.prolonged_resolution)
        / NULLIF(COUNT(*), 0),
        2
    ) AS prolonged_rate_pct,

    ROUND(
        AVG(c.operational_complexity_score)::numeric,
        2
    ) AS avg_complexity_score,

    ROUND(
        AVG(c.reassignment_count)::numeric,
        2
    ) AS avg_reassignments,

    ROUND(
        AVG(c.reopen_count)::numeric,
        2
    ) AS avg_reopens

FROM incidents i

INNER JOIN resolution_outcome r
    ON i.incident_id = r.incident_id

INNER JOIN incident_complexity c
    ON i.incident_id = c.incident_id

WHERE i.u_symptom IS NOT NULL
  AND TRIM(i.u_symptom) <> ''

GROUP BY i.u_symptom;