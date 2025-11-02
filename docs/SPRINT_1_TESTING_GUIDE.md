# Sprint 1 Testing Guide

Quick guide for testing Sprint 1 CRM features with test data.

---

## Quick Start

### Automated (Recommended)

```bash
cd scripts
./reset_and_import.sh
```

### Manual Steps

```bash
# 1. Generate test data
cd test_data
python3 generate_all_test_data.py

# 2. Delete existing CRM data
cd ../scripts
python3 delete_crm_data.py

# 3. Import all data
python3 import_all_sprint1.py

# 4. Verify
python3 verify_data.py
```

---

## Configuration

Copy and configure your credentials:

```bash
cd scripts
cp config.example.py config.py
# Edit config.py with your Odoo credentials
```

The `config.py` file is git-ignored for security.

---

## What Gets Imported

- **22 Staff** (1 Director, 3 Managers, 13 Sales, 5 Telesales)
- **7 Sales Teams** (Regional, Industry, Enterprise)
- **100 Customers** (Vietnamese companies with Tax IDs)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `delete_crm_data.py` | Delete CRM data |
| `import_staff.py` | Import users |
| `import_sales_teams.py` | Import teams |
| `import_customers.py` | Import customers |
| `import_all_sprint1.py` | Import everything |
| `verify_data.py` | Verify data |
| `reset_and_import.sh` | Complete workflow |

### Options

```bash
# Non-interactive mode
python3 delete_crm_data.py --no-confirm

# Auto-confirm all
./reset_and_import.sh -y

# Skip steps
./reset_and_import.sh --skip-delete
./reset_and_import.sh --skip-generate
```

---

## Troubleshooting

**Connection Error:**
```bash
# Check Odoo is running
docker ps | grep odoo

# Test config
python3 config.py
```

**Import Errors:**
```bash
# Restart Odoo
docker restart odoo_web

# Check logs
docker logs odoo_web
```

---

## Testing in Odoo

After import, test in Odoo UI:

1. **Customers:** CRM → Customers
   - Check Tax IDs, salespeople assigned
   - Verify 100 customers imported

2. **Sales Teams:** CRM → Configuration → Sales Teams
   - Verify 7 teams with leaders and members

3. **Users:** Settings → Users
   - Check 22 users created

---

## Useful Commands

```bash
# Odoo shell
docker exec -it odoo_web odoo shell -d your_db

# Count records (in Odoo shell)
env['res.users'].search_count([])
env['crm.team'].search_count([])
env['res.partner'].search_count([])

# View logs
docker logs -f odoo_web
```

---

## Next Steps

1. Verify data in Odoo UI
2. Create test leads for auto-assignment testing
3. Test Sprint 1 features per `SPRINT_1_REQUIREMENTS_EN.md`

---

**See also:** `scripts/README.md` for script details
