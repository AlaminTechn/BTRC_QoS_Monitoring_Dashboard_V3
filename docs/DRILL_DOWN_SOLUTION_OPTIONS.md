# Map Drill-Down Solution Options - BTRC QoS Dashboard

**Date:** 2026-02-09
**Critical Requirement:** R2.1 Division Performance Map - "click division to drill into districts"
**Current Issue:** Metabase v0.58 URL-based click behaviors not working on maps or tables

---

## Current State

✅ **Working:**
- Dashboard exists with 26 cards across 3 tabs
- Choropleth maps for Divisions (8) and Districts (64)
- Dropdown filters (Division, District, ISP)
- All data queries returning correct results
- Download/export buttons functional

❌ **Not Working:**
- Click on Division name/map → Navigate to district view (URL should change)
- Click on District name/map → Navigate to ISP view
- Breadcrumb navigation back through levels

---

## Option 1: Embedded Metabase + Custom JavaScript (QUICK FIX - 2-3 Days)

### Approach
Create a custom HTML page that:
1. Embeds Metabase dashboard via iframe
2. Adds JavaScript click handlers on the embedded charts
3. Listens for click events and manually navigates to dashboard with parameters

### Implementation
```html
<iframe id="metabase-dashboard" src="http://localhost:3000/dashboard/6"></iframe>
<script>
// Listen for clicks inside iframe
document.getElementById('metabase-dashboard').addEventListener('message', (event) => {
  if (event.data.type === 'division-click') {
    window.location.href = `/dashboard/6?division=${event.data.value}`;
  }
});
</script>
```

### Pros
- ✅ Quick (2-3 days)
- ✅ Keep all existing Metabase dashboards
- ✅ Full control over click behavior
- ✅ No database migration

### Cons
- ❌ Requires custom hosting (separate from Metabase)
- ❌ iframe communication limitations
- ❌ Metabase updates might break implementation
- ❌ More complex maintenance

### Effort
- **Development:** 2-3 days
- **Testing:** 1 day
- **Total:** 3-4 days

### Files to Create
- `custom_dashboard_wrapper.html` - Main HTML wrapper
- `dashboard_handler.js` - Click event handlers
- `nginx.conf` - Serve custom HTML + proxy Metabase

---

## Option 2: Switch to Helical Insight (NATIVE DRILL-DOWN - 1-2 Weeks)

### Why Helical Insight
From `docs/DRILL_DOWN_FILTER_TOOLS_COMPARISON.md`:
> **Helical Insight: BEST for Drill-Down Requirements**
> - Native map hierarchy drill-down (Division → District → Upazila)
> - Click region to filter dashboard
> - Drill-through built-in
> - Custom GeoJSON support

### Migration Path
1. **Day 1-2:** Install Helical Insight Docker, connect to TimescaleDB
2. **Day 3-5:** Upload Bangladesh GeoJSON, configure maps
3. **Day 6-8:** Recreate 26 charts from Metabase
4. **Day 9-10:** Configure drill-down hierarchy
5. **Day 11-12:** Testing & refinement

### Pros
- ✅ **Native map drill-down** (only OSS tool with this feature)
- ✅ Click Division → automatically shows districts
- ✅ Hierarchy support (National → Division → District)
- ✅ Self-hosted, free community edition
- ✅ Meets spec requirements 100%

### Cons
- ❌ Lose 2-3 days of Metabase work
- ❌ Smaller community than Metabase
- ❌ UI less modern than Metabase
- ❌ Learning curve for new tool

### Effort
- **Installation:** 1 day
- **Migration:** 7-10 days
- **Total:** 1-2 weeks

### Risk
- Medium - New tool, less documentation

---

## Option 3: Custom React Dashboard (FULL CONTROL - 10-15 Weeks)

### Approach
Build dashboard from scratch using:
- **Frontend:** Next.js + React + Tremor + React-Leaflet
- **Backend:** Next.js API routes + Prisma
- **Database:** Existing TimescaleDB

See `docs/CUSTOM_REACT_DASHBOARD_OPTION.md` for full specification.

### Pros
- ✅ **Full control** over drill-down behavior
- ✅ **Perfect UX** - exactly as you want it
- ✅ Custom branding, layout, features
- ✅ No tool limitations
- ✅ Production-ready solution

### Cons
- ❌ **10-15 weeks** development time
- ❌ Requires React developer
- ❌ Ongoing maintenance needed
- ❌ Must write all SQL queries manually
- ❌ No SQL Lab for ad-hoc queries

