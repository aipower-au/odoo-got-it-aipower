#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Configuration for Demo Data Generation
Small dataset for quick testing and debugging
"""

# ============================================================================
# ENTERPRISE DATA CONFIGURATION
# ============================================================================

TARGET_STAFF = 35
TARGET_CUSTOMERS = 100
TARGET_TEAMS = 10

# Staff distribution
STAFF_DISTRIBUTION = {
    'director': 1,      # 1 Sales Director
    'manager': 3,       # 3 Managers (North/Central/South)
    'sales': 20,        # 20 Sales Executives
    'telesales': 8,     # 8 Telesales/SDR
    'support': 3        # 3 Support roles
}

# ============================================================================
# CRM PIPELINE DATA CONFIGURATION
# ============================================================================

TARGET_LEADS = 50
TARGET_OPPORTUNITIES = 30
TARGET_ACTIVITIES = 80
TARGET_PRODUCTS = 15
TARGET_QUOTATIONS = 20

# ============================================================================
# DESCRIPTION
# ============================================================================

CONFIG_NAME = "Test Configuration"
CONFIG_DESCRIPTION = """
Small test dataset for quick validation:
  - 35 staff members (1 director, 3 managers, 20 sales, 8 telesales, 3 support)
  - 100 customers
  - 10 sales teams
  - 50 leads
  - 30 opportunities
  - 80 activities
  - 15 products
  - 20 quotations (~50 quotation lines)

Total records: ~420
Expected import time: 1-2 minutes
"""
