# BTRC QoS Dashboard - Custom Drill-Down Wrapper

## Overview

This custom dashboard wrapper adds **drill-down navigation** to the BTRC QoS Metabase dashboard. It allows users to click on Division → District → ISP names to navigate through data hierarchies with proper URL changes and browser back button support.

## URLs

### Old URL (Metabase Direct)
❌ **http://localhost:3000/dashboard/6** - Click behaviors don't work

### New URL (Custom Wrapper)
✅ **http://localhost:9000/dashboard** - Full drill-down navigation enabled

## Features

### ✅ Drill-Down Navigation
- **National View**: Shows all 8 divisions
- **Division View**: Click division name → Shows 13 districts (e.g., Dhaka)
- **District View**: Click district name → Shows ISPs in that district
- **ISP View**: Click ISP → Shows detailed performance metrics

### ✅ URL-Based Navigation
Each drill-down level has a unique URL:
```
National:  http://localhost:9000/dashboard
Division:  http://localhost:9000/dashboard?division=Dhaka
District:  http://localhost:9000/dashboard?division=Dhaka&district=Gazipur
ISP:       http://localhost:9000/dashboard?division=Dhaka&district=Gazipur&isp=Link3%20Technologies
```

### ✅ Browser Navigation
- **Back Button**: Returns to previous level
- **Forward Button**: Goes forward if you went back
- **Refresh**: Maintains current drill-down state
- **Shareable URLs**: Copy URL and share exact view with colleagues

### ✅ Breadcrumb Navigation
Visual breadcrumb at the top shows your current location:
```
🏠 National → 📍 Dhaka → 🏘️ Gazipur → 🏢 Link3 Technologies
```

Click any breadcrumb level to jump back to that view.

### ✅ Reset Button
Click **"↺ Reset View"** to return to National view instantly.

### ✅ Keyboard Shortcuts
- **Alt + Home**: Reset to national view
- **Alt + Backspace**: Go back one level

## How to Use

### Method 1: Click Navigation (Automatic)

1. **Open the dashboard**
   ```
   http://localhost:9000/dashboard
   ```

2. **View National Level**
   - You'll see all 8 divisions in the Division Performance Map and Table
   - Each division name is clickable

3. **Drill into Division**
   - Click any division name (e.g., "Dhaka") in the table
   - URL changes to: `?division=Dhaka`
   - Dashboard now shows only Dhaka's 13 districts
   - Breadcrumb updates: "National → Dhaka"

4. **Drill into District**
   - Click any district name (e.g., "Gazipur") in the District Ranking table
   - URL changes to: `?division=Dhaka&district=Gazipur`
   - Dashboard shows only ISPs in Gazipur
   - Breadcrumb updates: "National → Dhaka → Gazipur"

5. **Return to Previous Level**
   - Press browser **Back** button, or
   - Click breadcrumb level, or
   - Click **Reset View** button

### Method 2: Direct URL Access

You can also navigate directly using URLs:

**View Chattagram Division:**
```
http://localhost:9000/dashboard?division=Chattagram
```

**View Gazipur District (in Dhaka):**
```
http://localhost:9000/dashboard?division=Dhaka&district=Gazipur
```

**View Specific ISP:**
```
http://localhost:9000/dashboard?division=Dhaka&district=Gazipur&isp=Link3%20Technologies
```

### Method 3: Metabase Filters (Fallback)

If JavaScript click handlers don't work (due to browser restrictions):

1. Use Metabase dropdown filters at the top of the dashboard
2. Select Division → Select District → Select ISP
3. Copy the URL from the wrapper page (it updates automatically)
4. Share the URL with colleagues

## Architecture

### How It Works

```
┌────────────────────────────────────────────────────┐
│  Custom HTML Page (http://localhost:9000/dashboard) │
│                                                    │
│  ┌──────────────────────────────────────────┐    │
│  │  Header: Breadcrumb + Reset Button       │    │
│  └──────────────────────────────────────────┘    │
│                    ↓                               │
│  ┌──────────────────────────────────────────┐    │
│  │  JavaScript Layer (dashboard.js)          │    │
│  │  • Reads URL parameters                   │    │
│  │  • Builds Metabase URL with filters       │    │
│  │  • Updates breadcrumb                     │    │
│  │  • Detects clicks on tables               │    │
│  │  • Navigates to new drill-down URLs       │    │
│  └──────────────────────────────────────────┘    │
│                    ↓                               │
│  ┌──────────────────────────────────────────┐    │
│  │  Embedded Metabase Dashboard (iframe)     │    │
│  │  http://localhost:3000/dashboard/6        │    │
│  │  with filters applied                     │    │
│  └──────────────────────────────────────────┘    │
└────────────────────────────────────────────────────┘
```

### Technology Stack

- **Nginx**: Web server on port 9000
- **Custom HTML**: `dashboard.html` (wrapper page)
- **JavaScript**: `dashboard.js` (click handler + navigation logic)
- **Metabase**: Embedded via iframe, runs on port 3000
- **TimescaleDB**: Data source on port 5433

