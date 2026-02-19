# Troubleshooting Guide

Complete guide to diagnosing and fixing common issues in the BTRC QoS Dashboard.

## Table of Contents
1. [Docker Issues](#docker-issues)
2. [React/Vite Issues](#reactvite-issues)
3. [Metabase Issues](#metabase-issues)
4. [Database Issues](#database-issues)
5. [Network Issues](#network-issues)
6. [Performance Issues](#performance-issues)
7. [Deployment Issues](#deployment-issues)
8. [Common Error Messages](#common-error-messages)

---

## Docker Issues

### Issue 1: Container Won't Start

**Symptoms**:
```bash
docker compose up -d
# Error: Container btrc-v3-react-regional exited with code 1
```

**Diagnosis**:
```bash
# Check container logs
docker compose logs react-regional

# Check Docker daemon status
sudo systemctl status docker

# Check available disk space
df -h

# Check memory usage
free -h
```

**Solutions**:

**A. Port Already in Use**
```bash
# Find process using port 5173
sudo lsof -i :5173

# Kill process
sudo kill -9 <PID>

# Or change port in vite.config.js
server: {
  port: 5174,  # Use different port
}
```

**B. Out of Disk Space**
```bash
# Remove unused Docker images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune
```

**C. Memory Limit**
```bash
# Increase Docker memory (Docker Desktop)
# Settings → Resources → Memory → 8GB

# Or add to docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

---

### Issue 2: Container is Unhealthy

**Symptoms**:
```bash
docker compose ps
# btrc-v3-metabase    Up (unhealthy)
```

**Diagnosis**:
```bash
# Check health check logs
docker inspect btrc-v3-metabase --format='{{json .State.Health}}' | jq

# Check container logs
docker compose logs metabase | tail -100
```

**Solutions**:

**A. Service Not Ready Yet**
```bash
# Wait for service to start (Metabase takes ~2 min)
docker compose logs -f metabase

# Look for: "Metabase Initialization COMPLETE"
```

**B. Database Connection Failed**
```bash
# Check if TimescaleDB is healthy
docker compose ps

# Restart dependent service
docker compose restart metabase
```

**C. Custom Health Check Failing**
```bash
# Test health check manually
docker compose exec metabase curl -f http://localhost:3000/api/health

# If fails, check Metabase logs for errors
```

---

### Issue 3: Hot Reload Not Working

**Symptoms**:
- Edit `.jsx` file
- Save file
- Browser doesn't update

**Solutions**:

**A. Enable Polling (Docker)**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    watch: {
      usePolling: true,  // Required for Docker
      interval: 1000,    # Check every 1 second
    },
  },
})
```

**B. Check Volume Mounts**
```yaml
# docker-compose.yml
volumes:
  - ./btrc-react-regional/src:/app/src  # ✅ Correct
  # NOT:
  - ./btrc-react-regional/src:/app/src:ro  # ❌ Read-only breaks HMR
```

**C. Restart Dev Server**
```bash
# Inside container
docker compose restart react-regional

# Or restart Vite
docker compose exec react-regional yarn run dev
```

---

## React/Vite Issues

### Issue 1: Module Not Found

**Error**:
```
Error: Cannot find module 'antd'
```

**Solutions**:

**A. Install Missing Package**
```bash
cd btrc-react-regional
yarn add antd

# Or reinstall all
rm -rf node_modules yarn.lock
yarn install
```

**B. Check Import Path**
```javascript
// ❌ Wrong
import { Card } from 'ant-design';

// ✅ Correct
import { Card } from 'antd';
```

**C. Clear Vite Cache**
```bash
rm -rf node_modules/.vite
yarn run dev
```

---

### Issue 2: White Screen / Blank Page

**Symptoms**:
- Browser shows blank page
- No errors in console

**Diagnosis**:
```bash
# Check browser console (F12)
# Look for JavaScript errors

# Check network tab
# Look for failed requests (red)

# Check React DevTools
# Install React DevTools extension
# Check component tree
```

**Solutions**:

**A. JavaScript Error**
```javascript
// Check console for errors like:
// "Uncaught ReferenceError: loading81 is not defined"

// Fix: Remove or define the variable
const loading81 = false;  // Add missing variable
```

**B. API Error**
```javascript
// If API fails, component may not render
// Add error boundary:

class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

// Wrap app
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

**C. Routing Issue**
```javascript
// Check router configuration
// Ensure route matches URL

// App.jsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/sla" element={<SLAMonitoring />} />
  {/* Add missing routes */}
</Routes>
```

---

### Issue 3: Slow Build/Reload

**Symptoms**:
- Vite takes >10 seconds to start
- File changes take >5 seconds to reflect

**Solutions**:

**A. Optimize Dependencies**
```javascript
// vite.config.js
export default defineConfig({
  optimizeDeps: {
    include: ['react', 'react-dom', 'antd', 'echarts'],
  },
})
```

**B. Reduce File Watching**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    watch: {
      ignored: ['**/node_modules/**', '**/dist/**'],
    },
  },
})
```

**C. Clear Cache**
```bash
rm -rf node_modules/.vite
rm -rf dist
yarn run dev
```

---

### Issue 4: Node Version Mismatch

**Error**:
```
Vite requires Node.js version 20.19+ or 22.12+
You are using Node.js 22.5.1
```

**Solution**:
```bash
# Install correct Node.js version
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs=22.12.*

# Verify
node --version  # Should be 22.12+

# Or use nvm (Node Version Manager)
nvm install 22.12
nvm use 22.12
```

---

## Metabase Issues

### Issue 1: Cannot Login to Metabase

**Error**:
- "Incorrect username or password"

**Solutions**:

**A. Check Credentials**
```bash
# Default credentials:
Email: alamin.technometrics22@gmail.com
Password: Test@123

# Or check .env file
cat .env | grep METABASE
```

**B. Reset Password**
```bash
# Reset admin password via database
docker compose exec timescaledb psql -U btrc_admin -d metabase_meta

# Run SQL:
UPDATE core_user
SET password = '$2a$10$...new_hash...'
WHERE email = 'alamin.technometrics22@gmail.com';
```

**C. Create New Admin User**
```bash
# Via Metabase CLI
docker compose exec metabase java -jar metabase.jar reset-password admin@btrc.gov.bd
```

---

### Issue 2: Metabase Card Query Failed

**Error**:
```json
{
  "status": "failed",
  "error": "Column 'download_speed_mbps' not found"
}
```

**Solutions**:

**A. Check Table Schema**
```bash
# Connect to database
docker compose exec timescaledb psql -U btrc_admin -d btrc_qos_poc

# List tables
\dt

# Describe table
\d ts_qos_measurements

# Check column names
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'ts_qos_measurements';
```

**B. Fix SQL Query**
```sql
-- ❌ Wrong column name
SELECT download_speed FROM ts_qos_measurements;

-- ✅ Correct
SELECT download_speed_mbps FROM ts_qos_measurements;
```

**C. Sync Database Schema**
```bash
# In Metabase:
# 1. Admin → Databases
# 2. Click "BTRC QoS POC"
# 3. Click "Sync database schema now"
# 4. Wait for sync to complete
```

---

### Issue 3: Template Tags Not Working

**Symptoms**:
- Filters don't apply to query
- Data doesn't change when filter selected

**Solutions**:

**A. Check Template Tag Format**
```sql
-- ❌ Wrong: Missing brackets
SELECT * FROM table WHERE division = {{division}};

-- ✅ Correct: Optional clause
SELECT * FROM table WHERE 1=1 [[ AND division = {{division}} ]];
```

**B. Check Parameter Name Match**
```javascript
// React code sends:
{
  target: ['variable', ['template-tag', 'division']],
  value: 'Dhaka'
}

// SQL template tag must be named exactly: {{division}}
// NOT: {{Division}} or {{div}}
```

**C. Check Parameter Type**
```javascript
// Text parameter
{
  type: 'category',  // For text values
  target: ['variable', ['template-tag', 'division']],
  value: 'Dhaka'
}

// Number parameter
{
  type: 'number',
  target: ['variable', ['template-tag', 'threshold']],
  value: 90
}
```

---

### Issue 4: Session Expired

**Error**:
```json
{
  "status": 401,
  "message": "Unauthenticated"
}
```

**Solution**:
```javascript
// Implement auto-retry with re-login

const fetchWithRetry = async (cardId, parameters) => {
  try {
    return await fetchCardData(cardId, parameters);
  } catch (error) {
    if (error.response?.status === 401) {
      // Session expired - re-login
      localStorage.removeItem('metabase_session');

      const email = import.meta.env.VITE_METABASE_EMAIL;
      const password = import.meta.env.VITE_METABASE_PASSWORD;

      await login(email, password);

      // Retry request
      return await fetchCardData(cardId, parameters);
    }
    throw error;
  }
};
```

---

## Database Issues

### Issue 1: Cannot Connect to Database

**Error**:
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5433 failed
```

**Solutions**:

**A. Check Container Status**
```bash
# Is TimescaleDB running?
docker compose ps | grep timescaledb

# Check logs
docker compose logs timescaledb | tail -50
```

**B. Check Port Mapping**
```bash
# Verify port 5433 is exposed
docker compose ps

# Should show: 0.0.0.0:5433->5432/tcp

# If port conflict, change in docker-compose.yml:
ports:
  - "5434:5432"  # Use different external port
```

**C. Check Firewall**
```bash
# Allow port 5433
sudo ufw allow 5433/tcp

# Check if port is listening
sudo netstat -tlnp | grep 5433
```

---

### Issue 2: Database Out of Space

**Error**:
```
ERROR: could not extend file: No space left on device
```

**Solutions**:

**A. Check Disk Usage**
```bash
# Check available space
df -h

# Check Docker volume sizes
docker system df -v
```

**B. Clean Up Data**
```sql
-- Connect to database
docker compose exec timescaledb psql -U btrc_admin -d btrc_qos_poc

-- Delete old data
DELETE FROM ts_qos_measurements
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Vacuum to reclaim space
VACUUM FULL ts_qos_measurements;
```

**C. Increase Volume Size**
```bash
# Backup data first
docker compose exec timescaledb pg_dump -U btrc_admin btrc_qos_poc > backup.sql

# Remove volume and recreate
docker compose down -v
docker compose up -d

# Restore data
cat backup.sql | docker compose exec -T timescaledb psql -U btrc_admin btrc_qos_poc
```

---

### Issue 3: Slow Queries

**Symptoms**:
- Dashboard takes >5 seconds to load
- Metabase queries timeout

**Solutions**:

**A. Add Indexes**
```sql
-- Connect to database
docker compose exec timescaledb psql -U btrc_admin -d btrc_qos_poc

-- Create indexes on frequently queried columns
CREATE INDEX IF NOT EXISTS idx_measurements_timestamp
  ON ts_qos_measurements(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_measurements_division
  ON ts_qos_measurements(division);

CREATE INDEX IF NOT EXISTS idx_measurements_district
  ON ts_qos_measurements(district);

CREATE INDEX IF NOT EXISTS idx_measurements_isp
  ON ts_qos_measurements(isp_name);

-- Composite index for common filters
CREATE INDEX IF NOT EXISTS idx_measurements_div_dist_time
  ON ts_qos_measurements(division, district, timestamp DESC);

-- Analyze tables
ANALYZE ts_qos_measurements;
```

**B. Optimize Queries**
```sql
-- ❌ Slow: Full table scan
SELECT * FROM ts_qos_measurements;

-- ✅ Fast: Filter first, select only needed columns
SELECT division, AVG(download_speed_mbps) AS avg_download
FROM ts_qos_measurements
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY division;
```

**C. Enable Query Caching**
```bash
# In Metabase:
# 1. Admin → Settings → Caching
# 2. Enable "Cache results of queries"
# 3. Set TTL to 3600 seconds (1 hour)
```

---

## Network Issues

### Issue 1: CORS Error

**Error**:
```
Access to XMLHttpRequest at 'http://localhost:3000/api/card/76/query'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solutions**:

**A. Configure Metabase CORS**
```yaml
# docker-compose.yml
metabase:
  environment:
    MB_EMBEDDING_APP_ORIGIN: "http://localhost:5173,http://localhost:5180"
```

**B. Use Nginx Reverse Proxy**
```nginx
# nginx.conf
location /api/ {
    proxy_pass http://localhost:3000/api/;
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
}
```

**C. Proxy via Vite**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})
```

---

### Issue 2: API Timeout

**Error**:
```
Error: timeout of 30000ms exceeded
```

**Solutions**:

**A. Increase Timeout**
```javascript
// src/api/metabase.js
const metabaseApi = axios.create({
  baseURL: METABASE_URL,
  timeout: 60000,  // 60 seconds
});
```

**B. Optimize Query**
```sql
-- Add LIMIT to reduce data transfer
SELECT * FROM ts_qos_measurements
WHERE timestamp >= NOW() - INTERVAL '7 days'
LIMIT 10000;

-- Or add pagination
OFFSET 0 LIMIT 1000;
```

**C. Add Loading Indicator**
```javascript
// Show loading state for long queries
const [loading, setLoading] = useState(true);

useEffect(() => {
  const timer = setTimeout(() => {
    if (loading) {
      message.warning('This query is taking longer than usual...');
    }
  }, 5000);

  return () => clearTimeout(timer);
}, [loading]);
```

---

### Issue 3: Cannot Access Dashboard from Other Devices

**Symptoms**:
- Dashboard works on localhost
- Cannot access from other device on network (e.g., phone, tablet)

**Solutions**:

**A. Use Network IP**
```bash
# Find your local IP
ip addr show | grep 'inet '

# Access dashboard at:
# http://192.168.1.100:5173  (replace with your IP)
```

**B. Configure Vite Host**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    host: '0.0.0.0',  // Listen on all interfaces
    port: 5173,
  },
})
```

**C. Configure Firewall**
```bash
# Allow port 5173
sudo ufw allow 5173/tcp

# Or disable firewall temporarily (for testing only!)
sudo ufw disable
```

---

## Performance Issues

### Issue 1: Dashboard Loads Slowly

**Symptoms**:
- Initial page load >5 seconds
- Charts render slowly

**Solutions**:

**A. Code Splitting**
```javascript
// App.jsx - Lazy load pages
import { lazy, Suspense } from 'react';

const RegionalAnalysis = lazy(() => import('./pages/RegionalAnalysis'));

function App() {
  return (
    <Suspense fallback={<Spin size="large" />}>
      <Routes>
        <Route path="/regional" element={<RegionalAnalysis />} />
      </Routes>
    </Suspense>
  );
}
```

**B. Memoize Expensive Calculations**
```javascript
// Use React.useMemo for expensive transformations
const processedData = React.useMemo(() => {
  return data?.rows?.map(row => ({
    key: row[0],
    value: calculateExpensiveValue(row),
  }));
}, [data]);  // Only recalculate when data changes
```

**C. Optimize Images**
```bash
# Compress images
npm install -g imageoptim-cli
imageoptim public/**/*.png

# Use WebP format
cwebp input.png -o output.webp
```

**D. Enable Compression**
```nginx
# nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1024;
```

---

### Issue 2: High Memory Usage

**Symptoms**:
- Browser tab uses >500MB RAM
- Browser becomes slow/unresponsive

**Solutions**:

**A. Fix Memory Leaks**
```javascript
// Always cleanup in useEffect
useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 5000);

  // Cleanup on unmount
  return () => clearInterval(interval);
}, []);
```

**B. Limit Data**
```sql
-- Don't fetch all rows
SELECT * FROM table LIMIT 1000;

-- Or use pagination
SELECT * FROM table
OFFSET {{offset}} LIMIT {{page_size}};
```

**C. Use Virtualization**
```javascript
// For large tables, use react-window
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={data.length}
  itemSize={50}
>
  {({ index, style }) => (
    <div style={style}>{data[index]}</div>
  )}
</FixedSizeList>
```

---

## Deployment Issues

### Issue 1: Production Build Fails

**Error**:
```
yarn build
ERROR: Cannot read property 'map' of undefined
```

**Solutions**:

**A. Check for Undefined Data**
```javascript
// ❌ Crashes if data is null
const values = data.rows.map(row => row[0]);

// ✅ Safe with optional chaining
const values = data?.rows?.map(row => row[0]) || [];
```

**B. Set NODE_ENV**
```bash
# Build with production environment
NODE_ENV=production yarn build
```

**C. Check Build Logs**
```bash
# Build with verbose output
yarn build --logLevel verbose

# Check for warnings
yarn build 2>&1 | grep -i warning
```

---

### Issue 2: Production Site Shows 404

**Symptoms**:
- Build succeeds
- Accessing site shows "404 Not Found"

**Solutions**:

**A. Check Nginx Configuration**
```nginx
# nginx.conf
root /usr/share/nginx/html;

location / {
    try_files $uri $uri/ /index.html;  # SPA fallback
}
```

**B. Verify Build Output**
```bash
# Check dist/ directory exists
ls -la dist/

# Should contain:
# - index.html
# - assets/
```

**C. Check Base URL**
```javascript
// vite.config.js
export default defineConfig({
  base: '/',  // Use '/' for root deployment
  // OR
  base: '/dashboard/',  // For subdirectory deployment
})
```

---

## Common Error Messages

### Error: "loading81 is not defined"

**File**: SLAMonitoring.jsx:31

**Cause**: Reference to undefined variable

**Fix**:
```javascript
// Line 31: Remove loading81
const dataLoading = loading76 || loading77 || loading78 || loading79 || loading80;
// NOT: || loading81
```

---

### Error: "Cannot read property 'rows' of undefined"

**Cause**: Data not loaded yet

**Fix**:
```javascript
// ❌ Wrong
const value = data.rows[0][0];

// ✅ Correct
const value = data?.rows?.[0]?.[0] || 0;
```

---

### Error: "Hydration failed"

**Cause**: Server-rendered HTML doesn't match client render

**Fix**:
```javascript
// Ensure consistent rendering
// Remove random values, timestamps in initial render

// ❌ Wrong
<div>{Math.random()}</div>

// ✅ Correct
const [random, setRandom] = useState(0);
useEffect(() => {
  setRandom(Math.random());
}, []);
<div>{random}</div>
```

---

### Error: "Maximum update depth exceeded"

**Cause**: Infinite loop in useEffect

**Fix**:
```javascript
// ❌ Wrong: Missing dependencies
useEffect(() => {
  setCount(count + 1);  // Infinite loop
}, []);

// ✅ Correct: Proper dependencies
useEffect(() => {
  if (condition) {
    setCount(prevCount => prevCount + 1);
  }
}, [condition]);
```

---

## Getting Help

### 1. Check Logs

```bash
# Docker logs
docker compose logs -f

# Browser console
# Press F12 → Console tab

# Network tab
# Press F12 → Network tab → Check failed requests
```

### 2. Search Documentation

- React: https://react.dev/
- Vite: https://vitejs.dev/
- Ant Design: https://ant.design/
- Metabase: https://www.metabase.com/docs/

### 3. Debug Tools

- **React DevTools**: Browser extension for inspecting components
- **Redux DevTools**: State management debugging
- **Lighthouse**: Performance auditing
- **Postman**: API testing

### 4. Community Resources

- Stack Overflow: https://stackoverflow.com/questions/tagged/reactjs
- GitHub Issues: Check project repository
- Discord/Slack: React communities

---

## Quick Diagnostics Checklist

When encountering an issue:

- [ ] Check browser console for errors
- [ ] Check network tab for failed requests
- [ ] Check Docker container status: `docker compose ps`
- [ ] Check Docker logs: `docker compose logs -f`
- [ ] Verify environment variables in `.env`
- [ ] Try hard refresh: Ctrl+Shift+R
- [ ] Clear browser cache
- [ ] Restart Docker containers: `docker compose restart`
- [ ] Rebuild: `docker compose build --no-cache`

---

## Preventive Measures

### 1. Regular Maintenance

```bash
# Weekly: Update dependencies
yarn upgrade

# Monthly: Clean Docker
docker system prune -a

# Monthly: Vacuum database
docker compose exec timescaledb psql -U btrc_admin -d btrc_qos_poc -c "VACUUM ANALYZE;"
```

### 2. Monitoring

```bash
# Set up health checks
# See: COMPLETE_DEPLOYMENT_GUIDE.md

# Monitor logs
tail -f /var/log/nginx/error.log
docker compose logs -f --tail=100
```

### 3. Backups

```bash
# Automated daily backups
# See: COMPLETE_DEPLOYMENT_GUIDE.md → Backup & Restore
```

---

## Still Having Issues?

If this guide didn't solve your problem:

1. **Document the issue**:
   - What were you trying to do?
   - What happened instead?
   - Error messages (full text)
   - Steps to reproduce

2. **Gather information**:
   - OS and version
   - Node.js version: `node --version`
   - Docker version: `docker --version`
   - Browser and version
   - Relevant logs

3. **Try minimal reproduction**:
   - Can you reproduce in a fresh project?
   - Is it specific to certain data/filters?

4. **Ask for help**:
   - Include all information from steps 1-2
   - Provide code snippets if relevant
   - Share screenshots/screen recordings

---

## Additional Resources

- [React Setup Guide](./REACT_SETUP_GUIDE.md)
- [Metabase Integration Guide](./METABASE_BACKEND_INTEGRATION.md)
- [Development Workflow](./DEVELOPMENT_WORKFLOW.md)
- [Deployment Guide](./COMPLETE_DEPLOYMENT_GUIDE.md)
