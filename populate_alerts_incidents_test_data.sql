-- ============================================================================
-- Populate Test Data for alerts and incidents Tables
-- Based on existing ISPs, PoPs, and QoS Parameters
-- ============================================================================

-- ============================================================================
-- PART 1: Populate ALERTS Table (50 test records)
-- ============================================================================

-- Clear existing alerts (optional)
-- TRUNCATE TABLE alerts RESTART IDENTITY CASCADE;

-- Insert test alerts with various statuses and severities
INSERT INTO alerts (
    isp_id, pop_id, qos_parameter_id, metric_type,
    threshold_value, actual_value, deviation_pct,
    severity, status, detection_time,
    acknowledged_at, acknowledged_by,
    resolved_at, resolved_by, alert_message
) VALUES
-- CRITICAL OPEN alerts (last 2 hours)
(1, 1, 1, 'DOWNLOAD_SPEED', 50.00, 28.50, -43.00, 'CRITICAL', 'OPEN', NOW() - INTERVAL '45 minutes', NULL, NULL, NULL, NULL, 'Download speed critically below threshold at Link3 Central DC'),
(2, 4, 5, 'AVAILABILITY', 99.00, 92.30, -6.77, 'CRITICAL', 'OPEN', NOW() - INTERVAL '1.5 hours', NULL, NULL, NULL, NULL, 'Service availability dropped below 95% at Amber IT Central DC'),
(4, 10, 3, 'LATENCY_DOMESTIC', 20.00, 45.80, 129.00, 'CRITICAL', 'OPEN', NOW() - INTERVAL '30 minutes', NULL, NULL, NULL, NULL, 'Domestic latency exceeds threshold at ICC Central DC'),
(6, NULL, 6, 'PACKET_LOSS', 1.00, 3.45, 245.00, 'CRITICAL', 'OPEN', NOW() - INTERVAL '15 minutes', NULL, NULL, NULL, NULL, 'High packet loss detected across Aamra Networks'),

-- HIGH OPEN alerts (last 6 hours)
(3, 7, 1, 'DOWNLOAD_SPEED', 75.00, 55.20, -26.40, 'HIGH', 'OPEN', NOW() - INTERVAL '3 hours', NULL, NULL, NULL, NULL, 'Download speed below target at Carnival Central DC'),
(5, 13, 2, 'UPLOAD_SPEED', 25.00, 18.70, -25.20, 'HIGH', 'OPEN', NOW() - INTERVAL '4 hours', NULL, NULL, NULL, NULL, 'Upload speed degradation at Dot Central DC'),
(7, NULL, 8, 'UTILIZATION', 85.00, 92.50, 8.82, 'HIGH', 'OPEN', NOW() - INTERVAL '2 hours', NULL, NULL, NULL, NULL, 'Link utilization exceeds 85% at BRACNet Limited'),
(8, NULL, 5, 'AVAILABILITY', 98.00, 96.80, -1.22, 'HIGH', 'OPEN', NOW() - INTERVAL '5 hours', NULL, NULL, NULL, NULL, 'Availability slightly below target at Triangle Services'),
(9, NULL, 1, 'DOWNLOAD_SPEED', 100.00, 82.30, -17.70, 'HIGH', 'OPEN', NOW() - INTERVAL '3.5 hours', NULL, NULL, NULL, NULL, 'Download speed inconsistency at Dhakacom Limited'),

-- MEDIUM OPEN alerts (last 12 hours)
(10, NULL, 7, 'JITTER', 10.00, 13.20, 32.00, 'MEDIUM', 'OPEN', NOW() - INTERVAL '8 hours', NULL, NULL, NULL, NULL, 'Jitter levels elevated at X-Net Limited'),
(1, 2, 1, 'DOWNLOAD_SPEED', 50.00, 42.50, -15.00, 'MEDIUM', 'OPEN', NOW() - INTERVAL '10 hours', NULL, NULL, NULL, NULL, 'Speed drop at Link3 Shariatpur Edge'),
(2, 5, 6, 'PACKET_LOSS', 1.00, 1.80, 80.00, 'MEDIUM', 'OPEN', NOW() - INTERVAL '7 hours', NULL, NULL, NULL, NULL, 'Packet loss at Amber IT Chandpur Edge'),
(3, 8, 3, 'LATENCY_DOMESTIC', 20.00, 26.30, 31.50, 'MEDIUM', 'OPEN', NOW() - INTERVAL '9 hours', NULL, NULL, NULL, NULL, 'Latency spike at Carnival Pirojpur Edge'),
(4, 11, 1, 'DOWNLOAD_SPEED', 50.00, 43.20, -13.60, 'MEDIUM', 'OPEN', NOW() - INTERVAL '11 hours', NULL, NULL, NULL, NULL, 'Bandwidth constraint at ICC Dinajpur Edge'),

