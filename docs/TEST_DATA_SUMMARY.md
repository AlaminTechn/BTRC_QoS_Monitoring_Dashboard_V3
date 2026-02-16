# Test Data Summary - Alerts & Incidents

**Date:** 2026-02-10
**Status:** ✅ **TEST DATA POPULATED**

---

## Summary Statistics

| Table | Total Records | Open | Acknowledged | Closed/Resolved |
|-------|--------------|------|--------------|-----------------|
| **alerts** | 39 | 23 | 7 | 9 |
| **incidents** | 40 | 12 | 9 | 19 |

---

## Alerts Breakdown by Severity

| Status | Critical | High | Medium | Low |
|--------|----------|------|--------|-----|
| **OPEN** | 4 | 8 | 10 | 1 |
| **ACKNOWLEDGED** | 0 | 3 | 4 | 0 |
| **CLOSED** | 1 | 3 | 5 | 0 |

### Sample Open Alerts
```
ISP                  Metric            Threshold  Actual  Severity  Status
-------------------  ----------------  ---------  ------  --------  ------
Aamra Networks       PACKET_LOSS       1.00       3.45    CRITICAL  OPEN
ICC Communication    LATENCY_DOMESTIC  20.00      45.80   CRITICAL  OPEN
Link3 Technologies   DOWNLOAD_SPEED    50.00      28.50   CRITICAL  OPEN
Amber IT Limited     AVAILABILITY      99.00      92.30   CRITICAL  OPEN
BRACNet Limited      UTILIZATION       85.00      92.50   HIGH      OPEN
```

---

## Incidents Breakdown by Severity

| Status | Critical | High | Medium | Low |
|--------|----------|------|--------|-----|
| **OPEN** | 2 | 3 | 7 | 0 |
| **ACKNOWLEDGED** | 0 | 5 | 4 | 0 |
| **RESOLVED** | 2 | 5 | 10 | 2 |

### Sample Open Incidents
```
Incident ID  ISP                PoP Location           Metric Type       Status  Severity
-----------  -----------------  ---------------------  ----------------  ------  --------
INC-000002   Amber IT Limited   Amber IT Central DC    AVAILABILITY      OPEN    CRITICAL
INC-000001   Link3 Technologies Link3 Central DC       DOWNLOAD_SPEED    OPEN    CRITICAL
INC-000003   Carnival Internet  Carnival Central DC    PACKET_LOSS       OPEN    HIGH
INC-000004   ICC Communication  ICC Central DC         LATENCY_DOMESTIC  OPEN    HIGH
INC-000007   Amber IT Limited   Amber IT Chandpur Edge UPLOAD_SPEED      OPEN    MEDIUM
```

---

## Test Data Coverage

### Time Distribution
- **Recent (0-2 hours):** 4 critical alerts, 2 critical incidents
- **Today (2-24 hours):** 15 open alerts, 8 open incidents
- **This Week (1-7 days):** All 40 incidents, 39 alerts
- **Acknowledged:** In-progress investigations with field teams assigned
- **Resolved:** Completed incidents with resolution notes

### ISP Coverage
All 10 ISPs have test data:
1. Link3 Technologies
2. Amber IT Limited
3. Carnival Internet
4. ICC Communication
5. Dot Internet
6. Aamra Networks
7. BRACNet Limited
8. Triangle Services
9. Dhakacom Limited
10. X-Net Limited

### PoP Coverage
15 PoPs covered with incidents including:
- Central DCs (main data centers)
- Edge locations (regional PoPs)
- Mix of metro and remote locations

### Metric Types Covered
- ✅ DOWNLOAD_SPEED
- ✅ UPLOAD_SPEED
- ✅ LATENCY_DOMESTIC
- ✅ AVAILABILITY
- ✅ PACKET_LOSS
- ✅ JITTER
- ✅ UTILIZATION

---

## Realistic Scenarios Included

### Critical Issues (Immediate Attention)
1. **Network Outage** - Amber IT Central DC (85.3% availability)
2. **Severe Speed Drop** - Link3 Central DC (45% of target)
3. **High Packet Loss** - Aamra Networks (3.45% loss)
4. **Extreme Latency** - ICC Central DC (45ms vs 20ms target)

### High Priority Issues
1. **Bandwidth Congestion** - Multiple PoPs during peak hours
2. **Power Backup Failures** - UPS/generator issues
3. **Fiber Link Problems** - Speed degradation
4. **Capacity Issues** - Link utilization >90%

### Medium Priority Issues
1. **Intermittent Connectivity** - Occasional drops
2. **Jitter Problems** - Affecting VoIP/video
3. **Upload Asymmetry** - Upload speed below SLA
4. **Minor Packet Loss** - 1-2% range

