# Map Visualization Tools Comparison for BTRC Dashboard

**Date:** 2026-02-07
**Purpose:** Evaluate alternative BI tools for map visualization capabilities
**Current Tool:** Apache Superset 6.0.0

---

## Executive Summary

| Tool | Map Support | Custom GeoJSON | Drill-Down | Bangladesh Ready | Recommendation |
|------|-------------|----------------|------------|------------------|----------------|
| **Apache Superset** | Good | Yes | Limited | Partial | Current - Keep |
| **Metabase** | Good | Yes | Limited | Yes | **Best Alternative** |
| **Grafana** | Good | Yes (alpha) | No | Requires Setup | Specialized Use |
| **Redash** | Basic | No (Countries only) | No | No | Not Recommended |

**Recommendation:** If switching is needed, **Metabase** offers the best balance of map capabilities, ease of use, and PostgreSQL/TimescaleDB support.

---

## Tool 1: Apache Superset (Current)

### Overview
- **License:** Apache 2.0 (Open Source)
- **Version Used:** 6.0.0
- **Website:** https://superset.apache.org/

### Map Visualization Capabilities

| Feature | Support | Notes |
|---------|---------|-------|
| Choropleth Maps | Yes | `country_map` viz type (D3/SVG) |
| Custom GeoJSON | Yes | Replace built-in files in Docker |
| Bangladesh Divisions | Yes | 8-division GeoJSON added |
| Bangladesh Districts | No | country_map only supports 1 level |
| Point Maps (Markers) | Yes | deck.gl (broken in Chrome) |
| Heatmaps | Yes | deck.gl (broken in Chrome) |
| Click-to-Filter | Yes | `emit_filter: true` |
| Drill-Down (Geo) | No | Single level only |
| Time Series + Map | No | Separate charts needed |

### Current Issues in BTRC Project

| Issue | Severity | Workaround |
|-------|----------|------------|
| deck.gl broken in Chrome | High | Use Firefox or country_map |
| No district-level choropleth | Medium | Two-linked-tables approach |
| cartodiagram plugin not working | Medium | Would need custom build |
| Native filters API bug | Low | Create filters via UI |

### Strengths
- 50+ visualization types
- SQL Lab for ad-hoc queries
- Role-based access control
- Async queries with Celery
- Already deployed and configured

### Weaknesses
- deck.gl WebGL issues
- Single-level choropleth only
- Complex plugin system
- Steep learning curve for admins

---

## Tool 2: Metabase (Recommended Alternative)

### Overview
- **License:** AGPL (Open Source) / Commercial
- **Current Version:** 0.50+ (2025)
- **Website:** https://www.metabase.com/

### Map Visualization Capabilities

| Feature | Support | Notes |
|---------|---------|-------|
| Choropleth Maps | Yes | Region maps with custom GeoJSON |
| Custom GeoJSON | Yes | Admin panel upload (<5MB) |
| Bangladesh Divisions | Yes | Upload custom GeoJSON |
| Bangladesh Districts | Yes | Upload separate GeoJSON |
| Point Maps (Markers) | Yes | Pin maps with lat/lng |
| Heatmaps | No | Not built-in |
| Click-to-Filter | Partial | Dashboard filters, not map click |
| Drill-Down (Geo) | Limited | Custom click destinations |
| Time Series + Map | No | Separate charts needed |

### Key Features for BTRC

| Feature | Details |
|---------|---------|
| Custom Maps Upload | Admin > Maps > Add custom GeoJSON URL |
| Region Identifier | Match column to GeoJSON property |
| Multiple Map Layers | Can have Division + District maps |
| Dashboard Filters | Link filters to map selections |
| PostgreSQL Support | Native connector, 5-min setup |
| TimescaleDB Support | Works via PostgreSQL connector |

### Strengths
- Easier setup than Superset
- Better custom GeoJSON workflow
- Cleaner UI for non-technical users
- No WebGL dependencies (uses SVG)
- Active community and documentation

### Weaknesses
- No drill-through on custom maps
- Fewer chart types than Superset
- Less customizable than Superset
- AGPL license requires code sharing if modified

### Migration Effort: MEDIUM
- Recreate 24+ datasets as Questions
- Recreate dashboards manually
- Upload custom GeoJSON files
- Set up dashboard filters

---

## Tool 3: Grafana

### Overview
- **License:** AGPL (Open Source) / Commercial
- **Current Version:** 11.x (2025)
- **Website:** https://grafana.com/

### Map Visualization Capabilities

