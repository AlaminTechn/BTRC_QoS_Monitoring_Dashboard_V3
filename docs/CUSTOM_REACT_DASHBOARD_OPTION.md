# Custom React Dashboard Option - Technical Specification

**Date:** 2026-02-07
**Purpose:** Evaluate building custom dashboard with React and chart libraries
**Requirements:** Drill-down, Filters, Choropleth Maps, PostgreSQL/TimescaleDB

---

## Executive Summary

| Aspect | BI Tool (Superset/Metabase) | Custom React Dashboard |
|--------|----------------------------|------------------------|
| **Development Time** | Days | Weeks to Months |
| **Drill-Down Support** | Limited/Workaround | **Full Control** |
| **Filter Flexibility** | Pre-built | **Full Control** |
| **Map Customization** | Limited | **Full Control** |
| **Maintenance** | Low | High |
| **Cost** | Free (OSS) | Developer Time |
| **Scalability** | Good | Excellent |

**Verdict:** Custom React dashboard gives **FULL CONTROL** over drill-down and filters, but requires significant development effort.

---

## YES - You Can Build Everything with React

### What's Possible with Custom Code:

| Requirement | Achievable | Libraries |
|-------------|------------|-----------|
| Division → District → Upazila Drill-Down | **YES** | Leaflet, MapLibre, deck.gl |
| Click Map Region → Filter Dashboard | **YES** | React state + GeoJSON events |
| Cross-Filtering Between Charts | **YES** | React Context/Redux/Zustand |
| Native Filter Dropdowns | **YES** | Tremor, Shadcn, Ant Design |
| Cascading Filters (Division → District) | **YES** | React state management |
| Choropleth Maps with Custom GeoJSON | **YES** | Leaflet, MapLibre, D3.js |
| KPI Cards | **YES** | Tremor, Recharts |
| Tables with Sorting/Filtering | **YES** | TanStack Table, AG Grid |
| Time Series Charts | **YES** | Recharts, ECharts, Nivo |
| Real-Time Updates | **YES** | SWR, React Query, WebSocket |
| PostgreSQL/TimescaleDB Connection | **YES** | API routes (Next.js/Express) |
| Export to PDF/Excel | **YES** | jsPDF, xlsx libraries |
| Role-Based Access | **YES** | NextAuth, custom auth |

---

## Recommended Technology Stack

