-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 10: Incident Symptom Risk Features
-- ============================================================

DROP VIEW IF EXISTS incident_symptom_features;

CREATE VIEW incident_symptom_features AS

SELECT
    i.incident_id,
    i.u_symptom,

    COALESCE(s.incident_count, 0) AS symptom_incident_count,

    COALESCE(s.prolonged_incidents, 0) AS symptom_prolonged_incidents,

    COALESCE(s.prolonged_rate_pct, 0) AS symptom_prolonged_rate_pct,

    COALESCE(
        s.smoothed_prolonged_rate_pct,
        9.48
    ) AS symptom_smoothed_risk_pct,

    COALESCE(
        s.risk_lift_pct_points,
        0
    ) AS symptom_risk_lift_pct_points

FROM incidents i

LEFT JOIN symptom_risk_score s
    ON i.u_symptom = s.u_symptom;