| Feature | Support | Notes |
|---------|---------|-------|
| Choropleth Maps | Yes | Geomap panel |
| Custom GeoJSON | Alpha | Dynamic GeoJSON layer |
| Bangladesh Divisions | Requires Setup | Custom GeoJSON query |
| Bangladesh Districts | Requires Setup | PostGIS query needed |
| Point Maps (Markers) | Yes | Native support |
| Heatmaps | Yes | Native support |
| Click-to-Filter | Limited | Data links only |
| Drill-Down (Geo) | No | Not supported |
| Time Series + Map | Yes | Same panel possible |

### Key Features for BTRC

| Feature | Details |
|---------|---------|
| Geomap Panel | 8 layer types including GeoJSON |
| Dynamic GeoJSON | Query-based region styling (alpha) |
| PostGIS Integration | Direct geometry queries |
| Plugin Ecosystem | Unfolded Studio, Orchestra Cities |
| Real-time Updates | Optimized for streaming data |

### Strengths
- Best for real-time monitoring
- Excellent alerting system
- Strong time-series support
- PostGIS direct queries
- Mature plugin ecosystem

### Weaknesses
- Not designed for BI/reporting
- Complex GeoJSON setup
- Dynamic GeoJSON is alpha
- Less intuitive for business users
- Overkill for static dashboards

### Migration Effort: HIGH
- Different paradigm (monitoring vs BI)
- PostGIS queries for all geo data
- Dashboard layout redesign
- Learning curve for team

---

## Tool 4: Redash

### Overview
- **License:** BSD (Open Source)
- **Current Version:** 10.x
- **Website:** https://redash.io/

### Map Visualization Capabilities

| Feature | Support | Notes |
|---------|---------|-------|
| Choropleth Maps | Yes | Countries only |
| Custom GeoJSON | No | Built-in maps only |
| Bangladesh Divisions | No | Country is minimum unit |
| Bangladesh Districts | No | Not supported |
| Point Maps (Markers) | Yes | Basic support |
| Heatmaps | No | Not available |
| Click-to-Filter | No | Not supported |
| Drill-Down (Geo) | No | Not supported |
| Time Series + Map | No | Separate visualizations |

### Built-in Maps
- World countries (ISO 2/3 letter codes)
- USA subdivisions
- Japan prefectures
- **No Bangladesh subdivisions**

### Strengths
- Simple query interface
- Good for SQL-focused teams
- Lightweight deployment
- Easy sharing/embedding

### Weaknesses
- **Cannot visualize Bangladesh divisions/districts**
- No custom GeoJSON support
- Limited visualization options
- Less active development
- Feature requests pending for years

### Recommendation: NOT SUITABLE
Redash cannot meet BTRC requirements for Bangladesh sub-national visualization.

---

## Feature Comparison Matrix

### Map Visualization Features

| Feature | Superset | Metabase | Grafana | Redash |
|---------|----------|----------|---------|--------|
| Choropleth (Country) | Yes | Yes | Yes | Yes |
| Choropleth (Division) | Yes* | Yes | Yes* | No |
| Choropleth (District) | No | Yes | Yes* | No |
| Custom GeoJSON Upload | Manual | Yes | Alpha | No |
| Point/Marker Maps | Yes** | Yes | Yes | Yes |
| Heatmaps | Yes** | No | Yes | No |
| Bubble Maps | Yes** | No | Yes | No |
| Map + Time Animation | No | No | Yes | No |
| Click-to-Filter | Yes | Partial | Limited | No |
| Geo Drill-Down | No | Limited | No | No |
| Offline/Self-Hosted | Yes | Yes | Yes | Yes |

*Requires custom configuration
**deck.gl broken in Chrome

### Dashboard Features

| Feature | Superset | Metabase | Grafana | Redash |
|---------|----------|----------|---------|--------|
| Tabs | Yes | No | No | No |
| Native Filters | Yes | Yes | Yes | Yes |
| Cross-Filtering | Yes | Yes | Limited | No |
| Drill-Through | Limited | Yes | Limited | No |
| Embedding | Yes | Yes | Yes | Yes |
| PDF Export | Plugin | Yes | Plugin | Yes |
| Scheduled Reports | Yes | Yes | Yes | Yes |
| Role-Based Access | Yes | Yes | Yes | Limited |

### Database Connectivity

| Database | Superset | Metabase | Grafana | Redash |
|----------|----------|----------|---------|--------|
| PostgreSQL | Yes | Yes | Yes | Yes |
| TimescaleDB | Yes | Yes | Yes | Yes |
| PostGIS | Yes | Yes | Yes | Yes |
| Real-time/Streaming | Limited | No | Yes | No |

---

## BTRC-Specific Requirements Checklist

### Must-Have Features