-- ACKNOWLEDGED alerts (being worked on)
(5, 14, 5, 'AVAILABILITY', 99.00, 97.50, -1.52, 'HIGH', 'ACKNOWLEDGED', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '4 hours', 'ops_team_1', NULL, NULL, 'Investigating availability issue at Dot Bagerhat Edge'),
(6, NULL, 1, 'DOWNLOAD_SPEED', 100.00, 85.60, -14.40, 'MEDIUM', 'ACKNOWLEDGED', NOW() - INTERVAL '8 hours', NOW() - INTERVAL '6 hours', 'ops_team_2', NULL, NULL, 'Network team investigating speed at Aamra Networks'),
(7, NULL, 6, 'PACKET_LOSS', 1.00, 1.95, 95.00, 'HIGH', 'ACKNOWLEDGED', NOW() - INTERVAL '5 hours', NOW() - INTERVAL '3 hours', 'ops_team_1', NULL, NULL, 'Packet loss investigation ongoing at BRACNet'),
(8, NULL, 3, 'LATENCY_DOMESTIC', 20.00, 28.40, 42.00, 'MEDIUM', 'ACKNOWLEDGED', NOW() - INTERVAL '7 hours', NOW() - INTERVAL '5 hours', 'ops_team_3', NULL, NULL, 'Routing optimization in progress at Triangle Services'),

-- CLOSED alerts (recently resolved - last 24 hours)
(1, 3, 1, 'DOWNLOAD_SPEED', 50.00, 32.10, -35.80, 'CRITICAL', 'CLOSED', NOW() - INTERVAL '20 hours', NOW() - INTERVAL '18 hours', 'ops_team_1', NOW() - INTERVAL '15 hours', 'ops_team_1', 'Link upgrade completed at Link3 Coxsbazar Edge - speed restored'),
(2, 6, 5, 'AVAILABILITY', 99.00, 96.20, -2.83, 'HIGH', 'CLOSED', NOW() - INTERVAL '18 hours', NOW() - INTERVAL '16 hours', 'ops_team_2', NOW() - INTERVAL '14 hours', 'ops_team_2', 'Router reboot resolved availability at Amber IT Joypurhat Edge'),
(3, 9, 2, 'UPLOAD_SPEED', 25.00, 19.80, -20.80, 'MEDIUM', 'CLOSED', NOW() - INTERVAL '22 hours', NOW() - INTERVAL '20 hours', 'ops_team_1', NOW() - INTERVAL '19 hours', 'ops_team_1', 'QoS policy adjusted at Carnival Shariatpur Edge'),
(4, 12, 6, 'PACKET_LOSS', 1.00, 2.15, 115.00, 'HIGH', 'CLOSED', NOW() - INTERVAL '19 hours', NOW() - INTERVAL '17 hours', 'ops_team_3', NOW() - INTERVAL '16 hours', 'ops_team_3', 'Cable replacement fixed packet loss at ICC Barguna Edge'),
(5, 15, 3, 'LATENCY_DOMESTIC', 20.00, 31.20, 56.00, 'MEDIUM', 'CLOSED', NOW() - INTERVAL '21 hours', NOW() - INTERVAL '19 hours', 'ops_team_2', NOW() - INTERVAL '18 hours', 'ops_team_2', 'Routing table optimized at Dot Manikganj Edge'),