### Option A: Next.js Full-Stack (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
├─────────────────────────────────────────────────────────────┤
│  Framework    │ Next.js 14+ (App Router)                    │
│  UI Library   │ Tremor + Tailwind CSS + Shadcn/ui           │
│  Charts       │ Recharts / ECharts / Nivo                   │
│  Maps         │ React-Leaflet + Leaflet / MapLibre GL JS    │
│  Tables       │ TanStack Table (React Table v8)             │
│  State        │ Zustand / React Context + SWR               │
│  Forms        │ React Hook Form + Zod                       │
├─────────────────────────────────────────────────────────────┤
│                     BACKEND (API)                            │
├─────────────────────────────────────────────────────────────┤
│  API Routes   │ Next.js API Routes / tRPC                   │
│  ORM          │ Prisma / Drizzle ORM                        │
│  Database     │ PostgreSQL + TimescaleDB                    │
│  Auth         │ NextAuth.js / Clerk                         │
│  Caching      │ Redis (optional)                            │
└─────────────────────────────────────────────────────────────┘
```

### Option B: Separate Frontend/Backend

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND     │ React + Vite                                │
│  BACKEND      │ Node.js + Express / Fastify                 │
│  API          │ REST or GraphQL (Hasura)                    │
│  Database     │ PostgreSQL + TimescaleDB                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Package Recommendations

### 1. Chart Libraries

| Library | Best For | Drill-Down | License | Bundle Size |
|---------|----------|------------|---------|-------------|
| **Recharts** | Simple charts, good defaults | Manual | MIT | 140KB |
| **ECharts** | Complex, interactive | Built-in | Apache 2.0 | 400KB+ |
| **Nivo** | Beautiful, D3-based | Manual | MIT | Varies |
| **Victory** | Animations | Manual | MIT | 200KB |
| **Highcharts** | Enterprise features | Built-in | Commercial* | 300KB |

*Highcharts free for non-commercial/personal use

**Recommendation:**
- **Recharts** for simple KPI/line/bar charts
- **ECharts** for complex interactive charts with drill-down

### 2. Map Libraries

| Library | Best For | Drill-Down | GeoJSON | License |
|---------|----------|------------|---------|---------|
| **React-Leaflet** | Easy setup, plugins | Yes (events) | Yes | BSD |
| **MapLibre GL JS** | Vector tiles, WebGL | Yes (events) | Yes | BSD |
| **deck.gl** | Big data, WebGL | Yes | Yes | MIT |
| **React Simple Maps** | Simple choropleth | Manual | Yes | MIT |
| **Mapbox GL** | Premium features | Yes | Yes | Commercial |

**Recommendation:**
- **React-Leaflet** for simplicity and reliability
- **MapLibre GL JS** for performance with many features

### 3. UI Component Libraries

| Library | Style | Components | Maintained |
|---------|-------|------------|------------|
| **Tremor** | Tailwind | Dashboard-focused | Yes |
| **Shadcn/ui** | Tailwind | Copy-paste components | Yes |
| **Ant Design** | Custom CSS | Complete suite | Yes |
| **MUI (Material-UI)** | Material Design | Complete suite | Yes |
| **Chakra UI** | CSS-in-JS | Accessible | Yes |

**Recommendation:** **Tremor** (built for dashboards) + **Shadcn/ui** (flexible)

### 4. Table Libraries

| Library | Features | Virtual Scroll | License |
|---------|----------|----------------|---------|
| **TanStack Table** | Headless, flexible | Yes | MIT |
| **AG Grid** | Enterprise features | Yes | MIT/Commercial |
| **MUI DataGrid** | Material Design | Yes | MIT/Commercial |

**Recommendation:** **TanStack Table** (free, flexible, headless)

### 5. State Management

| Library | Complexity | Best For |
|---------|------------|----------|
| **Zustand** | Simple | Small-medium apps |
| **React Query/TanStack Query** | Medium | Server state |
| **Redux Toolkit** | Complex | Large apps |
| **Jotai** | Simple | Atomic state |

**Recommendation:** **Zustand** + **TanStack Query (SWR alternative)**

---

## Implementation Architecture

### Folder Structure (Next.js)

```
btrc-dashboard/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── executive/
│   │   │   └── page.tsx
│   │   ├── regulatory/
│   │   │   └── page.tsx
│   │   ├── operational/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── api/
│   │   ├── measurements/
│   │   │   └── route.ts
│   │   ├── violations/
│   │   │   └── route.ts
│   │   ├── divisions/
│   │   │   └── route.ts
│   │   └── districts/
│   │       └── route.ts
│   └── layout.tsx
├── components/
│   ├── charts/
│   │   ├── KPICard.tsx
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   └── StackedBarChart.tsx
│   ├── maps/
│   │   ├── ChoroplethMap.tsx
│   │   ├── DivisionMap.tsx
│   │   └── DistrictMap.tsx
│   ├── filters/
│   │   ├── DivisionFilter.tsx
│   │   ├── DistrictFilter.tsx
│   │   ├── ISPFilter.tsx
│   │   ├── DateRangeFilter.tsx
│   │   └── FilterProvider.tsx
│   ├── tables/
│   │   ├── DataTable.tsx
│   │   └── ViolationsTable.tsx
│   └── layout/
│       ├── Sidebar.tsx
│       ├── Header.tsx
│       └── DashboardLayout.tsx
├── lib/
│   ├── db.ts              # Prisma client
│   ├── queries/
│   │   ├── measurements.ts
│   │   ├── violations.ts
│   │   └── geography.ts
│   └── utils.ts
├── hooks/
│   ├── useFilters.ts
│   ├── useMeasurements.ts
│   └── useViolations.ts
├── store/
│   └── filterStore.ts     # Zustand store
├── types/
│   └── index.ts
├── geodata/
│   ├── divisions.geojson
│   ├── districts.geojson
│   └── upazilas.geojson
└── prisma/
    └── schema.prisma
```

---

## Drill-Down Implementation Example

### Map Component with Drill-Down

```tsx
// components/maps/DrillDownMap.tsx
import { useState } from 'react';
import { MapContainer, GeoJSON } from 'react-leaflet';
import divisionsGeoJSON from '@/geodata/divisions.geojson';
import districtsGeoJSON from '@/geodata/districts.geojson';
import upazilasGeoJSON from '@/geodata/upazilas.geojson';

type DrillLevel = 'national' | 'division' | 'district';

