# React Frontend Setup Guide

Complete step-by-step guide to set up the React dashboard from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Project Setup](#initial-project-setup)
3. [Project Structure](#project-structure)
4. [Installing Dependencies](#installing-dependencies)
5. [Configuration](#configuration)
6. [Development Server](#development-server)
7. [Building Components](#building-components)
8. [Docker Setup](#docker-setup)

---

## Prerequisites

### Required Software
- **Node.js**: v22.12+ or v20.19+ (required by Vite 7.3.1)
- **Yarn**: v1.22+ or npm v8+
- **Docker**: v20.10+ (for containerized development)
- **Git**: v2.30+

### Check Installed Versions
```bash
node --version   # Should be 22.12+ or 20.19+
yarn --version   # v1.22.22 recommended
docker --version # v20.10+
```

### Install Node.js (if needed)
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (using Homebrew)
brew install node@22

# Verify installation
node --version
npm --version
```

### Install Yarn
```bash
# Using npm
npm install -g yarn

# Verify installation
yarn --version
```

---

## Initial Project Setup

### Step 1: Create React + Vite Project

```bash
# Navigate to project root
cd /home/alamin/Desktop/Python\ Projects/BTRC-QoS-Monitoring-Dashboard-V3

# Create React app with Vite
yarn create vite btrc-react-regional --template react

# Navigate into project
cd btrc-react-regional
```

### Step 2: Project Structure

Create the following directory structure:

```
btrc-react-regional/
├── public/                      # Static assets
│   └── vite.svg
├── src/
│   ├── api/                     # API clients
│   │   └── metabase.js         # Metabase REST API client
│   ├── components/              # Reusable components
│   │   ├── charts/             # Chart components
│   │   │   ├── ScalarCard.jsx  # KPI metric cards
│   │   │   ├── BarChart.jsx    # Bar charts
│   │   │   ├── LineChart.jsx   # Line charts
│   │   │   ├── DataTable.jsx   # Data tables
│   │   │   └── MiniBar.jsx     # Mini progress bars
│   │   ├── maps/
│   │   │   └── ChoroplethMap.jsx  # Geographic maps
│   │   ├── filters/
│   │   │   └── FilterPanel.jsx    # Filter controls
│   │   └── layout/
│   │       ├── Sidebar.jsx        # Left navigation
│   │       ├── TopHeader.jsx      # Top header
│   │       ├── SecondHeader.jsx   # Dashboard title
│   │       └── FixedLayout.jsx    # Main layout wrapper
│   ├── hooks/                   # Custom React hooks
│   │   └── useMetabaseData.js  # Hook for fetching data
│   ├── pages/                   # Dashboard pages
│   │   ├── RegulatoryDashboard.jsx  # Main regulatory dashboard
│   │   ├── SLAMonitoring.jsx        # R2.1: SLA Monitoring
│   │   ├── RegionalAnalysis.jsx     # R2.2: Regional Analysis
│   │   └── ViolationReporting.jsx   # R2.3: Violation Reporting
│   ├── utils/                   # Utility functions
│   │   └── dataTransform.js    # Data transformation helpers
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── .env                         # Environment variables (local)
├── .env.docker                  # Environment variables (Docker)
├── package.json                 # Dependencies
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS config
├── postcss.config.js           # PostCSS config
├── Dockerfile                   # Docker build file
└── README.md                    # Project documentation
```

### Step 3: Create Directories

```bash
# Create directory structure
mkdir -p src/{api,components/{charts,maps,filters,layout},hooks,pages,utils}
```

---

## Installing Dependencies

### Step 1: Core Dependencies

```bash
# Install core React and routing
yarn add react@19.2.0 react-dom@19.2.0 react-router-dom@7.13.0

# Install UI library (Ant Design)
yarn add antd@6.3.0

# Install HTTP client
yarn add axios@1.13.5

# Install charting libraries
yarn add echarts@6.0.0 echarts-for-react@3.0.6

# Install map libraries
yarn add leaflet@1.9.4 react-leaflet@5.0.0

# Install utility libraries
yarn add clsx@2.1.1 class-variance-authority@0.7.1 tailwind-merge@3.4.1

# Install Radix UI components (for custom UI)
yarn add @radix-ui/react-dropdown-menu@2.1.16
yarn add @radix-ui/react-slot@1.2.4
yarn add @radix-ui/react-tabs@1.1.13

# Install icons
yarn add lucide-react@0.574.0
```

### Step 2: Development Dependencies

```bash
# Install Vite and plugins
yarn add -D vite@7.3.1 @vitejs/plugin-react@5.1.1

# Install Tailwind CSS
yarn add -D tailwindcss@4.1.18 postcss@8.5.6 autoprefixer@10.4.24

# Install ESLint
yarn add -D eslint@9.39.1 @eslint/js@9.39.1
yarn add -D eslint-plugin-react-hooks@7.0.1 eslint-plugin-react-refresh@0.4.24
yarn add -D globals@16.5.0

# Install TypeScript types (optional, for better IDE support)
yarn add -D @types/react@19.2.7 @types/react-dom@19.2.3
```

### Step 3: Verify Installation

```bash
# Check installed packages
yarn list --depth=0

# Verify package.json
cat package.json
```

---

## Configuration

### Step 1: Vite Configuration

Create `vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',      // Listen on all interfaces (required for Docker)
    port: 5173,           // Development server port
    strictPort: true,     // Fail if port is already in use
    watch: {
      usePolling: true,   // Required for file watching in Docker
    },
  },
  build: {
    outDir: 'dist',       // Output directory for production build
    sourcemap: true,      // Generate source maps for debugging
  },
})
```

### Step 2: Environment Variables

Create `.env` (for local development):

```bash
# Metabase API URL
VITE_METABASE_URL=http://localhost:3000

# Metabase credentials
VITE_METABASE_EMAIL=alamin.technometrics22@gmail.com
VITE_METABASE_PASSWORD=Test@123

# Dashboard IDs
VITE_EXECUTIVE_DASHBOARD_ID=5
VITE_REGULATORY_DASHBOARD_ID=6
```

Create `.env.docker` (for Docker):

```bash
# Metabase API URL (Docker internal network)
VITE_METABASE_URL=http://metabase:3000

# Metabase credentials
VITE_METABASE_EMAIL=alamin.technometrics22@gmail.com
VITE_METABASE_PASSWORD=Test@123

# Dashboard IDs
VITE_EXECUTIVE_DASHBOARD_ID=5
VITE_REGULATORY_DASHBOARD_ID=6
```

### Step 3: Tailwind CSS Configuration

Create `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
      },
    },
  },
  plugins: [],
}
```

Create `postcss.config.js`:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### Step 4: Update Global Styles

Update `src/index.css`:

```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Leaflet CSS (required for maps) */
@import 'leaflet/dist/leaflet.css';