-- Additional OPEN alerts for variety (2-7 days old)
(1, NULL, 2, 'UPLOAD_SPEED', 50.00, 42.30, -15.40, 'MEDIUM', 'OPEN', NOW() - INTERVAL '2 days', NULL, NULL, NULL, NULL, 'Consistent upload speed degradation at Link3 Technologies'),
(2, NULL, 7, 'JITTER', 10.00, 14.80, 48.00, 'MEDIUM', 'OPEN', NOW() - INTERVAL '3 days', NULL, NULL, NULL, NULL, 'Jitter affecting VoIP quality at Amber IT Limited'),
(3, NULL, 8, 'UTILIZATION', 80.00, 88.30, 10.38, 'HIGH', 'OPEN', NOW() - INTERVAL '2.5 days', NULL, NULL, NULL, NULL, 'High utilization indicates capacity issue at Carnival Internet'),
(4, NULL, 5, 'AVAILABILITY', 99.50, 98.20, -1.31, 'MEDIUM', 'OPEN', NOW() - INTERVAL '4 days', NULL, NULL, NULL, NULL, 'Availability dips during peak hours at ICC Communication'),
(5, NULL, 1, 'DOWNLOAD_SPEED', 200.00, 165.40, -17.30, 'HIGH', 'OPEN', NOW() - INTERVAL '1.5 days', NULL, NULL, NULL, NULL, 'High-tier package underperforming at Dot Internet'),
(6, NULL, 6, 'PACKET_LOSS', 0.50, 1.20, 140.00, 'HIGH', 'OPEN', NOW() - INTERVAL '3.5 days', NULL, NULL, NULL, NULL, 'Intermittent packet loss at Aamra Networks'),
(7, NULL, 3, 'LATENCY_DOMESTIC', 15.00, 22.70, 51.33, 'MEDIUM', 'OPEN', NOW() - INTERVAL '5 days', NULL, NULL, NULL, NULL, 'Latency trending upward at BRACNet Limited'),

-- Recently ACKNOWLEDGED (1-2 days ago)
(8, NULL, 1, 'DOWNLOAD_SPEED', 100.00, 78.90, -21.10, 'HIGH', 'ACKNOWLEDGED', NOW() - INTERVAL '36 hours', NOW() - INTERVAL '30 hours', 'ops_team_1', NULL, NULL, 'Investigating network congestion at Triangle Services'),
(9, NULL, 5, 'AVAILABILITY', 99.00, 97.10, -1.92, 'MEDIUM', 'ACKNOWLEDGED', NOW() - INTERVAL '40 hours', NOW() - INTERVAL '35 hours', 'ops_team_2', NULL, NULL, 'Scheduled maintenance affecting uptime at Dhakacom Limited'),
(10, NULL, 2, 'UPLOAD_SPEED', 75.00, 62.30, -16.93, 'MEDIUM', 'ACKNOWLEDGED', NOW() - INTERVAL '38 hours', NOW() - INTERVAL '32 hours', 'ops_team_3', NULL, NULL, 'Asymmetric routing issue being addressed at X-Net Limited'),