### Resolved Issues (Show Resolution Process)
1. **Fiber Cut** - Emergency repair completed
2. **BGP Routing** - Optimization reduced latency
3. **UPS Battery** - Replacement restored redundancy
4. **QoS Configuration** - Traffic shaping adjusted
5. **Link Upgrade** - Capacity doubled

---

## Assignments & Workflow

### Team Assignments
- **ops_team_1, ops_team_2, ops_team_3** - Network operations
- **field_team_1, field_team_2** - On-site technicians
- **noc_team_1, noc_team_2** - Network operations center
- **facility_team** - Power/facility management
- **capacity_team** - Capacity planning
- **network_team** - Core network engineering
- **maintenance_team** - Scheduled maintenance

### Resolution Notes Examples
- "Emergency fiber repair completed. Tested and verified."
- "Routing policy updated and latency returned to normal."
- "New UPS batteries installed. Power redundancy restored."
- "Traffic shaping rules optimized. Speed targets met."
- "Bandwidth upgrade from ISP completed successfully."

---

## Dashboard Testing

### R1.5: Real-Time Threshold Alerts
**Expected Results:**
- Show 30+ open/acknowledged alerts
- Critical alerts at top (red indicators)
- Duration calculated from detection_time
- Status indicators visible

**Test Query:**
```sql
SELECT COUNT(*) FROM alerts WHERE status IN ('OPEN', 'ACKNOWLEDGED');
```
**Result:** 30 alerts

### R1.6: PoP-Level Incident Table
**Expected Results:**
- Show 40 total incidents (last 7 days)
- Mix of Open/Acknowledged/Resolved
- PoP locations visible
- Duration calculated correctly

**Test Query:**
```sql
SELECT COUNT(*) FROM incidents WHERE created_at >= NOW() - INTERVAL '7 days';
```
**Result:** 40 incidents

---

## Verification Commands

### Check Alerts Data
```sql
-- Count by status
SELECT status, COUNT(*) FROM alerts GROUP BY status;

-- Recent critical alerts
SELECT i.name_en, a.metric_type, a.severity, a.status
FROM alerts a
JOIN isps i ON a.isp_id = i.id
WHERE a.severity = 'CRITICAL' AND a.status = 'OPEN'
ORDER BY a.detection_time DESC;
```

### Check Incidents Data
```sql
-- Count by status
SELECT status, COUNT(*) FROM incidents GROUP BY status;

-- Recent open incidents
SELECT inc.incident_id, i.name_en, inc.metric_type, inc.severity
FROM incidents inc
JOIN isps i ON inc.isp_id = i.id
WHERE inc.status = 'OPEN'
ORDER BY inc.created_at DESC;
```

### Refresh Metabase Cards
1. Open http://localhost:3000/dashboard/6
2. Navigate to R2.1: SLA Monitoring tab
3. Click refresh icon on R1.5 (alerts card)
4. Click refresh icon on R1.6 (incidents card)
5. Verify data displays correctly

---

## Data Refresh Schedule

### Current Setup
- **alerts:** Populated from sla_violations automatically
- **incidents:** Populated from sla_violations with pop_id

### Future Production Setup
You can set up triggers to auto-populate:
```sql
-- Trigger to create alerts from new violations
CREATE OR REPLACE FUNCTION create_alert_from_violation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO alerts (isp_id, pop_id, sla_threshold_id, qos_parameter_id,
                        metric_type, threshold_value, actual_value, deviation_pct,
                        severity, status, detection_time)
    VALUES (NEW.isp_id, NEW.pop_id, NEW.sla_threshold_id, NEW.qos_parameter_id,
            NEW.violation_type, NEW.expected_value, NEW.actual_value, NEW.deviation_pct,
            NEW.severity, 'OPEN', NEW.detection_time);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## Files Created

1. ✅ `populate_alerts_incidents_test_data.sql` - Test data script
2. ✅ `TEST_DATA_SUMMARY.md` - This documentation

---

## Next Steps

1. ✅ Test data populated (39 alerts + 40 incidents)
2. ✅ Queries verified working
3. 🔲 Open Metabase dashboard
4. 🔲 Refresh R1.5 and R1.6 cards
5. 🔲 Verify data displays correctly
6. 🔲 Test sorting and filtering
7. 🔲 Check drill-down functionality

---

## Dashboard Access

**URL:** http://localhost:3000/dashboard/6
**Tab:** R2.1: SLA Monitoring
**Cards to Test:**
- R1.5: Real-Time Threshold Alerts (Card 98)
- R1.6: PoP-Level Incident Table (Card 99)

---

**Status:** ✅ COMPLETE
**Records Created:** 79 total (39 alerts + 40 incidents)
**Data Quality:** Production-ready realistic test data

---

**End of Document**
