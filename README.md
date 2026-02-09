# BTRC QoS Monitoring Dashboard V3

**Fixed Broadband Quality of Service Monitoring Dashboard for the Bangladesh Telecommunication Regulatory Commission (BTRC)**

Built with **TimescaleDB** + **Metabase** for regulatory QoS monitoring, SLA compliance tracking, and geographic performance analysis.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Browser (Port 3000)                    │
│                  Metabase Dashboard UI                    │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│              Metabase (Docker Container)                  │
│              metabase/metabase:latest                     │
│              Port 3000 → 3000                             │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│            TimescaleDB (Docker Container)                 │
│            timescale/timescaledb-ha:pg15-latest           │
│            Port 5433 → 5432                               │
│                                                          │
│  Databases:                                              │
│  ├── btrc_qos_poc    (QoS data, measurements, ISPs)     │
│  └── metabase_meta   (Metabase internal metadata)        │
└──────────────────────────────────────────────────────────┘
```

## Dashboards

| # | Dashboard | URL | Description |
|---|-----------|-----|-------------|
| 1 | Executive Dashboard | http://localhost:3000/dashboard/5 | Performance scorecard, geographic intelligence, compliance overview |
| 2 | Regulatory Operations | http://localhost:3000/dashboard/6 | SLA monitoring, regional drill-down with maps, violation reporting |

### Dashboard Features
- **Choropleth Maps**: Division (8) and District (64) performance maps with custom Bangladesh GeoJSON
- **Dropdown Filters**: Division, District, ISP (static-list dropdowns)
- **Date Range Filters**: Start Date / End Date pickers
- **Drill-Down**: Division → District → ISP filter cascade
- **KPI Scorecards**: Compliant, At-Risk, Violation ISP counts
- **Violation Tracking**: Pending, Active, Resolved violations with trend charts

---

## Prerequisites

| Software | Version | Required |
|----------|---------|----------|
| Docker | 20.10+ | Yes |
| Docker Compose | v2.0+ | Yes |
| Python | 3.8+ | Yes |
| pip | Latest | Yes |
| Git | 2.x | Yes |

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd BTRC-QoS-Monitoring-Dashboard-V3
```

### Step 2: Create Environment File

The `.env` file is already included. Verify it contains:

```env
# TimescaleDB
DB_USER=btrc_admin
DB_PASSWORD=btrc_poc_2026
DB_NAME=btrc_qos_poc
DB_HOST=localhost
DB_PORT=5433

# Metabase
METABASE_PORT=3000
MB_DB_TYPE=postgres
MB_DB_DBNAME=metabase_meta
MB_DB_PORT=5432
MB_DB_USER=btrc_admin
MB_DB_PASS=btrc_poc_2026
MB_DB_HOST=timescaledb

# Dashboard Scripts
METABASE_URL=http://localhost:3000
METABASE_EMAIL=alamin.technometrics22@gmail.com
METABASE_PASSWORD=Test@123
```

### Step 3: Start Docker Containers

```bash
docker compose up -d
```

This starts:
- **TimescaleDB** on port `5433` (with PostGIS, UUID, TimescaleDB extensions)
- **Metabase** on port `3000` (connected to TimescaleDB for metadata storage)

Wait for containers to be healthy:

```bash
# Check container status
docker compose ps

# Wait for Metabase to be ready (~1-2 minutes on first start)
docker compose logs -f metabase
# Look for: "Metabase Initialization COMPLETE"
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs: `requests`, `python-dotenv`, `psycopg2-binary`

### Step 5: Load POC Data into TimescaleDB

```bash
python load_poc_data.py
```

This loads 22 JSON files in dependency order:
- **Tier 1 - Foundation**: Geographic hierarchy (Divisions, Districts, Upazilas, Unions), lookup tables
- **Tier 2 - Master**: ISPs (40), PoPs (120), Software Agents, Packages
- **Tier 3 - Relationships**: Agent-PoP mappings, Subscribers
- **Tier 4 - Timeseries**: QoS measurements (172,800 records), SNMP metrics
- **Tier 5 - Compliance**: SLA violations (150 records)

### Step 6: Load GeoJSON Boundaries (Optional)

```bash
python load_geojson_boundaries.py
```

This loads Bangladesh division and district boundaries into the database.

### Step 7: Configure Metabase

1. Open http://localhost:3000 in your browser
2. Complete the Metabase setup wizard:
   - Create admin account (use credentials from `.env`)
   - Add database connection:
     - **Type**: PostgreSQL
     - **Host**: `timescaledb` (Docker network) or `localhost`
     - **Port**: `5432` (internal) or `5433` (from host)
     - **Database**: `btrc_qos_poc`
     - **Username**: `btrc_admin`
     - **Password**: `btrc_poc_2026`

3. Configure Custom GeoJSON Maps (Admin → Settings → Maps):
   - **Bangladesh Divisions**: Upload/URL for `geodata/bgd_divisions.geojson` (region key: `shapeISO`)
   - **Bangladesh Districts**: Upload/URL for `geodata/bgd_districts.geojson` (region key: `shapeName`)

### Step 8: Create Dashboards

```bash
# Create Executive Dashboard (Dashboard 1)
python create_metabase_executive_dashboard.py

