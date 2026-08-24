-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 05: Resolution Outcome
-- ============================================================

DROP VIEW IF EXISTS resolution_outcome;

CREATE VIEW resolution_outcome AS

SELECT
    i.*,

    CASE
        WHEN i.resolution_hours >= 366.66
            THEN TRUE
        ELSE FALSE
    END AS prolonged_resolution,

    CASE
        WHEN i.resolution_hours >= 366.66
            THEN 'Prolonged'
        ELSE 'Standard'
    END AS resolution_group

FROM incidents i

WHERE i.resolution_hours IS NOT NULL
  AND i.resolution_hours >= 0;