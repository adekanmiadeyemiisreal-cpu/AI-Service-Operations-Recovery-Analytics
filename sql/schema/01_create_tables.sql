-- ============================================================
-- PROJECT 3: AI SERVICE OPERATIONS & RECOVERY ANALYTICS
-- PostgreSQL Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. INCIDENT STATES
-- Controlled vocabulary for lifecycle states.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incident_states (
    state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO incident_states (state_name)
VALUES
    ('New'),
    ('Active'),
    ('Awaiting User Info'),
    ('Awaiting Vendor'),
    ('Awaiting Problem'),
    ('Awaiting Evidence'),
    ('Resolved'),
    ('Closed'),
    ('Unknown')
ON CONFLICT (state_name) DO NOTHING;


-- ------------------------------------------------------------
-- 2. INCIDENTS
-- One row per unique incident.
-- Grain: 1 row = 1 incident.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incidents (
    incident_id VARCHAR(20) PRIMARY KEY,

    caller_id VARCHAR(100),
    opened_by VARCHAR(100),

    opened_at TIMESTAMP,
    sys_created_at TIMESTAMP,

    last_updated_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,

    resolution_timestamp_source VARCHAR(50),

    incident_state VARCHAR(50),
    active BOOLEAN,

    contact_type VARCHAR(100),
    location VARCHAR(100),

    category VARCHAR(100),
    subcategory VARCHAR(100),
    u_symptom VARCHAR(100),
    cmdb_ci VARCHAR(100),

    impact VARCHAR(50),
    urgency VARCHAR(50),
    priority VARCHAR(50),

    assignment_group VARCHAR(100),
    assigned_to VARCHAR(100),

    knowledge BOOLEAN,
    u_priority_confirmation BOOLEAN,
    notify VARCHAR(100),

    problem_id VARCHAR(100),
    rfc VARCHAR(100),
    vendor VARCHAR(100),
    caused_by VARCHAR(100),

    closed_code VARCHAR(100),
    resolved_by VARCHAR(100),

    reassignment_count INTEGER,
    reopen_count INTEGER,
    sys_mod_count INTEGER,

    made_sla BOOLEAN,

    resolution_hours NUMERIC(12,2),
    closure_hours NUMERIC(12,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 3. INCIDENT EVENTS
-- One row per lifecycle event.
-- Grain: 1 row = 1 recorded incident event.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS incident_events (
    event_id BIGSERIAL PRIMARY KEY,

    incident_id VARCHAR(20) NOT NULL,

    event_sequence INTEGER NOT NULL,

    incident_state VARCHAR(50),

    active BOOLEAN,
    made_sla BOOLEAN,

    reassignment_count INTEGER,
    reopen_count INTEGER,
    sys_mod_count INTEGER,

    caller_id VARCHAR(100),
    opened_by VARCHAR(100),

    opened_at TIMESTAMP,

    sys_created_by VARCHAR(100),
    sys_created_at TIMESTAMP,

    sys_updated_by VARCHAR(100),
    sys_updated_at TIMESTAMP,

    contact_type VARCHAR(100),
    location VARCHAR(100),

    category VARCHAR(100),
    subcategory VARCHAR(100),
    u_symptom VARCHAR(100),
    cmdb_ci VARCHAR(100),

    impact VARCHAR(50),
    urgency VARCHAR(50),
    priority VARCHAR(50),

    assignment_group VARCHAR(100),
    assigned_to VARCHAR(100),

    knowledge BOOLEAN,
    u_priority_confirmation BOOLEAN,
    notify VARCHAR(100),

    problem_id VARCHAR(100),
    rfc VARCHAR(100),
    vendor VARCHAR(100),
    caused_by VARCHAR(100),

    closed_code VARCHAR(100),
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,

    CONSTRAINT fk_incident_events_incident
        FOREIGN KEY (incident_id)
        REFERENCES incidents(incident_id)
);


-- ------------------------------------------------------------
-- INDEXES
-- Designed for lifecycle and operational analysis.
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_incident_events_incident_id
    ON incident_events(incident_id);

CREATE INDEX IF NOT EXISTS idx_incident_events_updated_at
    ON incident_events(sys_updated_at);

CREATE INDEX IF NOT EXISTS idx_incident_events_state
    ON incident_events(incident_state);

CREATE INDEX IF NOT EXISTS idx_incidents_category
    ON incidents(category);

CREATE INDEX IF NOT EXISTS idx_incidents_priority
    ON incidents(priority);

CREATE INDEX IF NOT EXISTS idx_incidents_assignment_group
    ON incidents(assignment_group);

CREATE INDEX IF NOT EXISTS idx_incidents_opened_at
    ON incidents(opened_at);


-- ------------------------------------------------------------
-- SCHEMA COMPLETE
-- ------------------------------------------------------------