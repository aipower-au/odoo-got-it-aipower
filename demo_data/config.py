"""
Configuration for Sprint 1 Demo Data Generation
"""

import os

# Odoo Connection Settings
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'gotit_odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

# Data Volume Configuration (Medium)
DATA_VOLUME = {
    'sales_teams': 5,
    'users': 15,  # Salespersons
    'customers': 80,  # Total customers
    'leads': 70,
    'opportunities': 50,
    'products': 60,
    'quotations': 40,
    'activities': 60,
}

# Test Scenarios Configuration
TEST_SCENARIOS = {
    # Duplicate Detection Tests
    'duplicate_tax_ids': 5,  # Customers with same Tax ID
    'duplicate_phones': 5,   # Customers with same phone
    'duplicate_emails': 3,   # Customers with same email
    'duplicate_leads': 10,   # Leads matching existing customers

    # Company Group Tests
    'company_groups': 10,    # Parent companies
    'subsidiaries_per_group': (2, 4),  # Min-max subsidiaries per group

    # Complex Relationships
    'customers_with_multiple_addresses': 20,
    'customers_with_multiple_invoices': 15,
    'addresses_per_customer': (2, 4),  # Min-max addresses

    # Assignment Rule Tests
    'unassigned_leads': 10,  # For auto-assignment testing
}

# Customer Status Distribution (percentage)
CUSTOMER_STATUS_DISTRIBUTION = {
    'potential': 0.40,  # 40% Potential customers
    'client': 0.50,     # 50% Active clients
    'lost': 0.10,       # 10% Lost customers
}

# Lead Stage Distribution
LEAD_STAGE_DISTRIBUTION = {
    'new': 0.30,
    'qualified': 0.25,
    'proposition': 0.20,
    'negotiation': 0.15,
    'won': 0.05,
    'lost': 0.05,
}

# Industry Distribution (for assignment rule testing)
INDUSTRY_DISTRIBUTION = {
    'Technology': 0.25,
    'F&B': 0.20,
    'Construction': 0.15,
    'Retail': 0.10,
    'Hospitality': 0.08,
    'Logistics': 0.08,
    'Healthcare': 0.06,
    'Finance': 0.04,
    'Education': 0.02,
    'Manufacturing': 0.02,
}

# Region Distribution (for assignment rule testing)
REGION_DISTRIBUTION = {
    'Hồ Chí Minh': 0.30,
    'Hà Nội': 0.25,
    'Đà Nẵng': 0.15,
    'Nha Trang': 0.08,
    'Vũng Tàu': 0.06,
    'Hải Phòng': 0.06,
    'Cần Thơ': 0.05,
    'Huế': 0.03,
    'Biên Hòa': 0.02,
}

# Customer Type Distribution (for assignment rule testing)
CUSTOMER_TYPE_DISTRIBUTION = {
    'SME': 0.50,
    'Enterprise': 0.30,
    'Startup': 0.20,
}

# Order Value Distribution (for assignment rule testing)
ORDER_VALUE_DISTRIBUTION = {
    '< 10M': 0.20,
    '10M - 50M': 0.30,
    '50M - 100M': 0.25,
    '100M - 500M': 0.20,
    '> 500M': 0.05,
}

# Sales Team Configuration
SALES_TEAM_REGIONS = {
    'North Team': ['Hà Nội', 'Hải Phòng'],
    'South Team': ['Hồ Chí Minh', 'Biên Hòa', 'Vũng Tàu'],
    'Central Team': ['Đà Nẵng', 'Huế', 'Nha Trang'],
    'Enterprise Team': None,  # Handles all regions for Enterprise customers
    'SME Team': None,  # Handles all regions for SME customers
}

# User Roles Distribution
USER_ROLES = {
    'telesale': 5,  # 5 telesale users
    'sales': 7,     # 7 sales users
    'manager': 3,   # 3 sales managers
}

# Product Configuration
PRODUCT_DISTRIBUTION = {
    'Software': 0.40,   # 40% software products
    'Service': 0.30,    # 30% services
    'Hardware': 0.20,   # 20% hardware
    'Gift': 0.10,       # 10% gifts
}

# Price Ranges (in VND)
PRICE_RANGES = {
    'Software': (5_000_000, 200_000_000),    # 5M - 200M VND
    'Service': (3_000_000, 50_000_000),      # 3M - 50M VND
    'Hardware': (2_000_000, 100_000_000),    # 2M - 100M VND
    'Gift': (50_000, 5_000_000),             # 50K - 5M VND
}

# Products with multiple prices
PRODUCTS_WITH_MULTIPLE_PRICES = 10  # Number of products with tiered pricing

# Activity Configuration
ACTIVITY_STATUS_DISTRIBUTION = {
    'overdue': 0.20,   # 20% overdue
    'today': 0.30,     # 30% due today
    'upcoming': 0.50,  # 50% upcoming
}

# Quotation Status Distribution
QUOTATION_STATUS_DISTRIBUTION = {
    'draft': 0.30,
    'sent': 0.40,
    'sale': 0.20,   # Confirmed/won
    'cancel': 0.10,
}

# Output Configuration
OUTPUT_CONFIG = {
    'show_progress': True,
    'generate_report': True,
    'export_csv': True,
    'csv_output_dir': 'demo_data/output',
}

# Validation Rules
VALIDATION = {
    'check_duplicates': True,
    'validate_tax_ids': True,
    'validate_relationships': True,
    'check_data_integrity': True,
}
