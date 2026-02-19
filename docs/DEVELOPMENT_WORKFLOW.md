# Development Workflow Guide

Day-to-day development guide for the BTRC QoS Monitoring Dashboard.

## Table of Contents
1. [Daily Development Setup](#daily-development-setup)
2. [Adding New Features](#adding-new-features)
3. [Creating Components](#creating-components)
4. [Working with Metabase](#working-with-metabase)
5. [Testing](#testing)
6. [Git Workflow](#git-workflow)
7. [Code Style](#code-style)
8. [Common Tasks](#common-tasks)

---

## Daily Development Setup

### Morning Routine

```bash
# 1. Navigate to project
cd /home/alamin/Desktop/Python\ Projects/BTRC-QoS-Monitoring-Dashboard-V3

# 2. Pull latest changes (if working in a team)
git pull origin main

# 3. Start Docker services
docker compose up -d

# 4. Check service health
docker compose ps

# 5. Navigate to React project
cd btrc-react-regional

# 6. Install any new dependencies
yarn install

# 7. Start development server
yarn run dev

# Output:
#   VITE v7.3.1  ready in 105 ms
#   ➜  Local:   http://localhost:5173/
```

### Open Development Tools

```bash
# Open browser to dashboard
xdg-open http://localhost:5173

# Open Metabase (for query testing)
xdg-open http://localhost:3000

# Open database client (optional)
dbeaver-ce  # Or pgAdmin, DataGrip
```

### Development Environment Checklist

- [ ] All Docker containers running (4/4 healthy)
- [ ] Vite dev server running (localhost:5173)
- [ ] Browser console open (F12)
- [ ] VS Code or IDE ready
- [ ] Terminal with logs visible

---

## Adding New Features

### Step 1: Plan the Feature

Example: Add "Top 10 ISPs by Speed" chart to Regional Analysis tab

1. **Identify data source**: Which Metabase card?
2. **Design component**: What type of chart (bar, line, table)?
3. **Define filters**: Does it need division/district filters?
4. **Plan layout**: Where does it fit in the page?

### Step 2: Create Metabase Query

```sql
-- In Metabase: New Question → Native Query
SELECT
  isp_name,
  AVG(download_speed_mbps) AS avg_download
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '7 days'
  [[ AND division = {{division}} ]]
  [[ AND district = {{district}} ]]
GROUP BY isp_name
ORDER BY avg_download DESC
LIMIT 10;
```

**Save as**: "Top 10 ISPs by Speed" → Note the Card ID (e.g., Card 100)

### Step 3: Create Hook for Data Fetching

In your component:

```javascript
import useMetabaseData from '../hooks/useMetabaseData';

const RegionalAnalysis = () => {
  const [filters, setFilters] = useState({ division: undefined, district: undefined });

  // Fetch data from Metabase Card 100
  const { data: topISPsData, loading: topISPsLoading } = useMetabaseData(100, filters);

  // Transform data for chart
  const chartData = React.useMemo(() => {
    if (!topISPsData?.rows) return { labels: [], values: [] };

    return {
      labels: topISPsData.rows.map(row => row[0]),  // ISP names
      values: topISPsData.rows.map(row => row[1]),  // Speeds
    };
  }, [topISPsData]);

  // ... rest of component
};
```

### Step 4: Create Chart Component

Create `src/components/charts/HorizontalBarChart.jsx`:

```javascript
import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Spin } from 'antd';

const HorizontalBarChart = ({ data, loading, title, unit = '' }) => {
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
      axisPointer: { type: 'shadow' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: unit,
    },
    yAxis: {
      type: 'category',
      data: data.labels,
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

  return <ReactECharts option={option} style={{ height: '500px' }} />;
};

export default HorizontalBarChart;
```

### Step 5: Add to Page

In `src/pages/RegionalAnalysis.jsx`:

```javascript
import HorizontalBarChart from '../components/charts/HorizontalBarChart';

// ... inside return statement:

<Row gutter={[16, 16]}>
  <Col xs={24}>
    <Card
      title="Top 10 ISPs by Download Speed"
      bordered={false}
      style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
    >
      <HorizontalBarChart
        data={chartData}
        loading={topISPsLoading}
        title=""
        unit="Mbps"
      />
    </Card>
  </Col>
</Row>
```

### Step 6: Test the Feature

1. **Visual check**: Does it render correctly?
2. **Filter test**: Apply division filter → chart updates?
3. **Loading state**: Does spinner show while loading?
4. **Error handling**: Disconnect network → error message?
5. **Responsive**: Resize browser → chart adapts?

---

## Creating Components

### Component Structure

```javascript
// src/components/charts/YourComponent.jsx

import React from 'react';
import { Card, Spin } from 'antd';
import PropTypes from 'prop-types';

/**
 * YourComponent - Brief description
 *
 * @param {Object} props
 * @param {*} props.data - Data to display
 * @param {boolean} props.loading - Loading state
 * @param {Object} props.error - Error object
 * @param {string} props.title - Component title
 */
const YourComponent = ({ data, loading, error, title }) => {
  // Handle loading state
  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Card>
        <Alert
          title="Error Loading Data"
          description={error.message}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  // Render component
  return (
    <Card title={title}>
      {/* Your component content */}
    </Card>
  );
};

// PropTypes for type checking
YourComponent.propTypes = {
  data: PropTypes.object,
  loading: PropTypes.bool,
  error: PropTypes.object,
  title: PropTypes.string,
};

// Default props
YourComponent.defaultProps = {
  loading: false,
  error: null,
  title: '',
};

export default YourComponent;
```

### Component Best Practices

1. **Single Responsibility**: One component, one purpose
2. **Reusability**: Make components generic and configurable
3. **Props Validation**: Use PropTypes or TypeScript
4. **Loading States**: Always handle loading and error states
5. **Memoization**: Use `React.useMemo` for expensive calculations
6. **Styling**: Use Ant Design components + Tailwind for consistency

### Component File Structure

```
src/components/
├── charts/              # Chart components
│   ├── BarChart.jsx
│   ├── LineChart.jsx
│   ├── DataTable.jsx
│   └── ScalarCard.jsx
├── maps/                # Map components
│   └── ChoroplethMap.jsx
├── filters/             # Filter components
│   └── FilterPanel.jsx
├── layout/              # Layout components
│   ├── Sidebar.jsx
│   ├── TopHeader.jsx
│   └── FixedLayout.jsx
└── common/              # Shared components
    ├── LoadingSpinner.jsx
    └── ErrorBoundary.jsx
```

---

## Working with Metabase

### Creating a New Card (Question)

1. **Open Metabase**: http://localhost:3000
2. **Login**: alamin.technometrics22@gmail.com / Test@123
3. **New Question** → **Native Query**
4. **Select Database**: BTRC QoS POC
5. **Write SQL**:

```sql
SELECT
  division,
  AVG(download_speed_mbps) AS avg_download
FROM ts_qos_measurements
WHERE timestamp >= (SELECT MAX(timestamp) FROM ts_qos_measurements) - INTERVAL '7 days'
  [[ AND division = {{division}} ]]
GROUP BY division
ORDER BY avg_download DESC;
```

6. **Add Variable**: Click "Variables" → Add `division` (Field Filter, Text)
7. **Save**: "Division Performance - Last 7 Days"
8. **Note Card ID**: URL shows `/question/101` → Card ID = 101

### Testing Metabase Query

```bash
# Get session token
curl -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d '{"username":"alamin.technometrics22@gmail.com","password":"Test@123"}'

# Output: {"id":"abc123-session-token"}

# Test card query
curl -X POST http://localhost:3000/api/card/101/query \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: abc123-session-token" \
  -d '{
    "parameters": [
      {
        "type": "category",
        "target": ["variable", ["template-tag", "division"]],
        "value": "Dhaka"
      }
    ]
  }'
```

### Metabase Card Types

| Type | Use Case | Example |
|------|----------|---------|
| **Scalar** | Single number | "Total ISPs: 40" |
| **Table** | Rows of data | "ISP Performance List" |
| **Bar** | Comparison | "Speed by Division" |
| **Line** | Trend over time | "Compliance Trend" |
| **Map** | Geographic | "Violations by District" |

### Updating Existing Cards

1. **Find card**: Metabase → Browse → Find card by name
2. **Edit SQL**: Click "Edit" → Modify query
3. **Test**: Click "Refresh" → Verify results
4. **Save**: Save changes
5. **Refresh React**: React dashboard auto-refreshes via API

---

## Testing

### Manual Testing Checklist

Before committing code:

- [ ] **Visual**: Component renders correctly
- [ ] **Filters**: All filters work (division, district, ISP)
- [ ] **Loading**: Spinner shows while fetching
- [ ] **Error**: Error message shows on API failure
- [ ] **Empty State**: Handles no data gracefully
- [ ] **Responsive**: Works on tablet and desktop
- [ ] **Browser Console**: No errors or warnings
- [ ] **Network Tab**: API calls succeed (200 OK)

### Testing Filters

```javascript
// Test filter combinations:
1. No filters (national view)
2. Division only (e.g., "Dhaka")
3. Division + District (e.g., "Dhaka" → "Gazipur")
4. All filters (Division + District + ISP)
5. Reset filters (back to national)
```

### Testing Error Scenarios

```javascript
// Simulate API errors:

// 1. Network error
// - Disconnect WiFi
// - Expect: Error alert shows

// 2. Session expired
// - Clear localStorage: localStorage.removeItem('metabase_session')
// - Refresh page
// - Expect: Auto-login and data loads

// 3. Invalid card ID
// - Use non-existent card ID (e.g., 9999)
// - Expect: Error message

// 4. Empty data
// - Query with filters that return no rows
// - Expect: "No data available" message
```

### Browser Testing

Test on multiple browsers:
- Chrome/Chromium (primary)
- Firefox
- Safari (if available)
- Edge

### Performance Testing

```javascript
// Check performance in browser DevTools:

// 1. Lighthouse (Chrome)
// - Press F12 → Lighthouse tab
// - Run audit
// - Target: 90+ score

// 2. Network tab
// - Check API call times
// - Target: <500ms per call

// 3. React DevTools
// - Install React DevTools extension
// - Check component render times
// - Look for unnecessary re-renders
```

---

## Git Workflow

### Branch Strategy

```bash
# Main branches
main          # Production-ready code
develop       # Integration branch (if team)

# Feature branches
feature/add-top-isps-chart
feature/improve-filters
bugfix/fix-loading-state
```

### Creating a Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/add-top-isps-chart

# Make changes
# ... edit files ...

# Check status
git status

# Stage changes
git add src/components/charts/HorizontalBarChart.jsx
git add src/pages/RegionalAnalysis.jsx

# Commit with descriptive message
git commit -m "Add Top 10 ISPs by Speed chart to Regional Analysis

- Created HorizontalBarChart component
- Integrated with Metabase Card 100
- Added filters support (division, district)
- Tested with all filter combinations"

# Push to remote
git push origin feature/add-top-isps-chart
```

### Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Updating dependencies, build tasks

**Examples**:

```bash
# Good commit messages
git commit -m "feat: Add district performance map to Regional Analysis tab"
git commit -m "fix: Resolve loading81 undefined error in SLAMonitoring"
git commit -m "refactor: Extract filter logic into custom hook"
git commit -m "docs: Update REACT_SETUP_GUIDE with Docker instructions"

# Bad commit messages
git commit -m "updates"
git commit -m "fixes"
git commit -m "changes to file"
```

### Pull Request Process

```bash
# 1. Ensure your branch is up to date
git checkout main
git pull origin main
git checkout feature/add-top-isps-chart
git merge main

# 2. Resolve any conflicts
# ... fix conflicts ...
git add .
git commit -m "Merge main into feature branch"

# 3. Push final changes
git push origin feature/add-top-isps-chart

# 4. Create Pull Request on GitHub/GitLab
# - Go to repository
# - Click "New Pull Request"
# - Select: main ← feature/add-top-isps-chart
# - Add description and screenshots
# - Request review (if team)

# 5. After approval, merge and delete branch
git checkout main
git pull origin main
git branch -d feature/add-top-isps-chart
```

---

## Code Style

### JavaScript/React Style

```javascript
// Use ES6+ features
const myFunction = (param) => { /* ... */ };

// Destructure props
const MyComponent = ({ data, loading }) => { /* ... */ };

// Use template literals
const message = `Hello, ${name}!`;

// Use optional chaining
const value = data?.rows?.[0]?.[0] || 0;

// Use meaningful variable names
const complianceRate = data.rows[0][0];  // ✅ Good
const x = data.rows[0][0];               // ❌ Bad

// Extract complex logic into functions
const calculateAverage = (values) => {
  return values.reduce((sum, val) => sum + val, 0) / values.length;
};
```

### Component Organization

```javascript
// 1. Imports
import React, { useState, useEffect } from 'react';
import { Card, Spin } from 'antd';
import useMetabaseData from '../hooks/useMetabaseData';

// 2. Component definition
const MyComponent = ({ cardId, filters }) => {
  // 3. State
  const [localState, setLocalState] = useState(null);

  // 4. Hooks
  const { data, loading, error } = useMetabaseData(cardId, filters);

  // 5. Effects
  useEffect(() => {
    // Side effects
  }, [/* dependencies */]);

  // 6. Event handlers
  const handleClick = () => {
    // Handle event
  };

  // 7. Memoized values
  const processedData = React.useMemo(() => {
    // Expensive calculation
    return data?.rows?.map(/* ... */);
  }, [data]);

  // 8. Render
  return (
    <Card>
      {/* JSX */}
    </Card>
  );
};

// 9. PropTypes and default props
MyComponent.propTypes = { /* ... */ };
MyComponent.defaultProps = { /* ... */ };

// 10. Export
export default MyComponent;
```

### CSS/Styling

```javascript
// Use inline styles for dynamic values
<div style={{ color: percent > 90 ? 'green' : 'red' }}>

// Use Tailwind for utility classes
<div className="flex items-center gap-4 p-4 rounded-lg">

// Use Ant Design theme tokens
import { theme } from 'antd';
const { token } = theme.useToken();
<div style={{ color: token.colorPrimary }}>
```

### File Naming

```
# Components: PascalCase
src/components/charts/HorizontalBarChart.jsx

# Pages: PascalCase
src/pages/RegionalAnalysis.jsx

# Hooks: camelCase with "use" prefix
src/hooks/useMetabaseData.js

# Utils: camelCase
src/utils/dataTransform.js

# API: camelCase
src/api/metabase.js
```

---

## Common Tasks

### Task 1: Add New Dashboard Tab

```bash
# 1. Create new page component
touch src/pages/NewTab.jsx

# 2. Implement component
# See "Creating Components" section

# 3. Add route (if using React Router)
# In App.jsx or router configuration:
<Route path="/new-tab" element={<NewTab />} />

# 4. Add to navigation sidebar
# In src/components/layout/Sidebar.jsx:
{
  key: 'new-tab',
  icon: <DatabaseOutlined />,
  label: 'New Tab',
  path: '/new-tab',
}
```

### Task 2: Update Metabase Card

```bash
# 1. Open Metabase → Find card
# 2. Edit SQL query
# 3. Save changes
# 4. React dashboard automatically uses updated data (no code changes needed)
# 5. Test in browser
```

### Task 3: Fix a Bug

```bash
# 1. Create bugfix branch
git checkout -b bugfix/fix-loading-error

# 2. Identify the issue
# - Check browser console
# - Check React DevTools
# - Check network tab

# 3. Fix the bug
# - Edit relevant file(s)
# - Test the fix

# 4. Commit and push
git add .
git commit -m "fix: Resolve loading81 undefined error in SLAMonitoring"
git push origin bugfix/fix-loading-error

# 5. Create pull request (if team) or merge to main
```

### Task 4: Update Dependencies

```bash
# Check outdated packages
yarn outdated

# Update specific package
yarn upgrade antd

# Update all packages
yarn upgrade

# Update Vite
yarn upgrade vite@latest

# Test after updates
yarn run dev
# ... verify everything works ...

# Commit changes
git add package.json yarn.lock
git commit -m "chore: Update dependencies (Vite 7.3.1, Ant Design 6.3.0)"
```

### Task 5: Debug Performance Issue

```bash
# 1. Open React DevTools Profiler
# - Install React DevTools extension
# - Open DevTools → Profiler tab
# - Click "Record" → Interact with app → Click "Stop"

# 2. Identify slow components
# - Look for components with long render times
# - Check for unnecessary re-renders

# 3. Optimize
# - Add React.memo() for expensive components
# - Use useMemo() for expensive calculations
# - Use useCallback() for event handlers

# Example:
const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = React.useMemo(() => {
    return data.map(/* expensive operation */);
  }, [data]);

  return <div>{processedData}</div>;
});
```

---

## Best Practices Summary

### Do's ✅

- **Write clear commit messages**
- **Test before committing**
- **Handle loading and error states**
- **Use meaningful variable names**
- **Add comments for complex logic**
- **Keep components small and focused**
- **Use React DevTools for debugging**
- **Check browser console regularly**

### Don'ts ❌

- **Don't commit broken code**
- **Don't push directly to main**
- **Don't ignore warnings**
- **Don't use magic numbers (use constants)**
- **Don't duplicate code (DRY principle)**
- **Don't skip testing**
- **Don't commit console.log() statements**

---

## Quick Reference

### Essential Commands

```bash
# Start development
docker compose up -d && cd btrc-react-regional && yarn run dev

# Stop development
docker compose down

# View logs
docker compose logs -f
yarn run dev  # React logs

# Rebuild
docker compose build --no-cache
yarn install

# Run tests (if configured)
yarn test

# Build production
yarn build
```

### Useful Shortcuts

| Action | Shortcut |
|--------|----------|
| Save file | Ctrl+S |
| Open DevTools | F12 |
| Refresh browser | Ctrl+R |
| Hard refresh | Ctrl+Shift+R |
| Search files (VS Code) | Ctrl+P |
| Search text (VS Code) | Ctrl+Shift+F |
| Git commit (VS Code) | Ctrl+Enter |

---

## Next Steps

1. **Practice**: Try adding a simple chart component
2. **Explore**: Familiarize yourself with Metabase queries
3. **Read**: Review existing components for patterns
4. **Experiment**: Test different filter combinations
5. **Document**: Update docs when you learn something new

---

## Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Ant Design Components](https://ant.design/components/overview/)
- [ECharts Examples](https://echarts.apache.org/examples/en/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
