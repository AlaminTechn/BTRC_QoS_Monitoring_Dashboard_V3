# Enable Dark Mode in Metabase

## Method 1: User Settings (Per User)

1. **Login to Metabase**
   ```
   http://localhost:3000
   ```

2. **Open User Settings**
   - Click your profile icon (top right)
   - Click "Account settings"
   - Go to "Display" or "Preferences" tab

3. **Select Theme**
   - Choose "Dark" theme
   - Click "Save"

**Note:** This changes theme for current user only.

---

## Method 2: Admin Settings (Global Default)

1. **Login as Admin**
   ```
   Email: alamin.technometrics22@gmail.com
   Password: Test@123
   ```

2. **Open Admin Panel**
   - Click gear icon (⚙️) in top right
   - Select "Admin settings"

3. **Navigate to Appearance**
   - Click "Appearance" in left menu
   - Under "Theme", select "Dark"
   - Click "Save changes"

---

## Method 3: Custom CSS (Advanced Styling)

For custom dark theme with your specific colors:

1. **Admin Panel → Appearance → Custom Styling**

2. **Add Custom CSS:**

```css
/* Dark Theme for BTRC Dashboard */
:root {
  --mb-color-bg-dark: #0a1929;
  --mb-color-bg-medium: #132f4c;
  --mb-color-bg-light: #1a3a52;
  --mb-color-text-dark: #ffffff;
  --mb-color-text-medium: #b0bec5;
  --mb-color-border: #2e4156;
}

/* Main background */
body {
  background-color: #0a1929 !important;
  color: #ffffff !important;
}

/* Dashboard background */
.Dashboard {
  background-color: #0a1929 !important;
}

/* Card backgrounds */
.Card {
  background-color: #132f4c !important;
  border: 1px solid #2e4156 !important;
  border-radius: 8px !important;
}

/* Text colors */
.text-dark {
  color: #ffffff !important;
}

.text-medium {
  color: #b0bec5 !important;
}

/* Header styling */
.DashboardHeader {
  background-color: #0a1929 !important;
  border-bottom: 1px solid #2e4156 !important;
}

/* Tab styling */
.DashboardTabs {
  background-color: #132f4c !important;
}

.Tab {
  color: #b0bec5 !important;
}

.Tab--selected {
  color: #90caf9 !important;
  border-bottom: 2px solid #90caf9 !important;
}
```

---

## Quick Toggle

**Keyboard Shortcut:** Many Metabase versions support theme toggle via browser settings or extensions.

**Browser Extension:** Install "Dark Reader" for Chrome/Firefox:
- Automatically converts light themes to dark
- Customizable colors
- Toggle on/off per site

---

## Verification

After enabling dark mode, you should see:
- ✅ Dark background on all pages
- ✅ Light text on dark background
- ✅ Cards with dark backgrounds
- ✅ Charts with dark-friendly colors

---

## Troubleshooting

**Issue:** Theme not applying
**Solution:** Clear browser cache and reload

**Issue:** Charts look bad in dark mode
**Solution:** Metabase automatically adjusts chart colors for dark theme

**Issue:** Text hard to read
**Solution:** Adjust brightness in custom CSS or use Method 1/2

---

## Screenshot After Dark Mode

Your dashboard should look like:
- Dark navy/black background (#0a1929)
- Cards with subtle borders
- Light text (#ffffff)
- Colored indicators for status (green/yellow/red)

