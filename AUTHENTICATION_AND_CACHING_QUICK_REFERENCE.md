# Authentication & Caching - Quick Reference

**Quick guide for implementing authentication and caching in BTRC Metabase Dashboard**

---

## 🔒 Authentication Options

### **Current Setup**
- ✅ Email/Password (Built-in)
- ✅ Public sharing links (No login)

### **Free Options to Add**

#### **1. Google OAuth (Easiest for Google Workspace)**
```yaml
# docker-compose.yml
metabase:
  environment:
    MB_GOOGLE_AUTH_CLIENT_ID: your-client-id
    MB_GOOGLE_AUTH_CLIENT_SECRET: your-secret
    MB_GOOGLE_AUTH_AUTO_CREATE_ACCOUNTS_DOMAIN: btrc.gov.bd
```

**Setup time:** 15 minutes
**Best for:** Organizations using Gmail/Google Workspace
**See:** METABASE_AUTHENTICATION_GUIDE.md (Page 8-12)

---

#### **2. LDAP/Active Directory (For Government Networks)**
```yaml
# docker-compose.yml
metabase:
  environment:
    MB_LDAP_ENABLED: true
    MB_LDAP_HOST: ad.btrc.local
    MB_LDAP_PORT: 389
    MB_LDAP_BIND_DN: cn=service,dc=btrc,dc=local
    MB_LDAP_PASSWORD: ${LDAP_PASSWORD}
    MB_LDAP_USER_BASE: ou=users,dc=btrc,dc=local
```

**Setup time:** 30 minutes
**Best for:** Organizations with Active Directory
**See:** METABASE_AUTHENTICATION_GUIDE.md (Page 13-17)

---

### **Paid Options**

- **SAML** (Enterprise Edition) - For Okta, Azure AD, OneLogin
- **JWT** (Enterprise Edition) - For custom integrations

---

## 🚀 Caching Options

### **Current Setup**
- ✅ Built-in caching (In-memory)
- ✅ Default TTL: 24 hours

### **Recommended Upgrade: Redis Caching**

#### **Quick Setup (5 minutes)**

**1. Add Redis to docker-compose.yml:**
```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: btrc-v3-redis
    restart: unless-stopped
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - btrc-v3

  metabase:
    environment:
      MB_REDIS_URI: redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

**2. Restart services:**
```bash
docker-compose down
docker-compose up -d
```

**3. Verify:**
```bash
docker exec btrc-v3-redis redis-cli ping
# Should return: PONG
```

**Performance Gain:** 50-70% faster dashboard loads ⚡

**See:** METABASE_CACHING_GUIDE.md (Page 10-16)

---

## 📊 Recommended Configuration for BTRC

### **Authentication Strategy**

**Phase 1 (Current):** ✅ Done
- Email/Password for admins
- Public links for dashboards

**Phase 2 (Optional):**
- Add Google OAuth if using Google Workspace
- OR add LDAP if using Active Directory

**Phase 3 (Future):**
- Upgrade to Enterprise for SAML + 2FA

---

### **Caching Strategy**

**Phase 1 (Current):** ✅ Done
- Built-in caching enabled
- 24-hour default TTL

**Phase 2 (Recommended - 5 min setup):**
- Add Redis for persistent caching
- Benefits:
  - ✅ Survives restarts
  - ✅ 50-70% faster loads
  - ✅ Better for multiple users

**Phase 3 (Optimization):**
- Add database indexes
- Create materialized views
- Use TimescaleDB continuous aggregates

---

## 🎯 Cache TTL Recommendations

### **Executive Dashboard**
```
E1 (KPIs):        1 hour   (updates hourly)
E2 (Maps):        1 hour   (updates hourly)
E3 (Compliance):  15 min   (updates frequently)
```

### **Regulatory Dashboard**
```
R1.1-R1.3 (Status):     5 min   (real-time)
R1.4 (Compliance):      1 hour  (stable data)
R1.5 (Alerts):          1 min   (critical alerts)
R1.6 (Incidents):       1 min   (active incidents)
R2 (Regional):          1 hour  (aggregated data)
R3 (Violations):        15 min  (investigation data)
```

---

## ⚡ Quick Commands

### **Authentication**

**Check current auth methods:**
```bash
docker logs btrc-v3-metabase | grep -i auth
```

**Create new user via API:**
```bash
curl -X POST http://localhost:3000/api/user \
  -H "X-Metabase-Session: YOUR_TOKEN" \
  -d '{"email":"user@btrc.gov.bd","password":"Pass123!"}'
```

---

### **Caching**

**Clear all cache:**
```bash
# Via API
curl -X POST http://localhost:3000/api/cache/clear \
  -H "X-Metabase-Session: YOUR_TOKEN"
```

**Check Redis cache:**
```bash
# If using Redis
docker exec btrc-v3-redis redis-cli INFO stats
docker exec btrc-v3-redis redis-cli KEYS "metabase*"
```

**Monitor cache hit rate:**
```bash
docker exec btrc-v3-redis redis-cli INFO stats | grep keyspace
```

---

## 📁 Documentation Files

| File | Purpose | Page Count |
|------|---------|-----------|
| `METABASE_AUTHENTICATION_GUIDE.md` | Complete auth guide | 25 pages |
| `METABASE_CACHING_GUIDE.md` | Complete caching guide | 30 pages |
| `AUTHENTICATION_AND_CACHING_QUICK_REFERENCE.md` | This file | 3 pages |

---

## 🚀 Next Steps

### **To Add Authentication:**
1. Read: METABASE_AUTHENTICATION_GUIDE.md
2. Choose: Google OAuth OR LDAP
3. Follow setup steps (15-30 minutes)
4. Test with real users

### **To Add Redis Caching:**
1. Read: METABASE_CACHING_GUIDE.md (Page 10-16)
2. Copy Redis config to docker-compose.yml
3. Run: `docker-compose up -d`
4. Verify: `docker exec btrc-v3-redis redis-cli ping`

### **To Optimize Performance:**
1. Set cache TTL per dashboard (see recommendations above)
2. Add database indexes for slow queries
3. Monitor cache hit rate (target: 80%+)
4. Consider materialized views for complex queries

---

## 📞 Support

**For questions about:**
- Authentication → See METABASE_AUTHENTICATION_GUIDE.md
- Caching → See METABASE_CACHING_GUIDE.md
- Technical issues → Check Metabase logs

**Metabase Docs:**
- https://www.metabase.com/docs/latest/

---

**Document Version:** 1.0
**Last Updated:** 2026-02-16
**Maintained By:** BTRC Technical Team
