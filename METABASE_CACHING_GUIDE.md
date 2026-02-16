# Metabase Caching System - Complete Guide

**Version:** Metabase v0.58.5.2
**Last Updated:** 2026-02-16

---

## 📋 Table of Contents

1. [Caching Overview](#caching-overview)
2. [Built-in Query Caching (Free)](#built-in-query-caching-free)
3. [Redis Caching (Recommended)](#redis-caching-recommended)
4. [Database-Level Caching](#database-level-caching)
5. [Dashboard Auto-Refresh](#dashboard-auto-refresh)
6. [Caching Strategies](#caching-strategies)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## 🎯 Caching Overview

### **What is Caching?**
Caching stores query results temporarily to avoid re-executing expensive database queries, improving dashboard load times significantly.

### **Current Setup**
- **Caching:** Default (built-in, in-memory)
- **Location:** Metabase application memory
- **TTL:** 24 hours (configurable)
- **Performance:** Good for small deployments

### **Why Add Caching?**
✅ **Faster dashboard loads** (from seconds to milliseconds)
✅ **Reduced database load** (fewer queries)
✅ **Better user experience** (instant responses)
✅ **Cost savings** (less compute resources)

### **Cache Types in Metabase**

1. **Query Result Cache** - Stores SQL query results
2. **Dashboard Cache** - Stores entire dashboard data
3. **Question Cache** - Stores individual question results
4. **Session Cache** - Stores user session data

---

## 1️⃣ Built-in Query Caching (Free)

### **Overview**
Metabase includes built-in in-memory caching. No external dependencies required.

### **How It Works**
1. User loads dashboard
2. Metabase executes SQL queries
3. Results stored in application memory
4. Subsequent loads use cached data (if not expired)
5. Cache expires after TTL (default: 24 hours)

### **Configuration**

#### **A. Enable Caching (Already On by Default)**

Check status via API:
```bash
curl http://localhost:3000/api/session/properties \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  | jq '.["enable-query-caching"]'
```

#### **B. Set Cache Duration**

Configure via environment variables:
```yaml
# docker-compose.yml
services:
  metabase:
    environment:
      # Enable query caching (default: true)
      MB_ENABLE_QUERY_CACHING: true

      # Default cache TTL in hours (default: 24)
      MB_QUERY_CACHING_TTL_RATIO: 24

      # Minimum cache TTL in seconds (default: 60)
      MB_QUERY_CACHING_MIN_TTL: 60

      # Maximum cache TTL in seconds (default: 100 days)
      MB_QUERY_CACHING_MAX_TTL: 8640000
```

#### **C. Configure Per-Question Caching**

**Via Web UI:**
1. Open any question/chart
2. Click ⚙️ (settings) icon
3. Scroll to "Cache configuration"
4. Set cache duration:
   - Use instance default
   - Custom duration (minutes/hours/days)
   - Don't cache
5. Save

**Via API:**
```bash
curl -X PUT http://localhost:3000/api/card/76 \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cache_ttl": 3600
  }'
```

### **Cache TTL Examples**

```yaml
# Quick-changing data (refresh every 5 minutes)
MB_QUERY_CACHING_TTL_RATIO: 0.083  # 5 minutes

# Hourly data
MB_QUERY_CACHING_TTL_RATIO: 1  # 1 hour

# Daily reports
MB_QUERY_CACHING_TTL_RATIO: 24  # 24 hours

# Static/historical data
MB_QUERY_CACHING_TTL_RATIO: 168  # 7 days
```

### **Pros & Cons**

✅ **Pros:**
- Free
- No setup required
- Works out of the box
- Simple configuration

❌ **Cons:**
- Limited to application memory
- Lost on container restart
- Not shared across instances
- No persistence

---

## 2️⃣ Redis Caching (Recommended)

### **Overview**
Redis provides persistent, distributed caching with better performance and reliability.

### **Benefits**
✅ Survives container restarts
✅ Shared across multiple Metabase instances
✅ Better memory management
✅ Faster cache lookup
✅ Production-ready

### **Setup Steps**

#### **Step 1: Add Redis to docker-compose.yml**

```yaml
services:
  # Existing services...
  timescaledb:
    # ... existing config ...

  metabase:
    # ... existing config ...
    environment:
      # Add Redis caching
      MB_ENABLE_QUERY_CACHING: true
      MB_REDIS_URI: redis://redis:6379/0
    depends_on:
      - timescaledb
      - redis

  nginx:
    # ... existing config ...

  # Add Redis service
  redis:
    image: redis:7-alpine
    container_name: btrc-v3-redis
    restart: unless-stopped
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - btrc-v3

volumes:
  timescale_data:
  metabase_data:
  redis_data:  # Add this

networks:
  btrc-v3:
    driver: bridge
```

#### **Step 2: Configure Redis Settings**

**Basic Configuration:**
```yaml
metabase:
  environment:
    # Redis connection
    MB_REDIS_URI: redis://redis:6379/0

    # Cache settings
    MB_ENABLE_QUERY_CACHING: true
    MB_QUERY_CACHING_TTL_RATIO: 24
```

**Advanced Configuration:**
```yaml
metabase:
  environment:
    # Redis with authentication
    MB_REDIS_URI: redis://:password@redis:6379/0

    # Redis connection pool
    MB_REDIS_POOL_SIZE: 10

    # Cache behavior
    MB_ENABLE_QUERY_CACHING: true
    MB_QUERY_CACHING_TTL_RATIO: 24
    MB_QUERY_CACHING_MIN_TTL: 60
    MB_QUERY_CACHING_MAX_TTL: 8640000
```

#### **Step 3: Redis with Password (Recommended)**

**1. Create redis.conf:**
```bash
# redis.conf
bind 0.0.0.0
protected-mode yes
requirepass YourStrongRedisPassword123!
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

**2. Update docker-compose.yml:**
```yaml
redis:
  image: redis:7-alpine
  container_name: btrc-v3-redis
  restart: unless-stopped
  command: redis-server /usr/local/etc/redis/redis.conf
  volumes:
    - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
    - redis_data:/data
  ports:
    - "6379:6379"
  networks:
    - btrc-v3

metabase:
  environment:
    MB_REDIS_URI: redis://:YourStrongRedisPassword123!@redis:6379/0
```

#### **Step 4: Start Services**

```bash
# Restart with Redis
docker-compose down
docker-compose up -d

# Verify Redis is running
docker exec btrc-v3-redis redis-cli ping
# Should return: PONG

# Check Metabase logs
docker logs btrc-v3-metabase | grep -i redis
```

#### **Step 5: Verify Caching**

```bash
# Check Redis keys
docker exec btrc-v3-redis redis-cli KEYS "*"

# Monitor Redis in real-time
docker exec -it btrc-v3-redis redis-cli MONITOR

# Check cache statistics
docker exec btrc-v3-redis redis-cli INFO stats
```

### **Redis Memory Management**

**Configure Memory Limit:**
```yaml
redis:
  command: >
    redis-server
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
```

**Memory Policies:**
- `allkeys-lru` - Evict least recently used keys (Recommended)
- `volatile-lru` - Evict expiring keys only
- `allkeys-random` - Evict random keys
- `volatile-ttl` - Evict keys with nearest expiration

**Recommended Sizes:**
- Small deployment: 256MB
- Medium deployment: 512MB (BTRC)
- Large deployment: 1-2GB

### **Pros & Cons**

✅ **Pros:**
- Persistent cache
- Survives restarts
- Scalable
- Battle-tested
- Free (open-source)

❌ **Cons:**
- Additional service to manage
- Requires more resources
- Slightly more complex setup

---

## 3️⃣ Database-Level Caching

### **TimescaleDB Continuous Aggregates**

Use TimescaleDB's built-in caching for time-series data:

```sql
-- Create materialized view for hourly averages
CREATE MATERIALIZED VIEW qos_hourly_avg
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS hour,
    isp_id,
    pop_id,
    AVG(target_download) AS avg_download,
    AVG(target_upload) AS avg_upload,
    AVG(service_availability) AS avg_availability
FROM ts_qos_measurements
GROUP BY hour, isp_id, pop_id;

-- Refresh policy (automatic)
SELECT add_continuous_aggregate_policy('qos_hourly_avg',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

**Benefits:**
- Pre-computed aggregations
- Near-instant query response
- Automatic refresh
- Reduces query complexity

### **PostgreSQL Query Result Caching**

PostgreSQL caches query results automatically:
- Shared buffers (RAM)
- OS page cache
- Disk cache

**Optimize:**
```sql
-- Increase shared buffers (in postgresql.conf)
shared_buffers = 1GB

-- Increase effective cache size
effective_cache_size = 4GB
```

---

## 4️⃣ Dashboard Auto-Refresh

### **Configure Auto-Refresh**

**Per Dashboard:**
1. Open dashboard
2. Click ⚙️ (settings)
3. Enable "Auto-refresh"
4. Set interval (1 min, 5 min, 10 min, etc.)
5. Save

**Via API:**
```bash
curl -X PUT http://localhost:3000/api/dashboard/6 \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": [],
    "auto_apply_filters": true,
    "cache_ttl": 300,
    "enable_embedding": true
  }'
```

### **Smart Auto-Refresh Strategy**

**Real-time monitoring dashboards:**
- Auto-refresh: 1-5 minutes
- Cache TTL: 1 minute
- Use: Alerts, incidents, live metrics

**Executive dashboards:**
- Auto-refresh: 15-30 minutes
- Cache TTL: 1 hour
- Use: High-level KPIs, trends

**Historical reports:**
- Auto-refresh: Off
- Cache TTL: 24 hours
- Use: Monthly reports, compliance

---

## 5️⃣ Caching Strategies

### **Strategy 1: Hot Data (Real-time)**

For data that changes frequently:
```yaml
# Low cache TTL
MB_QUERY_CACHING_MIN_TTL: 60  # 1 minute
MB_QUERY_CACHING_TTL_RATIO: 0.25  # 15 minutes

# Fast refresh
Auto-refresh: 5 minutes
```

**Use for:**
- Real-time alerts (R1.5)
- Current incidents (R1.6)
- Live metrics

### **Strategy 2: Warm Data (Hourly/Daily)**

For data that updates periodically:
```yaml
# Medium cache TTL
MB_QUERY_CACHING_MIN_TTL: 300  # 5 minutes
MB_QUERY_CACHING_TTL_RATIO: 1  # 1 hour

# Moderate refresh
Auto-refresh: 15-30 minutes
```

**Use for:**
- Performance scorecards
- Compliance status
- Regional analysis

### **Strategy 3: Cold Data (Historical)**

For data that rarely changes:
```yaml
# High cache TTL
MB_QUERY_CACHING_MIN_TTL: 3600  # 1 hour
MB_QUERY_CACHING_TTL_RATIO: 168  # 7 days

# No auto-refresh
Auto-refresh: Off
```

**Use for:**
- Monthly reports
- Historical trends
- Archived data

### **BTRC Dashboard Caching Strategy**

**Executive Dashboard (ID: 5)**
```
E1.1-E1.3 (KPIs):         Cache 1 hour,  Auto-refresh 15 min
E1.5 (Trends):            Cache 24 hours, No refresh
E2.1-E2.2 (Maps/Tables):  Cache 1 hour,  Auto-refresh 30 min
E3.1-E3.5 (Compliance):   Cache 1 hour,  Auto-refresh 15 min
```

**Regulatory Dashboard (ID: 6)**
```
R1.1-R1.3 (Status Cards): Cache 5 min,   Auto-refresh 5 min
R1.4 (Compliance Matrix): Cache 1 hour,  Auto-refresh 30 min
R1.5 (Alerts):            Cache 1 min,   Auto-refresh 2 min
R1.6 (Incidents):         Cache 1 min,   Auto-refresh 2 min
R2.1-R2.4 (Regional):     Cache 1 hour,  Auto-refresh 30 min
R3.1-R3.6 (Violations):   Cache 15 min,  Auto-refresh 10 min
```

---

## 6️⃣ Performance Optimization

### **1. Optimize SQL Queries**

**Before (Slow):**
```sql
SELECT * FROM ts_qos_measurements
WHERE timestamp > NOW() - INTERVAL '30 days';
```

**After (Fast):**
```sql
-- Use indexes
CREATE INDEX idx_qos_timestamp ON ts_qos_measurements(timestamp DESC);

-- Use TimescaleDB time_bucket
SELECT
    time_bucket('1 hour', timestamp) AS hour,
    AVG(target_download) AS avg_download
FROM ts_qos_measurements
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY hour;
```

### **2. Use Materialized Views**

```sql
-- Pre-compute expensive aggregations
CREATE MATERIALIZED VIEW daily_isp_performance AS
SELECT
    DATE(timestamp) AS date,
    isp_id,
    AVG(target_download) AS avg_download,
    AVG(target_upload) AS avg_upload,
    COUNT(*) AS measurement_count
FROM ts_qos_measurements
GROUP BY date, isp_id;

-- Refresh daily
REFRESH MATERIALIZED VIEW daily_isp_performance;
```

### **3. Enable Query Folding**

Metabase can push aggregations to database:
- Use native SQL queries
- Enable "Use cached results" in questions
- Avoid sub-queries when possible

### **4. Database Connection Pooling**

```yaml
metabase:
  environment:
    # Increase max connections
    MB_DB_MAX_CONNECTIONS: 20

    # Connection timeout
    MB_DB_CONNECTION_TIMEOUT: 10000
```

### **5. Compress Dashboard Payloads**

```yaml
metabase:
  environment:
    # Enable gzip compression
    MB_JETTY_MIN_THREADS: 20
    MB_JETTY_MAX_THREADS: 100
```

---

## 7️⃣ Monitoring & Troubleshooting

### **Monitor Cache Performance**

#### **Check Cache Hit Rate**

```bash
# Via Metabase API
curl http://localhost:3000/api/session/properties \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  | jq '.cache'
```

#### **Monitor Redis (If using)**

```bash
# Connect to Redis
docker exec -it btrc-v3-redis redis-cli

# Check stats
INFO stats

# Monitor commands in real-time
MONITOR

# Check memory usage
INFO memory

# Check cache keys
KEYS metabase*
```

#### **Key Metrics to Monitor**

```bash
# Redis CLI
redis-cli INFO stats | grep -E 'keyspace_hits|keyspace_misses'

# Calculate hit rate
Hit Rate = keyspace_hits / (keyspace_hits + keyspace_misses) * 100
```

**Target:** 80%+ hit rate

### **Clear Cache**

#### **Clear All Cache (UI)**
1. Admin Settings → Troubleshooting
2. Click "Clear cache"
3. Confirm

#### **Clear Cache (API)**
```bash
curl -X POST http://localhost:3000/api/cache/clear \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

#### **Clear Redis Cache**
```bash
# Clear all Metabase cache keys
docker exec btrc-v3-redis redis-cli KEYS "metabase*" | xargs docker exec btrc-v3-redis redis-cli DEL

# Or flush entire Redis database
docker exec btrc-v3-redis redis-cli FLUSHDB
```

#### **Clear Single Question Cache**
```bash
curl -X POST http://localhost:3000/api/card/76/query/clear_cache \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

### **Troubleshooting**

#### **Problem: Cache not working**

**Check:**
```bash
# 1. Verify caching is enabled
curl http://localhost:3000/api/session/properties | jq '.["enable-query-caching"]'

# 2. Check Redis connection (if using)
docker logs btrc-v3-metabase | grep -i redis

# 3. Test Redis
docker exec btrc-v3-redis redis-cli ping
```

#### **Problem: Stale data showing**

**Solution:**
```bash
# Clear cache for specific dashboard
curl -X POST http://localhost:3000/api/dashboard/6/cache/clear \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"

# Or reduce cache TTL
# Update question settings to lower cache duration
```

#### **Problem: High memory usage**

**Solution:**
```bash
# Reduce Redis max memory
docker exec btrc-v3-redis redis-cli CONFIG SET maxmemory 256mb

# Change eviction policy
docker exec btrc-v3-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### **Problem: Slow dashboard loads despite caching**

**Check:**
1. Query execution time (not cache issue)
2. Network latency
3. Dashboard complexity (too many cards)
4. Database performance

**Optimize:**
- Add database indexes
- Use materialized views
- Reduce cards per dashboard
- Optimize SQL queries

---

## 📊 Performance Comparison

### **Before Caching**
```
Dashboard Load Time: 15-30 seconds
Database Load: High (40 queries)
Concurrent Users: 5-10
Response Time: Variable
```

### **After Built-in Caching**
```
Dashboard Load Time: 5-10 seconds (first load), <1 second (cached)
Database Load: Medium (queries cached)
Concurrent Users: 20-30
Response Time: Consistent
```

### **After Redis Caching**
```
Dashboard Load Time: 3-5 seconds (first load), <500ms (cached)
Database Load: Low (most queries cached)
Concurrent Users: 50-100+
Response Time: Very consistent
```

### **After Full Optimization**
```
Dashboard Load Time: 1-2 seconds (first load), <200ms (cached)
Database Load: Minimal
Concurrent Users: 100+
Response Time: Excellent
```

---

## 🚀 Recommended Setup for BTRC

### **Phase 1: Enable Built-in Caching (Immediate)**

```yaml
# docker-compose.yml
metabase:
  environment:
    MB_ENABLE_QUERY_CACHING: true
    MB_QUERY_CACHING_TTL_RATIO: 1  # 1 hour default
```

**Status:** Already enabled by default ✅

---

### **Phase 2: Add Redis (Recommended)**

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    container_name: btrc-v3-redis
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - btrc-v3

  metabase:
    environment:
      MB_REDIS_URI: redis://redis:6379/0
      MB_ENABLE_QUERY_CACHING: true
    depends_on:
      - redis

volumes:
  redis_data:
```

**Benefit:** 50-70% faster dashboard loads

---

### **Phase 3: Optimize Queries (As needed)**

- Add database indexes
- Create materialized views for expensive queries
- Use TimescaleDB continuous aggregates

**Benefit:** 80-90% reduction in query execution time

---

## 📝 Implementation Script

Create `enable_redis_caching.sh`:

```bash
#!/bin/bash
# Enable Redis caching for Metabase

echo "Adding Redis to docker-compose.yml..."

# Backup current file
cp docker-compose.yml docker-compose.yml.backup

# Add Redis service (manual edit required)
echo "
Please add the following to your docker-compose.yml:

services:
  redis:
    image: redis:7-alpine
    container_name: btrc-v3-redis
    restart: unless-stopped
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - \"6379:6379\"
    volumes:
      - redis_data:/data
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - btrc-v3

  metabase:
    environment:
      MB_REDIS_URI: redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
"

echo "
After editing, run:
  docker-compose up -d

Verify:
  docker exec btrc-v3-redis redis-cli ping
  docker logs btrc-v3-metabase | grep -i redis
"
```

---

## 📞 Support

### **Metabase Documentation**
- Caching: https://www.metabase.com/docs/latest/configuring-metabase/caching
- Performance: https://www.metabase.com/docs/latest/administration-guide/performance

### **Redis Documentation**
- Redis: https://redis.io/documentation
- Docker: https://hub.docker.com/_/redis

---

**Document Version:** 1.0
**Last Updated:** 2026-02-16
**Maintained By:** BTRC Technical Team
