#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Configuration for Demo Data Generation
Full enterprise-scale dataset for realistic CRM demonstration
"""

# ============================================================================
# ENTERPRISE DATA CONFIGURATION
# ============================================================================

TARGET_STAFF = 150
TARGET_CUSTOMERS = 3000
TARGET_TEAMS = 35

# Staff distribution
STAFF_DISTRIBUTION = {
    'director': 1,          # 1 Sales Director
    'manager': 15,          # 15 Sales Managers/Regional Directors
    'sales': 100,           # 100 Sales Executives
    'telesales': 25,        # 25 Telesales/SDR
    'support': 9            # 9 Support roles
}

# ============================================================================
# CRM PIPELINE DATA CONFIGURATION
# ============================================================================

TARGET_LEADS = 2000
TARGET_OPPORTUNITIES = 1500
TARGET_ACTIVITIES = 3000
TARGET_PRODUCTS = 50
TARGET_QUOTATIONS = 600

# ============================================================================
# DESCRIPTION
# ============================================================================

CONFIG_NAME = "Production Configuration"
CONFIG_DESCRIPTION = """
Full enterprise-scale dataset for realistic CRM demonstration:
  - 150 staff members (1 director, 15 managers, 100 sales, 25 telesales, 9 support)
  - 3000 customers (Enterprise/SME/Startup distribution)
  - 35 sales teams (regional and specialized)
  - 2000 leads (various stages and sources)
  - 1500 opportunities (~377B VND pipeline)
  - 3000 activities (calls, meetings, emails, todos)
  - 50 products (software/hardware/services/subscription)
  - 600 quotations (~1800 quotation lines, ~273B VND)

Total records: ~9,300+
Expected import time: 20-30 minutes
"""