# Create Regulatory Operations Dashboard (Dashboard 2)
python create_metabase_regulatory_dashboard.py
```

### Step 9: Verify

- Executive Dashboard: http://localhost:3000/dashboard/5
- Regulatory Dashboard: http://localhost:3000/dashboard/6

---

## Server Deployment

### Prerequisites for Production

| Component | Requirement |
|-----------|-------------|
| Server OS | Ubuntu 22.04 LTS / RHEL 8+ |
| RAM | 4 GB minimum (8 GB recommended) |
| Storage | 20 GB minimum (SSD recommended) |
| CPU | 2 cores minimum (4 recommended) |
| Network | Open ports: 3000 (Metabase), 5433 (TimescaleDB, optional) |
| Domain | Optional (for HTTPS with reverse proxy) |

### Step 1: Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Verify installations
docker --version
docker compose version
python3 --version
```

### Step 2: Deploy the Application

```bash
# Clone repository
git clone <repository-url> /opt/btrc-qos-dashboard
cd /opt/btrc-qos-dashboard

# Update .env for production
# Change passwords, set proper METABASE_URL, etc.
nano .env
```

**Production `.env` changes:**

```env
# Change default passwords!
DB_PASSWORD=<strong-password-here>
MB_DB_PASS=<strong-password-here>
METABASE_PASSWORD=<strong-password-here>

# Set server URL (used by dashboard scripts)
METABASE_URL=http://<server-ip>:3000
# or with domain:
METABASE_URL=https://dashboard.btrc.gov.bd
```

### Step 3: Start Services

```bash
docker compose up -d

# Verify containers are running
docker compose ps

# Check logs
docker compose logs -f
```

### Step 4: Load Data and Create Dashboards

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Load POC data
python3 load_poc_data.py

# Complete Metabase setup wizard in browser first!
# Then configure GeoJSON maps in Admin → Settings → Maps

# Create dashboards
python3 create_metabase_executive_dashboard.py
python3 create_metabase_regulatory_dashboard.py
```

### Step 5: Configure Reverse Proxy (Recommended)

Using **Nginx** as a reverse proxy with SSL:

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx config:

```nginx
# /etc/nginx/sites-available/btrc-dashboard
server {
    listen 80;
    server_name dashboard.btrc.gov.bd;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for Metabase live updates)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and configure SSL:

```bash
sudo ln -s /etc/nginx/sites-available/btrc-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate (if domain is configured)
sudo certbot --nginx -d dashboard.btrc.gov.bd
```

### Step 6: Configure Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable

# Do NOT expose port 5433 (database) to the internet
```

### Step 7: Set Up Backups

```bash
# Create backup script
cat > /opt/btrc-qos-dashboard/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/btrc-qos-dashboard/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Backup TimescaleDB data
docker exec btrc-v3-timescaledb pg_dump -U btrc_admin btrc_qos_poc | gzip > "$BACKUP_DIR/btrc_qos_poc.sql.gz"

# Backup Metabase metadata
docker exec btrc-v3-timescaledb pg_dump -U btrc_admin metabase_meta | gzip > "$BACKUP_DIR/metabase_meta.sql.gz"

echo "Backup completed: $BACKUP_DIR"

# Keep only last 30 days of backups
find /opt/btrc-qos-dashboard/backups/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
EOF

chmod +x /opt/btrc-qos-dashboard/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/btrc-qos-dashboard/backup.sh") | crontab -
```

### Step 8: Set Up Auto-Restart

Docker Compose services already have `restart: unless-stopped`. For extra reliability:

```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Verify auto-restart policy
docker inspect btrc-v3-metabase --format '{{.HostConfig.RestartPolicy.Name}}'
# Should output: unless-stopped
```

---

## GeoJSON Map Configuration

Custom Bangladesh GeoJSON maps must be configured in Metabase Admin for choropleth visualizations.

### Option A: Serve GeoJSON from a URL (Recommended for Production)

Host the GeoJSON files on a web server accessible to the Metabase container:

```bash
# Example: serve from a static file server
# Files: bgd_divisions.geojson, bgd_districts.geojson
```

Then in Metabase Admin → Settings → Maps → Custom Maps:
1. **Bangladesh Divisions**
   - URL: `http://<file-server>/bgd_divisions.geojson`
   - Region key: `shapeISO`
   - Region name: `shapeName`

2. **Bangladesh Districts**
   - URL: `http://<file-server>/bgd_districts.geojson`
   - Region key: `shapeName`
   - Region name: `shapeName`

### Option B: Use Metabase API

```bash
# Upload GeoJSON via Metabase settings API
curl -X PUT http://localhost:3000/api/setting/custom-geojson \
  -H "X-Metabase-Session: <session-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "custom-id-1": {
      "name": "Bangladesh Divisions",
      "url": "http://<file-server>/bgd_divisions.geojson",
      "region_key": "shapeISO",
      "region_name": "shapeName"
    }
  }'
```