-- Recently CLOSED (2-5 days ago)
(1, 1, 5, 'AVAILABILITY', 99.50, 97.80, -1.71, 'MEDIUM', 'CLOSED', NOW() - INTERVAL '4 days', NOW() - INTERVAL '3.5 days', 'ops_team_1', NOW() - INTERVAL '3 days', 'ops_team_1', 'Power backup issue resolved at Link3 Central DC'),
(2, 4, 3, 'LATENCY_DOMESTIC', 20.00, 27.40, 37.00, 'MEDIUM', 'CLOSED', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4.5 days', 'ops_team_2', NOW() - INTERVAL '4 days', 'ops_team_2', 'BGP optimization reduced latency at Amber IT Central DC'),
(3, 7, 1, 'DOWNLOAD_SPEED', 75.00, 58.30, -22.27, 'HIGH', 'CLOSED', NOW() - INTERVAL '3.5 days', NOW() - INTERVAL '3 days', 'ops_team_3', NOW() - INTERVAL '2.5 days', 'ops_team_3', 'Bandwidth upgrade completed at Carnival Central DC'),
(4, 10, 6, 'PACKET_LOSS', 1.00, 1.85, 85.00, 'MEDIUM', 'CLOSED', NOW() - INTERVAL '4.5 days', NOW() - INTERVAL '4 days', 'ops_team_1', NOW() - INTERVAL '3.5 days', 'ops_team_1', 'Faulty switch port replaced at ICC Central DC'),

-- Some older alerts still OPEN (needs attention)
(5, 13, 1, 'DOWNLOAD_SPEED', 100.00, 82.50, -17.50, 'MEDIUM', 'OPEN', NOW() - INTERVAL '6 days', NULL, NULL, NULL, NULL, 'Persistent speed issue at Dot Central DC'),
(6, NULL, 5, 'AVAILABILITY', 99.00, 98.30, -0.71, 'LOW', 'OPEN', NOW() - INTERVAL '7 days', NULL, NULL, NULL, NULL, 'Minor availability fluctuation at Aamra Networks');

-- Update created_at to match detection_time for realism
UPDATE alerts SET created_at = detection_time;

-- ============================================================================
-- PART 2: Populate INCIDENTS Table (40 test records)
-- ============================================================================

-- Clear existing incidents (optional)
-- TRUNCATE TABLE incidents RESTART IDENTITY CASCADE;

-- Insert test incidents with various statuses
INSERT INTO incidents (
    incident_id, isp_id, pop_id, qos_parameter_id,
    metric_type, severity, status, description,
    expected_value, actual_value,
    created_at, acknowledged_at, acknowledged_by,
    resolved_at, resolved_by, resolution_notes
) VALUES
-- OPEN incidents (recent, needs attention)
('INC-000001', 1, 1, 1, 'DOWNLOAD_SPEED', 'CRITICAL', 'OPEN', 'Critical speed degradation affecting 500+ subscribers at Link3 Central DC', 100.00, 45.20, NOW() - INTERVAL '2 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000002', 2, 4, 5, 'AVAILABILITY', 'CRITICAL', 'OPEN', 'Network outage at Amber IT Central DC affecting multiple areas', 99.50, 85.30, NOW() - INTERVAL '1.5 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000003', 3, 7, 6, 'PACKET_LOSS', 'HIGH', 'OPEN', 'High packet loss causing VoIP call quality issues at Carnival Central DC', 0.50, 2.80, NOW() - INTERVAL '3 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000004', 4, 10, 3, 'LATENCY_DOMESTIC', 'HIGH', 'OPEN', 'Latency spike affecting online gaming and streaming at ICC Central DC', 20.00, 48.50, NOW() - INTERVAL '4 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000005', 5, 13, 1, 'DOWNLOAD_SPEED', 'MEDIUM', 'OPEN', 'Speed inconsistency during peak hours at Dot Central DC', 150.00, 110.30, NOW() - INTERVAL '6 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000006', 1, 2, 5, 'AVAILABILITY', 'MEDIUM', 'OPEN', 'Intermittent connectivity at Link3 Shariatpur Edge', 99.00, 96.80, NOW() - INTERVAL '8 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000007', 2, 5, 2, 'UPLOAD_SPEED', 'MEDIUM', 'OPEN', 'Upload speed below SLA at Amber IT Chandpur Edge', 50.00, 38.70, NOW() - INTERVAL '5 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000008', 3, 8, 7, 'JITTER', 'MEDIUM', 'OPEN', 'Jitter affecting video conferencing at Carnival Pirojpur Edge', 10.00, 16.20, NOW() - INTERVAL '7 hours', NULL, NULL, NULL, NULL, NULL),

-- ACKNOWLEDGED incidents (being worked on)
('INC-000009', 4, 11, 1, 'DOWNLOAD_SPEED', 'HIGH', 'ACKNOWLEDGED', 'Bandwidth congestion at ICC Dinajpur Edge - investigating fiber link', 100.00, 62.40, NOW() - INTERVAL '12 hours', NOW() - INTERVAL '10 hours', 'field_team_1', NULL, NULL, NULL),
('INC-000010', 5, 14, 5, 'AVAILABILITY', 'HIGH', 'ACKNOWLEDGED', 'Power backup failure causing outages at Dot Bagerhat Edge', 99.50, 94.20, NOW() - INTERVAL '10 hours', NOW() - INTERVAL '8 hours', 'field_team_2', NULL, NULL, NULL),
('INC-000011', 1, 3, 6, 'PACKET_LOSS', 'MEDIUM', 'ACKNOWLEDGED', 'Faulty cable suspected at Link3 Coxsbazar Edge', 1.00, 2.30, NOW() - INTERVAL '14 hours', NOW() - INTERVAL '11 hours', 'field_team_1', NULL, NULL, NULL),
('INC-000012', 2, 6, 3, 'LATENCY_DOMESTIC', 'MEDIUM', 'ACKNOWLEDGED', 'Router CPU high at Amber IT Joypurhat Edge', 20.00, 32.10, NOW() - INTERVAL '16 hours', NOW() - INTERVAL '13 hours', 'noc_team_1', NULL, NULL, NULL),
('INC-000013', 3, 9, 1, 'DOWNLOAD_SPEED', 'HIGH', 'ACKNOWLEDGED', 'Capacity planning needed at Carnival Shariatpur Edge', 75.00, 52.80, NOW() - INTERVAL '18 hours', NOW() - INTERVAL '15 hours', 'noc_team_2', NULL, NULL, NULL),

-- RESOLVED incidents (recently closed - last 1-3 days)
('INC-000014', 4, 12, 6, 'PACKET_LOSS', 'CRITICAL', 'RESOLVED', 'Fiber cut resolved at ICC Barguna Edge', 0.50, 5.20, NOW() - INTERVAL '2 days', NOW() - INTERVAL '1.8 days', 'field_team_1', NOW() - INTERVAL '1.5 days', 'field_team_1', 'Emergency fiber repair completed. Tested and verified.'),
('INC-000015', 5, 15, 3, 'LATENCY_DOMESTIC', 'HIGH', 'RESOLVED', 'BGP routing issue fixed at Dot Manikganj Edge', 20.00, 45.30, NOW() - INTERVAL '2.5 days', NOW() - INTERVAL '2.3 days', 'noc_team_1', NOW() - INTERVAL '2 days', 'noc_team_1', 'Routing policy updated and latency returned to normal.'),
('INC-000016', 1, 1, 5, 'AVAILABILITY', 'HIGH', 'RESOLVED', 'UPS battery replacement at Link3 Central DC', 99.50, 96.10, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2.8 days', 'facility_team', NOW() - INTERVAL '2.5 days', 'facility_team', 'New UPS batteries installed. Power redundancy restored.'),
('INC-000017', 2, 4, 1, 'DOWNLOAD_SPEED', 'MEDIUM', 'RESOLVED', 'QoS configuration adjusted at Amber IT Central DC', 200.00, 155.40, NOW() - INTERVAL '1.5 days', NOW() - INTERVAL '1.3 days', 'noc_team_2', NOW() - INTERVAL '1 day', 'noc_team_2', 'Traffic shaping rules optimized. Speed targets met.'),
('INC-000018', 3, 7, 2, 'UPLOAD_SPEED', 'MEDIUM', 'RESOLVED', 'Upstream bandwidth increased at Carnival Central DC', 100.00, 78.20, NOW() - INTERVAL '2.2 days', NOW() - INTERVAL '2 days', 'capacity_team', NOW() - INTERVAL '1.8 days', 'capacity_team', 'Bandwidth upgrade from ISP completed successfully.'),
('INC-000019', 4, 10, 8, 'UTILIZATION', 'HIGH', 'RESOLVED', 'Link upgrade to 10G at ICC Central DC', 85.00, 93.50, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2.7 days', 'network_team', NOW() - INTERVAL '2.3 days', 'network_team', 'Link capacity doubled. Utilization now at 45%.'),
('INC-000020', 5, 13, 5, 'AVAILABILITY', 'MEDIUM', 'RESOLVED', 'Redundant path activated at Dot Central DC', 99.00, 97.50, NOW() - INTERVAL '1.8 days', NOW() - INTERVAL '1.6 days', 'noc_team_1', NOW() - INTERVAL '1.4 days', 'noc_team_1', 'Failover mechanism tested and working properly.'),

-- Older incidents (4-7 days ago)
('INC-000021', 1, 2, 1, 'DOWNLOAD_SPEED', 'MEDIUM', 'RESOLVED', 'Congestion management at Link3 Shariatpur Edge', 50.00, 38.90, NOW() - INTERVAL '5 days', NOW() - INTERVAL '4.8 days', 'field_team_2', NOW() - INTERVAL '4.5 days', 'field_team_2', 'Additional bandwidth allocated to edge PoP.'),
('INC-000022', 2, 5, 5, 'AVAILABILITY', 'HIGH', 'RESOLVED', 'Generator maintenance issue at Amber IT Chandpur Edge', 99.50, 92.30, NOW() - INTERVAL '6 days', NOW() - INTERVAL '5.8 days', 'facility_team', NOW() - INTERVAL '5.5 days', 'facility_team', 'Generator serviced and tested under load.'),
('INC-000023', 3, 8, 6, 'PACKET_LOSS', 'MEDIUM', 'RESOLVED', 'Switch port error at Carnival Pirojpur Edge', 1.00, 2.10, NOW() - INTERVAL '4.5 days', NOW() - INTERVAL '4.3 days', 'field_team_1', NOW() - INTERVAL '4 days', 'field_team_1', 'Faulty SFP module replaced.'),
('INC-000024', 4, 11, 3, 'LATENCY_DOMESTIC', 'MEDIUM', 'RESOLVED', 'Routing loop at ICC Dinajpur Edge', 20.00, 38.40, NOW() - INTERVAL '7 days', NOW() - INTERVAL '6.8 days', 'noc_team_2', NOW() - INTERVAL '6.5 days', 'noc_team_2', 'Spanning tree protocol reconfigured.'),
('INC-000025', 5, 14, 1, 'DOWNLOAD_SPEED', 'HIGH', 'RESOLVED', 'Fiber alignment issue at Dot Bagerhat Edge', 100.00, 55.70, NOW() - INTERVAL '5.5 days', NOW() - INTERVAL '5.3 days', 'field_team_2', NOW() - INTERVAL '5 days', 'field_team_2', 'Fiber optic connector cleaned and realigned.'),

-- Mix of statuses from recent week
('INC-000026', 1, 3, 2, 'UPLOAD_SPEED', 'MEDIUM', 'OPEN', 'Upload asymmetry at Link3 Coxsbazar Edge', 50.00, 35.60, NOW() - INTERVAL '1 day', NULL, NULL, NULL, NULL, NULL),
('INC-000027', 2, 6, 7, 'JITTER', 'MEDIUM', 'ACKNOWLEDGED', 'Jitter investigation at Amber IT Joypurhat Edge', 10.00, 15.80, NOW() - INTERVAL '20 hours', NOW() - INTERVAL '18 hours', 'noc_team_1', NULL, NULL, NULL),
('INC-000028', 3, 9, 5, 'AVAILABILITY', 'MEDIUM', 'RESOLVED', 'Scheduled maintenance at Carnival Shariatpur Edge', 99.00, 98.20, NOW() - INTERVAL '2 days', NOW() - INTERVAL '1.9 days', 'maintenance_team', NOW() - INTERVAL '1.7 days', 'maintenance_team', 'Firmware upgrade completed successfully.'),
('INC-000029', 4, 12, 1, 'DOWNLOAD_SPEED', 'HIGH', 'OPEN', 'Performance degradation at ICC Barguna Edge', 75.00, 48.30, NOW() - INTERVAL '9 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000030', 5, 15, 6, 'PACKET_LOSS', 'HIGH', 'ACKNOWLEDGED', 'RF interference suspected at Dot Manikganj Edge', 1.00, 2.95, NOW() - INTERVAL '15 hours', NOW() - INTERVAL '12 hours', 'field_team_1', NULL, NULL, NULL),

-- Additional varied incidents
('INC-000031', 1, 1, 8, 'UTILIZATION', 'MEDIUM', 'RESOLVED', 'Peak hour capacity at Link3 Central DC', 80.00, 88.70, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2.8 days', 'capacity_team', NOW() - INTERVAL '2.5 days', 'capacity_team', 'Load balancing configuration optimized.'),
('INC-000032', 2, 4, 6, 'PACKET_LOSS', 'MEDIUM', 'OPEN', 'Intermittent loss at Amber IT Central DC', 0.50, 1.60, NOW() - INTERVAL '10 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000033', 3, 7, 3, 'LATENCY_DOMESTIC', 'HIGH', 'ACKNOWLEDGED', 'Latency investigation at Carnival Central DC', 15.00, 35.20, NOW() - INTERVAL '13 hours', NOW() - INTERVAL '11 hours', 'noc_team_2', NULL, NULL, NULL),
('INC-000034', 4, 10, 5, 'AVAILABILITY', 'CRITICAL', 'RESOLVED', 'Core switch failure at ICC Central DC', 99.50, 78.40, NOW() - INTERVAL '4 days', NOW() - INTERVAL '3.9 days', 'field_team_1', NOW() - INTERVAL '3.6 days', 'field_team_1', 'Emergency switch replacement completed.'),
('INC-000035', 5, 13, 2, 'UPLOAD_SPEED', 'MEDIUM', 'RESOLVED', 'Asynchronous rate limiting at Dot Central DC', 150.00, 115.60, NOW() - INTERVAL '1.5 days', NOW() - INTERVAL '1.3 days', 'noc_team_1', NOW() - INTERVAL '1.1 days', 'noc_team_1', 'Rate limit policy corrected.'),

-- Final batch
('INC-000036', 1, 2, 6, 'PACKET_LOSS', 'LOW', 'RESOLVED', 'Minor packet loss at Link3 Shariatpur Edge', 1.00, 1.40, NOW() - INTERVAL '6 days', NOW() - INTERVAL '5.8 days', 'noc_team_2', NOW() - INTERVAL '5.5 days', 'noc_team_2', 'Transient issue resolved automatically.'),
('INC-000037', 2, 5, 3, 'LATENCY_DOMESTIC', 'MEDIUM', 'OPEN', 'Routing delay at Amber IT Chandpur Edge', 20.00, 29.50, NOW() - INTERVAL '11 hours', NULL, NULL, NULL, NULL, NULL),
('INC-000038', 3, 8, 1, 'DOWNLOAD_SPEED', 'MEDIUM', 'ACKNOWLEDGED', 'Subscriber spike at Carnival Pirojpur Edge', 75.00, 58.20, NOW() - INTERVAL '17 hours', NOW() - INTERVAL '14 hours', 'capacity_team', NULL, NULL, NULL),
('INC-000039', 4, 11, 5, 'AVAILABILITY', 'MEDIUM', 'RESOLVED', 'Power fluctuation at ICC Dinajpur Edge', 99.00, 97.30, NOW() - INTERVAL '2.5 days', NOW() - INTERVAL '2.3 days', 'facility_team', NOW() - INTERVAL '2 days', 'facility_team', 'Voltage stabilizer installed.'),
('INC-000040', 5, 14, 7, 'JITTER', 'LOW', 'RESOLVED', 'Minor jitter at Dot Bagerhat Edge', 10.00, 12.30, NOW() - INTERVAL '4 days', NOW() - INTERVAL '3.8 days', 'noc_team_1', NOW() - INTERVAL '3.5 days', 'noc_team_1', 'QoS queue tuning resolved issue.');

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Count alerts by status
SELECT status, severity, COUNT(*) as count
FROM alerts
GROUP BY status, severity
ORDER BY status, severity;

-- Count incidents by status
SELECT status, severity, COUNT(*) as count
FROM incidents
GROUP BY status, severity
ORDER BY status, severity;

-- Show recent open alerts
SELECT id, i.name_en as isp, a.metric_type, a.severity, a.status,
       TO_CHAR(a.detection_time, 'YYYY-MM-DD HH24:MI') as detected
FROM alerts a
JOIN isps i ON a.isp_id = i.id
WHERE a.status = 'OPEN'
ORDER BY a.detection_time DESC
LIMIT 10;

-- Show recent open incidents
SELECT incident_id, i.name_en as isp, p.name_en as pop,
       inc.metric_type, inc.severity, inc.status,
       TO_CHAR(inc.created_at, 'YYYY-MM-DD HH24:MI') as created
FROM incidents inc
JOIN isps i ON inc.isp_id = i.id
LEFT JOIN pops p ON inc.pop_id = p.id
WHERE inc.status = 'OPEN'
ORDER BY inc.created_at DESC
LIMIT 10;

-- Summary statistics
SELECT 'Alerts' as table_name, COUNT(*) as total_records,
       SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_count,
       SUM(CASE WHEN status = 'ACKNOWLEDGED' THEN 1 ELSE 0 END) as ack_count,
       SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as closed_count
FROM alerts
UNION ALL
SELECT 'Incidents' as table_name, COUNT(*) as total_records,
       SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_count,
       SUM(CASE WHEN status = 'ACKNOWLEDGED' THEN 1 ELSE 0 END) as ack_count,
       SUM(CASE WHEN status = 'RESOLVED' THEN 1 ELSE 0 END) as resolved_count
FROM incidents;

-- ============================================================================
-- Success Message
-- ============================================================================
SELECT '✅ Test data population complete!' as message,
       (SELECT COUNT(*) FROM alerts) as alerts_created,
       (SELECT COUNT(*) FROM incidents) as incidents_created;
