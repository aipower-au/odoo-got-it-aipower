# SPRINT 1 TESTING GUIDE

Complete guide for testing Sprint 1 CRM features with test data import/export.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Step-by-Step Guide](#detailed-step-by-step-guide)
5. [Script Reference](#script-reference)
6. [Manual Testing Procedures](#manual-testing-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Docker Commands](#docker-commands)

---

## Overview

This guide helps you test Sprint 1 CRM requirements by:

- Cleaning existing CRM data from Odoo
- Generating fresh test data (100 customers, 22 staff, 7 teams)
- Importing data via Python scripts using XML-RPC
- Verifying data integrity

### Sprint 1 Features to Test

Based on `SPRINT_1_REQUIREMENTS_EN.md`:

1. **Customer/Merchant/Supplier Management**
   - Tax ID (MST) duplicate checking
   - Salesperson assignment
   - Customer information updates
   - Status management (Potential → Client)

2. **Lead Management**
   - Auto-assign leads by rules (region, industry, customer type, order value)
   - Duplicate lead detection
   - Salesperson reassignment

3. **Sales Teams**
   - Regional teams (North, South, Central)
   - Industry-focused teams
   - Team member management

---

## Prerequisites

### System Requirements

- **Odoo 18** running in Docker containers
- **Python 3** installed on host machine
- **Network access** to Odoo at `http://localhost:8069`

### Check Your Setup

```bash
# Check Docker containers are running
docker ps

# Expected output: odoo_web and odoo_db containers

# Check Python version
python3 --version
# Should be Python 3.7+

# Check Odoo is accessible
curl http://localhost:8069/web/database/selector
```

### File Structure

```
odoo-got-it-aipower/
├── test_data/
│   ├── generate_all_test_data.py    # CSV generator
│   ├── customers_sprint1.csv         # 100 customers
│   ├── staff_sprint1.csv             # 22 staff members
│   └── sales_teams_sprint1.csv       # 7 sales teams
├── scripts/
│   ├── config.py                     # Connection settings
│   ├── delete_crm_data.py            # Data cleanup
│   ├── import_staff.py               # Import users
│   ├── import_sales_teams.py         # Import teams
│   ├── import_customers.py           # Import customers
│   ├── import_all_sprint1.py         # Master import script
│   ├── verify_data.py                # Data verification
│   └── reset_and_import.sh           # Automated workflow
└── docs/
    └── SPRINT_1_TESTING_GUIDE.md     # This file
```

---

## Quick Start

### Option 1: Automated (Recommended)

Run the complete workflow with one command:

```bash
cd scripts
./reset_and_import.sh
```

This will:
1. Generate fresh CSV test data
2. Delete existing CRM data
3. Import staff, teams, and customers
4. Verify all data

### Option 2: Step by Step

```bash
cd scripts

# Step 1: Generate test data
cd ../test_data
python3 generate_all_test_data.py
cd ../scripts

# Step 2: Delete existing data
python3 delete_crm_data.py

# Step 3: Import all data
python3 import_all_sprint1.py

# Step 4: Verify
python3 verify_data.py
```

---

## Detailed Step-by-Step Guide

### Step 1: Configure Connection Settings

Edit `scripts/config.py` if needed:

```python
# Odoo server URL
ODOO_URL = 'http://localhost:8069'

# Database name
ODOO_DB = 'odoo'

# Admin credentials
ODOO_USERNAME = 'admin@gotit.vn'
ODOO_PASSWORD = 'Aipower!123'
```

Or use environment variables:

```bash
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin@gotit.vn
export ODOO_PASSWORD=Aipower!123
```

### Step 2: Generate Test Data

```bash
cd test_data
python3 generate_all_test_data.py
```

**Expected Output:**
```
======================================================================
SPRINT 1 TEST DATA GENERATOR
======================================================================

Generating staff data...
  ✓ Generated 22 staff members
Generating customer data...
  ✓ Generated 100 customers
Generating sales teams data...
  ✓ Generated 7 sales teams

✅ All test data files generated successfully!
```

**Generated Files:**
- `staff_sprint1.csv` - 22 users (1 Director, 3 Managers, 13 Sales Executives, 5 Telesales)
- `customers_sprint1.csv` - 100 Vietnamese companies
- `sales_teams_sprint1.csv` - 7 teams (3 Regional, 2 Industry, 1 Enterprise, 1 Telesales)

### Step 3: Delete Existing CRM Data

**⚠️ Warning:** This will delete all leads, opportunities, sales teams, and customer partners!

```bash
cd scripts
python3 delete_crm_data.py
```

**Interactive Mode:**
```
Do you want to continue? (yes/no): yes
Delete non-admin users too? (yes/no): no
```

**Non-Interactive Mode:**
```bash
python3 delete_crm_data.py --no-confirm
```

**What Gets Deleted:**
- ✓ All CRM leads/opportunities
- ✓ All sales teams
- ✓ All partner/customer records (except those linked to users)
- ✓ Optionally: non-admin users

**What's Preserved:**
- ✓ Admin user
- ✓ System users
- ✓ User-linked partner records
- ✓ Module configurations

### Step 4: Import Staff (Users)

```bash
python3 import_staff.py
```

**What It Does:**
- Creates res.users records from `staff_sprint1.csv`
- Assigns appropriate user groups (Sales, Sales Manager)
- Sets default password: `gotit2025`

**Expected Output:**
```
✓ Created: Phạm Minh Tuấn
✓ Created: Lê Quốc Bảo
✓ Created: Nguyễn Văn Thành
...
✅ Successfully processed: 22 users
```

**CSV Mapping:**
- `name` → User name
- `login` → Login username
- `email` → Email address
- `phone` → Phone number
- `job_title` → Determines user groups

### Step 5: Import Sales Teams

```bash
python3 import_sales_teams.py
```

**What It Does:**
- Creates crm.team records from `sales_teams_sprint1.csv`
- Links team leaders (user_id)
- Assigns team members (member_ids)

**Expected Output:**
```
✓ Created: North Regional Team (4 members)
✓ Created: South Regional Team (5 members)
✓ Created: Central Regional Team (4 members)
...
✅ Successfully processed: 7 teams
```

**Teams Created:**
1. North Regional Team - Hà Nội, Hải Phòng, Huế
2. South Regional Team - Hồ Chí Minh, Biên Hòa, Vũng Tàu
3. Central Regional Team - Đà Nẵng, Nha Trang, Quy Nhơn, Cần Thơ
4. Technology & Digital Team
5. F&B & Retail Team
6. Enterprise Sales Team
7. Telesales Team

### Step 6: Import Customers

```bash
python3 import_customers.py
```

**What It Does:**
- Creates res.partner records from `customers_sprint1.csv`
- Links to salespeople (user_id)
- Sets Vietnamese company attributes

**Expected Output:**
```
... 20 processed (15 created, 5 updated)
... 40 processed (35 created, 5 updated)
...
✅ Successfully processed: 100 customers
```

**Customer Fields:**
- `company_name` → Partner name
- `tax_id` (MST) → VAT number
- `phone`, `email` → Contact info
- `delivery_address` → Street address
- `salesperson` → Linked to res.users
- `status` → Potential/Client/Lost (for testing)

### Step 7: Verify Data

```bash
python3 verify_data.py
```

**What It Checks:**
- Record counts (users, teams, partners)
- Relationship integrity (teams → leaders → members)
- Data quality (salespeople assigned, Tax IDs present)

**Expected Output:**
```
📊 Record Counts:
   Users: 24 (Sales: 22)
   Sales Teams: 7
   Customers: 100 (Companies: 100)

📈 Data Quality:
   Customers with Salesperson: 100/100
   Customers with Tax ID: 100/100

✅ All relationship checks passed!
```

### Step 8: Master Import (All in One)

Instead of steps 4-6, you can run:

```bash
python3 import_all_sprint1.py
```

This runs all three imports in sequence with a single command.

---

## Script Reference

### `config.py`

Central configuration file.

**Test Configuration:**
```bash
python3 config.py
```

### `delete_crm_data.py`

Delete CRM data safely.

**Usage:**
```bash
# Interactive
python3 delete_crm_data.py

# Auto-confirm
python3 delete_crm_data.py --no-confirm
python3 delete_crm_data.py -y
```

**Options:**
- `--no-confirm`, `-y` - Skip confirmation prompts

### `import_staff.py`

Import staff as Odoo users.

**Usage:**
```bash
python3 import_staff.py
```

**Default Password:** `gotit2025`

### `import_sales_teams.py`

Import sales teams.

**Usage:**
```bash
python3 import_sales_teams.py
```

### `import_customers.py`

Import customer/partner records.

**Usage:**
```bash
python3 import_customers.py
```

### `import_all_sprint1.py`

Master import script (runs all imports).

**Usage:**
```bash
python3 import_all_sprint1.py
```

**Execution Order:**
1. Staff (users must exist first)
2. Sales Teams (requires users)
3. Customers (requires users for salesperson links)

### `verify_data.py`

Verify imported data integrity.

**Usage:**
```bash
python3 verify_data.py
```

**Checks:**
- Record counts
- Relationship integrity
- Data quality metrics

### `reset_and_import.sh`

Automated workflow script.

**Usage:**
```bash
# Full workflow
./reset_and_import.sh

# Auto-confirm (no prompts)
./reset_and_import.sh -y

# Skip deletion
./reset_and_import.sh --skip-delete

# Skip CSV generation
./reset_and_import.sh --skip-generate

# Skip verification
./reset_and_import.sh --skip-verify

# Help
./reset_and_import.sh --help
```

**Options:**
- `-y, --yes` - Auto-confirm all prompts
- `--skip-delete` - Skip data deletion step
- `--skip-generate` - Skip CSV generation
- `--skip-verify` - Skip verification
- `-h, --help` - Show help

---

## Manual Testing Procedures

After importing data, test these Sprint 1 features manually in Odoo:

### 1. Test Customer Management

**Access:** CRM → Customers

**Tests:**
1. **Duplicate Tax ID Check:**
   - Try to create a new customer with an existing Tax ID
   - Expected: Warning or prevention of duplicate

2. **Salesperson Assignment:**
   - View customers, check salesperson field
   - Expected: All have assigned salespeople

3. **Customer Information:**
   - Open a customer record
   - Check: Tax ID, contact info, address, status
   - Expected: All fields populated from CSV

### 2. Test Sales Teams

**Access:** CRM → Configuration → Sales Teams

**Tests:**
1. **Team Structure:**
   - View all 7 teams
   - Check team leaders and members
   - Expected: 3 regional, 2 industry, 1 enterprise, 1 telesales

2. **Regional Coverage:**
   - North Team: Hà Nội, Hải Phòng, Huế
   - South Team: Hồ Chí Minh, Biên Hòa, Vũng Tàu
   - Central Team: Đà Nẵng, Nha Trang, Quy Nhơn, Cần Thơ

### 3. Test User Access

**Access:** Settings → Users & Companies → Users

**Tests:**
1. **Login as Sales User:**
   - Username: One from `staff_sprint1.csv` (e.g., `thành.n`)
   - Password: `gotit2025`
   - Expected: Can access CRM module

2. **Check User Groups:**
   - Sales Executives should have Sales User rights
   - Sales Managers should have Sales Manager rights

### 4. Test Lead Assignment Rules

**Access:** CRM → Leads

**Tests:**
1. **Create Test Lead:**
   - Set region: Hà Nội
   - Expected: Should suggest North Regional Team

2. **Auto-Assignment by Industry:**
   - Create lead with industry: Technology
   - Expected: Could be assigned to Technology & Digital Team

---

## Troubleshooting

### Connection Errors

**Error:** `Authentication failed`

**Solution:**
```bash
# Check credentials in config.py
python3 config.py

# Test Odoo access
curl http://localhost:8069
```

### File Not Found Errors

**Error:** `File not found: staff_sprint1.csv`

**Solution:**
```bash
# Generate CSV files first
cd test_data
python3 generate_all_test_data.py
```

### Import Errors

**Error:** `❌ Error with <name>: ...`

**Solutions:**
1. Check if Odoo is running:
   ```bash
   docker ps | grep odoo
   ```

2. Check database connection:
   ```bash
   docker exec -it odoo_db psql -U odoo -d odoo -c "\dt"
   ```

3. Restart Odoo:
   ```bash
   docker restart odoo_web
   ```

### Duplicate Import Issues

**Problem:** Running import twice creates duplicates

**Solution:**
```bash
# Delete data first
python3 delete_crm_data.py --no-confirm

# Then import
python3 import_all_sprint1.py
```

Or the scripts handle this by checking for existing records and updating them.

### Permission Errors

**Error:** Access denied errors in Odoo

**Solution:**
1. Make sure you're logged in as admin
2. Check user groups are assigned correctly
3. Update module if needed:
   ```bash
   docker exec -it odoo_web odoo -d odoo -u crm --stop-after-init
   ```

---

## Docker Commands

### Useful Docker Commands for Testing

```bash
# View Odoo logs
docker logs -f odoo_web

# Access Odoo container shell
docker exec -it odoo_web bash

# Access Odoo shell (Python)
docker exec -it odoo_web odoo shell -d odoo

# Restart Odoo
docker restart odoo_web

# Access PostgreSQL
docker exec -it odoo_db psql -U odoo -d odoo

# Backup database
docker exec odoo_db pg_dump -U odoo odoo > backup.sql

# Restore database
cat backup.sql | docker exec -i odoo_db psql -U odoo odoo
```

### Odoo Shell Commands

```bash
# Start shell
docker exec -it odoo_web odoo shell -d odoo
```

**In shell:**
```python
# Count records
env['res.users'].search_count([])
env['crm.team'].search_count([])
env['res.partner'].search_count([])

# List users
users = env['res.users'].search([])
for u in users:
    print(f"{u.name} ({u.login})")

# List teams
teams = env['crm.team'].search([])
for t in teams:
    print(f"{t.name} - Leader: {t.user_id.name}")

# Find customer by Tax ID
partner = env['res.partner'].search([('vat', '=', '1001366353')])
print(partner.name, partner.user_id.name)
```

---

## Expected Data After Import

### Users (22 total)
- 1 Sales Director
- 3 Sales Managers (North, South, Central)
- 8 Sales Executives (main team from CSV)
- 5 Additional Sales Executives
- 5 Telesales Executives

### Sales Teams (7 total)
- North Regional Team (4 members)
- South Regional Team (5 members)
- Central Regional Team (4 members)
- Technology & Digital Team (3 members)
- F&B & Retail Team (4 members)
- Enterprise Sales Team (3 members)
- Telesales Team (5 members)

### Customers (100 total)
- All Vietnamese companies
- Distributed across 10 regions
- Status: ~55 Client, ~36 Potential, ~9 Lost
- All have Tax ID (MST)
- All assigned to salespeople

---

## Next Steps After Import

1. **Verify in Odoo UI:**
   - Login to http://localhost:8069
   - Navigate to CRM module
   - Check Customers, Teams, Users

2. **Create Test Leads:**
   - Create leads with different regions
   - Test auto-assignment rules
   - Check duplicate detection

3. **Test Workflows:**
   - Telesale → Sales conversion
   - Status changes (Potential → Client)
   - Salesperson reassignment

4. **Develop Sprint 1 Features:**
   - Implement duplicate Tax ID checking
   - Build auto-assignment rules
   - Create status change automation

---

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Review Sprint 1 requirements: `docs/SPRINT_1_REQUIREMENTS_EN.md`
3. Check Odoo logs: `docker logs odoo_web`
4. Verify test data: `python3 scripts/verify_data.py`

---

**Last Updated:** 2025-11-02
**Odoo Version:** 18.0
**Python Version:** 3.7+
