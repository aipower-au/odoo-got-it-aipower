#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for Odoo Sprint 1 testing scripts
Copy this file to config.py and fill in your credentials
"""

import os

# ============================================================================
# ODOO CONNECTION SETTINGS
# ============================================================================

# Odoo server URL (accessible from host machine)
ODOO_URL = 'http://localhost:8069'

# Database name
ODOO_DB = 'odoo'

# Admin credentials - FILL IN YOUR CREDENTIALS HERE
ODOO_USERNAME = 'your_admin_username'
ODOO_PASSWORD = 'your_admin_password'

# ============================================================================
# FILE PATHS
# ============================================================================

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test data directory
TEST_DATA_DIR = os.path.join(BASE_DIR, 'test_data')

# CSV file paths
STAFF_CSV = os.path.join(TEST_DATA_DIR, 'staff_sprint1.csv')
SALES_TEAMS_CSV = os.path.join(TEST_DATA_DIR, 'sales_teams_sprint1.csv')
CUSTOMERS_CSV = os.path.join(TEST_DATA_DIR, 'customers_sprint1.csv')

# ============================================================================
# IMPORT SETTINGS
# ============================================================================

# Default password for imported users - CHANGE THIS
DEFAULT_USER_PASSWORD = 'changeme123'

# User groups to assign
USER_GROUPS = {
    'base': 'base.group_user',
    'sales': 'sales_team.group_sale_salesman',
    'sales_manager': 'sales_team.group_sale_manager'
}

# Batch size for bulk operations
BATCH_SIZE = 50

# ============================================================================
# ODOO FIELD MAPPINGS
# ============================================================================

# Map CSV fields to Odoo res.users fields
STAFF_FIELD_MAPPING = {
    'name': 'name',
    'login': 'login',
    'email': 'email',
    'phone': 'phone',
}

# Map CSV fields to Odoo res.partner fields
CUSTOMER_FIELD_MAPPING = {
    'company_name': 'name',
    'tax_id': 'vat',
    'phone': 'phone',
    'email': 'email',
    'delivery_address': 'street',
}

# Map CSV fields to Odoo crm.team fields
TEAM_FIELD_MAPPING = {
    'team_name': 'name',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_connection_info():
    """Return formatted connection information"""
    return {
        'url': ODOO_URL,
        'database': ODOO_DB,
        'username': ODOO_USERNAME,
        'password_length': len(ODOO_PASSWORD) if ODOO_PASSWORD else 0
    }

def validate_config():
    """Validate configuration settings"""
    errors = []

    # Check if CSV files exist
    if not os.path.exists(STAFF_CSV):
        errors.append(f"Staff CSV not found: {STAFF_CSV}")

    if not os.path.exists(SALES_TEAMS_CSV):
        errors.append(f"Sales Teams CSV not found: {SALES_TEAMS_CSV}")

    if not os.path.exists(CUSTOMERS_CSV):
        errors.append(f"Customers CSV not found: {CUSTOMERS_CSV}")

    # Check if credentials are set
    if not ODOO_USERNAME or ODOO_USERNAME == 'your_admin_username':
        errors.append("ODOO_USERNAME must be configured")

    if not ODOO_PASSWORD or ODOO_PASSWORD == 'your_admin_password':
        errors.append("ODOO_PASSWORD must be configured")

    if not DEFAULT_USER_PASSWORD or DEFAULT_USER_PASSWORD == 'changeme123':
        errors.append("DEFAULT_USER_PASSWORD must be changed")

    return errors

if __name__ == "__main__":
    """Test configuration"""
    print("=" * 70)
    print("ODOO SPRINT 1 CONFIGURATION TEST")
    print("=" * 70)

    info = get_connection_info()
    print(f"\nConnection Settings:")
    print(f"  URL: {info['url']}")
    print(f"  Database: {info['database']}")
    print(f"  Username: {info['username']}")
    print(f"  Password: {'*' * info['password_length']}")

    print(f"\nFile Paths:")
    print(f"  Base Dir: {BASE_DIR}")
    print(f"  Test Data: {TEST_DATA_DIR}")
    print(f"  Staff CSV: {os.path.basename(STAFF_CSV)}")
    print(f"  Teams CSV: {os.path.basename(SALES_TEAMS_CSV)}")
    print(f"  Customers CSV: {os.path.basename(CUSTOMERS_CSV)}")

    print(f"\nValidating configuration...")
    errors = validate_config()

    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("\n✅ Configuration is valid!")

    print("=" * 70)
