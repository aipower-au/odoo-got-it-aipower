# Sprint 1 Demo Data Generator

Comprehensive demo data generator for testing GotIt CRM Sprint 1 requirements with realistic Vietnamese business data.

## Overview

This tool generates medium-volume (50-100 records per entity) demo data including:
- **Sales Teams & Users**: 5 teams, 15 salespeople
- **Customers**: 80 customers with Vietnamese company names and Tax IDs
- **Leads**: 70 leads with assignment rule testing
- **Opportunities**: 50 opportunities in various pipeline stages
- **Products**: 60 products across multiple categories
- **Quotations**: 40 sales orders with line items
- **Activities**: 60 activities and tasks

## Features

### Realistic Vietnamese Data
- ✓ Vietnamese company names (Công ty TNHH, Công ty CP, etc.)
- ✓ Valid 10-digit Tax ID (MST) format
- ✓ Vietnamese person names and addresses
- ✓ Real regions: Hồ Chí Minh, Hà Nội, Đà Nẵng, Nha Trang, etc.
- ✓ Local industries: F&B, Construction, Logistics, Technology, etc.
- ✓ Vietnamese phone numbers (+84...)
- ✓ Business email patterns (.vn domains)

### Test Scenarios Included

#### 1. Duplicate Detection Tests
- **5 customers** with duplicate Tax IDs (same MST, different names)
- **5 customers** with duplicate phone numbers
- **3 customers** with duplicate emails
- **10 leads** matching existing customer data

#### 2. Assignment Rule Tests
Data distributed across 4 dimensions for testing auto-assignment:
- **Industry Groups**: Technology (25%), F&B (20%), Construction (15%), Others
- **Regions**: HCM (30%), Hanoi (25%), Da Nang (15%), Others
- **Customer Types**: SME (50%), Enterprise (30%), Startup (20%)
- **Order Values**: <10M (20%), 10-50M (30%), 50-100M (25%), >100M (25%)

#### 3. Status Transition Tests
- **40% Potential** customers (ready to convert)
- **50% Client** customers (with order history)
- **10% Lost** customers (with loss reasons)
- Lead → Opportunity → Won/Lost flows

#### 4. Complex Relationships
- **10 company groups** (parent companies with 2-4 subsidiaries each)
- **20 customers** with multiple delivery addresses
- **15 customers** with multiple invoice accounts
- Contract/quotation history (3-5 per active customer)

## Installation

