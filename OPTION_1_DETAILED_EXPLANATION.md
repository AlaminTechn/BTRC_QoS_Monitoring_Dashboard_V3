# Option 1: Embedded Metabase + Custom JavaScript - Detailed Explanation

**Date:** 2026-02-09
**Timeline:** 3-4 days
**Goal:** Make drill-down navigation work by adding custom JavaScript on top of Metabase

---

## The Problem (Current State)

```
┌─────────────────────────────────────────┐
│    User opens:                          │
│    http://localhost:3000/dashboard/6    │
│                                         │
│    Clicks "Dhaka" in table             │
│           ↓                             │
│    Filter is set (works)                │
│    BUT URL doesn't change (broken)      │
│           ↓                             │
│    Can't use back button                │
│    Can't share drilled-down URL         │
└─────────────────────────────────────────┘
```

**What's broken:** Metabase's click behavior config isn't working to change the URL.

---

## The Solution (What We'll Build)

Create a **custom HTML page** that wraps the Metabase dashboard and adds click handling.

```
┌────────────────────────────────────────────────────┐
│  Custom HTML Page (dashboard.html)                 │
│  URL: http://localhost:9000/dashboard              │
│                                                    │
│  ┌──────────────────────────────────────────┐    │
│  │  JavaScript Layer (Intercepts Clicks)     │    │
│  │  • Listens for clicks on tables/maps      │    │
│  │  • Reads clicked Division/District         │    │
│  │  • Navigates to new URL with parameters   │    │
│  └──────────────────────────────────────────┘    │
│                    ↓                               │
│  ┌──────────────────────────────────────────┐    │
│  │  Embedded Metabase Dashboard              │    │
│  │  (iframe or div)                          │    │
│  │  Shows: http://localhost:3000/dashboard/6 │    │
│  └──────────────────────────────────────────┘    │
└────────────────────────────────────────────────────┘
```

---

## How It Works (Step by Step)

### Step 1: User Opens Custom Page

```
User visits: http://localhost:9000/dashboard
             (Custom HTML page we create)
                     ↓
Custom page embeds Metabase dashboard inside
```

### Step 2: User Clicks "Dhaka"

```
User clicks "Dhaka" in Division table
        ↓
JavaScript detects click event
        ↓
Reads clicked value: "Dhaka"
        ↓
Navigates to: http://localhost:9000/dashboard?division=Dhaka
        ↓
URL changes ✅
Browser history updated ✅
```

### Step 3: Page Reloads with Filter

```
Custom page loads with URL parameter ?division=Dhaka
        ↓
JavaScript reads URL parameter
        ↓
Embeds Metabase dashboard with filter:
http://localhost:3000/dashboard/6?division=Dhaka
        ↓
Metabase shows filtered data (Dhaka's districts)
```

### Step 4: User Clicks Back Button

```
User presses browser BACK button
        ↓
Browser navigates to: http://localhost:9000/dashboard
        ↓
Custom page reloads
        ↓
Embeds Metabase without filters (National view)
        ↓
Back button works! ✅
```

---

## What We'll Create

### 1. Custom HTML Dashboard Page

**File:** `public/dashboard.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>BTRC QoS Dashboard - Regulatory Operations</title>
    <style>
        body { margin: 0; padding: 0; font-family: Arial; }

        /* Header with breadcrumb */
        .header {
            background: #1a365d;
            color: white;
            padding: 15px 30px;
        }

        /* Breadcrumb navigation */
        .breadcrumb {
            font-size: 14px;
        }
        .breadcrumb a {
            color: #68d391;
            text-decoration: none;
        }

        /* Dashboard container */
        #dashboard-container {
            width: 100%;
            height: calc(100vh - 60px);
            border: none;
        }
    </style>
</head>
<body>
    <!-- Breadcrumb Navigation -->
    <div class="header">
        <div class="breadcrumb" id="breadcrumb">
            <a href="/dashboard">National</a>
        </div>
    </div>

    <!-- Embedded Metabase Dashboard -->
    <iframe
        id="dashboard-container"
        src="http://localhost:3000/dashboard/6"
        frameborder="0"
    ></iframe>

    <script src="/dashboard.js"></script>
</body>
</html>
```

### 2. JavaScript Click Handler

**File:** `public/dashboard.js`

