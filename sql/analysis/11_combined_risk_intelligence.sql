-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 11: Combined Risk Intelligence
-- ============================================================

DROP VIEW IF EXISTS combined_risk_intelligence;

CREATE VIEW combined_risk_intelligence AS

SELECT
    f.incident_id,

    f.complexity_risk_flag,

    f.prolonged_resolution,

    s.u_symptom,

    s.symptom_incident_count,

    s.symptom_prolonged_incidents,

    s.symptom_prolonged_rate_pct,

    s.symptom_smoothed_risk_pct,

    s.symptom_risk_lift_pct_points,

    CASE

        WHEN f.complexity_risk_flag
             AND s.symptom_smoothed_risk_pct > 9.48
            THEN 'High: Complexity + Symptom'

        WHEN f.complexity_risk_flag
            THEN 'Elevated: Complexity only'

        WHEN s.symptom_smoothed_risk_pct > 9.48
            THEN 'Elevated: Symptom only'

        ELSE 'Standard: Neither'

    END AS combined_risk_band

FROM incident_risk_features f

INNER JOIN incident_symptom_features s
    ON f.incident_id = s.incident_id;