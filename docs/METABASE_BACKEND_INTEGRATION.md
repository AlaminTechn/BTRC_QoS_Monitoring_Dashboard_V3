# Metabase Backend Integration Guide

Complete guide for integrating React dashboard with Metabase REST API.

## Table of Contents
1. [Metabase Architecture](#metabase-architecture)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Fetching Dashboard Data](#fetching-dashboard-data)
5. [Template Tags & Filters](#template-tags--filters)
6. [Creating Charts from Metabase Data](#creating-charts-from-metabase-data)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Metabase Architecture

### System Overview

```
┌─────────────────┐         ┌──────────────┐         ┌──────────────┐
│  React Frontend │  HTTP   │   Metabase   │  SQL    │ TimescaleDB  │
│  (Port 5173)    │────────>│  (Port 3000) │────────>│ (Port 5433)  │
│                 │  REST   │              │         │              │
│  - UI/UX        │  API    │  - BI Engine │         │  - QoS Data  │
│  - Filtering    │         │  - Caching   │         │  - POC Data  │
│  - Charts       │         │  - Queries   │         │              │
└─────────────────┘         └──────────────┘         └──────────────┘
```

### Components

1. **React Frontend**: User interface and visualization
2. **Metabase**: Business Intelligence layer (query engine, caching)
3. **TimescaleDB**: PostgreSQL database with time-series extensions

### Data Flow

```
User clicks filter → React updates state → API call to Metabase
                                                 ↓
Metabase checks cache → If miss, queries TimescaleDB → Returns JSON
                                                 ↓
React receives data → Transforms to chart format → Renders chart
```

---

## Authentication

### Step 1: Understanding Metabase Sessions

Metabase uses session-based authentication:
- Login with email/password → Receive session token
- Include token in all API requests via `X-Metabase-Session` header
- Token expires after 14 days of inactivity

### Step 2: Login API

Create `src/api/metabase.js`:

```javascript
import axios from 'axios';

const METABASE_URL = import.meta.env.VITE_METABASE_URL || 'http://localhost:3000';

const metabaseApi = axios.create({
  baseURL: METABASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Login to Metabase and get session token
 * @param {string} email - Metabase user email
 * @param {string} password - Metabase user password
 * @returns {Promise<string>} Session token
 */
export const login = async (email, password) => {
  try {
    const response = await metabaseApi.post('/api/session', {
      username: email,
      password: password,
    });

    const sessionToken = response.data.id;

    // Store token in localStorage for reuse
    localStorage.setItem('metabase_session', sessionToken);

    return sessionToken;
  } catch (error) {
    console.error('Metabase login failed:', error.response?.data || error.message);
    throw new Error('Failed to authenticate with Metabase');
  }
};

/**
 * Logout from Metabase
 */
export const logout = async () => {
  try {
    const sessionToken = localStorage.getItem('metabase_session');

    if (sessionToken) {
      await metabaseApi.delete('/api/session', {
        headers: {
          'X-Metabase-Session': sessionToken,
        },
      });
    }

    localStorage.removeItem('metabase_session');
  } catch (error) {
    console.error('Logout failed:', error);
  }
};

export default metabaseApi;
```

### Step 3: Session Management Hook

Create `src/hooks/useMetabaseAuth.js`:

```javascript
import { useState, useEffect } from 'react';
import { login } from '../api/metabase';

const useMetabaseAuth = () => {
  const [sessionToken, setSessionToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initSession = async () => {
      try {
        setLoading(true);

        // Check for existing token
        let token = localStorage.getItem('metabase_session');

        // If no token, login
        if (!token) {
          const email = import.meta.env.VITE_METABASE_EMAIL;
          const password = import.meta.env.VITE_METABASE_PASSWORD;

          if (!email || !password) {
            throw new Error('Metabase credentials not configured');
          }

          token = await login(email, password);
        }

        setSessionToken(token);
      } catch (err) {
        setError(err);
        console.error('Session initialization failed:', err);
      } finally {
        setLoading(false);
      }
    };

    initSession();
  }, []);

  return { sessionToken, loading, error };
};

export default useMetabaseAuth;
```

---

## API Endpoints

### Core Metabase REST API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/api/session` | POST | Login | `POST /api/session` |
| `/api/session` | DELETE | Logout | `DELETE /api/session` |
| `/api/user/current` | GET | Get current user | `GET /api/user/current` |
| `/api/dashboard` | GET | List dashboards | `GET /api/dashboard` |
| `/api/dashboard/:id` | GET | Get dashboard details | `GET /api/dashboard/6` |
| `/api/card/:id` | GET | Get card (question) details | `GET /api/card/76` |
| `/api/card/:id/query` | POST | Execute card query | `POST /api/card/76/query` |
| `/api/database` | GET | List databases | `GET /api/database` |
| `/api/database/:id` | GET | Get database details | `GET /api/database/2` |

### Dashboard Structure

Metabase Dashboard (ID=6):
```json
{
  "id": 6,
  "name": "Regulatory Operations Dashboard",
  "tabs": [
    {
      "id": 1,
      "name": "R2.1 SLA Monitoring",
      "dashboard_cards": [76, 77, 78, 79, 80]
    },
    {
      "id": 2,
      "name": "R2.2 Regional Analysis",
      "dashboard_cards": [79, 80, 81, 87, 94, 95]
    }
  ],
  "parameters": [
    {"slug": "division", "type": "category"},
    {"slug": "district", "type": "category"},
    {"slug": "isp", "type": "category"}
  ]
}
```

### Card (Question) Structure

Metabase Card (ID=76):
```json
{
  "id": 76,
  "name": "Overall SLA Compliance Rate",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT ...",
      "template-tags": {
        "division": {
          "type": "text",
          "required": false
        }
      }
    },
    "database": 2
  },
  "display": "scalar",
  "visualization_settings": {}
}
```

---

## Fetching Dashboard Data

### Step 1: Fetch Card Data Function

Add to `src/api/metabase.js`:

```javascript
/**
 * Fetch data from a Metabase card (question)
 * @param {number} cardId - Card ID
 * @param {Object} parameters - Filter parameters
 * @returns {Promise<Object>} Card data
 */
export const fetchCardData = async (cardId, parameters = {}) => {
  try {
    const sessionToken = localStorage.getItem('metabase_session');

    if (!sessionToken) {
      throw new Error('Not authenticated. Please login first.');
    }

    // Build parameter array for Metabase
    const paramArray = [];

    if (parameters.division) {
      paramArray.push({
        type: 'category',
        target: ['variable', ['template-tag', 'division']],
        value: parameters.division,
      });
    }

    if (parameters.district) {
      paramArray.push({
        type: 'category',
        target: ['variable', ['template-tag', 'district']],
        value: parameters.district,
      });
    }

    if (parameters.isp) {
      paramArray.push({
        type: 'category',
        target: ['variable', ['template-tag', 'isp']],
        value: parameters.isp,
      });
    }

    const response = await metabaseApi.post(
      `/api/card/${cardId}/query`,
      { parameters: paramArray },
      {
        headers: {
          'X-Metabase-Session': sessionToken,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error(`Failed to fetch card ${cardId}:`, error.response?.data || error.message);

    // If session expired, try to re-login
    if (error.response?.status === 401) {
      localStorage.removeItem('metabase_session');
      throw new Error('Session expired. Please refresh the page.');
    }

    throw error;
  }
};

/**
 * Fetch dashboard details
 * @param {number} dashboardId - Dashboard ID
 * @returns {Promise<Object>} Dashboard details
 */
export const fetchDashboard = async (dashboardId) => {
  try {
    const sessionToken = localStorage.getItem('metabase_session');

    const response = await metabaseApi.get(`/api/dashboard/${dashboardId}`, {
      headers: {
        'X-Metabase-Session': sessionToken,
      },
    });

    return response.data;
  } catch (error) {
    console.error(`Failed to fetch dashboard ${dashboardId}:`, error);
    throw error;
  }
};
```

### Step 2: Create Custom Hook

Create `src/hooks/useMetabaseData.js`:

```javascript
import { useState, useEffect } from 'react';
import { fetchCardData, login } from '../api/metabase';

/**
 * Custom hook to fetch data from Metabase card
 * @param {number} cardId - Metabase card ID
 * @param {Object} filters - Filter parameters {division, district, isp}
 * @returns {Object} {data, loading, error, refetch}
 */
const useMetabaseData = (cardId, filters = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Ensure we have a session token
      let sessionToken = localStorage.getItem('metabase_session');

      if (!sessionToken) {
        const email = import.meta.env.VITE_METABASE_EMAIL;
        const password = import.meta.env.VITE_METABASE_PASSWORD;

        sessionToken = await login(email, password);
      }

      // Fetch data
      const result = await fetchCardData(cardId, filters);

      setData(result.data);
    } catch (err) {
      setError(err);
      console.error(`Error fetching card ${cardId}:`, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (cardId) {
      fetchData();
    }
  }, [cardId, filters.division, filters.district, filters.isp]);

  return {
    data,
    loading,
    error,
    refetch: fetchData // Allow manual refetch
  };
};

export default useMetabaseData;
```

### Step 3: Use Hook in Component

Example usage in `src/pages/SLAMonitoring.jsx`:

```javascript
import React, { useState } from 'react';
import useMetabaseData from '../hooks/useMetabaseData';
import ScalarCard from '../components/charts/ScalarCard';

const SLAMonitoring = () => {
  const [filters, setFilters] = useState({
    division: undefined,
    district: undefined,
    isp: undefined,
  });

  // Fetch Card 76: Overall SLA Compliance Rate
  const { data: card76Data, loading: loading76, error: error76 } = useMetabaseData(76, filters);

  // Fetch Card 77: Critical Violations
  const { data: card77Data, loading: loading77, error: error77 } = useMetabaseData(77, filters);

  // Extract values from Metabase response
  const complianceRate = card76Data?.rows?.[0]?.[0] || 0;
  const criticalCount = card77Data?.rows?.[0]?.[0] || 0;

  return (
    <div>
      <ScalarCard
        value={complianceRate}
        title="SLA Compliance Rate"
        unit="%"
        loading={loading76}
      />

      <ScalarCard
        value={criticalCount}
        title="Critical Violations"
        loading={loading77}
      />
    </div>
  );
};

export default SLAMonitoring;
```

---

## Template Tags & Filters

### Understanding Metabase Template Tags

Template tags allow parameterized SQL queries:

```sql
-- Card 79: Division Performance Summary
SELECT
  division,
  AVG(download_speed_mbps) AS avg_download,
  AVG(upload_speed_mbps) AS avg_upload,
  COUNT(*) AS measurement_count
FROM ts_qos_measurements
WHERE 1=1
  [[ AND division = {{division}} ]]
  [[ AND district = {{district}} ]]
GROUP BY division
ORDER BY division;
```

**Key Points**:
- `{{variable}}` - Template tag placeholder
- `[[ ... ]]` - Optional clause (only included if parameter provided)
- Parameter not provided → clause is omitted from query

### Filter Parameter Format

Metabase expects parameters in this format:

```javascript
{
  parameters: [
    {
      type: 'category',              // Parameter type
      target: ['variable', ['template-tag', 'division']],  // Target template tag
      value: 'Dhaka'                 // Filter value
    },
    {
      type: 'category',
      target: ['variable', ['template-tag', 'district']],
      value: 'Gazipur'
    }
  ]
}
```

### Building Parameters Dynamically

Helper function in `src/utils/filterBuilder.js`:

```javascript
/**
 * Build Metabase parameter array from filter object
 * @param {Object} filters - {division, district, isp}
 * @returns {Array} Metabase parameters array
 */
export const buildMetabaseParameters = (filters) => {
  const parameters = [];

  if (filters.division) {
    parameters.push({
      type: 'category',
      target: ['variable', ['template-tag', 'division']],
      value: filters.division,
    });
  }

  if (filters.district) {
    parameters.push({
      type: 'category',
      target: ['variable', ['template-tag', 'district']],
      value: filters.district,
    });
  }

  if (filters.isp) {
    parameters.push({
      type: 'category',
      target: ['variable', ['template-tag', 'isp']],
      value: filters.isp,
    });
  }

  return parameters;
};
```

### Filter Cascading

For hierarchical filters (Division → District → ISP):

```javascript
const [filters, setFilters] = useState({
  division: undefined,
  district: undefined,
  isp: undefined,
});

// When division changes, reset district and isp
const handleDivisionChange = (value) => {
  setFilters({
    division: value,
    district: undefined,  // Reset dependent filter
    isp: undefined,       // Reset dependent filter
  });
};

// When district changes, reset isp only
const handleDistrictChange = (value) => {
  setFilters({
    ...filters,
    district: value,
    isp: undefined,       // Reset dependent filter
  });
};
```

---

## Creating Charts from Metabase Data

### Data Structure

Metabase returns data in this format:

```json
{
  "data": {
    "rows": [
      ["Dhaka", 41.34, 8.21, 22.15, 98.45, 12],
      ["Chattogram", 38.76, 7.89, 25.34, 97.21, 8]
    ],
    "cols": [
      {"name": "division", "display_name": "Division", "base_type": "type/Text"},
      {"name": "avg_download", "display_name": "Avg Download", "base_type": "type/Float"},
      {"name": "avg_upload", "display_name": "Avg Upload", "base_type": "type/Float"},
      {"name": "avg_latency", "display_name": "Avg Latency", "base_type": "type/Float"},
      {"name": "availability", "display_name": "Availability", "base_type": "type/Float"},
      {"name": "isp_count", "display_name": "ISP Count", "base_type": "type/Integer"}
    ]
  }
}
```

### Transform to Table Data

Create `src/utils/dataTransform.js`:

```javascript
/**
 * Transform Metabase rows to Ant Design table format
 * @param {Object} metabaseData - Metabase card data
 * @returns {Array} Table rows with keys
 */
export const transformToTableData = (metabaseData) => {
  if (!metabaseData || !metabaseData.rows) {
    return [];
  }

  return metabaseData.rows.map((row, index) => {
    const rowData = { key: `row-${index}` };

    // Map array values to column indices
    row.forEach((value, colIndex) => {
      rowData[colIndex] = value;
    });

    return rowData;
  });
};

/**
 * Transform Metabase rows to ECharts format
 * @param {Object} metabaseData - Metabase card data
 * @param {number} labelIndex - Column index for labels (x-axis)
 * @param {number} valueIndex - Column index for values (y-axis)
 * @returns {Object} ECharts option
 */
export const transformToBarChart = (metabaseData, labelIndex = 0, valueIndex = 1) => {
  if (!metabaseData || !metabaseData.rows) {
    return { xAxis: { data: [] }, series: [{ data: [] }] };
  }

  const labels = metabaseData.rows.map(row => row[labelIndex]);
  const values = metabaseData.rows.map(row => row[valueIndex]);

  return {
    xAxis: {
      type: 'category',
      data: labels,
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        type: 'bar',
        data: values,
      },
    ],
  };
};
```

### Example: Bar Chart Component

Create `src/components/charts/BarChart.jsx`:

```javascript
import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Spin } from 'antd';

const BarChart = ({ data, loading, title }) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  const option = {
    title: {
      text: title,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: data.labels,
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        type: 'bar',
        data: data.values,
        itemStyle: {
          color: '#3b82f6',
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '400px' }} />;
};

export default BarChart;
```

---

## Best Practices

### 1. Error Handling

Always handle API errors gracefully:

```javascript
const { data, loading, error } = useMetabaseData(76, filters);

if (error) {
  return (
    <Alert
      title="Error Loading Data"
      description={error.message}
      type="error"
      showIcon
    />
  );
}
```

### 2. Loading States

Show loading indicators while fetching:

```javascript
{loading ? (
  <Spin size="large" />
) : (
  <ScalarCard value={data} />
)}
```

### 3. Caching

Metabase has built-in caching (default 1 hour). To leverage:

```javascript
// Don't refetch unnecessarily
const { data, loading } = useMetabaseData(76, filters);

// Only refetch when filters actually change
useEffect(() => {
  // Fetch logic
}, [filters.division, filters.district]); // Specific dependencies
```

### 4. Session Management

Handle expired sessions:

```javascript
try {
  await fetchCardData(cardId);
} catch (error) {
  if (error.response?.status === 401) {
    // Session expired - re-login
    localStorage.removeItem('metabase_session');
    await login(email, password);
    // Retry request
    await fetchCardData(cardId);
  }
}
```

### 5. Performance Optimization

- **Lazy Load**: Only fetch data for visible components
- **Debounce**: Debounce filter changes to reduce API calls
- **Parallel Requests**: Fetch independent cards in parallel

```javascript
// Parallel fetching
const [data1, data2, data3] = await Promise.all([
  fetchCardData(76),
  fetchCardData(77),
  fetchCardData(78),
]);
```

---

## Troubleshooting

### Issue 1: CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Configure Metabase CORS settings:

```bash
# In docker-compose.yml
environment:
  MB_EMBEDDING_APP_ORIGIN: "http://localhost:5173"
```

### Issue 2: Session Expired

**Error**: `401 Unauthorized`

**Solution**: Implement auto-retry with re-login:

```javascript
const fetchWithRetry = async (cardId) => {
  try {
    return await fetchCardData(cardId);
  } catch (error) {
    if (error.response?.status === 401) {
      // Re-login
      await login(email, password);
      // Retry
      return await fetchCardData(cardId);
    }
    throw error;
  }
};
```

### Issue 3: Wrong Data Format

**Error**: `Cannot read property 'rows' of undefined`

**Solution**: Always check data structure:

```javascript
const value = data?.rows?.[0]?.[0] || 0;  // Safe access with fallback
```

### Issue 4: Template Tags Not Working

**Error**: Filters don't apply to query

**Solution**: Ensure parameter format matches template tag name:

```javascript
// SQL template tag: {{division}}
// Parameter must be:
{
  target: ['variable', ['template-tag', 'division']],  // Match 'division'
  value: 'Dhaka'
}
```

### Issue 5: Slow Queries

**Solution**: Check Metabase query caching:

1. Open Metabase → Admin → Settings → Caching
2. Enable "Cache results of queries"
3. Set TTL to 1 hour (3600 seconds)

---

## Card ID Reference

### R2.1 SLA Monitoring Tab
- **Card 76**: Overall SLA Compliance Rate (scalar)
- **Card 77**: Critical Violations (scalar)
- **Card 78**: ISPs Below Threshold (scalar)
- **Card 79**: SLA Compliance by Package Tier (table)
- **Card 80**: SLA Compliance Trend (table)

### R2.2 Regional Analysis Tab
- **Card 79**: Division Performance Summary (table)
- **Card 80**: District Ranking Table (table)
- **Card 81**: ISP Performance by Area (table, 10 columns)
- **Card 87**: Division Violation Data (for map)
- **Card 94**: Division Performance Map (GeoJSON)
- **Card 95**: District Performance Map (GeoJSON)

### R2.3 Violation Reporting Tab
- **Card 82-87**: Violation Analysis cards

---

## Next Steps

1. **Read**: [Development Workflow Guide](./DEVELOPMENT_WORKFLOW.md)
2. **Read**: [Complete Deployment Guide](./COMPLETE_DEPLOYMENT_GUIDE.md)
3. **Read**: [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)

---

## Additional Resources

- [Metabase REST API Documentation](https://www.metabase.com/docs/latest/api-documentation)
- [Metabase Embedding Guide](https://www.metabase.com/docs/latest/embedding/introduction)
- [Metabase SQL Parameters](https://www.metabase.com/docs/latest/questions/native-editor/sql-parameters)