### Prerequisites
- Python 3.7 or higher
- Odoo 18 instance running (http://localhost:8069)
- Admin access to Odoo database

### Setup

1. **No additional packages required** - Uses Python standard library only:
   ```bash
   # Optional: Install in virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Verify Odoo is running**:
   ```bash
   curl http://localhost:8069/web/health
   ```

## Usage

### Basic Usage

```bash
# Run with default configuration
python3 demo_data/generate_sprint1_data.py
```

### Using Environment Variables

```bash
# Set connection parameters
export ODOO_URL=http://localhost:8069
export ODOO_DB=gotit_odoo
export ODOO_USERNAME=admin
export ODOO_PASSWORD=admin

# Run generator
python3 demo_data/generate_sprint1_data.py
```

### Using Command Line Arguments

```bash
python3 demo_data/generate_sprint1_data.py \
  --url http://localhost:8069 \
  --db gotit_odoo \
  --user admin \
  --password admin
```

### Make Script Executable (Linux/Mac)

```bash
chmod +x demo_data/generate_sprint1_data.py
./demo_data/generate_sprint1_data.py
```

## Configuration

Edit `config.py` to customize data volume and distribution:

### Data Volume
```python
DATA_VOLUME = {
    'sales_teams': 5,
    'users': 15,
    'customers': 80,
    'leads': 70,
    'opportunities': 50,
    'products': 60,
    'quotations': 40,
    'activities': 60,
}
```

### Test Scenarios
```python
TEST_SCENARIOS = {
    'duplicate_tax_ids': 5,
    'duplicate_phones': 5,
    'duplicate_emails': 3,
    'duplicate_leads': 10,
    'company_groups': 10,
    'unassigned_leads': 10,
}
```

### Distribution Weights
```python
INDUSTRY_DISTRIBUTION = {
    'Technology': 0.25,
    'F&B': 0.20,
    'Construction': 0.15,
    # ...
}

REGION_DISTRIBUTION = {
    'Hồ Chí Minh': 0.30,
    'Hà Nội': 0.25,
    'Đà Nẵng': 0.15,
    # ...
}
```

## Output

### Console Output
```
======================================================================
GOTIT CRM - SPRINT 1 DEMO DATA GENERATOR
======================================================================

Connecting to Odoo at http://localhost:8069...
✓ Connected as user ID: 2

Creating Sales Teams...
  → Created team: North Team
  → Created team: South Team
  → Created team: Central Team
  → Created team: Enterprise Team
  → Created team: SME Team

Creating Salespeople...
  → Created telesale: Nguyễn Văn Hùng (telesale_1)
  → Created telesale: Trần Thu Trang (telesale_2)
  ...

Creating Customers...
  → Creating duplicate Tax ID test cases...
  → Creating duplicate phone test cases...
  → Creating duplicate email test cases...
  → Creating company groups...

Creating Leads...
  → Creating duplicate lead test cases...
  → Creating unassigned leads...

...

======================================================================
DEMO DATA GENERATION REPORT
======================================================================

Connection: http://localhost:8069
Database: gotit_odoo
Generated at: 2025-01-15 14:30:45

📊 RECORDS CREATED:
----------------------------------------------------------------------
  Crm Team......................................... 5 records
  Res Users....................................... 15 records
  Res Partner..................................... 80 records
  Crm Lead....................................... 120 records
  Product Product................................. 60 records
  Sale Order...................................... 40 records
  Mail Activity................................... 60 records

🧪 TEST SCENARIOS INCLUDED:
----------------------------------------------------------------------
  Duplicate Tax IDs.................... 5 cases
  Duplicate Phones..................... 5 cases
  Duplicate Emails..................... 3 cases
  Duplicate Leads...................... 10 cases
  Company Groups....................... 10 groups
  Unassigned Leads..................... 10 leads

✅ SPRINT 1 REQUIREMENTS COVERAGE:
----------------------------------------------------------------------
  ✓ Customer Management (duplicate detection, assignment)
  ✓ Lead Management (caretaker, auto-assignment rules)
  ✓ Opportunity Management (pipeline data)
  ✓ Product Management (pricing, categories)
  ✓ Task/Activity Management
  ✓ Vietnamese business data (regions, industries)

======================================================================
✓ Demo data generation completed successfully!
======================================================================
```

## Sprint 1 Requirements Coverage

### 1. Customer/Merchant/Supplier Management ✅
- ✓ Tax ID (MST) duplicate checking - 5 test cases with duplicate MST
- ✓ Salesperson assignment - Users assigned to customers
- ✓ Customer status tracking - Potential (40%), Client (50%), Lost (10%)
- ✓ Customer types and regions - Distributed for assignment rule testing
- ✓ Company groups - 10 parent companies with subsidiaries

### 2. Lead Management ✅
- ✓ Lead data - 70 leads with various stages
- ✓ Assignment rules - Distributed by industry, region, customer type, order value
- ✓ Duplicate detection - 10 leads matching existing customers
- ✓ Unassigned leads - 10 leads for auto-assignment testing

### 3. Opportunity Management ✅
- ✓ Pipeline data - 50 opportunities in various stages
- ✓ Expected revenue - Calculated based on customer type and order value
- ✓ Converted leads - Some opportunities created from leads

### 4. Product Management ✅
- ✓ Multiple categories - Software (40%), Service (30%), Hardware (20%), Gifts (10%)
- ✓ Pricing - Cost prices and selling prices
- ✓ Product types - Service and consumable products

### 5. Task Management ✅
- ✓ Activities - 60 activities assigned to leads/opportunities
- ✓ Due dates - Overdue (20%), Today (30%), Upcoming (50%)

### 6. Discussion ✅
- ✓ Data ready - All records can use Odoo's discussion/chatter module

## Vietnamese Data Details

### Regions Covered
- Hồ Chí Minh (South)
- Hà Nội (North)
- Đà Nẵng (Central)
- Nha Trang (Coastal)
- Vũng Tàu (Southeast)
- Hải Phòng (North)
- Cần Thơ (Mekong Delta)
- Huế (Central)
- Biên Hòa (Southeast)

### Industries Covered
- Technology (Công nghệ thông tin)
- F&B (Thực phẩm & Đồ uống)
- Construction (Xây dựng)
- Retail (Bán lẻ)
- Hospitality (Khách sạn & Du lịch)
- Logistics (Logistics & Vận tải)
- Healthcare (Y tế & Sức khỏe)
- Finance (Tài chính & Ngân hàng)
- Education (Giáo dục & Đào tạo)
- Manufacturing (Sản xuất)

### Sample Data Examples

**Company Name Examples:**
- Công ty TNHH Thương Mại Phát Triển Việt Nam
- Công ty Cổ phần Công Nghệ Số Sài Gòn
- Công ty Trách nhiệm Hữu hạn Vận Tải Logistics Quốc Tế

**Person Name Examples:**
- Nguyễn Văn Hùng
- Trần Thu Trang
- Lê Minh Khoa
- Phạm Ngọc Linh

**Tax ID Format:** 0123456789 (10 digits)

**Phone Format:** +84901234567

**Email Format:** hung.nguyen@thuongmai.vn

## Troubleshooting

### Connection Issues

**Error: "Authentication failed!"**
```bash
# Verify credentials
python3 -c "import xmlrpc.client; \
  common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common'); \
  print('Version:', common.version())"
```

**Error: "Connection refused"**
```bash
# Check if Odoo is running
docker compose ps
# or
curl http://localhost:8069
```

### Permission Issues

**Error: "Access Denied"**
- Ensure the user has Admin access rights
- Check that CRM and Sales apps are installed
- Verify user has create permissions on all models

### Data Issues

**Duplicate records on re-run:**
- The script doesn't clean existing data by default
- To start fresh, either:
  1. Reinitialize the database (see main README.md)
  2. Manually delete demo records from Odoo UI

## File Structure

```
demo_data/
├── config.py                  # Configuration settings
├── vietnam_data.py            # Vietnamese data sets
├── generate_sprint1_data.py   # Main generation script
├── requirements.txt           # Python dependencies (none needed)
└── README.md                  # This file
```

## Development

### Adding New Data Types

1. Add configuration to `config.py`:
   ```python
   DATA_VOLUME = {
       'your_model': 50,
   }
   ```

2. Add generation method to `generate_sprint1_data.py`:
   ```python
   def create_your_model(self):
       """Create your model records"""
       print("\nCreating Your Model...")
       # Implementation
   ```

3. Call in `main()` function:
   ```python
   generator.create_your_model()
   ```

### Customizing Vietnamese Data

Edit `vietnam_data.py` to:
- Add more company names
- Add new regions/cities
- Add industry-specific products
- Customize naming patterns

## Support

For issues or questions:
1. Check this README
2. Review `config.py` for configuration options
3. Check Odoo logs: `docker compose logs odoo`
4. Verify database: http://localhost:5050 (pgAdmin)

## License

Part of GotIt CRM Odoo 18 project.