## Setup & Deployment

### Prerequisites

- Docker and Docker Compose installed
- Existing Metabase dashboard running on port 3000
- TimescaleDB running on port 5433

### Start Custom Dashboard

1. **Start all services**
   ```bash
   cd /home/alamin/Desktop/Python\ Projects/BTRC-QoS-Monitoring-Dashboard-V3
   docker-compose up -d
   ```

2. **Verify nginx is running**
   ```bash
   docker ps | grep nginx
   ```

   You should see:
   ```
   btrc-v3-nginx   nginx:alpine   Up   0.0.0.0:9000->9000/tcp
   ```

3. **Access the dashboard**
   ```
   http://localhost:9000/dashboard
   ```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# Nginx logs
docker logs btrc-v3-nginx

# All services
docker-compose logs -f
```

## Files

### Created Files

```
public/
├── dashboard.html      # Main wrapper page with header + iframe
├── dashboard.js        # JavaScript click handler and navigation
└── README.md          # This file

nginx.conf             # Nginx configuration
docker-compose.yml     # Updated with nginx service
```

### File Descriptions

**dashboard.html**
- Custom HTML page with BTRC branding
- Shows breadcrumb navigation header
- Embeds Metabase dashboard via iframe
- Includes loading indicator and reset button

**dashboard.js**
- Reads URL parameters (division, district, isp)
- Builds Metabase URL: `/dashboard/6?division=X&district=Y&tab=14`
- Updates breadcrumb: "National → Dhaka → Gazipur"
- Attempts to inject click handlers on table cells
- Handles browser back/forward navigation
- Provides keyboard shortcuts

**nginx.conf**
- Serves custom HTML from `/dashboard` route
- Proxies all other requests to Metabase (port 3000)
- Enables WebSocket for Metabase live updates
- Adds health check endpoint

## Troubleshooting

### Issue: Dashboard doesn't load

**Check nginx is running:**
```bash
docker ps | grep nginx
```

**Check nginx logs:**
```bash
docker logs btrc-v3-nginx
```

**Restart nginx:**
```bash
docker-compose restart nginx
```

### Issue: Click doesn't navigate (URL doesn't change)

**Hard refresh browser:**
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

**Check browser console:**
- Press `F12` → Console tab
- Look for JavaScript errors

**Try direct URL:**
```
http://localhost:9000/dashboard?division=Dhaka
```

If direct URL works but clicking doesn't, it's a click detection issue. Use Metabase filters manually as fallback.

### Issue: Metabase shows "Not Found"

**Check Metabase is running:**
```bash
docker ps | grep metabase
```

**Access Metabase directly:**
```
http://localhost:3000/dashboard/6
```

If Metabase works directly but not through wrapper, check nginx proxy configuration.

### Issue: CORS errors in browser console

This means JavaScript can't access iframe content. The drill-down will still work via URL parameters, but automatic click detection won't work. Use Metabase filters as fallback.

### Issue: Port 9000 already in use

**Change nginx port in docker-compose.yml:**
```yaml
nginx:
  ports:
    - "9001:9000"  # Changed from 9000 to 9001
```

**Restart:**
```bash
docker-compose up -d nginx
```

**Access:**
```
http://localhost:9001/dashboard
```

## Comparison: Old vs New

### Before (Metabase Direct)

**URL:** http://localhost:3000/dashboard/6

❌ Click Division → Filter is set, but URL stays same
❌ Can't use browser back button
❌ Can't share drill-down state via URL
❌ Maps don't support clicks

### After (Custom Wrapper)

**URL:** http://localhost:9000/dashboard

✅ Click Division → URL changes to `?division=Dhaka`
✅ Browser back button works
✅ Shareable URLs: `?division=Dhaka&district=Gazipur`
✅ Breadcrumb navigation
✅ Keyboard shortcuts
✅ Reset button

## Next Steps

### Production Deployment

For production deployment on a server:

1. **Update URLs in dashboard.js:**
   ```javascript
   const CONFIG = {
       metabaseUrl: 'http://your-server-ip:3000',  // Change this
       dashboardId: 6,
       tabId: 14,
   };
   ```

2. **Update nginx port (optional):**
   ```yaml
   nginx:
     ports:
       - "80:9000"  # Map standard HTTP port to nginx port 9000
   ```

3. **Add domain and SSL (recommended):**
   - Set up nginx reverse proxy with Let's Encrypt SSL
   - See main README.md for full deployment guide

### Future Enhancements

Potential improvements:
- Add ISP drill-down to PoP level
- Add "Export PDF" button for current view
- Add "Share Link" button to copy current URL
- Add keyboard navigation (arrow keys)
- Add touch gestures for mobile
- Add animated transitions between levels

## Support

**Created:** 2026-02-09
**Version:** 1.0
**Dashboard:** Regulatory Operations (Dashboard 6)
**Tab:** R2.2 Regional Analysis (Tab 14)

For issues or questions, refer to the main project README.md.

---

**✅ Custom Drill-Down Navigation - Ready to Use!**
