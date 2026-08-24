-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 02: State Transition Analysis
-- ============================================================

DROP VIEW IF EXISTS incident_state_transitions;

CREATE VIEW incident_state_transitions AS

WITH state_history AS (

    SELECT
        incident_id,
        event_sequence,
        incident_state,
        sys_updated_at,

        LAG(incident_state) OVER (
            PARTITION BY incident_id
            ORDER BY event_sequence
        ) AS previous_state

    FROM incident_events
),

transitions AS (

    SELECT
        incident_id,
        event_sequence,
        previous_state,
        incident_state AS current_state,
        sys_updated_at

    FROM state_history

    WHERE previous_state IS NOT NULL
      AND previous_state <> incident_state
)

SELECT
    previous_state,
    current_state,
    COUNT(*) AS transition_count,
    COUNT(DISTINCT incident_id) AS affected_incidents

FROM transitions

GROUP BY
    previous_state,
    current_state

ORDER BY
    transition_count DESC;