### Known GeoJSON Name Mappings

The database uses modern Bengali names while GeoJSON uses older English names. The dashboard SQL handles these mappings:

| Database Name | GeoJSON Name | Type |
|---------------|-------------|------|
| Chattagram | Chittagong (BD-B) | Division |
| Rajshahi | Rajshani (BD-E) | Division |
| Bogura | Bogra | District |
| Brahmanbaria | Brahamanbaria | District |
| Chapainawabganj | Nawabganj | District |
| Chattogram | Chittagong | District |
| Coxsbazar | Cox's Bazar | District |
| Jashore | Jessore | District |
| Jhalakathi | Jhalokati | District |
| Moulvibazar | Maulvibazar | District |
| Netrokona | Netrakona | District |

---

## Project Structure

```
BTRC-QoS-Monitoring-Dashboard-V3/
├── docker-compose.yml                          # Docker services (TimescaleDB + Metabase)
├── .env                                        # Environment variables
├── requirements.txt                            # Python dependencies
├── load_poc_data.py                            # Load POC JSON data into TimescaleDB
├── load_geojson_boundaries.py                  # Load GeoJSON boundaries
├── create_metabase_executive_dashboard.py      # Create Executive Dashboard
├── create_metabase_regulatory_dashboard.py     # Create Regulatory Dashboard
├── superset_vs_metabase_comparison.html        # BI tool comparison report
│
├── docker/
│   └── timescaledb/
│       └── init.sql                            # Database initialization script
│
├── geodata/
│   ├── bgd_divisions.geojson                   # Bangladesh 8 divisions boundaries
│   ├── bgd_districts.geojson                   # Bangladesh 64 districts boundaries
│   └── bangladesh_divisions_8.geojson          # Alternative divisions file
│
├── poc_data_v2.8/                              # POC test data (JSON files)
│   ├── 01-foundation/                          # Geographic hierarchy + lookups
│   ├── 02-master/                              # ISPs, PoPs, Agents, Packages
│   ├── 03-relationships/                       # Agent-PoP mappings, Subscribers
│   ├── 04-timeseries/                          # QoS measurements, SNMP metrics
│   └── 05-compliance/                          # SLA violations
│
├── docs/
│   ├── DRILL_DOWN_FILTER_TOOLS_COMPARISON.md   # BI tools drill-down comparison
│   ├── EXECUTIVE_DASHBOARD_STATUS.md           # Executive dashboard status
│   ├── REGULATORY_DASHBOARD_STATUS.md          # Regulatory dashboard status
│   ├── MAP_VISUALIZATION_TOOLS_COMPARISON.md   # Map visualization comparison
│   └── CUSTOM_REACT_DASHBOARD_OPTION.md        # Custom React dashboard option
│
└── BTRC-FXBB-QOS-POC_Dev-Spec(...).md         # Requirements specification
```

---

## Useful Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f metabase
docker compose logs -f timescaledb

# Connect to TimescaleDB
psql -h localhost -p 5433 -U btrc_admin -d btrc_qos_poc

# Check data counts
docker exec btrc-v3-timescaledb psql -U btrc_admin -d btrc_qos_poc \
  -c "SELECT 'measurements' as table, count(*) FROM ts_qos_measurements
      UNION ALL SELECT 'isps', count(*) FROM isps
      UNION ALL SELECT 'violations', count(*) FROM sla_violations;"

# Restart Metabase only
docker compose restart metabase

# Full reset (destroys all data)
docker compose down -v
docker compose up -d
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Metabase won't start | Check logs: `docker compose logs metabase`. Ensure TimescaleDB is healthy first. |
| "Connection refused" on port 3000 | Wait 1-2 minutes for Metabase to initialize. Check: `docker compose ps` |
| Dashboard shows no data | Verify data was loaded: connect to DB and run `SELECT count(*) FROM ts_qos_measurements;` |
| Maps not showing | Configure custom GeoJSON in Admin → Settings → Maps. See GeoJSON section above. |
| Filters show as text inputs | Ensure dashboard parameters have `values_query_type: "list"` and `values_source_type: "static-list"` |
| Dashboard script fails with 401 | Metabase session expired. Re-run the script (it creates a new session). |
| Port 5433 already in use | Another PostgreSQL instance is running. Stop it or change `DB_PORT` in `.env` and `docker-compose.yml`. |

---

## Data Overview (POC)

| Metric | Count |
|--------|-------|
| Divisions | 8 |
| Districts | 64 |
| Upazilas | 495 |
| ISPs | 40 |
| PoPs (Points of Presence) | 120 |
| QoS Measurements | 172,800 |
| SLA Violations | 150 |
| Date Range | Nov 30 - Dec 15, 2025 |

---

## License

This project is developed for the Bangladesh Telecommunication Regulatory Commission (BTRC) as part of the Fixed Broadband QoS Monitoring POC.

- **Metabase**: AGPL v3 License
- **TimescaleDB**: Timescale License (open-source edition)