### Effort
- **Foundation:** 2-3 weeks
- **Components:** 3-4 weeks
- **Maps + Drill-down:** 2-3 weeks
- **Dashboards:** 2-3 weeks
- **Polish + Deploy:** 1-2 weeks
- **Total:** 10-15 weeks (1 developer)

### Cost Estimate
- Development: $15,000-30,000 (varies by region)
- Maintenance: $2,000-5,000/month

---

## Option 4: Accept Metabase Limitations (WORKAROUND - 0 Days)

### Approach
Use filters instead of drill-down navigation:
1. User clicks "Dhaka" → Filter is set (but URL doesn't change)
2. Dashboard updates to show Dhaka districts
3. To go back: Clear filter (no back button support)

### Pros
- ✅ **Works NOW** (already implemented)
- ✅ Zero additional work
- ✅ Functional, just not perfect
- ✅ All data is correct

### Cons
- ❌ No URL navigation (can't use back button)
- ❌ Can't share drill-down state via URL
- ❌ Not true drill-down (spec requirement)
- ❌ Maps don't support click at all

### Effort
- **Development:** 0 days (done)
- **Total:** 0 days

### Spec Compliance
- ⚠️ **Partial** - Filters work, but not "click-to-navigate"

---

## Hybrid Approach (RECOMMENDED)

### Phase 1: POC with Metabase (NOW - Complete)
- ✅ Use current Metabase dashboard
- ✅ Accept filter-based drill-down (not navigation)
- ✅ Demonstrate functionality to BTRC
- ✅ Get feedback on data and layout

### Phase 2: Quick Fix (If BTRC Requires True Drill-Down)
- 🔧 Implement **Option 1** (Embedded Metabase + JavaScript)
- 📅 Timeline: 3-4 days
- 💰 Cost: Minimal (developer time only)

### Phase 3: Production Decision (After POC Approval)
Based on BTRC feedback:
- **If drill-down CRITICAL** → **Option 2** (Helical Insight) or **Option 3** (Custom React)
- **If filters acceptable** → Keep Metabase, polish features
- **If budget available** → **Option 3** (Custom React) for long-term

---

## Decision Matrix

| Criteria | Metabase + JS (Opt 1) | Helical Insight (Opt 2) | Custom React (Opt 3) | Accept Workaround (Opt 4) |
|----------|----------------------|------------------------|---------------------|--------------------------|
| **Meets Spec 100%** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Partial |
| **Timeline** | 3-4 days | 1-2 weeks | 10-15 weeks | 0 days |
| **Cost** | Low | Low | High | Zero |
| **Maintenance** | Medium | Low | High | Low |
| **Map Drill-Down** | ✅ Custom | ✅ Native | ✅ Full Control | ❌ None |
| **Risk** | Low | Medium | Low | None |
| **Tool Change** | No | Yes | Yes | No |

---

## My Recommendation

### For POC Stage (Next 2-3 Days)
**Choose Option 1: Embedded Metabase + Custom JavaScript**

**Why:**
1. Quick implementation (3-4 days)
2. Meets spec requirement for drill-down
3. Keeps all existing Metabase work
4. Low risk, proven approach
5. Can pivot to other options later if needed

### For Production (After BTRC Approval)
**Choose Option 2: Helical Insight**

**Why:**
1. Native drill-down (no hacks)
2. Free and self-hosted
3. Better long-term maintenance
4. Designed for hierarchical navigation
5. Only 1-2 weeks migration time

---

## Next Steps

**If you choose Option 1 (Embedded Metabase + JS):**
1. I'll create `custom_dashboard_wrapper.html`
2. Add JavaScript click handlers for maps and tables
3. Set up nginx to serve custom HTML + proxy Metabase
4. Test drill-down navigation
5. **Timeline: Ready in 3-4 days**

**If you choose Option 2 (Helical Insight):**
1. Install Helical Insight via Docker
2. Connect to existing TimescaleDB
3. Migrate dashboards one by one
4. Configure drill-down hierarchy
5. **Timeline: Ready in 1-2 weeks**

**If you choose Option 3 (Custom React):**
1. Set up Next.js project structure
2. Implement core components (weeks 1-3)
3. Build map drill-down (weeks 4-6)
4. Create dashboards (weeks 7-9)
5. **Timeline: Ready in 10-15 weeks**

**If you choose Option 4 (Accept Limitations):**
1. No work needed
2. Document limitation for BTRC
3. Proceed with POC as-is

---

## What Do You Want to Do?

Please let me know which option you prefer, and I'll start implementation immediately.
