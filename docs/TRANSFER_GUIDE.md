# Transfer Guide - BTRC Dashboard to Server

**Package:** `btrc-dashboard-v3-deployment.tar.gz`
**Size:** 119 MB
**Files:** 91 files total

---

## 📦 Package Location

```
/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3/btrc-dashboard-v3-deployment.tar.gz
```

---

## 🚀 Transfer Methods

### Method 1: SCP (Secure Copy) - Recommended

**From your current machine to server:**

```bash
# Navigate to project directory
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"

# Transfer to server
scp btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/

# Example:
scp btrc-dashboard-v3-deployment.tar.gz ubuntu@192.168.1.100:/home/ubuntu/
```

**With custom SSH port:**
```bash
scp -P 2222 btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/
```

**With SSH key:**
```bash
scp -i ~/.ssh/your-key.pem btrc-dashboard-v3-deployment.tar.gz ubuntu@your-server-ip:/home/ubuntu/
```

**Progress indicator:**
```bash
scp -v btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/
```

---

### Method 2: SFTP (Interactive Transfer)

```bash
# Connect via SFTP
sftp your-username@your-server-ip

# Navigate to target directory
cd /home/your-username

# Upload file
put "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3/btrc-dashboard-v3-deployment.tar.gz"

# Verify upload
ls -l

# Exit
bye
```

---

### Method 3: rsync (Resume-able Transfer)

**Best for slow/unstable connections:**

```bash
rsync -avz --progress \
    btrc-dashboard-v3-deployment.tar.gz \
    your-username@your-server-ip:/home/your-username/

# With SSH key:
rsync -avz --progress -e "ssh -i ~/.ssh/your-key.pem" \
    btrc-dashboard-v3-deployment.tar.gz \
    ubuntu@your-server-ip:/home/ubuntu/
```

**Advantages:**
- Resumes if interrupted
- Shows progress
- Compresses during transfer

---

### Method 4: FTP/SFTP Client (GUI)

**Using FileZilla, WinSCP, or Cyberduck:**

1. **Open FTP client**
2. **Connect to server:**
   - Host: `your-server-ip`
   - Username: `your-username`
   - Password: `your-password`
   - Port: 22 (SFTP)
3. **Navigate to:** `/home/your-username/`
4. **Drag and drop:** `btrc-dashboard-v3-deployment.tar.gz`
5. **Wait for transfer** to complete

---

### Method 5: Cloud Storage (Alternative)

**If direct transfer is not possible:**

**Upload to cloud:**
```bash
# Google Drive, Dropbox, or similar
# Use web interface or CLI tool
```

**Then download on server:**
```bash
# On server:
wget "https://your-cloud-storage-url/btrc-dashboard-v3-deployment.tar.gz"

# Or with curl:
curl -L -o btrc-dashboard-v3-deployment.tar.gz "https://your-cloud-storage-url/..."
```

---

### Method 6: USB Drive (Offline Transfer)

**If no network connection:**

1. **Copy to USB:**
   ```bash
   cp btrc-dashboard-v3-deployment.tar.gz /media/your-username/USB_DRIVE/
   ```

2. **Connect USB to server**

3. **Copy from USB:**
   ```bash
   sudo cp /media/USB_DRIVE/btrc-dashboard-v3-deployment.tar.gz /home/your-username/
   ```

---

## ✅ Verify Transfer

**On server, after transfer:**

```bash
# Check file exists
ls -lh ~/btrc-dashboard-v3-deployment.tar.gz

# Should show:
# -rw-rw-r-- 1 user user 119M Feb 10 12:21 btrc-dashboard-v3-deployment.tar.gz

# Verify size (should be ~119MB)
du -h ~/btrc-dashboard-v3-deployment.tar.gz

# Test archive integrity
tar -tzf ~/btrc-dashboard-v3-deployment.tar.gz > /dev/null
echo $?  # Should print 0 (success)
```

---

## 📂 Extract on Server

**After successful transfer:**

