# Dashboard Styling Guide - Match Demo UI

**Goal:** Transform Metabase dashboard to match your dark-themed demo UI

---

## Step 1: Enable Dark Mode

### Quick Method
1. Login to Metabase: http://localhost:3000
2. Click profile icon (top right) → **Account settings**
3. Select **Theme: Dark**
4. Click **Save**

---

## Step 2: Update Card Styling

### Current Status
✅ **Cards Updated:**
- R1.1: Compliant (shows count + percentage in green)
- R1.2: At Risk (shows count + percentage in orange)
- R1.3: Violation (shows count + percentage in red)

### Card Display Format
```
847
87% of total ISPs
```

---

## Step 3: Advanced Styling (Custom CSS)

### Option A: Admin Settings

1. **Login as Admin**
2. **Gear Icon (⚙️) → Admin Settings**
3. **Appearance → Custom Styling**

### Option B: Browser Extension

Install **Stylus** extension for Chrome/Firefox, then add this CSS:

```css
/* ========================================
   BTRC Dashboard - Dark Theme Custom CSS
   ======================================== */

/* Main Background */
body,
.Dashboard,
.DashboardBody {
  background-color: #0a1929 !important;
  color: #ffffff !important;
}

/* Dashboard Header */
.DashboardHeader {
  background-color: #0a1929 !important;
  border-bottom: 1px solid #1e3a52 !important;
}

.DashboardHeader h1 {
  color: #ffffff !important;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Dashboard Tabs */
.DashboardTabs {
  background-color: #132f4c !important;
  border-bottom: 1px solid #1e3a52 !important;
}

.Tab {
  color: #90caf9 !important;
  padding: 12px 24px;
  font-weight: 500;
}

.Tab--selected {
  color: #ffffff !important;
  border-bottom: 3px solid #2196f3 !important;
  background-color: rgba(33, 150, 243, 0.1) !important;
}

/* Card Containers */
.DashCard {
  background-color: #132f4c !important;
  border: 1px solid #1e3a52 !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
  transition: all 0.3s ease !important;
}

.DashCard:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-2px) !important;
}

/* Card Titles */
.DashCard .Card-title {
  color: #b0bec5 !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  margin-bottom: 8px !important;
}

/* Scalar Cards (Number Display) */
.ScalarValue {
  color: #ffffff !important;
  font-size: 48px !important;
  font-weight: 700 !important;
  line-height: 1.2 !important;
}

.ScalarValue-description {
  color: #90caf9 !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  margin-top: 8px !important;
}

/* Colored Border for Status Cards */
/* Compliant Card (Green) */
.DashCard[data-card-id="76"] {
  border-left: 4px solid #10b981 !important;
  background: linear-gradient(135deg, #132f4c 0%, #0d3b2f 100%) !important;
}

/* At Risk Card (Orange) */
.DashCard[data-card-id="77"] {
  border-left: 4px solid #f59e0b !important;
  background: linear-gradient(135deg, #132f4c 0%, #3b2a0d 100%) !important;
}

/* Violation Card (Red) */
.DashCard[data-card-id="78"] {
  border-left: 4px solid #ef4444 !important;
  background: linear-gradient(135deg, #132f4c 0%, #3b0d0d 100%) !important;
}

/* Status Icons */
.DashCard[data-card-id="76"]::before {
  content: "✓";
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 24px;
  color: #10b981;
  opacity: 0.5;
}

.DashCard[data-card-id="77"]::before {
  content: "⚠";
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 24px;
  color: #f59e0b;
  opacity: 0.5;
}

.DashCard[data-card-id="78"]::before {
  content: "⊗";
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 24px;
  color: #ef4444;
  opacity: 0.5;
}

/* Table Styling */
.TableInteractive {
  background-color: #132f4c !important;
  border: 1px solid #1e3a52 !important;
}

.TableInteractive-header {
  background-color: #1a3a52 !important;
  color: #90caf9 !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #2196f3 !important;
}

.TableInteractive-cellWrapper {
  border-color: #1e3a52 !important;
  color: #ffffff !important;
}

.TableInteractive tbody tr:hover {
  background-color: #1a3a52 !important;
}

/* Charts */
.Chart {
  background-color: #132f4c !important;
}

/* Tooltip */
.Popover {
  background-color: #1a3a52 !important;
  border: 1px solid #2e4156 !important;
  color: #ffffff !important;
}

/* Buttons */
.Button {
  background-color: #2196f3 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 4px !important;
  font-weight: 500 !important;
}

.Button:hover {
  background-color: #1976d2 !important;
}

/* Filter Bar */
.DashboardParametersAndCards .DashboardParameters {
  background-color: #132f4c !important;
  border-bottom: 1px solid #1e3a52 !important;
}

/* Loading State */
.LoadingSpinner {
  border-color: #2196f3 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background-color: #0a1929;
}

::-webkit-scrollbar-thumb {
  background-color: #2196f3;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #1976d2;
}

/* Footer Info (Total Monitored) */
.DashboardFooter {
  background-color: #132f4c !important;
  border-top: 1px solid #1e3a52 !important;
  color: #90caf9 !important;
  padding: 12px 24px;
  font-size: 13px;
}

/* Last Check Indicator */
.DashboardHeader-refreshIndicator {
  color: #90caf9 !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}

/* Animation for New Data */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.DashCard--pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

---

## Step 4: Dashboard Configuration

### Add "Total Monitored" Text

1. **Edit Dashboard**
2. **Add Text Card**
3. **Content:**
```markdown
**Total Monitored:** 970 ISPs
```
4. **Position:** Below the three status cards
5. **Styling:** Set background to match dashboard

### Add "Last Check" Indicator

Metabase automatically shows refresh time, but to customize:

1. **Dashboard Settings**
2. **Auto-refresh:** Set to 5 minutes
3. **Show timestamp:** Enable

---

## Step 5: Color Scheme Reference

### Your Demo UI Colors

| Element | Color | Hex Code |
|---------|-------|----------|
| Background | Dark Navy | `#0a1929` |
| Card Background | Medium Navy | `#132f4c` |
| Border | Dark Blue | `#1e3a52` |
| Text Primary | White | `#ffffff` |
| Text Secondary | Light Blue | `#90caf9` |
| Text Muted | Gray Blue | `#b0bec5` |
| Compliant | Green | `#10b981` |
| At Risk | Orange | `#f59e0b` |
| Violation | Red | `#ef4444` |
| Accent | Blue | `#2196f3` |

