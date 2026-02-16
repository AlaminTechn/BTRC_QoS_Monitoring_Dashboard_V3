# Metabase Authentication System - Complete Guide

**Version:** Metabase v0.58.5.2
**Last Updated:** 2026-02-16

---

## 📋 Table of Contents

1. [Current Authentication Setup](#current-authentication-setup)
2. [Built-in Authentication (Free)](#built-in-authentication-free)
3. [Google OAuth (Free)](#google-oauth-free)
4. [LDAP/Active Directory (Free)](#ldapactive-directory-free)
5. [SAML (Enterprise)](#saml-enterprise)
6. [JWT (Enterprise)](#jwt-enterprise)
7. [User Management](#user-management)
8. [Security Best Practices](#security-best-practices)
9. [Implementation Examples](#implementation-examples)

---

## 🔒 Current Authentication Setup

### **Status**
- **Method:** Email/Password (Built-in)
- **Admin Account:** alamin.technometrics22@gmail.com
- **User Database:** PostgreSQL (metabase_meta)
- **Public Sharing:** Enabled (anonymous access to specific dashboards)

### **Current Users**
- Admin: alamin.technometrics22@gmail.com

---

## 1️⃣ Built-in Authentication (Free)

### **Overview**
Metabase's default authentication using email and password stored in the database.

### **Features**
✅ Email/Password login
✅ Password reset via email
✅ User groups and permissions
✅ Session management
✅ Remember me option

### **Configuration**

#### **A. Enable Email Authentication**
Already enabled by default. No configuration needed.

#### **B. Configure Email Server (For password reset)**

Add to `docker-compose.yml`:
```yaml
metabase:
  environment:
    # Email server settings
    MB_EMAIL_SMTP_HOST: smtp.gmail.com
    MB_EMAIL_SMTP_PORT: 587
    MB_EMAIL_SMTP_SECURITY: tls
    MB_EMAIL_SMTP_USERNAME: your-email@gmail.com
    MB_EMAIL_SMTP_PASSWORD: your-app-password
    MB_EMAIL_FROM_ADDRESS: noreply@btrc.gov.bd
```

#### **C. Create New Users**

**Via Web UI:**
1. Admin Settings → People
2. Click "Invite someone"
3. Enter email address
4. Select group (Admin/Viewer/etc.)
5. Click "Create"

**Via API:**
```bash
curl -X POST http://localhost:3000/api/user \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@btrc.gov.bd",
    "password": "SecurePassword123!"
  }'
```

### **Pros & Cons**

✅ **Pros:**
- Free
- Simple setup
- No external dependencies
- Works offline

❌ **Cons:**
- Manual user management
- No single sign-on (SSO)
- Users need separate passwords
- No integration with existing directory

---

## 2️⃣ Google OAuth (Free)

### **Overview**
Allow users to sign in with their Google accounts. Perfect for organizations using Google Workspace.

### **Setup Steps**

#### **Step 1: Create Google OAuth App**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "BTRC Metabase"
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen:
   - App name: BTRC Dashboard
   - User support email: your-email@btrc.gov.bd
   - Authorized domains: btrc.gov.bd
6. Create OAuth Client:
   - Application type: Web application
   - Name: BTRC Metabase Auth
   - Authorized redirect URIs:
     ```
     http://localhost:3000/auth/google/callback
     http://your-domain.com/auth/google/callback
     ```
7. Copy **Client ID** and **Client Secret**

#### **Step 2: Configure Metabase**

Add to `docker-compose.yml`:
```yaml
metabase:
  environment:
    # Google OAuth
    MB_GOOGLE_AUTH_CLIENT_ID: your-client-id.apps.googleusercontent.com
    MB_GOOGLE_AUTH_CLIENT_SECRET: your-client-secret
    MB_GOOGLE_AUTH_AUTO_CREATE_ACCOUNTS_DOMAIN: btrc.gov.bd
```

#### **Step 3: Enable in Metabase UI**

1. Admin Settings → Authentication
2. Enable "Sign in with Google"
3. Enter Client ID and Client Secret
4. Set "Automatically create accounts": Yes
5. Set domain filter: `btrc.gov.bd` (optional)
6. Save

#### **Step 4: Test**

1. Logout
2. Click "Sign in with Google"
3. Login with Google account
4. Should auto-create account in Metabase

### **Auto-Create Configuration**

**Allow specific domain only:**
```yaml
MB_GOOGLE_AUTH_AUTO_CREATE_ACCOUNTS_DOMAIN: btrc.gov.bd
```

**Assign default group:**
Set in Admin UI → Authentication → Google Sign-In

### **Pros & Cons**

✅ **Pros:**
- Free
- Single Sign-On (SSO)
- Auto account creation
- No password management
- Familiar to users

❌ **Cons:**
- Requires Google accounts
- Internet dependency
- Limited to Google Workspace users
- Less control over user lifecycle

---

## 3️⃣ LDAP/Active Directory (Free)

### **Overview**
Integrate with your organization's LDAP or Active Directory for centralized authentication.

### **Setup Steps**

#### **Step 1: Prepare LDAP Server**

Ensure you have:
- LDAP server address
- Bind DN (service account)
- Bind password
- User search base DN
- Group search base DN (optional)

#### **Step 2: Configure Metabase**

Add to `docker-compose.yml`:
```yaml
metabase:
  environment:
    # LDAP Configuration
    MB_LDAP_ENABLED: true
    MB_LDAP_HOST: ldap.btrc.gov.bd
    MB_LDAP_PORT: 389
    MB_LDAP_SECURITY: starttls
    MB_LDAP_BIND_DN: cn=metabase,ou=services,dc=btrc,dc=gov,dc=bd
    MB_LDAP_PASSWORD: your-bind-password

    # User mapping
    MB_LDAP_USER_BASE: ou=users,dc=btrc,dc=gov,dc=bd
    MB_LDAP_USER_FILTER: (objectClass=inetOrgPerson)

    # Attribute mapping
    MB_LDAP_ATTRIBUTE_EMAIL: mail
    MB_LDAP_ATTRIBUTE_FIRSTNAME: givenName
    MB_LDAP_ATTRIBUTE_LASTNAME: sn

    # Group mapping (optional)
    MB_LDAP_GROUP_SYNC: true
    MB_LDAP_GROUP_BASE: ou=groups,dc=btrc,dc=gov,dc=bd
```

#### **Step 3: Enable in Metabase UI**

1. Admin Settings → Authentication → LDAP
2. Configure settings:
   - LDAP Host: ldap.btrc.gov.bd
   - LDAP Port: 389 (or 636 for LDAPS)
   - Security: STARTTLS or LDAPS
   - Username/Bind DN: service account
   - Password: service account password
3. Configure User Schema:
   - User search base: `ou=users,dc=btrc,dc=gov,dc=bd`
   - User filter: `(objectClass=inetOrgPerson)`
4. Test connection
5. Save

#### **Step 4: Group Mapping (Optional)**

Map LDAP groups to Metabase groups:
1. Admin Settings → People → Groups
2. Click on a group
3. Enable "LDAP group mapping"
4. Enter LDAP group DN:
   ```
   cn=metabase-admins,ou=groups,dc=btrc,dc=gov,dc=bd
   ```

### **Example LDAP Structure**

```
dc=btrc,dc=gov,dc=bd
├── ou=users
│   ├── uid=john.doe
│   ├── uid=jane.smith
│   └── uid=admin
└── ou=groups
    ├── cn=metabase-admins
    ├── cn=metabase-viewers
    └── cn=metabase-analysts
```

### **Pros & Cons**

✅ **Pros:**
- Free
- Centralized user management
- Auto-sync with directory
- Group-based permissions
- Works with AD, OpenLDAP, etc.

❌ **Cons:**
- Requires LDAP infrastructure
- Complex initial setup
- Network dependency
- Troubleshooting can be difficult

---

## 4️⃣ SAML (Enterprise - Paid)

### **Overview**
SAML 2.0 Single Sign-On integration with identity providers like Okta, Azure AD, OneLogin.

### **Requirements**
⚠️ **Requires Metabase Enterprise Edition** (Paid)

### **Supported Identity Providers**
- Okta
- Azure Active Directory
- Google Workspace (SAML)
- OneLogin
- Auth0
- Keycloak
- Any SAML 2.0 compliant IdP

### **Setup Overview**

1. **In IdP (Okta/Azure AD):**
   - Create SAML application
   - Set ACS URL: `https://your-domain.com/auth/sso`
   - Set Entity ID: `https://your-domain.com`
   - Configure attribute mappings

2. **In Metabase Enterprise:**
   - Admin Settings → Authentication → SAML
   - Upload IdP metadata XML
   - Configure attribute mappings
   - Enable SAML

### **Configuration**
```yaml
metabase:
  environment:
    MB_SAML_ENABLED: true
    MB_SAML_IDENTITY_PROVIDER_URI: https://idp.btrc.gov.bd/saml
    MB_SAML_IDENTITY_PROVIDER_CERTIFICATE: /path/to/cert.pem
```

### **Pros & Cons**

✅ **Pros:**
- Enterprise-grade SSO
- Support for MFA
- Centralized access control
- Audit logging
- Just-in-time provisioning

❌ **Cons:**
- **Requires paid license**
- Complex setup
- Requires identity provider
- Higher cost

---

## 5️⃣ JWT (Enterprise - Paid)

### **Overview**
JSON Web Token authentication for custom integrations and embedded dashboards.

### **Requirements**
⚠️ **Requires Metabase Enterprise Edition** (Paid)

### **Use Cases**
- Custom authentication systems
- Embedded dashboards with SSO
- API-only access
- Mobile apps

### **Configuration**
```yaml
metabase:
  environment:
    MB_JWT_ENABLED: true
    MB_JWT_SHARED_SECRET: your-secret-key
    MB_JWT_IDENTITY_PROVIDER_URI: https://auth.btrc.gov.bd
```

### **Token Generation Example**
```python
import jwt
import datetime

payload = {
    'email': 'user@btrc.gov.bd',
    'first_name': 'John',
    'last_name': 'Doe',
    'groups': ['Viewers'],
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')
```

### **Pros & Cons**

✅ **Pros:**
- Flexible integration
- Stateless authentication
- Good for APIs
- Custom logic support

❌ **Cons:**
- **Requires paid license**
- Complex implementation
- Security considerations
- Token management overhead

---

## 👥 User Management

### **User Roles**

1. **Administrator**
   - Full access
   - Can manage users
   - Can modify settings
   - Can create/edit everything

2. **Analyst**
   - Can create queries
   - Can create dashboards
   - Can access data browser
   - Cannot manage users

3. **Viewer**
   - Can view dashboards
   - Can use filters
   - Cannot create content
   - Read-only access

### **User Groups**

Create groups for better permission management:

**Example Structure:**
```
BTRC Organization
├── Administrators
│   └── alamin.technometrics22@gmail.com
├── Management Team
│   ├── ceo@btrc.gov.bd
│   └── cto@btrc.gov.bd
├── Operations Team
│   ├── pm@btrc.gov.bd
│   └── analyst@btrc.gov.bd
└── Viewers
    └── external-consultant@example.com
```

### **Creating User Groups**

**Via Web UI:**
1. Admin Settings → People → Groups
2. Click "Create a group"
3. Name: "Operations Team"
4. Add members
5. Set data permissions
6. Save

**Permissions Matrix Example:**
```
Group              | Databases | Collections | Dashboards
-------------------|-----------|-------------|------------
Administrators     | Full      | Full        | Full
Management Team    | View      | View        | Edit own
Operations Team    | View      | View        | View
Viewers            | None      | None        | View public
```

---

## 🔐 Security Best Practices

### **1. Password Policy**

Configure strong password requirements:
```yaml
metabase:
  environment:
    MB_PASSWORD_COMPLEXITY: strong
    MB_PASSWORD_LENGTH: 12
```

### **2. Session Management**

Configure session timeouts:
```yaml
metabase:
  environment:
    MB_SESSION_TIMEOUT: 1440  # 24 hours in minutes
```

### **3. IP Whitelisting**

Restrict access to specific IPs (use reverse proxy):
```nginx
# nginx.conf
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://metabase:3000;
}
```

### **4. HTTPS Enforcement**

Always use HTTPS in production:
```yaml
metabase:
  environment:
    MB_SITE_URL: https://dashboard.btrc.gov.bd
```

### **5. Audit Logging**

Enable audit logs (Enterprise):
```yaml
metabase:
  environment:
    MB_AUDIT_LOG_ENABLED: true
```

### **6. Two-Factor Authentication (2FA)**

⚠️ **Not supported in open-source version**
- Available in Enterprise Edition
- Or use OAuth with 2FA-enabled providers (Google, Microsoft)

---

## 📝 Implementation Examples

### **Example 1: Google OAuth for BTRC Staff**

```yaml
# docker-compose.yml
services:
  metabase:
    environment:
      # Google OAuth
      MB_GOOGLE_AUTH_CLIENT_ID: 123456-abc.apps.googleusercontent.com
      MB_GOOGLE_AUTH_CLIENT_SECRET: GOCSPX-xxxxxxxxxxxxx
      MB_GOOGLE_AUTH_AUTO_CREATE_ACCOUNTS_DOMAIN: btrc.gov.bd

      # Site URL
      MB_SITE_URL: https://dashboard.btrc.gov.bd
```

**Result:**
- All @btrc.gov.bd Google accounts can sign in
- Accounts auto-created on first login
- Assigned to "All Users" group by default

---

### **Example 2: LDAP for Government Network**

```yaml
# docker-compose.yml
services:
  metabase:
    environment:
      # LDAP
      MB_LDAP_ENABLED: true
      MB_LDAP_HOST: ad.btrc.local
      MB_LDAP_PORT: 389
      MB_LDAP_SECURITY: starttls
      MB_LDAP_BIND_DN: cn=svc-metabase,ou=service-accounts,dc=btrc,dc=local
      MB_LDAP_PASSWORD: ${LDAP_PASSWORD}

      # User mapping
      MB_LDAP_USER_BASE: ou=employees,dc=btrc,dc=local
      MB_LDAP_USER_FILTER: (&(objectClass=user)(memberOf=cn=dashboard-users,ou=groups,dc=btrc,dc=local))
      MB_LDAP_ATTRIBUTE_EMAIL: userPrincipalName
      MB_LDAP_ATTRIBUTE_FIRSTNAME: givenName
      MB_LDAP_ATTRIBUTE_LASTNAME: sn

      # Group sync
      MB_LDAP_GROUP_SYNC: true
      MB_LDAP_GROUP_BASE: ou=groups,dc=btrc,dc=local
```

**Result:**
- Users authenticate with Windows credentials
- Group membership synced from Active Directory
- Permissions managed centrally

---

### **Example 3: Hybrid (Email + Public Links)**

Current BTRC setup:
```yaml
# docker-compose.yml
services:
  metabase:
    environment:
      # Email auth (default)
      MB_EMAIL_SMTP_HOST: smtp.gmail.com
      MB_EMAIL_SMTP_PORT: 587
      MB_EMAIL_SMTP_SECURITY: tls
      MB_EMAIL_SMTP_USERNAME: noreply@btrc.gov.bd
      MB_EMAIL_SMTP_PASSWORD: ${SMTP_PASSWORD}

      # Site settings
      MB_SITE_URL: http://192.168.200.52:3000
      MB_EMBEDDING_APP_ORIGIN: http://localhost:8080
```

**Public Dashboard Access:**
- Executive Dashboard: No login required
- Regulatory Dashboard: No login required
- Admin panel: Email/password required

---

## 🚀 Recommended Setup for BTRC

### **Phase 1: Current (Immediate)**
✅ Email/Password authentication
✅ Public sharing links
✅ Admin account only

**Status:** Already implemented

---

### **Phase 2: Internal Staff (Short-term)**

**Option A: Google OAuth (If using Google Workspace)**
```yaml
MB_GOOGLE_AUTH_CLIENT_ID: your-id
MB_GOOGLE_AUTH_CLIENT_SECRET: your-secret
MB_GOOGLE_AUTH_AUTO_CREATE_ACCOUNTS_DOMAIN: btrc.gov.bd
```

**Option B: LDAP (If using Active Directory)**
```yaml
MB_LDAP_ENABLED: true
MB_LDAP_HOST: ad.btrc.local
MB_LDAP_PORT: 389
MB_LDAP_BIND_DN: service-account-dn
```

---

### **Phase 3: Enterprise (Long-term)**

For production deployment:
- Upgrade to Metabase Enterprise
- Implement SAML with Azure AD/Okta
- Enable audit logging
- Configure 2FA
- Set up role-based access control (RBAC)

---

## 📞 Support

### **Metabase Documentation**
- https://www.metabase.com/docs/latest/people-and-groups/start
- https://www.metabase.com/docs/latest/people-and-groups/google-and-ldap

### **Community**
- Metabase Discourse: https://discourse.metabase.com/
- GitHub Issues: https://github.com/metabase/metabase/issues

### **Enterprise Support**
- Contact: sales@metabase.com
- For SAML, JWT, and advanced features

---

**Document Version:** 1.0
**Last Updated:** 2026-02-16
**Maintained By:** BTRC Technical Team
