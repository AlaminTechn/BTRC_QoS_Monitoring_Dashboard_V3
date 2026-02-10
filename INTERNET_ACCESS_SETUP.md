# Setup Internet Access for BTRC Dashboard

## Option 1: Port Forwarding (Quick Setup)

### Steps:
1. **Login to your router** (usually 192.168.1.1 or 192.168.0.1)
2. **Find Port Forwarding** (may be called Virtual Server/NAT)
3. **Add new rule:**
   - Service Name: BTRC Dashboard
   - External Port: 3000
   - Internal IP: 192.168.200.52
   - Internal Port: 3000
   - Protocol: TCP
4. **Get your public IP:**
   ```bash
   curl ifconfig.me
   ```
5. **Share public links:**
   ```
   http://YOUR_PUBLIC_IP:3000/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
   http://YOUR_PUBLIC_IP:3000/public/dashboard/bac7ee8a-62d3-422f-a1e9-123673b52c5f
   ```

⚠️ **Security Warning:** This exposes your dashboard to the internet. Consider using VPN instead.

---

## Option 2: VPN Access (Recommended - Secure)

### Using WireGuard VPN:

1. **Install WireGuard on server:**
   ```bash
   sudo apt update
   sudo apt install wireguard
   ```

2. **Generate keys:**
   ```bash
   wg genkey | tee privatekey | wg pubkey > publickey
   ```

3. **Create config:** `/etc/wireguard/wg0.conf`
   ```ini
   [Interface]
   Address = 10.0.0.1/24
   ListenPort = 51820
   PrivateKey = <server-private-key>

   [Peer]
   # CEO's device
   PublicKey = <client-public-key>
   AllowedIPs = 10.0.0.2/32
   ```

4. **Start VPN:**
   ```bash
   sudo wg-quick up wg0
   sudo systemctl enable wg-quick@wg0
   ```

5. **Give clients config file** to install WireGuard app on their devices

6. **After VPN connection, they access:**
   ```
   http://10.0.0.1:3000/public/dashboard/...
   ```

---

## Option 3: Domain Name with HTTPS (Professional)

### Using Cloudflare Tunnel (Free, Secure):

1. **Create Cloudflare account** (free)

2. **Install cloudflared:**
   ```bash
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

3. **Login:**
   ```bash
   cloudflared tunnel login
   ```

4. **Create tunnel:**
   ```bash
   cloudflared tunnel create btrc-dashboard
   ```

5. **Configure tunnel:** `~/.cloudflared/config.yml`
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /home/alamin/.cloudflared/<tunnel-id>.json

   ingress:
     - hostname: dashboard.btrc.gov.bd
       service: http://localhost:3000
     - service: http_status:404
   ```

6. **Add DNS record in Cloudflare:**
   - Type: CNAME
   - Name: dashboard
   - Target: <tunnel-id>.cfargotunnel.com

7. **Run tunnel:**
   ```bash
   cloudflared tunnel run btrc-dashboard
   ```

8. **Share professional URL:**
   ```
   https://dashboard.btrc.gov.bd/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
   ```

✅ **Benefits:** Free HTTPS, No port forwarding, DDoS protection

---

## Option 4: Reverse Proxy with Let's Encrypt (Self-hosted)

### Using Nginx + Certbot:

1. **Install nginx and certbot:**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure nginx:** `/etc/nginx/sites-available/btrc-dashboard`
   ```nginx
   server {
       listen 80;
       server_name dashboard.btrc.gov.bd;

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/btrc-dashboard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d dashboard.btrc.gov.bd
   ```

5. **Share HTTPS URL:**
   ```
   https://dashboard.btrc.gov.bd/public/dashboard/54733c64-24e2-4977-9d2f-2ed086219635
   ```

---

## Security Checklist

Before exposing to internet:

- [ ] Enable Metabase's security features
- [ ] Set up firewall rules (ufw/iptables)
- [ ] Use HTTPS (not HTTP)
- [ ] Enable Metabase audit logging
- [ ] Set up automatic backups
- [ ] Monitor access logs
- [ ] Use strong passwords
- [ ] Consider IP whitelisting
- [ ] Enable fail2ban for brute force protection
- [ ] Regular security updates

---

## Quick Comparison

| Method | Security | Ease | Cost | Best For |
|--------|----------|------|------|----------|
| Port Forwarding | ⚠️ Low | ⭐⭐⭐ Easy | Free | Quick demo only |
| VPN | ✅ High | ⭐⭐ Medium | Free | Small team |
| Cloudflare Tunnel | ✅ High | ⭐⭐ Medium | Free | Production use |
| Reverse Proxy | ✅ High | ⭐ Hard | Free | Full control |

---

## Recommended Approach for BTRC:

**For PM/CEO (Trusted Users):**
- Use **VPN** (WireGuard) for secure remote access
- Or use **Cloudflare Tunnel** for professional domain

**For Public/External Stakeholders:**
- Use **Cloudflare Tunnel** with custom domain
- Enable Metabase's embedding with signed tokens (more secure than public links)

---

Need help setting up any of these? Let me know which option you prefer!