export function DrillDownMap({ onRegionSelect }) {
  const [level, setLevel] = useState<DrillLevel>('national');
  const [selectedDivision, setSelectedDivision] = useState<string | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);

  const getCurrentGeoJSON = () => {
    switch (level) {
      case 'national':
        return divisionsGeoJSON;
      case 'division':
        return {
          ...districtsGeoJSON,
          features: districtsGeoJSON.features.filter(
            f => f.properties.division_id === selectedDivision
          )
        };
      case 'district':
        return {
          ...upazilasGeoJSON,
          features: upazilasGeoJSON.features.filter(
            f => f.properties.district_id === selectedDistrict
          )
        };
    }
  };

  const handleRegionClick = (feature) => {
    if (level === 'national') {
      setSelectedDivision(feature.properties.id);
      setLevel('division');
    } else if (level === 'division') {
      setSelectedDistrict(feature.properties.id);
      setLevel('district');
    }
    onRegionSelect(feature.properties);
  };

  const handleDrillUp = () => {
    if (level === 'district') {
      setSelectedDistrict(null);
      setLevel('division');
    } else if (level === 'division') {
      setSelectedDivision(null);
      setLevel('national');
    }
  };

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex gap-2 mb-2">
        <button onClick={() => { setLevel('national'); setSelectedDivision(null); }}>
          Bangladesh
        </button>
        {selectedDivision && (
          <>
            <span>→</span>
            <button onClick={() => { setLevel('division'); setSelectedDistrict(null); }}>
              {selectedDivision}
            </button>
          </>
        )}
        {selectedDistrict && (
          <>
            <span>→</span>
            <span>{selectedDistrict}</span>
          </>
        )}
      </div>

      {/* Map */}
      <MapContainer center={[23.8, 90.4]} zoom={7}>
        <GeoJSON
          data={getCurrentGeoJSON()}
          style={(feature) => ({
            fillColor: getColor(feature.properties.value),
            weight: 1,
            color: '#666',
            fillOpacity: 0.7
          })}
          onEachFeature={(feature, layer) => {
            layer.on('click', () => handleRegionClick(feature));
          }}
        />
      </MapContainer>
    </div>
  );
}
```

### Filter State Management

```tsx
// store/filterStore.ts
import { create } from 'zustand';

interface FilterState {
  division: string | null;
  district: string | null;
  isp: string | null;
  dateRange: { start: Date; end: Date };

  setDivision: (division: string | null) => void;
  setDistrict: (district: string | null) => void;
  setISP: (isp: string | null) => void;
  setDateRange: (range: { start: Date; end: Date }) => void;
  resetFilters: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  division: null,
  district: null,
  isp: null,
  dateRange: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date()
  },

  setDivision: (division) => set({ division, district: null }), // Reset district when division changes
  setDistrict: (district) => set({ district }),
  setISP: (isp) => set({ isp }),
  setDateRange: (dateRange) => set({ dateRange }),
  resetFilters: () => set({ division: null, district: null, isp: null }),
}));
```

### Cross-Filtering Hook

```tsx
// hooks/useMeasurements.ts
import { useQuery } from '@tanstack/react-query';
import { useFilterStore } from '@/store/filterStore';