/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

/* Ant Design overrides */
.ant-table-thead > tr > th {
  background-color: #f0f2f5;
  font-weight: 600;
}
```

---

## Development Server

### Step 1: Local Development (without Docker)

```bash
# Navigate to React project
cd btrc-react-regional

# Install dependencies (if not already done)
yarn install

# Start development server
yarn run dev

# Output:
#   VITE v7.3.1  ready in 105 ms
#   ➜  Local:   http://localhost:5173/
#   ➜  Network: http://192.168.200.52:5173/
```

### Step 2: Open in Browser

```bash
# Open browser (Ubuntu/Linux)
xdg-open http://localhost:5173

# Or manually navigate to: http://localhost:5173
```

### Step 3: Hot Module Reload (HMR)

Vite provides instant hot module reload:

1. Make changes to any `.jsx` file
2. Save the file
3. Browser automatically updates (no refresh needed)

Example HMR output:
```
4:25:09 PM [vite] (client) hmr update /src/pages/RegionalAnalysis.jsx
```

### Step 4: Build for Production

```bash
# Build optimized production bundle
yarn build

# Output: dist/
#   - assets/index-abc123.js (minified JavaScript)
#   - assets/index-xyz789.css (minified CSS)
#   - index.html (entry point)

# Preview production build
yarn preview

