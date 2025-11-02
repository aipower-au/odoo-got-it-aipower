# Sprint 1 Testing Scripts

Python scripts for managing Odoo CRM test data import/export.

## Quick Start

### Option 1: Automated (Recommended)

```bash
./reset_and_import.sh
```

### Option 2: Manual Steps

```bash
# 1. Generate CSV files
cd ../test_data
python3 generate_all_test_data.py

# 2. Delete existing data
cd ../scripts
python3 delete_crm_data.py

# 3. Import all data
python3 import_all_sprint1.py

# 4. Verify
python3 verify_data.py
```

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `config.py` | Configuration settings | `python3 config.py` (test) |
| `delete_crm_data.py` | Delete CRM data | `python3 delete_crm_data.py` |
| `import_staff.py` | Import users | `python3 import_staff.py` |
| `import_sales_teams.py` | Import teams | `python3 import_sales_teams.py` |
| `import_customers.py` | Import customers | `python3 import_customers.py` |
| `import_all_sprint1.py` | Import everything | `python3 import_all_sprint1.py` |
| `verify_data.py` | Verify data | `python3 verify_data.py` |
| `reset_and_import.sh` | Complete workflow | `./reset_and_import.sh` |

## Configuration

Edit `config.py` or set environment variables:

```bash
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin@gotit.vn
export ODOO_PASSWORD=Aipower!123
```

## Common Commands

```bash
# Delete data without confirmation
python3 delete_crm_data.py --no-confirm

# Full workflow with auto-confirm
./reset_and_import.sh -y

# Skip deletion step
./reset_and_import.sh --skip-delete

# Help
./reset_and_import.sh --help
```

## Default Settings

- **Default User Password:** `gotit2025`
- **Default Odoo URL:** `http://localhost:8069`
- **Default Database:** `odoo`

## Documentation

See detailed guide: `../docs/SPRINT_1_TESTING_GUIDE.md`

## Requirements

- Python 3.7+
- Odoo 18 running in Docker
- Network access to Odoo

## Troubleshooting

**Connection Error:**
```bash
# Check Odoo is running
docker ps | grep odoo

# Test configuration
python3 config.py
```

**Import Errors:**
```bash
# Check logs
docker logs odoo_web

# Restart Odoo
docker restart odoo_web
```
