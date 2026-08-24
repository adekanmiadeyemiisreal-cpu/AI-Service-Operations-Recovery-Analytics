-- ============================================================
-- PROJECT 3
-- AI SERVICE OPERATIONS & RECOVERY ANALYTICS
--
-- Step 86 - Power BI Export Layer
-- ============================================================

\copy (SELECT * FROM recovery_recommendation_summary ORDER BY recommended_priority) TO 'data/powerbi/recovery_recommendation_summary.csv' WITH (FORMAT CSV, HEADER TRUE);

\copy (SELECT * FROM service_recovery_recommendations) TO 'data/powerbi/service_recovery_recommendations.csv' WITH (FORMAT CSV, HEADER TRUE);

\copy (SELECT * FROM combined_risk_intelligence) TO 'data/powerbi/combined_risk_intelligence.csv' WITH (FORMAT CSV, HEADER TRUE);

\copy (SELECT * FROM symptom_risk_score) TO 'data/powerbi/symptom_risk_score.csv' WITH (FORMAT CSV, HEADER TRUE);