# Output:
#   ➜  Local:   http://localhost:4173/
```

---

## Building Components

### Step 1: Create Metabase API Client

Create `src/api/metabase.js`:

```javascript
import axios from 'axios';

const METABASE_URL = import.meta.env.VITE_METABASE_URL || 'http://localhost:3000';

// Create axios instance
const metabaseApi = axios.create({
  baseURL: METABASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Login and get session token
export const login = async (email, password) => {
  try {
    const response = await metabaseApi.post('/api/session', {
      username: email,
      password: password,
    });
    return response.data.id; // Session token
  } catch (error) {
    console.error('Metabase login failed:', error);
    throw error;
  }
};

// Fetch card data
export const fetchCardData = async (cardId, parameters = {}) => {
  try {
    const sessionToken = localStorage.getItem('metabase_session');

    const response = await metabaseApi.post(
      `/api/card/${cardId}/query`,
      { parameters },
      {
        headers: {
          'X-Metabase-Session': sessionToken,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error(`Failed to fetch card ${cardId}:`, error);
    throw error;
  }
};

export default metabaseApi;
```

### Step 2: Create Custom Hook

Create `src/hooks/useMetabaseData.js`:

```javascript
import { useState, useEffect } from 'react';
import { fetchCardData, login } from '../api/metabase';

const useMetabaseData = (cardId, filters = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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
          localStorage.setItem('metabase_session', sessionToken);
        }

        // Build parameters for Metabase template tags
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

        // Fetch data from Metabase
        const result = await fetchCardData(cardId, parameters);
        setData(result.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    if (cardId) {
      fetchData();
    }
  }, [cardId, filters.division, filters.district, filters.isp]);

  return { data, loading, error };
};

export default useMetabaseData;
```

### Step 3: Create Reusable Components

Create `src/components/charts/ScalarCard.jsx`:

```javascript
import React from 'react';
import { Card, Spin } from 'antd';

const ScalarCard = ({
  value,
  title,
  unit = '',
  icon,
  color = '#3b82f6',
  loading = false,
  precision = 0,
  subtitle = ''
}) => {
  const formattedValue = typeof value === 'number'
    ? value.toFixed(precision)
    : value || 'N/A';

  return (
    <Card
      bordered={false}
      bodyStyle={{ padding: '24px' }}
      style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '30px 0' }}>
          <Spin size="large" />
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{
              fontSize: 28,
              color,
              background: `${color}15`,
              padding: '8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {icon}
            </div>
            <div>
              <h3 style={{ fontSize: 28, fontWeight: 'bold', margin: 0, color }}>
                {formattedValue}{unit}
              </h3>
            </div>
          </div>
          <p style={{ fontSize: 14, fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>
            {title}
          </p>
          {subtitle && (
            <p style={{ fontSize: 12, color: '#6b7280', margin: 0 }}>
              {subtitle}
            </p>
          )}
        </div>
      )}
    </Card>
  );
};

export default ScalarCard;
```

### Step 4: Create Dashboard Page

Create `src/pages/SLAMonitoring.jsx`:

```javascript
import React, { useState } from 'react';
import { Row, Col, Card } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import ScalarCard from '../components/charts/ScalarCard';
import useMetabaseData from '../hooks/useMetabaseData';

const SLAMonitoring = () => {
  const [filters, setFilters] = useState({
    division: undefined,
    district: undefined,
    isp: undefined,
  });

  // Fetch data from Metabase Card 76
  const { data: complianceData, loading: loading76 } = useMetabaseData(76, filters);

  // Extract scalar value
  const complianceRate = complianceData?.rows?.[0]?.[0] || 0;

  return (
    <div style={{ padding: '32px' }}>
      <h1>SLA Monitoring</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <ScalarCard
            value={complianceRate}
            title="Overall SLA Compliance Rate"
            unit="%"
            icon={<CheckCircleOutlined />}
            color="#10b981"
            loading={loading76}
            precision={2}
          />
        </Col>
      </Row>
    </div>
  );
};

export default SLAMonitoring;
```

---

## Docker Setup

### Step 1: Create Dockerfile

Create `Dockerfile` in `btrc-react-regional/`:

```dockerfile
# Multi-stage Dockerfile for React + Vite app

# Development stage
FROM node:22-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json yarn.lock* ./

# Install dependencies with yarn
RUN yarn install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server with hot reload
CMD ["yarn", "run", "dev", "--host", "0.0.0.0"]

# Production build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json yarn.lock* ./
RUN yarn install

COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx-prod.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Step 2: Update docker-compose.yml

Add React service to root `docker-compose.yml`:

```yaml
services:
  # ... (other services)

  react-regional:
    build:
      context: ./btrc-react-regional
      dockerfile: Dockerfile
      target: development
    container_name: btrc-v3-react-regional
    restart: unless-stopped
    ports:
      - "5180:5173"
    volumes:
      - ./btrc-react-regional/src:/app/src:ro
      - ./btrc-react-regional/public:/app/public:ro
      - ./btrc-react-regional/.env.docker:/app/.env:ro
    environment:
      - NODE_ENV=development
      - VITE_METABASE_URL=http://localhost:3000
    depends_on:
      metabase:
        condition: service_healthy
    networks:
      - btrc-v3
```

### Step 3: Build and Run

```bash
# Navigate to project root
cd /home/alamin/Desktop/Python\ Projects/BTRC-QoS-Monitoring-Dashboard-V3

# Build React container
docker-compose build react-regional

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f react-regional

# Access dashboard
# Docker: http://localhost:5180
# Local:  http://localhost:5173
```

### Step 4: Docker Commands Reference

```bash
# Stop all services
docker-compose down

# Rebuild specific service
docker-compose build --no-cache react-regional

# Restart service
docker-compose restart react-regional

# View logs
docker-compose logs -f react-regional

# Execute commands inside container
docker-compose exec react-regional sh
docker-compose exec react-regional yarn add package-name

# Remove volumes (clean slate)
docker-compose down -v
```

---

## Troubleshooting

### Issue 1: Port Already in Use

**Error**: `Error: listen EADDRINUSE: address already in use :::5173`

**Solution**:
```bash
# Find process using port 5173
lsof -i :5173

# Kill process
kill -9 <PID>

# Or use different port in vite.config.js
```

### Issue 2: Node Version Mismatch

**Error**: `Vite requires Node.js version 20.19+ or 22.12+`

**Solution**:
```bash
# Check current version
node --version

# Install correct version
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node --version
```

### Issue 3: Module Not Found

**Error**: `Cannot find module 'antd'`

**Solution**:
```bash
# Reinstall dependencies
rm -rf node_modules yarn.lock
yarn install

# Or install specific package
yarn add antd
```

### Issue 4: Hot Reload Not Working in Docker

**Solution**: Ensure `usePolling: true` in `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    watch: {
      usePolling: true, // Required for Docker
    },
  },
})
```

---

## Next Steps

1. **Read**: [Metabase Backend Integration Guide](./METABASE_BACKEND_INTEGRATION.md)
2. **Read**: [Development Workflow Guide](./DEVELOPMENT_WORKFLOW.md)
3. **Read**: [Complete Deployment Guide](./COMPLETE_DEPLOYMENT_GUIDE.md)
4. **Read**: [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)

---

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Ant Design Components](https://ant.design/components/overview/)
- [React Router](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
- [Leaflet Maps](https://leafletjs.com/)
- [ECharts](https://echarts.apache.org/)
