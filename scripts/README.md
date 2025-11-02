# Odoo Enterprise CRM Demo Data

Python scripts for managing enterprise-scale Odoo CRM demo data with complete pipeline (leads, opportunities, quotations, activities).

## Quick Start

### Complete Enterprise Demo Setup

```bash
# 1. Generate all demo data (one-time)
cd ../test_data
python3 generate_enterprise_demo_data.py  # Foundation: staff, customers, teams
python3 generate_crm_demo_data.py         # Pipeline: leads, opportunities, quotations

# 2. Delete existing CRM data
cd ../scripts
python3 delete_all_crm_data.py

# 3. Import complete enterprise demo
python3 import_all_enterprise_demo.py

# 4. Verify imported data
python3 verify_enterprise_demo.py
```

### Skip Confirmation Prompts

```bash
python3 delete_all_crm_data.py --no-confirm
```

### Command-Line Options

```bash
# Import without re-importing staff or customers (if already imported)
python3 import_all_enterprise_demo.py --skip-staff --skip-customers

# Keep existing users when deleting
python3 delete_all_crm_data.py --keep-users
```

## What Gets Imported

**Foundation Data:**
- 150 staff members (hierarchical org structure: Director → Managers → Sales → Support)
- 35 sales teams (regional, industry, product-based, customer-type)
- 3000 customers (35% Enterprise, 40% SME, 25% Startup)
- 50 products (software, hardware, services, subscriptions)
- CRM foundation (7 stages, 9 sources, 24 tags)

**CRM Pipeline Data:**
- 2000 leads (various sources and stages)
- 1500 opportunities (realistic stage distribution: New → Won/Lost)
- 600 quotations (~1800 line items, draft/sent/confirmed states)
- 3000 activities (20% overdue, 30% this week, 40% next 2 weeks)

**Total:** ~9,300 records representing a realistic enterprise CRM environment

**Expected Import Time:** 25-40 minutes for complete dataset

## Scripts Overview

### Data Generation Scripts

Located in `../test_data/`

| Script | Purpose | Output |
|--------|---------|--------|
| `generate_enterprise_demo_data.py` | Generate foundation data | 150 staff, 3000 customers, 35 teams |
| `generate_crm_demo_data.py` | Generate pipeline data | 2000 leads, 1500 opps, 600 quotes, 3000 activities |

### Import Scripts

| Script | Purpose | Records | Batch Size |
|--------|---------|---------|------------|
| `import_staff_enterprise.py` | Import staff | 150 users | 50/batch |
| `import_customers_enterprise.py` | Import customers | 3000 partners | 100/batch |
| `import_sales_teams_enterprise.py` | Import teams | 35 teams | All at once |
| `import_crm_foundation.py` | Import CRM foundation | Stages, sources, tags | All at once |
| `import_leads.py` | Import leads | 2000 records | 200/batch |
| `import_opportunities.py` | Import opportunities | 1500 records | 150/batch |
| `import_quotations.py` | Import quotations & lines | 600 + ~1800 lines | 100/batch |
| `import_activities.py` | Import activities | 3000 records | 200/batch |
| **`import_all_enterprise_demo.py`** | **Master import script** | **All of the above** | Various |

### Management Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `delete_all_crm_data.py` | Delete all CRM data | Handles FK constraints properly |
| `verify_enterprise_demo.py` | Verify imported data | Shows counts & distributions |
| `config.py` | Configuration settings | Connection details |

## Configuration

Copy the example config and edit with your credentials:

```bash
cp config.example.py config.py
# Edit config.py with your Odoo credentials
```

The `config.py` file is git-ignored for security.

### Configuration Variables

```python
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin@gotit.vn"
ODOO_PASSWORD = "your_password"
DEFAULT_USER_PASSWORD = "gotit2025"  # For imported users
```

## Import Order

The master import script (`import_all_enterprise_demo.py`) imports data in this order to respect foreign key dependencies:

1. **Staff** (150 users) - Creates user accounts with proper groups
2. **Sales Teams** (35 teams) - Assigns team leaders
3. **Customers** (3000 partners) - Creates customer records
4. **CRM Foundation** - Stages, sources, tags
5. **Products** (50 items) - Software, hardware, services
6. **Leads** (2000) - Links to staff, teams, sources
7. **Opportunities** (1500) - Links to customers, staff, teams
8. **Quotations** (600 + lines) - Links to opportunities, customers, products
9. **Activities** (3000) - Links to opportunities, staff

## Deletion Order

The delete script (`delete_all_crm_data.py`) deletes in reverse order to avoid foreign key constraint violations:

1. Activities
2. Quotation Lines
3. Quotations
4. Leads & Opportunities
5. Products
6. Sales Teams
7. Customers
8. Users (optional - use `--keep-users` to skip)

## Verification

After import, run the verification script to check data:

```bash
python3 verify_enterprise_demo.py
```

**Verification checks:**
- Record counts for all data types
- Distribution by stage (opportunities)
- Distribution by state (quotations)
- Expected counts validation
- Overall pass/fail status

**Expected output:**
```
✓ Staff: 150
✓ Customers: 3000+
✓ Sales Teams: 32-35
✓ CRM Foundation: 40+ items
✓ Products: 50
✓ Leads: 2000
✓ Opportunities: 1500
✓ Quotations: 600
✓ Activities: 3000
```

## Default Settings

- **Default User Password:** `gotit2025`
- **Default Odoo URL:** `http://localhost:8069`
- **Default Database:** `odoo`
- **Admin Email:** `admin@gotit.vn`

