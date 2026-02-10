-- ============================================================================
-- Create Missing Tables: alerts and incidents
-- Based on BTRC-FXBB-QOS-POC_Dev-Spec requirements
-- ============================================================================

-- ============================================================================
-- ALERTS TABLE (for R1.5: Real-Time Threshold Alerts)
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_uuid UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    isp_id INTEGER NOT NULL REFERENCES isps(id),
    pop_id INTEGER REFERENCES pops(id),
    sla_threshold_id INTEGER REFERENCES sla_thresholds(id),
    qos_parameter_id INTEGER REFERENCES qos_parameters(id),
    metric_type VARCHAR(50) NOT NULL,
    threshold_value DECIMAL(10,4) NOT NULL,
    actual_value DECIMAL(10,4) NOT NULL,
    deviation_pct DECIMAL(6,2),
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'OPEN',
    detection_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(100),
    duration_seconds INTEGER,
    alert_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Index for performance
CREATE INDEX idx_alerts_status_severity ON alerts(status, severity, detection_time DESC);
CREATE INDEX idx_alerts_isp ON alerts(isp_id, status);

-- ============================================================================
-- INCIDENTS TABLE (for R1.6: PoP-Level Incident Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(50) UNIQUE NOT NULL,
    isp_id INTEGER NOT NULL REFERENCES isps(id),
    pop_id INTEGER REFERENCES pops(id),
    qos_parameter_id INTEGER REFERENCES qos_parameters(id),
    metric_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'OPEN',
    description TEXT,
    impact_summary TEXT,
    expected_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    updated_at TIMESTAMPTZ
);

-- Index for performance
CREATE INDEX idx_incidents_status ON incidents(status, created_at DESC);
CREATE INDEX idx_incidents_pop ON incidents(pop_id, status);
CREATE INDEX idx_incidents_isp ON incidents(isp_id, status);

-- ============================================================================
-- Populate alerts from sla_violations (active violations become alerts)
-- ============================================================================
INSERT INTO alerts (
    isp_id,
    pop_id,
    sla_threshold_id,
    qos_parameter_id,
    metric_type,
    threshold_value,
    actual_value,
    deviation_pct,
    severity,
    status,
    detection_time,
    acknowledged_at,
    resolved_at,
    alert_message
)
SELECT
    v.isp_id,
    v.pop_id,
    v.sla_threshold_id,
    v.qos_parameter_id,
    v.violation_type as metric_type,
    v.expected_value as threshold_value,
    v.actual_value,
    v.deviation_pct,
    v.severity,
    CASE
        WHEN v.status = 'DETECTED' THEN 'OPEN'
        WHEN v.status = 'ACKNOWLEDGED' THEN 'ACKNOWLEDGED'
        WHEN v.status = 'RESOLVED' THEN 'CLOSED'
        ELSE 'OPEN'
    END as status,
    v.detection_time,
    v.isp_response_at as acknowledged_at,
    v.resolved_at,
    v.evidence_summary as alert_message
FROM sla_violations v
WHERE v.detection_time >= NOW() - INTERVAL '30 days'
ON CONFLICT (alert_uuid) DO NOTHING;

-- ============================================================================
-- Populate incidents from sla_violations (violations with pop_id become incidents)
-- ============================================================================
INSERT INTO incidents (
    incident_id,
    isp_id,
    pop_id,
    qos_parameter_id,
    metric_type,
    severity,
    status,
    description,
    expected_value,
    actual_value,
    created_at,
    acknowledged_at,
    acknowledged_by,
    resolved_at,
    resolved_by,
    resolution_notes
)
SELECT
    'INC-' || LPAD(v.id::TEXT, 6, '0') as incident_id,
    v.isp_id,
    v.pop_id,
    v.qos_parameter_id,
    v.violation_type as metric_type,
    v.severity,
    CASE
        WHEN v.status = 'DETECTED' THEN 'OPEN'
        WHEN v.status = 'ACKNOWLEDGED' THEN 'ACKNOWLEDGED'
        WHEN v.status = 'RESOLVED' THEN 'RESOLVED'
        ELSE v.status
    END as status,
    v.evidence_summary as description,
    v.expected_value,
    v.actual_value,
    v.detection_time as created_at,
    v.isp_response_at as acknowledged_at,
    v.resolved_by as acknowledged_by,
    v.resolved_at,
    v.resolved_by,
    v.resolution_notes
FROM sla_violations v
WHERE v.pop_id IS NOT NULL
    AND v.detection_time >= NOW() - INTERVAL '30 days'
ON CONFLICT (incident_id) DO NOTHING;

-- ============================================================================
-- Grant permissions
-- ============================================================================
GRANT SELECT ON alerts TO btrc_admin;
GRANT SELECT ON incidents TO btrc_admin;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check alerts table
SELECT 'Alerts created:' as message, COUNT(*) as count FROM alerts;

-- Check incidents table
SELECT 'Incidents created:' as message, COUNT(*) as count FROM incidents;

-- Sample alerts
SELECT * FROM alerts WHERE status = 'OPEN' LIMIT 5;

-- Sample incidents
SELECT * FROM incidents WHERE status = 'OPEN' LIMIT 5;
