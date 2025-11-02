# Odoo CRM Demo Data Scripts

Python scripts for importing enterprise-scale demo data into Odoo 18 CRM.

## Quick Start

### Test Dataset (Small - 2 mins)

```bash
# 1. Generate test data
cd ../test_data
python3 generate_enterprise_demo_data.py --config test
python3 generate_crm_demo_data.py --config test

# 2. Import
cd ../scripts
python3 delete_all_crm_data.py --no-confirm
python3 import_all_enterprise_demo.py

# Result: ~420 records (35 staff, 100 customers, 50 leads, etc.)
```

### Production Dataset (Full - 25 mins)

```bash
# 1. Generate production data
cd ../test_data
python3 generate_enterprise_demo_data.py --config production
python3 generate_crm_demo_data.py --config production

# 2. Import
cd ../scripts
python3 delete_all_crm_data.py --no-confirm
python3 import_all_enterprise_demo.py

# Result: ~9,300 records (150 staff, 3000 customers, 2000 leads, etc.)
```

### Verify Import

```bash
python3 verify_enterprise_demo.py
```

---

## Configuration

**Test Mode:** `config_test.py`
- 35 staff, 100 customers, 10 teams
- 50 leads, 30 opportunities, 20 quotations, 80 activities
- Total: ~420 records

**Production Mode:** `config_production.py`
- 150 staff, 3000 customers, 35 teams
- 2000 leads, 1500 opportunities, 600 quotations, 3000 activities
- Total: ~9,300 records

---

## Configuration File

Copy and edit:

```bash
cp config.example.py config.py
# Edit config.py with your Odoo URL, database, username, password
```

Required settings:
```python
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin@gotit.vn"
ODOO_PASSWORD = "your_password"
```

---

## Scripts Reference

### Master Scripts

| Script | Purpose |
|--------|---------|
| `import_all_enterprise_demo.py` | Import everything |
| `delete_all_crm_data.py` | Delete all CRM data |
| `verify_enterprise_demo.py` | Verify data counts |

### Individual Import Scripts

| Script | What It Imports |
|--------|----------------|
| `import_staff_enterprise.py` | Staff/users |
| `import_customers_enterprise.py` | Customers/partners |
| `import_sales_teams_enterprise.py` | Sales teams |
| `import_crm_foundation.py` | Stages, sources, tags |
| `import_leads.py` | Leads |
| `import_opportunities.py` | Opportunities |
| `import_quotations.py` | Quotations + lines |
| `import_activities.py` | Activities |

### Utilities

| File | Purpose |
|------|---------|
| `odoo_utils.py` | Common functions (connection, lookups) |
| `config.py` | Connection settings |

---

## Import Order

1. Staff → 2. Teams → 3. Customers → 4. CRM Foundation → 5. Products → 6. Leads → 7. Opportunities → 8. Quotations → 9. Activities

**Why?** Respects foreign key dependencies.

---

## Deletion Order

1. Activities → 2. Quotations (cancel → delete) → 3. Leads/Opportunities → 4. Products → 5. Teams → 6. Customers → 7. Users

**Why?** Avoids FK constraint errors.

---

## Common Commands

```bash
# Skip staff/customers import (if already exist)
python3 import_all_enterprise_demo.py --skip-staff --skip-customers

# Keep users when deleting
python3 delete_all_crm_data.py --keep-users --no-confirm

# Import specific data only
python3 import_leads.py
python3 import_opportunities.py
```

---

## Troubleshooting

**Connection Error:** Check ODOO_URL, ensure Odoo is running

**Import Failures:** Check foreign keys exist (customers, users, teams)

**Slow Performance:** Normal for 9300 records, takes 25-40 mins

**Quotation Lines Error:** Fixed - now uses flexible CSV column names

---

## CSV Column Requirements

### Quotations
- `quotation_id`, `name`, `partner_name`, `assigned_to`, `date_order`, `amount_total`, `state`

### Quotation Lines
- `quotation_id`, `product_id` or `product_name`, `quantity`, `unit_price` or `price_unit`

### Activities
- `res_id`, `res_type`, `activity_type_name`, `summary`, `date_deadline` or `due_date`, `assigned_to`

### Leads/Opportunities
- `name`, `partner_name`, `assigned_to`, `team`, `stage_id`, `expected_revenue`

---

## File Structure

```
scripts/
├── import_all_enterprise_demo.py    # Master import
├── import_*.py                       # Individual imports
├── delete_all_crm_data.py           # Delete script
├── verify_enterprise_demo.py        # Verification
├── odoo_utils.py                    # Common functions
├── config.py                        # Your settings (git-ignored)
├── config.example.py                # Settings template
└── debug/                           # Legacy/debug scripts

test_data/
├── generate_enterprise_demo_data.py # Generate foundation
├── generate_crm_demo_data.py        # Generate pipeline
├── config_test.py                   # Test config
├── config_production.py             # Production config
└── *.csv                            # Generated data files
```

---

## Support

- Check logs for specific error messages
- Verify Odoo modules are installed (CRM, Sales)
- Ensure proper permissions for user
- Review `odoo_utils.py` for lookup functions