## Data Distribution Details

### Staff Hierarchy
- 1 Sales Director
- 15 Sales Managers
- 100 Sales Executives
- 25 Telesales Representatives
- 9 Support Staff

### Regional Distribution (Customers)
- North: 30%
- Central: 25%
- South: 45%

### Opportunity Stage Distribution
- New: 25%
- Qualified: 20%
- Meeting: 15%
- Proposal: 20%
- Negotiation: 10%
- Won: 5%
- Lost: 5%

### Activity Timeline
- Overdue: 20%
- This week: 30%
- Next 2 weeks: 40%
- Future: 10%

## Requirements

- Python 3.7+
- Odoo 18 running in Docker
- Network access to Odoo
- Required Python modules: `xmlrpc.client`, `csv`, `faker`

## Troubleshooting

### Connection Error

```bash
# Check Odoo is running
docker ps | grep odoo

# Test configuration
python3 config.py

# Check Odoo logs
docker logs odoo_web
```

### Import Errors

**Symptom:** Import fails with authentication error

**Solution:**
```bash
# Verify credentials in config.py
python3 config.py

# Restart Odoo
docker restart odoo_web
```

**Symptom:** Foreign key constraint errors

**Solution:**
```bash
# Delete data first, then re-import
python3 delete_all_crm_data.py --no-confirm
python3 import_all_enterprise_demo.py
```

**Symptom:** Duplicate records

**Solution:**
```bash
# The scripts handle duplicates by updating existing records
# To force fresh import:
python3 delete_all_crm_data.py --no-confirm
python3 import_all_enterprise_demo.py
```

### Performance Issues

**Symptom:** Import is very slow

**Solutions:**
- Increase batch sizes in individual import scripts
- Check Odoo server resources (CPU, memory)
- Reduce dataset size in generation scripts
- Run imports during off-peak hours

## Common Use Cases

### Reset and Start Fresh

```bash
cd scripts
python3 delete_all_crm_data.py --no-confirm
python3 import_all_enterprise_demo.py
python3 verify_enterprise_demo.py
```

### Add More Data Without Deleting

```bash
cd test_data
# Modify generation scripts to create different data
python3 generate_enterprise_demo_data.py
python3 generate_crm_demo_data.py

cd ../scripts
python3 import_all_enterprise_demo.py
```

### Import Only Specific Data Types

```bash
# Import only leads
python3 import_leads.py

# Import only opportunities
python3 import_opportunities.py

# Import only quotations
python3 import_quotations.py

# Import only activities
python3 import_activities.py
```

### Keep Users But Reset Everything Else

```bash
python3 delete_all_crm_data.py --no-confirm --keep-users
python3 import_all_enterprise_demo.py --skip-staff
```

## File Locations

```
odoo-got-it-aipower/
├── test_data/
│   ├── generate_enterprise_demo_data.py    # Generate foundation
│   ├── generate_crm_demo_data.py           # Generate pipeline
│   ├── staff_sprint1_enterprise.csv        # 150 staff
│   ├── customers_sprint1_enterprise.csv    # 3000 customers
│   ├── sales_teams_sprint1_enterprise.csv  # 35 teams
│   ├── products_demo.csv                   # 50 products
│   ├── leads_demo.csv                      # 2000 leads
│   ├── opportunities_demo.csv              # 1500 opportunities
│   ├── quotations_demo.csv                 # 600 quotations
│   ├── quotation_lines_demo.csv            # ~1800 lines
│   ├── activities_demo.csv                 # 3000 activities
│   ├── crm_stages.csv                      # 7 stages
│   ├── crm_sources.csv                     # 9 sources
│   └── crm_tags.csv                        # 24 tags
│
└── scripts/
    ├── config.py                           # Configuration
    ├── import_all_enterprise_demo.py       # Master import
    ├── delete_all_crm_data.py              # Delete all data
    ├── verify_enterprise_demo.py           # Verify data
    ├── import_staff_enterprise.py          # Import staff
    ├── import_customers_enterprise.py      # Import customers
    ├── import_sales_teams_enterprise.py    # Import teams
    ├── import_crm_foundation.py            # Import foundation
    ├── import_leads.py                     # Import leads
    ├── import_opportunities.py             # Import opportunities
    ├── import_quotations.py                # Import quotations
    └── import_activities.py                # Import activities
```

## Testing Sprint 1 Features

After importing the demo data, you can test Sprint 1 features:

1. **Log into Odoo**
   - URL: http://localhost:8069
   - User: Any imported staff member (login format: `lastname.firstinitial@gotit.vn`)
   - Password: `gotit2025`

2. **Test CRM Features**
   - Browse leads and opportunities
   - Convert leads to opportunities
   - Create quotations from opportunities
   - Schedule activities
   - View pipeline and forecasts

3. **Test Sales Teams**
   - View team performance
   - Assign leads to team members
   - Track team quotas

4. **Test Customer Management**
   - View customer details
   - Track customer interactions
   - Manage customer opportunities

## Documentation

For detailed Sprint 1 requirements, see:
- `../docs/sprint1_requirements_en.md` (English)
- `../docs/sprint1_requirements_vi.md` (Vietnamese)

## Support

For issues or questions:
1. Check this README troubleshooting section
2. Review Odoo logs: `docker logs odoo_web`
3. Verify configuration: `python3 config.py`
4. Check data generation output in test_data/
