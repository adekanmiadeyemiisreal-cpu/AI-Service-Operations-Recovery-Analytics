-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Analysis 01: Incident Lifecycle Reconstruction
-- ============================================================

DROP VIEW IF EXISTS incident_lifecycle;

CREATE VIEW incident_lifecycle AS

WITH ordered_events AS (

    SELECT
        e.incident_id,
        e.event_sequence,
        e.incident_state,
        e.active,
        e.made_sla,
        e.sys_updated_at,

        FIRST_VALUE(e.incident_state)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
            ) AS first_state,

        LAST_VALUE(e.incident_state)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND UNBOUNDED FOLLOWING
            ) AS final_state,

        FIRST_VALUE(e.made_sla)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
            ) AS initial_sla_status,

        LAST_VALUE(e.made_sla)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND UNBOUNDED FOLLOWING
            ) AS final_sla_status,

        FIRST_VALUE(e.sys_updated_at)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
            ) AS first_event_at,

        LAST_VALUE(e.sys_updated_at)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
                ROWS BETWEEN UNBOUNDED PRECEDING
                AND UNBOUNDED FOLLOWING
            ) AS last_event_at,

        COUNT(*) OVER (
            PARTITION BY e.incident_id
        ) AS event_count,

        LAG(e.incident_state)
            OVER (
                PARTITION BY e.incident_id
                ORDER BY e.event_sequence
            ) AS previous_state

    FROM incident_events e
),

lifecycle_summary AS (

    SELECT
        incident_id,

        MIN(first_state) AS first_state,
        MIN(final_state) AS final_state,

        BOOL_OR(initial_sla_status) AS initial_sla_status,
        BOOL_OR(final_sla_status) AS final_sla_status,

        MIN(first_event_at) AS first_event_at,
        MIN(last_event_at) AS last_event_at,

        MAX(event_count) AS event_count,

        COUNT(*) FILTER (
            WHERE previous_state IS NOT NULL
              AND previous_state <> incident_state
        ) AS state_transition_count

    FROM ordered_events

    GROUP BY incident_id
)

SELECT
    incident_id,
    first_state,
    final_state,
    initial_sla_status,
    final_sla_status,
    first_event_at,
    last_event_at,
    event_count,
    state_transition_count,

    EXTRACT(
        EPOCH FROM (
            last_event_at - first_event_at
        )
    ) / 3600.0 AS lifecycle_hours

FROM lifecycle_summary;
