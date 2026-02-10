# Chrome Connection Refused - Fix Steps

## Step 1: Clear Chrome's Network Cache

1. Open Chrome and go to:
   ```
   chrome://net-internals/#sockets
   ```

2. Click the **"Close idle sockets"** button

3. Click the **"Flush socket pools"** button

4. Then go to:
   ```
   chrome://net-internals/#dns
   ```

5. Click **"Clear host cache"**

6. **Restart Chrome completely** (close all windows)

7. Try again: http://localhost:9000/dashboard

---

## Step 2: Check Chrome Site Settings

1. Go to:
   ```
   chrome://settings/content/all
   ```

2. Search for: `localhost:9000`

3. If you see it listed, click it and select **"Remove"**

4. Try again: http://localhost:9000/dashboard

---

## Step 3: Disable Chrome Extensions

Some extensions (like VPN, proxy, ad blockers) can block localhost:

1. Go to:
   ```
   chrome://extensions/
   ```

2. Disable ALL extensions temporarily

3. Try again: http://localhost:9000/dashboard

4. If it works, re-enable extensions one by one to find the culprit

---

## Step 4: Check Chrome Flags

1. Go to:
   ```
   chrome://flags/
   ```

2. Search for: `insecure`

3. Make sure **"Insecure origins treated as secure"** is NOT blocking localhost

4. Try again: http://localhost:9000/dashboard

---

## Step 5: Use 127.0.0.1 Instead of localhost

Chrome might be trying IPv6 for localhost. Try:

```
http://127.0.0.1:9000/dashboard
```

---

## Step 6: Check Proxy Settings

1. Go to:
   ```
   chrome://settings/system
   ```

2. Click **"Open your computer's proxy settings"**

3. Make sure **"localhost"** and **"127.0.0.1"** are in the "bypass proxy" list

4. Or disable proxy completely

---

## Step 7: Reset Chrome Network Settings

1. Close Chrome completely

2. Open Terminal and run:
   ```bash
   rm -rf ~/.config/google-chrome/Default/Cache
   rm -rf ~/.cache/google-chrome
   ```

3. Restart Chrome

4. Try again: http://localhost:9000/dashboard

---

## Step 8: Try Different URL Format

Try these variations:

1. **With explicit IP:**
   ```
   http://127.0.0.1:9000/dashboard
   ```

2. **With trailing slash:**
   ```
   http://localhost:9000/dashboard/
   ```

3. **Test health endpoint first:**
   ```
   http://localhost:9000/health
   ```

---

## Step 9: Check Chrome Developer Console

1. Press F12 to open DevTools

2. Go to **Console** tab

3. Try opening: http://localhost:9000/dashboard

4. Check for error messages in the console

5. Go to **Network** tab

6. Try again and see what request is made

7. **Take a screenshot of the error and share it**

---

## Alternative: Use Firefox

If Chrome still doesn't work, Firefox definitely will:

```bash
firefox http://localhost:9000/dashboard
```

Or install Firefox:
```bash
sudo snap install firefox
```

---

## Last Resort: Change Port to 8080

If Chrome has port 9000 blacklisted, we can change to port 8080:

Edit docker-compose.yml:
```yaml
nginx:
  ports:
    - "8080:80"  # Changed from 9000
```

Then:
```bash
docker-compose restart nginx
```

Try: http://localhost:8080/dashboard
