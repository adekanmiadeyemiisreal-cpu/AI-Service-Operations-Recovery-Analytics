-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 06: Incident Risk Features
-- ============================================================

DROP VIEW IF EXISTS incident_risk_features;

CREATE VIEW incident_risk_features AS

SELECT
    c.incident_id,

    -- Operational complexity
    c.operational_complexity_score,
    c.complexity_band,
    c.transition_count,
    c.reassignment_count,
    c.reopen_count,
    c.modification_count,

    -- Incident severity/context
    c.priority,
    c.impact,
    c.urgency,
    c.made_sla,

    -- Outcome label
    r.prolonged_resolution,
    r.resolution_group,

    -- Explainable risk signal
    CASE
        WHEN c.operational_complexity_score >= 20
            THEN TRUE
        ELSE FALSE
    END AS complexity_risk_flag,

    CASE
        WHEN c.operational_complexity_score >= 20
            THEN 'Elevated'
        ELSE 'Standard'
    END AS initial_risk_band

FROM incident_complexity c

INNER JOIN resolution_outcome r
    ON c.incident_id = r.incident_id;