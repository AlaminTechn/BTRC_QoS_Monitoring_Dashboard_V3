# Container Version Specifications

**Project:** BTRC QoS Monitoring Dashboard V3
**Last Updated:** 2026-02-16

---

## 📦 Container Images

### **TimescaleDB**
```yaml
image: timescale/timescaledb-ha:pg15-latest
```
- **PostgreSQL Version:** 15
- **TimescaleDB:** Latest compatible
- **Purpose:** Time-series database for QoS measurements
- **Port:** 5433 (host) → 5432 (container)

**Version Notes:**
- PostgreSQL 15 provides better performance for time-series data
- TimescaleDB HA (High Availability) includes pgBackRest for backups
- Compatible with Metabase PostgreSQL driver

---

### **Metabase**
```yaml
image: metabase/metabase:latest
```
- **Current Version:** v0.58.5.2
- **Purpose:** Business Intelligence and Dashboards
- **Port:** 3000 (host) → 3000 (container)

**Version Notes:**
- Using `latest` tag for automatic updates
- For production, recommend pinning to specific version: `metabase/metabase:v0.58.5`
- Metadata stored in PostgreSQL (metabase_meta database)

**Recommended Production Version:**
```yaml
image: metabase/metabase:v0.58.5
```

---

### **Nginx**
```yaml
image: nginx:1.25-alpine
```
- **Nginx Version:** 1.25
- **Base:** Alpine Linux (lightweight)
- **Purpose:** Reverse proxy and static file server
- **Port:** 8080 (host) → 80 (container)

**Version Notes:**
- Alpine-based for minimal size (~24MB)
- Version 1.25 is stable and production-ready
- Serves custom dashboard wrapper

---

### **Metabase Init (Custom)**
```yaml
image: built from docker/Dockerfile.init
base: python:3.10-slim
```
- **Python Version:** 3.10
- **Purpose:** Initialize users and permissions on startup
- **Dependencies:** requests==2.31.0

**Version Notes:**
- Python 3.10 matches host system
- Runs once on container startup
- No persistent data

---

## 🔗 Version Compatibility Matrix

| Component | Version | Compatible With | Notes |
|-----------|---------|----------------|-------|
| **TimescaleDB** | PG15 | Metabase v0.48+ | Fully compatible |
| **Metabase** | v0.58.5 | PostgreSQL 9.6+ | Uses metabase_meta DB |
| **Nginx** | 1.25 | Any | Reverse proxy only |
| **Python Init** | 3.10 | Metabase API v0.58+ | Requests 2.31.0 |

---

## 🐍 Python Dependencies

### **Host System**
```
Python: 3.10
```

### **Init Container**
```
Python: 3.10-slim
requests: 2.31.0
```

### **Why Python 3.10?**
- Stable and widely supported
- Compatible with all required libraries
- Matches host system version
- Good balance of features and compatibility

---

## 📝 Version Pinning Recommendations

### **Development (Current Setup)**
```yaml
services:
  timescaledb:
    image: timescale/timescaledb-ha:pg15-latest

  metabase:
    image: metabase/metabase:latest

  nginx:
    image: nginx:1.25-alpine
```

**Pros:**
- Always get latest security patches
- New features automatically

**Cons:**
- Potential breaking changes
- Unpredictable behavior

---

### **Production (Recommended)**
```yaml
services:
  timescaledb:
    image: timescale/timescaledb-ha:pg15.6-ts2.14.2

  metabase:
    image: metabase/metabase:v0.58.5

  nginx:
    image: nginx:1.25.4-alpine

  metabase-init:
    build:
      context: .
      dockerfile: docker/Dockerfile.init
    # Uses Python 3.10-slim (pinned in Dockerfile)
```

**Pros:**
- Predictable behavior
- Controlled updates
- Easier rollback

**Cons:**
- Manual version updates required
- May miss security patches

---

## 🔄 Update Strategy

### **Check for Updates**
```bash
# Check current versions
docker-compose images

# Pull latest versions
docker-compose pull

# Rebuild custom images
docker-compose build metabase-init
```

### **Update Process**
1. **Backup data:**
   ```bash
   docker exec btrc-v3-timescaledb pg_dump -U btrc_admin -d btrc_qos_poc > backup.sql
   docker exec btrc-v3-timescaledb pg_dump -U btrc_admin -d metabase_meta > metabase_backup.sql
   ```

2. **Update docker-compose.yml:**
   ```yaml
   # Change version tags
   image: metabase/metabase:v0.59.0  # New version
   ```

3. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Verify:**
   ```bash
   docker-compose ps
   docker-compose logs -f metabase
   ```

---

## ⚠️ Breaking Changes to Watch

### **Metabase Updates**
- v0.48+: New permission system
- v0.50+: API changes
- v0.52+: PostgreSQL 12+ required for metadata DB

### **TimescaleDB Updates**
- Major version changes may require dump/restore
- Check TimescaleDB upgrade docs before PG version upgrade

### **Python Dependencies**
- requests 2.x → 3.x (major breaking changes expected)
- Always test in development first

---

## 🧪 Testing Version Compatibility

### **Before Updating**
```bash
# Test in separate environment
docker-compose -f docker-compose.test.yml up

# Run test queries
docker exec btrc-v3-metabase curl -f http://localhost:3000/api/health

# Check logs
docker-compose logs --tail=100 metabase
```

### **After Updating**
1. Check dashboards load correctly
2. Test user permissions
3. Verify queries run successfully
4. Test filters and drill-downs
5. Check public sharing links

---

## 📊 Current Versions (Running System)

To check running versions:

```bash
# Metabase version
docker exec btrc-v3-metabase cat /app/metabase.jar | head -c 100

# Or via API
curl http://localhost:3000/api/session/properties | jq '.version'

# PostgreSQL version
docker exec btrc-v3-timescaledb psql -U btrc_admin -c "SELECT version();"

# Nginx version
docker exec btrc-v3-nginx nginx -v

# Python version (init container)
docker run --rm btrc-v3-metabase-init python --version
```

---

## 🔐 Security Considerations

### **Keep Updated**
- Security patches released regularly
- Subscribe to security mailing lists:
  - Metabase: https://github.com/metabase/metabase/security/advisories
  - PostgreSQL: https://www.postgresql.org/support/security/
  - Nginx: https://nginx.org/en/security_advisories.html

### **Version Pinning for Security**
```yaml
# Pin to patch versions only
image: metabase/metabase:v0.58.5  # Good
image: metabase/metabase:v0.58    # Better (auto patch updates)
image: metabase/metabase:latest   # Risky (unexpected changes)
```

---

## 📞 Support Resources

### **Version Documentation**
- **Metabase:** https://www.metabase.com/docs/latest/
- **TimescaleDB:** https://docs.timescale.com/
- **Nginx:** https://nginx.org/en/docs/
- **Python:** https://docs.python.org/3.10/

### **Release Notes**
- **Metabase:** https://github.com/metabase/metabase/releases
- **TimescaleDB:** https://github.com/timescale/timescaledb/releases

---

**Document Version:** 1.0
**Maintained By:** BTRC Technical Team
