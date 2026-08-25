CREATE TABLE IF NOT EXISTS operator_actions (
    action_id BIGSERIAL PRIMARY KEY,

    incident_id VARCHAR(50) NOT NULL,

    action_type VARCHAR(50) NOT NULL,

    operator_note TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_operator_action_incident
        FOREIGN KEY (incident_id)
        REFERENCES incidents(incident_id),

    CONSTRAINT chk_operator_action_type
        CHECK (
            action_type IN (
                'Escalate',
                'Assign for Review',
                'Continue Monitoring'
            )
        )
);
