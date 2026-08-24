-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 03: Incident Operational Complexity
-- ============================================================

DROP VIEW IF EXISTS incident_complexity;

CREATE VIEW incident_complexity AS

WITH transition_counts AS (

    SELECT
        incident_id,
        COUNT(*) AS transition_count

    FROM (

        SELECT
            incident_id,
            event_sequence,
            incident_state,

            LAG(incident_state) OVER (
                PARTITION BY incident_id
                ORDER BY event_sequence
            ) AS previous_state

        FROM incident_events

    ) state_history

    WHERE previous_state IS NOT NULL
      AND previous_state <> incident_state

    GROUP BY incident_id
),

base AS (

    SELECT
        i.incident_id,

        COALESCE(t.transition_count, 0) AS transition_count,

        COALESCE(i.reassignment_count, 0) AS reassignment_count,

        COALESCE(i.reopen_count, 0) AS reopen_count,

        COALESCE(i.modification_count, 0) AS modification_count,

        i.resolution_hours,

        i.closure_hours,

        i.resolution_to_closure_hours,

        i.priority,

        i.impact,

        i.urgency,

        i.made_sla,

        i.incident_state

    FROM incidents i

    LEFT JOIN transition_counts t
        ON i.incident_id = t.incident_id
)

SELECT
    *,

    (
        transition_count
        + reassignment_count
        + (reopen_count * 2)
        + modification_count
    ) AS operational_complexity_score,

    CASE

        WHEN (
            transition_count
            + reassignment_count
            + (reopen_count * 2)
            + modification_count
        ) >= 50
            THEN 'High'

        WHEN (
            transition_count
            + reassignment_count
            + (reopen_count * 2)
            + modification_count
        ) >= 15
            THEN 'Medium'

        ELSE 'Low'

    END AS complexity_band

FROM base;