```bash
# Create application directory
sudo mkdir -p /opt/btrc-qos-dashboard
sudo chown $USER:$USER /opt/btrc-qos-dashboard

# Extract files
cd /opt/btrc-qos-dashboard
tar -xzf ~/btrc-dashboard-v3-deployment.tar.gz

# Verify extraction
ls -la

# Should see:
# - docker-compose.yml
# - nginx.conf
# - deploy.sh
# - backup.sh
# - public/
# - docs/
# - *.md files
```

---

## 🚀 Deploy After Extraction

```bash
# Make scripts executable
chmod +x deploy.sh backup.sh

# Run deployment
./deploy.sh
```

---

## 🐛 Troubleshooting

### Transfer Too Slow

**Solution 1: Compress more**
```bash
# Create smaller archive with better compression
tar -czf --best btrc-dashboard-v3-deployment-small.tar.gz \
    --exclude='backups' \
    --exclude='logs' \
    --exclude='*.geojson' \
    .
```

**Solution 2: Use rsync with compression**
```bash
rsync -avz --compress-level=9 --progress \
    btrc-dashboard-v3-deployment.tar.gz \
    your-username@your-server-ip:/home/your-username/
```

### Permission Denied

**On local machine:**
```bash
chmod 644 btrc-dashboard-v3-deployment.tar.gz
```

**On server:**
```bash
# If target directory not writable:
sudo chown $USER:$USER /home/your-username/
```

### Connection Refused

**Check SSH service:**
```bash
# On server:
sudo systemctl status ssh

# If not running:
sudo systemctl start ssh
```

**Check firewall:**
```bash
# On server:
sudo ufw status
sudo ufw allow 22/tcp
```

### File Corrupted After Transfer

**Verify checksums:**

```bash
# On local machine:
md5sum btrc-dashboard-v3-deployment.tar.gz > checksum.txt
scp checksum.txt your-username@your-server-ip:/home/your-username/

# On server:
md5sum -c checksum.txt
```

If checksums don't match, re-transfer the file.

---

## 📊 Transfer Time Estimates

| Connection Speed | Estimated Time |
|-----------------|----------------|
| 1 Mbps | ~16 minutes |
| 10 Mbps | ~2 minutes |
| 100 Mbps | ~10 seconds |
| 1 Gbps | ~1 second |

---

## 🔐 Security Best Practices

### Use SSH Keys (Recommended)

**Generate SSH key (if you don't have one):**
```bash
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

**Copy to server:**
```bash
ssh-copy-id your-username@your-server-ip
```

**Transfer with key:**
```bash
scp -i ~/.ssh/id_rsa btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/
```

### Disable Password Authentication

**After setting up SSH keys:**
```bash
# On server:
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no

# Restart SSH:
sudo systemctl restart ssh
```

---

## 📝 Quick Command Summary

**Transfer:**
```bash
cd "/home/alamin/Desktop/Python Projects/BTRC-QoS-Monitoring-Dashboard-V3"
scp btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/
```

**Extract on Server:**
```bash
sudo mkdir -p /opt/btrc-qos-dashboard
sudo chown $USER:$USER /opt/btrc-qos-dashboard
cd /opt/btrc-qos-dashboard
tar -xzf ~/btrc-dashboard-v3-deployment.tar.gz
```

**Deploy:**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Post-Transfer Checklist

After transfer and extraction:

- [ ] File size matches (~119 MB)
- [ ] Archive integrity verified
- [ ] Files extracted successfully
- [ ] deploy.sh exists and is executable
- [ ] backup.sh exists and is executable
- [ ] docker-compose.yml exists
- [ ] nginx.conf exists
- [ ] public/ directory exists
- [ ] All .md documentation files present

---

## 📞 Need Help?

**Common Issues:**
- Can't connect to server → Check SSH service and firewall
- Permission denied → Check file/directory permissions
- Transfer interrupted → Use rsync for resume capability
- Slow transfer → Use compression or split into smaller files

**For more help:**
- See DEPLOYMENT_GUIDE.md
- See QUICK_START.md

---

**Ready to transfer?**

```bash
scp btrc-dashboard-v3-deployment.tar.gz your-username@your-server-ip:/home/your-username/
```

Good luck! 🚀