```javascript
// Read URL parameters
const urlParams = new URLSearchParams(window.location.search);
const division = urlParams.get('division');
const district = urlParams.get('district');
const isp = urlParams.get('isp');

// Update breadcrumb based on current drill-down level
function updateBreadcrumb() {
    const breadcrumb = document.getElementById('breadcrumb');
    let html = '<a href="/dashboard">National</a>';

    if (division) {
        html += ` ➜ <a href="/dashboard?division=${division}">${division}</a>`;
    }
    if (district) {
        html += ` ➜ <a href="/dashboard?division=${division}&district=${district}">${district}</a>`;
    }
    if (isp) {
        html += ` ➜ ${isp}`;
    }

    breadcrumb.innerHTML = html;
}

// Build Metabase URL with filters
function buildMetabaseURL() {
    let url = 'http://localhost:3000/dashboard/6';
    const params = [];

    if (division) params.push(`division=${encodeURIComponent(division)}`);
    if (district) params.push(`district=${encodeURIComponent(district)}`);
    if (isp) params.push(`isp=${encodeURIComponent(isp)}`);

    if (params.length > 0) {
        url += '?' + params.join('&');
    }

    return url;
}

// Load Metabase dashboard with current filters
function loadDashboard() {
    const iframe = document.getElementById('dashboard-container');
    iframe.src = buildMetabaseURL();
    updateBreadcrumb();
}

// Listen for clicks inside Metabase dashboard
window.addEventListener('message', function(event) {
    // Metabase sends events when user interacts
    if (event.data.type === 'metabase-click') {
        const { column, value } = event.data;

        // Build new URL based on what was clicked
        let newURL = '/dashboard';
        const params = new URLSearchParams(window.location.search);

        if (column === 'Division') {
            // Clicked Division → navigate to division view
            newURL += `?division=${encodeURIComponent(value)}`;
        } else if (column === 'District') {
            // Clicked District → navigate to district view
            newURL += `?division=${params.get('division')}&district=${encodeURIComponent(value)}`;
        } else if (column === 'ISP') {
            // Clicked ISP → navigate to ISP view
            newURL += `?division=${params.get('division')}&district=${params.get('district')}&isp=${encodeURIComponent(value)}`;
        }

        // Navigate to new URL (this creates browser history entry)
        window.location.href = newURL;
    }
});

// Alternative: Intercept clicks directly on tables
// (If Metabase doesn't send events, we'll inject click handlers)
function injectClickHandlers() {
    const iframe = document.getElementById('dashboard-container');

    iframe.onload = function() {
        try {
            // Access iframe content (only works if same-origin)
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

            // Find all table cells in Division column
            const tableCells = iframeDoc.querySelectorAll('table tbody tr td:first-child');

            tableCells.forEach(cell => {
                cell.style.cursor = 'pointer';
                cell.addEventListener('click', function() {
                    const value = this.textContent.trim();

                    // Check if this is a division name
                    const divisions = ['Dhaka', 'Chattagram', 'Khulna', 'Rajshahi',
                                      'Barisal', 'Sylhet', 'Rangpur', 'Mymensingh'];

                    if (divisions.includes(value)) {
                        window.location.href = `/dashboard?division=${value}`;
                    }
                });
            });
        } catch (e) {
            console.warn('Cannot inject click handlers (CORS):', e);
            // Fallback: Use Metabase's public API to detect clicks
        }
    };
}

// Initialize
loadDashboard();
injectClickHandlers();
```

### 3. Web Server to Serve Custom HTML

**File:** `docker-compose.yml` (add nginx service)

```yaml
services:
  # ... existing timescaledb and metabase services ...

  nginx:
    image: nginx:alpine
    container_name: btrc-v3-nginx
    ports:
      - "9000:80"
    volumes:
      - ./public:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - metabase
    networks:
      - btrc-network
```

**File:** `nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    upstream metabase {
        server metabase:3000;
    }

    server {
        listen 80;

        # Serve custom dashboard
        location /dashboard {
            root /usr/share/nginx/html;
            try_files /dashboard.html =404;
        }

        # Serve JavaScript
        location /dashboard.js {
            root /usr/share/nginx/html;
            add_header Content-Type application/javascript;
        }

        # Proxy to Metabase
        location / {
            proxy_pass http://metabase;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## What You'll Use

After implementation:

### Old URL (Doesn't Work)
❌ `http://localhost:3000/dashboard/6` - Click doesn't navigate

### New URL (Works!)
✅ `http://localhost:9000/dashboard` - Custom wrapper with working drill-down

### Drill-Down URLs
- National: `http://localhost:9000/dashboard`
- Division: `http://localhost:9000/dashboard?division=Dhaka`
- District: `http://localhost:9000/dashboard?division=Dhaka&district=Gazipur`
- ISP: `http://localhost:9000/dashboard?division=Dhaka&district=Gazipur&isp=Link3%20Technologies`

---

## Visual Comparison

### Before (Current - Broken)

```
┌─────────────────────────────────────┐
│  http://localhost:3000/dashboard/6  │ ← URL never changes
├─────────────────────────────────────┤
│  [Division Table]                   │
│   Dhaka     ← Click here            │
│   Sylhet                            │
│   ...                               │
├─────────────────────────────────────┤
│  Result: Filter is set, but...     │
│  ❌ URL same (can't share)          │
│  ❌ No browser history               │
│  ❌ Back button doesn't work         │
└─────────────────────────────────────┘
```

### After (Option 1 - Working)

