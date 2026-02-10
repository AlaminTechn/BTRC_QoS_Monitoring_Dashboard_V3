# Fix Scalar Card Font Size - Step by Step

## Problem
The COMPLIANT, AT RISK, and VIOLATION cards have numbers that are too large and the percentage text gets cut off.

## ✅ Step 1: Card Settings Updated (DONE)
The script has already updated the internal card settings to use medium font size.

---

## 📝 Step 2: Apply Custom CSS (Do This Now)

### Method 1: Using Browser Extension (Quick Test)

1. **Install Stylus Extension:**
   - Chrome: https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/styl-us/

2. **Create New Style:**
   - Click Stylus icon
   - Click "Manage"
   - Click "Write new style"
   - Name: "BTRC Dashboard Fix"
   - URLs: `http://localhost:3000`

3. **Paste CSS:**
   - Copy entire content from `scalar_cards_complete_fix.css`
   - Paste into the style editor
   - Click "Save"

4. **Refresh Dashboard:**
   - Go to http://localhost:3000/dashboard/6
   - Press Ctrl+Shift+R (hard refresh)
   - Numbers should now be smaller and readable

---

### Method 2: Metabase Admin Settings (Permanent)

1. **Open Metabase:**
   ```
   http://localhost:3000
   ```

2. **Login as Admin:**
   - Email: alamin.technometrics22@gmail.com
   - Password: Test@123

3. **Go to Admin Settings:**
   - Click gear icon ⚙️ (top right)
   - Select "Admin settings"

4. **Open Appearance:**
   - Click "Appearance" in left menu

5. **Find Custom Styling Section:**
   - Scroll down to "Custom Styling" or "Custom CSS"
   - You should see a text box

6. **Paste CSS:**
   - Copy entire content from `scalar_cards_complete_fix.css`
   - Paste into the Custom CSS text box
   - Click "Save changes" at bottom

7. **Test:**
   - Open dashboard: http://localhost:3000/dashboard/6
   - Press Ctrl+Shift+R to hard refresh
   - Check if font sizes are better

---

## 🧪 Step 3: Verify the Fix

After applying CSS, you should see:

### Before (Current Issue):
```
┌──────────────┐
│ COMPLIANT    │
│              │
│    0         │  ← Too large
│ 0% of total  │  ← Cut off
└──────────────┘
```

### After (Fixed):
```
┌──────────────┐
│ COMPLIANT  ✓ │
│              │
│     0        │  ← Perfect size
│ 0% of total  │  ← Fully visible
│     ISPs     │
└──────────────┘
```

### What Should Change:
- ✅ Numbers smaller (28-32px instead of 48px)
- ✅ Percentage text visible and not cut off
- ✅ Better spacing between title and number
- ✅ Colored left borders (green/orange/red)
- ✅ Status icons (✓, ⚠, ✕) in top right
- ✅ Better text wrapping

---

## 🔧 Step 4: If Still Not Working

### Option A: Try Browser Developer Tools (Quick Test)

1. Open dashboard: http://localhost:3000/dashboard/6
2. Press F12 (open DevTools)
3. Click "Console" tab
4. Paste this code:
```javascript
// Quick CSS injection test
const style = document.createElement('style');
style.textContent = `
  .ScalarValue {
    font-size: 28px !important;
    line-height: 1.3 !important;
  }
  .ScalarValue + div {
    font-size: 11px !important;
  }
`;
document.head.appendChild(style);
```
5. Press Enter
6. If this works, the CSS is correct but not being loaded properly

### Option B: Check Card Dimensions

The cards might be too small. Let me check:

1. Go to dashboard edit mode
2. Click on COMPLIANT card
3. Look at size: Should be at least 4 units wide × 3 units tall
4. If too small, resize the card

### Option C: Check SQL Query Format

The query should return text in this format:
```
0
0% of total ISPs
```

Run this to verify:
```sql
-- Test query
SELECT '0' || E'\n' || '0% of total ISPs' as result;
```

Should show two lines, not one long line.

---

## 📊 Expected Results

### Card Measurements:
- **Font size:** 28-32px (down from 48px)
- **Line height:** 1.3x
- **Percentage text:** 11px (down from 13px)
- **Card padding:** 16px
- **Min card height:** 120px

### Visual Appearance:
- ✅ All text visible (no cutoff)
- ✅ Proper line breaks
- ✅ Colored borders and backgrounds
- ✅ Status icons in corner
- ✅ Centered text
- ✅ Responsive on mobile

---

## 🆘 Troubleshooting

### Issue: "CSS not applying"
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Try incognito/private mode
- Check if Stylus/extension is enabled

### Issue: "Text still too large"
**Solution:**
- Open browser DevTools (F12)
- Click "Elements" tab
- Find `.ScalarValue` element
- Check "Computed" styles
- Look for font-size value
- If still 48px, CSS isn't loading

### Issue: "Percentage text on separate card"
**Solution:**
- SQL query issue - should use `E'\\n'` for newline
- Check query: `SELECT count || E'\\n' || percentage || '% of total ISPs'`

### Issue: "Cards too small"
**Solution:**
- Edit dashboard
- Resize cards to at least 4×3 grid units
- Save dashboard

---

## 📸 Screenshots

**Take screenshots after applying fix to verify:**

1. Dashboard overview (all 3 cards visible)
2. Close-up of each card (readable text)
3. Mobile view (responsive)

---

## 🎯 Final Checklist

After applying the fix:

- [ ] Numbers are smaller and readable
- [ ] Percentage text is fully visible
- [ ] Cards have colored left borders
- [ ] Status icons appear in top right
- [ ] Text is centered properly
- [ ] No text cutoff
- [ ] Looks good on mobile
- [ ] Print preview looks good

---

## 🔗 Next Steps

If this fixes the issue:
1. ✅ Keep CSS in Admin Settings (permanent)
2. ✅ Test on different browsers
3. ✅ Test on mobile devices
4. ✅ Share updated dashboard links

If still having issues:
1. Send screenshot showing:
   - The problematic cards
   - Browser DevTools (F12) with Computed styles
   - Current card dimensions
2. I'll help debug further

---

**Status:** Ready to apply CSS fix
**Files to use:** `scalar_cards_complete_fix.css`
**Expected time:** 5 minutes

---

**End of Instructions**
