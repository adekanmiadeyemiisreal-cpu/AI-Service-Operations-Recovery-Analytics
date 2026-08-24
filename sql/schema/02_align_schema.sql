-- ============================================================
-- PROJECT 3: SCHEMA ALIGNMENT MIGRATION
-- Align PostgreSQL with validated ETL outputs
-- ============================================================

-- ------------------------------------------------------------
-- INCIDENTS
-- Add analytical fields produced by the ETL pipeline.
-- ------------------------------------------------------------

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS resolution_timestamp TIMESTAMP;

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS resolution_timestamp_source VARCHAR(50);

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS resolution_to_closure_hours NUMERIC(12,2);

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS reopen_flag BOOLEAN;

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS reassignment_intensity NUMERIC(12,4);

ALTER TABLE incidents
ADD COLUMN IF NOT EXISTS modification_count INTEGER;


-- ------------------------------------------------------------
-- INCIDENT EVENTS
-- Add event-level analytical fields produced by ETL.
-- ------------------------------------------------------------

ALTER TABLE incident_events
ADD COLUMN IF NOT EXISTS reopen_flag BOOLEAN;

ALTER TABLE incident_events
ADD COLUMN IF NOT EXISTS reassignment_intensity NUMERIC(12,4);

ALTER TABLE incident_events
ADD COLUMN IF NOT EXISTS modification_count INTEGER;


-- ------------------------------------------------------------
-- INDEXES FOR ANALYTICAL WORK
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_incidents_resolution_hours
    ON incidents(resolution_hours);

CREATE INDEX IF NOT EXISTS idx_incidents_reopen_flag
    ON incidents(reopen_flag);

CREATE INDEX IF NOT EXISTS idx_incidents_resolution_source
    ON incidents(resolution_timestamp_source);

CREATE INDEX IF NOT EXISTS idx_incident_events_reopen_flag
    ON incident_events(reopen_flag);

-- ------------------------------------------------------------
-- MIGRATION COMPLETE
-- ------------------------------------------------------------