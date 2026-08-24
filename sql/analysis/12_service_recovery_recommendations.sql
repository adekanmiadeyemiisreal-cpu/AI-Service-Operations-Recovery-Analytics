-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Step 84 - Service Recovery Recommendation Layer
-- ============================================================

DROP VIEW IF EXISTS service_recovery_recommendations;

CREATE VIEW service_recovery_recommendations AS

SELECT
    incident_id,
    u_symptom,
    combined_risk_band,
    prolonged_resolution,

    symptom_incident_count,
    symptom_prolonged_incidents,
    symptom_prolonged_rate_pct,
    symptom_smoothed_risk_pct,
    symptom_risk_lift_pct_points,
    complexity_risk_flag,

    CASE
        WHEN combined_risk_band = 'High: Complexity + Symptom'
            THEN 'Immediate escalation and senior ownership review'

        WHEN combined_risk_band = 'Elevated: Complexity only'
            THEN 'Review operational complexity and assignment ownership'

        WHEN combined_risk_band = 'Elevated: Symptom only'
            THEN 'Apply symptom-specific troubleshooting and knowledge guidance'

        ELSE
            'Continue standard workflow with routine monitoring'
    END AS primary_recommendation,

    CASE
        WHEN combined_risk_band = 'High: Complexity + Symptom'
            THEN 'Both operational complexity and symptom risk are elevated'

        WHEN combined_risk_band = 'Elevated: Complexity only'
            THEN 'Operational complexity is the dominant risk signal'

        WHEN combined_risk_band = 'Elevated: Symptom only'
            THEN 'The symptom pattern has elevated prolonged-resolution risk'

        ELSE
            'No elevated complexity or symptom risk signal detected'
    END AS recommendation_reason,

    CASE
        WHEN combined_risk_band = 'High: Complexity + Symptom'
            THEN 1

        WHEN combined_risk_band LIKE 'Elevated:%'
            THEN 2

        ELSE 3
    END AS recommended_priority

FROM combined_risk_intelligence;