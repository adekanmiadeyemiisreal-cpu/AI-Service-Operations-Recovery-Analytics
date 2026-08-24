-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 04: Complexity Summary
-- ============================================================

DROP VIEW IF EXISTS complexity_summary;

CREATE VIEW complexity_summary AS

SELECT
    complexity_band,

    COUNT(*) AS incident_count,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS pct_of_incidents,

    ROUND(
        AVG(operational_complexity_score),
        2
    ) AS avg_complexity_score,

    ROUND(
        AVG(transition_count),
        2
    ) AS avg_transitions,

    ROUND(
        AVG(reassignment_count),
        2
    ) AS avg_reassignments,

    ROUND(
        AVG(reopen_count),
        2
    ) AS avg_reopens,

    ROUND(
        AVG(modification_count),
        2
    ) AS avg_modifications,

    ROUND(
        AVG(resolution_hours),
        2
    ) AS avg_resolution_hours,

    ROUND(
        AVG(closure_hours),
        2
    ) AS avg_closure_hours,

    ROUND(
        AVG(resolution_to_closure_hours),
        2
    ) AS avg_resolution_to_closure_hours,

    ROUND(
        100.0 * AVG(
            CASE
                WHEN made_sla THEN 1.0
                ELSE 0.0
            END
        ),
        2
    ) AS sla_rate_pct

FROM incident_complexity

GROUP BY complexity_band

ORDER BY
    CASE complexity_band
        WHEN 'Low' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'High' THEN 3
    END;