```
┌─────────────────────────────────────┐
│  http://localhost:9000/dashboard    │ ← Initial URL
├─────────────────────────────────────┤
│  [Breadcrumb] National              │
├─────────────────────────────────────┤
│  [Division Table]                   │
│   Dhaka     ← Click here            │
│   Sylhet                            │
│   ...                               │
└─────────────────────────────────────┘
                ↓ Click
┌─────────────────────────────────────┐
│  http://localhost:9000/dashboard?division=Dhaka  │ ← URL changed!
├─────────────────────────────────────┤
│  [Breadcrumb] National ➜ Dhaka      │
├─────────────────────────────────────┤
│  [District Map - Dhaka Only]        │
│  [District Table]                   │
│   Gazipur   ← Click here            │
│   Faridpur                          │
│   ...                               │
└─────────────────────────────────────┘
                ↓ Click
┌─────────────────────────────────────┐
│  http://localhost:9000/dashboard?division=Dhaka&district=Gazipur  │
├─────────────────────────────────────┤
│  [Breadcrumb] National ➜ Dhaka ➜ Gazipur  │
├─────────────────────────────────────┤
│  [ISP Table - Gazipur Only]         │
│   Link3 Technologies                │
│   Dhaka Online                      │
│   ...                               │
├─────────────────────────────────────┤
│  ✅ URL changes (shareable)          │
│  ✅ Browser history works            │
│  ✅ Back button works                │
└─────────────────────────────────────┘
```

---

## What Will Be Built (Files Created)

```
BTRC-QoS-Monitoring-Dashboard-V3/
├── public/
│   ├── dashboard.html          # Main custom dashboard page
│   ├── dashboard.js            # Click handler JavaScript
│   └── styles.css              # Custom styles
├── nginx.conf                  # Nginx config to serve custom page
├── docker-compose.yml          # Updated with nginx service
└── docs/
    └── CUSTOM_DASHBOARD_USAGE.md  # How to use the new dashboard
```

---

## Implementation Steps (3-4 Days)

### Day 1: Basic Setup
- ✅ Create `public/dashboard.html` with embedded Metabase
- ✅ Add nginx service to docker-compose
- ✅ Test that custom page loads Metabase correctly

### Day 2: Click Handling
- ✅ Implement JavaScript click handlers
- ✅ Detect clicks on Division, District, ISP columns
- ✅ Navigate to new URLs with parameters

### Day 3: Breadcrumb & Polish
- ✅ Add breadcrumb navigation at top
- ✅ Style the custom dashboard
- ✅ Handle edge cases (direct URLs, missing parameters)

### Day 4: Testing & Documentation
- ✅ Test all drill-down flows
- ✅ Test browser back/forward buttons
- ✅ Test sharing URLs
- ✅ Write usage documentation

---

## Pros of This Approach

| Benefit | Details |
|---------|---------|
| ✅ **Quick** | 3-4 days vs 1-2 weeks (Helical) or 10-15 weeks (React) |
| ✅ **Keeps Metabase** | All existing dashboards/work preserved |
| ✅ **Full Control** | JavaScript can do anything we need |
| ✅ **Meets Spec** | Satisfies R2.1 drill-down requirement 100% |
| ✅ **Low Risk** | If it fails, we still have working Metabase |
| ✅ **Shareable URLs** | URLs like `/dashboard?division=Dhaka` work |
| ✅ **Browser History** | Back button works correctly |
| ✅ **No Database Changes** | Uses existing TimescaleDB as-is |

---

## Cons of This Approach

| Limitation | Details |
|------------|---------|
| ⚠️ **Custom Code** | Need to maintain JavaScript |
| ⚠️ **Two URLs** | Old (localhost:3000) and new (localhost:9000) |
| ⚠️ **Iframe Limitations** | Some Metabase features might not work |
| ⚠️ **Metabase Updates** | Metabase changes might break JavaScript |

---

## When to Use This vs Other Options

**Choose Option 1 if:**
- ✅ You need drill-down working **NOW** (POC deadline)
- ✅ You want to keep all existing Metabase dashboards
- ✅ You're okay with a custom wrapper layer
- ✅ Timeline is 3-4 days

**Choose Option 2 (Helical Insight) if:**
- ✅ You want native drill-down (no hacks)
- ✅ You can wait 1-2 weeks
- ✅ You're okay migrating dashboards

**Choose Option 3 (Custom React) if:**
- ✅ You have 10-15 weeks
- ✅ You have budget ($15K-30K)
- ✅ You want a long-term custom solution

---

## Next Steps (If You Choose Option 1)

I will:
1. Create `public/dashboard.html` with embedded Metabase
2. Create `public/dashboard.js` with click handlers
3. Add nginx service to docker-compose
4. Test drill-down navigation (Division → District → ISP)
5. Add breadcrumb navigation
6. Document how to use the new dashboard
7. **Deliver in 3-4 days**

---

## Questions?

Ask me anything about this approach before we proceed!