---

## Step 6: Alternative - Custom Dashboard Theme

If you want complete control, you can create a custom theme JSON:

```json
{
  "colors": {
    "brand": "#2196f3",
    "text-dark": "#ffffff",
    "text-medium": "#90caf9",
    "text-light": "#b0bec5",
    "bg-black": "#0a1929",
    "bg-dark": "#132f4c",
    "bg-medium": "#1a3a52",
    "border": "#1e3a52",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444"
  },
  "typography": {
    "font-family": "'Inter', 'Roboto', 'Helvetica Neue', sans-serif",
    "font-weight-normal": 400,
    "font-weight-bold": 600
  }
}
```

**Apply via:**
1. Admin Settings → Appearance → Theme JSON
2. Paste JSON
3. Save

---

## Step 7: Verification Checklist

After applying all changes:

- [ ] Dark background visible (#0a1929)
- [ ] Cards have dark navy background (#132f4c)
- [ ] R1.1 has green left border
- [ ] R1.2 has orange left border
- [ ] R1.3 has red left border
- [ ] Text is white and readable
- [ ] Percentages display under main numbers
- [ ] Status icons visible (✓, ⚠, ⊗)
- [ ] Tables have dark styling
- [ ] Charts use dark-friendly colors
- [ ] Hover effects work on cards

---

## Step 8: Screenshots

### Before
- Light theme
- Simple cards
- No percentages

### After
- Dark theme matching demo
- Styled cards with borders
- Count + percentage format
- Status icons
- Professional appearance

---

## Troubleshooting

### Issue: CSS not applying
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard reload (Ctrl+Shift+R)
- Check if Stylus extension is enabled

### Issue: Card colors not showing
**Solution:**
- Check card IDs match (76, 77, 78)
- Use browser inspector to verify IDs
- Update CSS selectors if IDs differ

### Issue: Text hard to read
**Solution:**
- Increase font weight in CSS
- Adjust text color brightness
- Add text shadow for better contrast

### Issue: Percentages not displaying
**Solution:**
- Run update_r1_cards_design.py again
- Check SQL query returns correct format
- Verify newline character (\\n) in query

---

## Additional Resources

### Metabase Styling Docs
- https://www.metabase.com/docs/latest/configuring-metabase/appearance

### CSS Tools
- Chrome DevTools (F12)
- Stylus Extension
- Color Picker

### Font Recommendations
- **Inter** - Modern, clean
- **Roboto** - Google's material design
- **SF Pro** - Apple's system font

---

## Next Steps

1. ✅ Update R1.1, R1.2, R1.3 cards (DONE)
2. 🔲 Apply dark theme
3. 🔲 Add custom CSS
4. 🔲 Test on dashboard
5. 🔲 Fine-tune colors
6. 🔲 Add "Total Monitored" text
7. 🔲 Configure auto-refresh

---

**Your Dashboard Will Look Like:**
```
┌─────────────────────────────────────────────────┐
│  SLA COMPLIANCE OVERVIEW    Last Check: 2 min ago │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ ✓        │  │ ⚠        │  │ ⊗        │      │
│  │COMPLIANT │  │ AT RISK  │  │VIOLATION │      │
│  │   847    │  │    89    │  │    34    │      │
│  │ 87% of   │  │  9% of   │  │  4% of   │      │
│  │total ISPs│  │total ISPs│  │total ISPs│      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  └green border  └orange      └red border       │
│                                                   │
│  Total Monitored: 970 ISPs                      │
└─────────────────────────────────────────────────┘
```

---

**Status:** ✅ Cards Updated, CSS Guide Ready
**Next:** Apply dark theme and custom CSS

---

**End of Guide**