export function useMeasurements() {
  const { division, district, isp, dateRange } = useFilterStore();

  return useQuery({
    queryKey: ['measurements', division, district, isp, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (division) params.append('division', division);
      if (district) params.append('district', district);
      if (isp) params.append('isp', isp);
      params.append('start', dateRange.start.toISOString());
      params.append('end', dateRange.end.toISOString());

      const res = await fetch(`/api/measurements?${params}`);
      return res.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });
}
```

---

## Development Timeline Estimate

### Phase 1: Foundation (2-3 weeks)
- [ ] Project setup (Next.js, TypeScript, Tailwind)
- [ ] Database connection (Prisma + TimescaleDB)
- [ ] Authentication (NextAuth)
- [ ] Base layout and navigation
- [ ] Filter state management

### Phase 2: Core Components (3-4 weeks)
- [ ] KPI card components
- [ ] Chart components (Line, Bar, Stacked)
- [ ] Table component with sorting/filtering
- [ ] Basic API routes

### Phase 3: Map Implementation (2-3 weeks)
- [ ] Choropleth map component
- [ ] GeoJSON loading and styling
- [ ] Click-to-filter functionality
- [ ] Drill-down navigation (Division → District → Upazila)
- [ ] Breadcrumb navigation

### Phase 4: Dashboards (2-3 weeks)
- [ ] Executive Dashboard
- [ ] Regulatory Dashboard
- [ ] Operational Dashboard
- [ ] Cross-filtering between components

### Phase 5: Polish & Deploy (1-2 weeks)
- [ ] Performance optimization
- [ ] Error handling
- [ ] Loading states
- [ ] Export functionality
- [ ] Deployment (Docker/Vercel)

**Total Estimate: 10-15 weeks** (1 developer)

---

## Pros vs Cons

### Advantages of Custom React Dashboard

| Advantage | Details |
|-----------|---------|
| **Full Drill-Down Control** | Click Division → District → Upazila works exactly as needed |
| **Custom Filter Logic** | Cascading filters, complex conditions |
| **UI/UX Flexibility** | Match BTRC branding exactly |
| **Performance** | Optimize for specific use cases |
| **No Tool Limitations** | Not constrained by BI tool features |
| **Ownership** | Full control of codebase |
| **Integration** | Easy to add authentication, APIs |

### Disadvantages of Custom React Dashboard

| Disadvantage | Details |
|--------------|---------|
| **Development Time** | 10-15 weeks vs days for BI tool |
| **Maintenance** | Ongoing developer needed |
| **SQL Queries** | Must write all queries manually |
| **No SQL Lab** | No ad-hoc query interface |
| **Bug Fixes** | Your responsibility |
| **Feature Additions** | Require development work |

---

## Cost Comparison

| Aspect | BI Tool (Superset) | Custom React |
|--------|-------------------|--------------|
| Initial Development | $0 (free tool) | $15,000-30,000* |
| Monthly Hosting | ~$50-100 | ~$50-100 |
| Maintenance | Low (updates) | $2,000-5,000/month* |
| New Features | Sometimes available | Development cost |

*Estimated developer costs (varies by region)

---

## Recommendation

### When to Choose Custom React Dashboard:

1. **Drill-down is non-negotiable** - Must click map regions to drill into sub-regions
2. **Unique UI requirements** - BTRC branding, specific layouts
3. **Long-term product** - Will be used for years, worth investment
4. **In-house developers** - Team can maintain the code
5. **Complex integrations** - Need custom APIs, authentication

### When to Stick with BI Tool:

1. **POC/MVP stage** - Need quick results
2. **Limited budget** - Can't afford development time
3. **No developers** - No team to maintain custom code
4. **Standard requirements** - Filter-based drill-down is acceptable
5. **SQL Lab needed** - Ad-hoc queries for analysts

---

## Hybrid Approach (Recommended)

```
Phase 1 (Now): Use Superset for POC
├── Quick to deploy
├── Demonstrates value to BTRC
└── Identifies exact requirements

Phase 2 (After POC approval): Evaluate options
├── Option A: Helical Insight (if drill-down sufficient)
├── Option B: Metabase (if workarounds acceptable)
└── Option C: Custom React (if full control needed)

Phase 3 (Production): Build custom if needed
├── Use POC learnings
├── Exact requirements known
└── Budget secured
```

---

## Quick Start Commands

```bash
# Create Next.js project with TypeScript and Tailwind
npx create-next-app@latest btrc-dashboard --typescript --tailwind --app

# Install core dependencies
cd btrc-dashboard
npm install @tremor/react recharts leaflet react-leaflet
npm install @tanstack/react-query zustand
npm install prisma @prisma/client

# Install map dependencies
npm install @types/leaflet

# Initialize Prisma
npx prisma init

# Development
npm run dev
```

---

## Sources

- [Tremor React Dashboard Library](https://www.tremor.so/)
- [Recharts Documentation](https://recharts.org/)
- [React-Leaflet Documentation](https://react-leaflet.js.org/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [TanStack Query](https://tanstack.com/query)
- [Zustand State Management](https://zustand-demo.pmnd.rs/)
- [Building Choropleth Maps with React and D3.js](https://www.react-graph-gallery.com/choropleth-map)
- [Syncfusion React Maps with Drill-Down](https://www.syncfusion.com/react-components/react-maps-library)
- [Next.js Dashboard Tutorial](https://www.freecodecamp.org/news/build-an-analytical-dashboard-with-nextjs/)
- [TimescaleDB Custom Dashboards](https://docs.timescale.com/timescaledb/latest/tutorials/custom-timescaledb-dashboards/)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-07