| Requirement | Superset | Metabase | Grafana | Redash |
|-------------|----------|----------|---------|--------|
| Bangladesh 8 Divisions Map | Yes | Yes | Yes | No |
| Bangladesh 64 Districts Map | No* | Yes | Yes* | No |
| Division-level Choropleth | Yes | Yes | Yes | No |
| District-level Choropleth | No* | Yes | Yes* | No |
| PostgreSQL/TimescaleDB | Yes | Yes | Yes | Yes |
| Self-Hosted/On-Premise | Yes | Yes | Yes | Yes |
| Role-Based Access | Yes | Yes | Yes | Limited |
| Dashboard Filters | Yes | Yes | Yes | Yes |
| KPI Cards | Yes | Yes | Yes | Yes |
| Tables with Sorting | Yes | Yes | Yes | Yes |
| Bar/Line Charts | Yes | Yes | Yes | Yes |

*Requires workaround or complex setup

### Nice-to-Have Features

| Requirement | Superset | Metabase | Grafana | Redash |
|-------------|----------|----------|---------|--------|
| Click Map to Filter | Yes | Partial | Limited | No |
| Division→District Drill | No | Limited | No | No |
| Real-time Updates | Limited | No | Yes | No |
| PDF Reports | Plugin | Yes | Plugin | Yes |
| Mobile Responsive | Yes | Yes | Yes | Yes |
| Bengali Language | No | No | No | No |
| Audit Logging | Yes | Yes | Yes | Limited |

---

## Recommendations

### Option A: Keep Apache Superset (Recommended for POC)
**Effort:** None (already deployed)
**Risk:** Low

**Rationale:**
- Already configured with data and dashboards
- Workarounds in place for map issues
- Two-linked-tables approach for drill-down works
- Division map (country_map) functioning
- POC timeline constraint

**Action Items:**
1. Continue using country_map for divisions
2. Use tables for district-level data
3. Document known limitations
4. Plan Metabase pilot for Phase 2

### Option B: Migrate to Metabase (Best for Production)
**Effort:** 2-3 weeks
**Risk:** Medium

**Rationale:**
- Better custom GeoJSON workflow
- Can have both Division and District maps
- Easier for non-technical BTRC staff
- No WebGL issues
- Active development and community

**Migration Steps:**
1. Deploy Metabase (Docker)
2. Connect to TimescaleDB
3. Upload Bangladesh GeoJSON files (Division + District)
4. Recreate dashboards
5. Configure filters and permissions
6. User training

### Option C: Add Grafana for Real-Time (Future Phase)
**Effort:** 1-2 weeks (additional)
**Risk:** Low (complementary)

**Rationale:**
- Best for real-time monitoring
- Can complement Superset/Metabase
- Use for operational alerts
- Keep Superset for reporting

---

## Cost Comparison

| Tool | License | Hosting | Total (Self-Hosted) |
|------|---------|---------|---------------------|
| Superset | Free (Apache 2.0) | Server costs only | Free |
| Metabase | Free (AGPL) | Server costs only | Free |
| Metabase Pro | $500/month | Server costs | $6,000/year |
| Grafana OSS | Free (AGPL) | Server costs only | Free |
| Grafana Cloud | $49/user/month | Included | Variable |
| Redash | Free (BSD) | Server costs only | Free |

All open-source options are free for self-hosted deployment.

---

## Conclusion

For the **BTRC QoS Monitoring Dashboard POC**:

1. **Continue with Apache Superset** for the current POC phase
   - Workarounds are functional
   - No migration risk
   - Timeline preserved

2. **Evaluate Metabase** for Phase 2 production
   - Better custom map support
   - Easier user experience
   - Plan pilot deployment

3. **Consider Grafana** for real-time monitoring component
   - Complementary to BI tool
   - Best for live data dashboards

---

## Sources

- [Metabase Official](https://www.metabase.com/)
- [Metabase Custom Maps Documentation](https://www.metabase.com/docs/latest/configuring-metabase/custom-maps)
- [Metabase vs Superset Comparison](https://www.metabase.com/lp/metabase-vs-superset)
- [Apache Superset vs Metabase 2026](https://bix-tech.com/apache-superset-vs-metabase-the-nononsense-guide-to-choosing-the-right-opensource-bi-platform-in-2026/)
- [Grafana Geomap Documentation](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/visualizations/geomap/)
- [Grafana Custom GeoJSON Discussion](https://community.grafana.com/t/adding-custom-geojson-to-geomap/57991)
- [Redash Choropleth Limitations](https://discuss.redash.io/t/choropleth-map-per-regions/4437)
- [Top Open Source Dashboard Tools 2026](https://www.metricfire.com/blog/top-8-open-source-dashboards/)

---

**Document Version:** 1.0
**Prepared By:** Claude Code Assistant
**Last Updated:** 2026-02-07
