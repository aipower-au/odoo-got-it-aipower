#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise-Scale Demo Data Generator for Odoo CRM
Generates: staff, customers, and sales teams

Usage:
  python3 generate_enterprise_demo_data.py                    # Production config (default)
  python3 generate_enterprise_demo_data.py --config test      # Test config
  python3 generate_enterprise_demo_data.py --config production # Production config (explicit)
"""

import csv
import random
import argparse
import importlib
from datetime import datetime, timedelta
from collections import defaultdict

# ============================================================================
# PARSE COMMAND LINE ARGUMENTS
# ============================================================================

parser = argparse.ArgumentParser(description='Generate enterprise demo data for Odoo CRM')
parser.add_argument('--config', type=str, choices=['test', 'production'], default='production',
                    help='Configuration to use: test (small dataset) or production (full scale)')
args = parser.parse_args()

# ============================================================================
# LOAD CONFIGURATION
# ============================================================================

config_module = f"config_{args.config}"
try:
    config = importlib.import_module(config_module)
    TARGET_STAFF = config.TARGET_STAFF
    TARGET_CUSTOMERS = config.TARGET_CUSTOMERS
    TARGET_TEAMS = config.TARGET_TEAMS
    STAFF_DISTRIBUTION = config.STAFF_DISTRIBUTION
except ImportError:
    print(f"❌ Error: Could not find {config_module}.py")
    print(f"   Please ensure config_{args.config}.py exists in the current directory")
    exit(1)

print("=" * 80)
print("ENTERPRISE CRM DEMO DATA GENERATOR")
print("=" * 80)
print(f"Configuration: {config.CONFIG_NAME}")
print(f"  - Staff: {TARGET_STAFF}")
print(f"  - Customers: {TARGET_CUSTOMERS}")
print(f"  - Teams: {TARGET_TEAMS}")
print("=" * 80)
print()

# ============================================================================
# VIETNAMESE NAME POOLS (EXPANDED)
# ============================================================================

# Family names (Họ) - expanded list
FAMILY_NAMES = [
    'Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
    'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Trương', 'Tô', 'Mai',
    'Đào', 'Hà', 'Cao', 'Chu', 'Lưu', 'La', 'Tạ', 'Trịnh', 'Quách', 'Viễn',
]

# Middle names (Tên đệm)
MIDDLE_NAMES_MALE = [
    'Văn', 'Đức', 'Minh', 'Quốc', 'Hữu', 'Xuân', 'Hoàng', 'Thanh', 'Ngọc', 'Bảo',
    'Anh', 'Gia', 'Quang', 'Tuấn', 'Mạnh', 'Đình', 'Phương', 'Hùng', 'Thành', 'Công'
]

MIDDLE_NAMES_FEMALE = [
    'Thị', 'Thu', 'Hồng', 'Kim', 'Phương', 'Ngọc', 'Bảo', 'Hạ', 'Anh', 'Lan',
    'Thanh', 'Minh', 'Quỳnh', 'Hoàng', 'Diệu', 'My', 'Linh', 'Hương', 'Thúy', 'Mai'
]

# Given names (Tên)
GIVEN_NAMES_MALE = [
    'Thành', 'Long', 'Hùng', 'Tài', 'Tuấn', 'Anh', 'Khoa', 'Phúc', 'Bình', 'Dũng',
    'Hải', 'Đạt', 'Quân', 'Linh', 'Quỳnh', 'Khánh', 'Tâm', 'Trí', 'Tùng', 'Mạnh',
    'Hiếu', 'Nam', 'Huy', 'Kiên', 'Sơn', 'Đức', 'Minh', 'Cường', 'Hưng', 'Vinh'
]

GIVEN_NAMES_FEMALE = [
    'Lan', 'Hà', 'Mai', 'Hương', 'Trang', 'Nga', 'Yến', 'Nhung', 'Vy', 'Hằng',
    'Phương', 'Tuyết', 'Linh', 'Quỳnh', 'Hoa', 'Thảo', 'Ngọc', 'Anh', 'Chi', 'Hiền',
    'Dung', 'Thu', 'Hồng', 'Bích', 'Diệp', 'Huyền', 'Khánh', 'My', 'Như', 'Xuân'
]

# ============================================================================
# REGIONS & TERRITORIES
# ============================================================================

REGIONS = {
    'North': {
        'cities': ['Hà Nội', 'Hải Phòng', 'Quảng Ninh', 'Nam Định', 'Thái Bình'],
        'weight': 0.30
    },
    'Central': {
        'cities': ['Đà Nẵng', 'Huế', 'Quy Nhơn', 'Nha Trang', 'Pleiku'],
        'weight': 0.25
    },
    'South': {
        'cities': ['Hồ Chí Minh', 'Biên Hòa', 'Vũng Tàu', 'Cần Thơ', 'Long Xuyên'],
        'weight': 0.45
    }
}

# ============================================================================
# INDUSTRIES
# ============================================================================

INDUSTRIES = [
    'Technology', 'F&B', 'Manufacturing', 'Retail', 'Healthcare',
    'Education', 'Construction', 'Logistics', 'Hospitality', 'Fashion',
    'Finance', 'Real Estate', 'Automotive', 'Agriculture', 'Telecommunications'
]

CUSTOMER_TYPES = ['Enterprise', 'SME', 'Startup']

# ============================================================================
# VIETNAMESE TO ASCII CONVERSION
# ============================================================================

VIETNAMESE_TO_ASCII = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
}

def remove_vietnamese_accents(text):
    """Convert Vietnamese characters to ASCII equivalents"""
    result = []
    for char in text:
        result.append(VIETNAMESE_TO_ASCII.get(char.lower(), char.lower()))
    return ''.join(result)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

PHONE_PREFIXES = ['091', '094', '088', '083', '084', '085', '081', '082', '090', '093',
                  '070', '079', '077', '076', '078', '089', '086', '096', '097', '098']

def generate_phone():
    """Generate Vietnamese phone number"""
    prefix = random.choice(PHONE_PREFIXES)
    return f"+84{prefix[1:]}{random.randint(1000000, 9999999)}"

def generate_person_name(gender='random', used_names=None):
    """Generate unique Vietnamese person name"""
    if used_names is None:
        used_names = set()

    max_attempts = 100
    for _ in range(max_attempts):
        if gender == 'random':
            gender = random.choice(['male', 'female'])

        family = random.choice(FAMILY_NAMES)
        if gender == 'male':
            middle = random.choice(MIDDLE_NAMES_MALE)
            given = random.choice(GIVEN_NAMES_MALE)
        else:
            middle = random.choice(MIDDLE_NAMES_FEMALE)
            given = random.choice(GIVEN_NAMES_FEMALE)

        name = f"{family} {middle} {given}"
        if name not in used_names:
            used_names.add(name)
            return name

    # Fallback: add number if can't generate unique name
    return f"{family} {middle} {given} {random.randint(1, 999)}"

def generate_login(name):
    """Generate login from name (ASCII only)"""
    ascii_name = remove_vietnamese_accents(name)
    parts = ascii_name.lower().split()
    if len(parts) >= 2:
        # Format: lastname.firstinitial
        return f"{parts[-1]}.{parts[0][0]}"
    return parts[0]

def generate_email(name, domain='gotit.vn'):
    """Generate email from name (ASCII only)"""
    login = generate_login(name)
    return f"{login}@{domain}"

def generate_hire_date(seniority):
    """Generate hire date based on seniority"""
    ranges = {
        'director': (1800, 2500),
        'manager': (1095, 1825),
        'sales': (365, 1095),
        'telesales': (90, 730),
        'support': (180, 1095)
    }
    days = random.randint(*ranges.get(seniority, (180, 545)))
    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")

def generate_sales_target(job_title):
    """Generate monthly sales target in VND"""
    targets = {
        'Sales Director': (2000000000, 3000000000),
        'Sales Manager': (500000000, 1000000000),
        'Regional Director': (600000000, 1200000000),
        'Sales Executive': (100000000, 300000000),
        'Telesales Executive': (0, 0),
        'Sales Operations Manager': (0, 0),
        'Sales Coordinator': (0, 0),
        'Sales Analyst': (0, 0)
    }
    range_selected = targets.get(job_title, (50000000, 150000000))
    if range_selected[0] == 0:
        return 0
    return random.randint(range_selected[0], range_selected[1])

# ============================================================================
# STAFF GENERATION
# ============================================================================

def generate_staff_enterprise():
    """Generate 150 staff members with hierarchical structure"""
    print(f"Generating {TARGET_STAFF} staff members...")
    staff = []
    used_names = set()
    used_logins = {}
    emp_id = 1

    # Track staff by role for team assignment
    directors = []
    managers = []
    sales_execs = []
    telesales = []
    support_staff = []

    # 1. Sales Director
    director_name = generate_person_name('male', used_names)
    login = generate_login(director_name)

    # Handle duplicate logins
    if login in used_logins:
        login = f"{login}{emp_id}"
    used_logins[login] = director_name

    director = {
        'employee_code': f'EMP{emp_id:04d}',
        'name': director_name,
        'login': login,
        'email': generate_email(director_name),
        'phone': generate_phone(),
        'job_title': 'Sales Director',
        'department': 'Sales',
        'manager': '',
        'region_territory': 'All Vietnam',
        'industry_specialization': 'All',
        'customer_type_focus': 'All',
        'active': 'True',
        'hire_date': generate_hire_date('director'),
        'monthly_sales_target': generate_sales_target('Sales Director'),
        'user_type': 'Director',
        'sales_team': 'Leadership'
    }
    staff.append(director)
    directors.append(director)
    emp_id += 1

    # 2. Sales Managers / Regional Directors (based on STAFF_DISTRIBUTION)
    manager_count = STAFF_DISTRIBUTION['manager']
    # Distribute managers across regions proportionally
    north_count = (manager_count + 2) // 3
    central_count = manager_count // 3
    south_count = manager_count - north_count - central_count

    regions_for_managers = (['North'] * north_count +
                           ['Central'] * central_count +
                           ['South'] * south_count)
    manager_titles = ['Sales Manager'] * (manager_count - 1) + ['Regional Director']

    for i, region in enumerate(regions_for_managers):
        manager_name = generate_person_name('random', used_names)
        login = generate_login(manager_name)

        # Handle duplicate logins
        counter = 1
        original_login = login
        while login in used_logins:
            login = f"{original_login}{counter}"
            counter += 1
        used_logins[login] = manager_name

        title = manager_titles[i]

        manager = {
            'employee_code': f'EMP{emp_id:04d}',
            'name': manager_name,
            'login': login,
            'email': generate_email(manager_name),
            'phone': generate_phone(),
            'job_title': title,
            'department': 'Sales',
            'manager': director_name,
            'region_territory': region,
            'industry_specialization': random.choice([
                'Technology,F&B', 'Manufacturing,Retail', 'Healthcare,Education',
                'Construction,Logistics', 'All'
            ]),
            'customer_type_focus': random.choice(['Enterprise', 'SME', 'All']),
            'active': 'True',
            'hire_date': generate_hire_date('manager'),
            'monthly_sales_target': generate_sales_target(title),
            'user_type': 'Manager',
            'sales_team': f'{region} Regional Team'
        }
        staff.append(manager)
        managers.append(manager)
        emp_id += 1

    # 3. Sales Executives (100)
    for i in range(STAFF_DISTRIBUTION['sales']):
        exec_name = generate_person_name('random', used_names)
        login = generate_login(exec_name)

        # Handle duplicate logins
        counter = 1
        original_login = login
        while login in used_logins:
            login = f"{original_login}{counter}"
            counter += 1
        used_logins[login] = exec_name

        # Assign to a manager
        manager = random.choice(managers)
        region = manager['region_territory']

        # Select industry specialization
        industries = random.sample(INDUSTRIES, random.randint(1, 3))
        industry_spec = ','.join(industries)

        exec_member = {
            'employee_code': f'EMP{emp_id:04d}',
            'name': exec_name,
            'login': login,
            'email': generate_email(exec_name),
            'phone': generate_phone(),
            'job_title': 'Sales Executive',
            'department': 'Sales',
            'manager': manager['name'],
            'region_territory': region,
            'industry_specialization': industry_spec,
            'customer_type_focus': random.choice(CUSTOMER_TYPES),
            'active': 'True',
            'hire_date': generate_hire_date('sales'),
            'monthly_sales_target': generate_sales_target('Sales Executive'),
            'user_type': 'Sales',
            'sales_team': manager['sales_team']
        }
        staff.append(exec_member)
        sales_execs.append(exec_member)
        emp_id += 1

    # 4. Telesales / SDR (based on STAFF_DISTRIBUTION)
    tele_count = STAFF_DISTRIBUTION['telesales']
    # Split across regions proportionally
    tele_north = (tele_count + 2) // 3
    tele_central = tele_count // 3
    tele_south = tele_count - tele_north - tele_central

    tele_regions = (['North'] * tele_north +
                    ['Central'] * tele_central +
                    ['South'] * tele_south)

    for region in tele_regions:
        tele_name = generate_person_name('random', used_names)
        login = generate_login(tele_name)

        # Handle duplicate logins
        counter = 1
        original_login = login
        while login in used_logins:
            login = f"{original_login}{counter}"
            counter += 1
        used_logins[login] = tele_name

        # Find a manager in the same region
        region_managers = [m for m in managers if m['region_territory'] == region]
        manager = random.choice(region_managers) if region_managers else random.choice(managers)

        tele_member = {
            'employee_code': f'EMP{emp_id:04d}',
            'name': tele_name,
            'login': login,
            'email': generate_email(tele_name),
            'phone': generate_phone(),
            'job_title': 'Telesales Executive',
            'department': 'Telesales',
            'manager': manager['name'],
            'region_territory': region,
            'industry_specialization': 'All',
            'customer_type_focus': 'Lead Qualification',
            'active': 'True',
            'hire_date': generate_hire_date('telesales'),
            'monthly_sales_target': generate_sales_target('Telesales Executive'),
            'user_type': 'Telesales',
            'sales_team': f'{region} Telesales Team'
        }
        staff.append(tele_member)
        telesales.append(tele_member)
        emp_id += 1

    # 5. Support Staff (based on STAFF_DISTRIBUTION)
    support_count = STAFF_DISTRIBUTION['support']
    all_support_roles = [
        ('Sales Operations Manager', 'Sales Ops', 'All Vietnam'),
        ('Sales Coordinator', 'Sales Ops', 'North'),
        ('Sales Coordinator', 'Sales Ops', 'South'),
        ('Sales Coordinator', 'Sales Ops', 'Central'),
        ('Sales Analyst', 'Sales Analytics', 'All Vietnam'),
        ('Sales Analyst', 'Sales Analytics', 'All Vietnam'),
        ('Sales Enablement Manager', 'Sales Enablement', 'All Vietnam'),
        ('Channel Partner Manager', 'Partner Channel', 'All Vietnam'),
        ('Customer Success Manager', 'Customer Success', 'All Vietnam')
    ]
    # Take only the first N support roles based on configuration
    support_roles = all_support_roles[:support_count]

    for title, dept, region in support_roles:
        support_name = generate_person_name('random', used_names)
        login = generate_login(support_name)

        # Handle duplicate logins
        counter = 1
        original_login = login
        while login in used_logins:
            login = f"{original_login}{counter}"
            counter += 1
        used_logins[login] = support_name

        support_member = {
            'employee_code': f'EMP{emp_id:04d}',
            'name': support_name,
            'login': login,
            'email': generate_email(support_name),
            'phone': generate_phone(),
            'job_title': title,
            'department': dept,
            'manager': director_name,
            'region_territory': region,
            'industry_specialization': 'All',
            'customer_type_focus': 'All',
            'active': 'True',
            'hire_date': generate_hire_date('support'),
            'monthly_sales_target': generate_sales_target(title),
            'user_type': 'Support',
            'sales_team': dept
        }
        staff.append(support_member)
        support_staff.append(support_member)
        emp_id += 1

    print(f"  ✓ Generated {len(staff)} staff members")
    print(f"    - Directors: {len(directors)}")
    print(f"    - Managers: {len(managers)}")
    print(f"    - Sales Executives: {len(sales_execs)}")
    print(f"    - Telesales: {len(telesales)}")
    print(f"    - Support Staff: {len(support_staff)}")

    return staff, {
        'directors': directors,
        'managers': managers,
        'sales_execs': sales_execs,
        'telesales': telesales,
        'support': support_staff
    }

# ============================================================================
# SALES TEAMS GENERATION (35 TEAMS)
# ============================================================================

def generate_sales_teams_enterprise(staff_dict):
    """Generate 35 sales teams with proper member assignments"""
    print(f"Generating {TARGET_TEAMS} sales teams...")
    teams = []
    team_id = 1

    # 1. Leadership Team (1)
    teams.append({
        'team_id': f'TEAM{team_id:03d}',
        'team_name': 'Leadership',
        'team_leader': staff_dict['directors'][0]['name'],
        'member_count': 1 + len(staff_dict['managers']),
        'revenue_target': sum([s['monthly_sales_target'] for s in staff_dict['managers']]) + staff_dict['directors'][0]['monthly_sales_target'],
        'team_type': 'Management',
        'focus_area': 'Strategic Planning'
    })
    team_id += 1

    # 2. Regional Teams (3)
    for region in ['North', 'South', 'Central']:
        region_managers = [m for m in staff_dict['managers'] if m['region_territory'] == region]
        region_sales = [s for s in staff_dict['sales_execs'] if s['region_territory'] == region]

        leader = region_managers[0]['name'] if region_managers else staff_dict['directors'][0]['name']
        member_count = len(region_managers) + len(region_sales)
        revenue_target = sum([s['monthly_sales_target'] for s in region_managers + region_sales])

        teams.append({
            'team_id': f'TEAM{team_id:03d}',
            'team_name': f'{region} Regional Team',
            'team_leader': leader,
            'member_count': member_count,
            'revenue_target': revenue_target,
            'team_type': 'Regional',
            'focus_area': region
        })
        team_id += 1

    # 3. Telesales Teams by Region (3)
    for region in ['North', 'South', 'Central']:
        region_tele = [t for t in staff_dict['telesales'] if t['region_territory'] == region]

        if region_tele:
            # Find a manager in that region to lead
            region_managers = [m for m in staff_dict['managers'] if m['region_territory'] == region]
            leader = region_managers[0]['name'] if region_managers else staff_dict['directors'][0]['name']

            teams.append({
                'team_id': f'TEAM{team_id:03d}',
                'team_name': f'{region} Telesales Team',
                'team_leader': leader,
                'member_count': len(region_tele),
                'revenue_target': 0,  # Telesales don't have direct revenue targets
                'team_type': 'Telesales',
                'focus_area': region
            })
            team_id += 1

    # 4. Industry-Focused Teams (10)
    industry_teams = [
        'Technology', 'F&B', 'Manufacturing', 'Retail', 'Healthcare',
        'Education', 'Construction', 'Logistics', 'Finance', 'Hospitality'
    ]

    for industry in industry_teams:
        # Find sales execs specializing in this industry
        industry_sales = [s for s in staff_dict['sales_execs']
                         if industry in s['industry_specialization']]

        # Pick a manager who specializes in this industry or random
        industry_managers = [m for m in staff_dict['managers']
                            if industry in m['industry_specialization'] or m['industry_specialization'] == 'All']

        leader = industry_managers[0]['name'] if industry_managers else staff_dict['managers'][team_id % len(staff_dict['managers'])]['name']
        member_count = min(len(industry_sales), 15)  # Cap at 15 members per industry team
        selected_sales = random.sample(industry_sales, member_count) if len(industry_sales) > member_count else industry_sales

        revenue_target = sum([s['monthly_sales_target'] for s in selected_sales])

        teams.append({
            'team_id': f'TEAM{team_id:03d}',
            'team_name': f'{industry} Team',
            'team_leader': leader,
            'member_count': member_count,
            'revenue_target': revenue_target,
            'team_type': 'Industry',
            'focus_area': industry
        })
        team_id += 1

    # 5. Customer-Type Teams (3)
    for customer_type in ['Enterprise', 'SME', 'Startup']:
        # Find sales execs focusing on this customer type
        type_sales = [s for s in staff_dict['sales_execs']
                     if s['customer_type_focus'] == customer_type]

        # Find matching managers
        type_managers = [m for m in staff_dict['managers']
                        if customer_type in m['customer_type_focus'] or m['customer_type_focus'] == 'All']

        leader = type_managers[0]['name'] if type_managers else staff_dict['managers'][0]['name']
        member_count = min(len(type_sales), 20)
        selected_sales = random.sample(type_sales, member_count) if len(type_sales) > member_count else type_sales

        revenue_target = sum([s['monthly_sales_target'] for s in selected_sales])

        teams.append({
            'team_id': f'TEAM{team_id:03d}',
            'team_name': f'{customer_type} Team',
            'team_leader': leader,
            'member_count': member_count,
            'revenue_target': revenue_target,
            'team_type': 'Customer Type',
            'focus_area': customer_type
        })
        team_id += 1

    # 6. Product/Service Teams (7)
    product_teams = [
        'Software Licenses', 'Professional Services', 'Support & Maintenance',
        'Training & Education', 'Hardware & Equipment', 'Cloud Solutions', 'Custom Development'
    ]

    for product in product_teams:
        # Randomly assign sales execs to product teams
        available_sales = random.sample(staff_dict['sales_execs'], random.randint(5, 12))
        leader = random.choice(staff_dict['managers'])['name']
        member_count = len(available_sales)
        revenue_target = sum([s['monthly_sales_target'] for s in available_sales])

        teams.append({
            'team_id': f'TEAM{team_id:03d}',
            'team_name': product,
            'team_leader': leader,
            'member_count': member_count,
            'revenue_target': revenue_target,
            'team_type': 'Product',
            'focus_area': product
        })
        team_id += 1

    # 7. Support Teams (5)
    support_team_configs = [
        ('Inside Sales Team', 'Inside Sales', 15),
        ('Key Accounts Team', 'Key Accounts', 10),
        ('Partner Channel Team', 'Channel', 8),
        ('Renewals Team', 'Renewals', 12),
        ('Sales Operations', 'Operations', len(staff_dict['support']))
    ]

    for team_name, focus, size in support_team_configs:
        if 'Operations' in team_name:
            members = staff_dict['support']
            leader = staff_dict['directors'][0]['name']
        else:
            members = random.sample(staff_dict['sales_execs'], min(size, len(staff_dict['sales_execs'])))
            leader = random.choice(staff_dict['managers'])['name']

        member_count = len(members)
        revenue_target = sum([s.get('monthly_sales_target', 0) for s in members])

        teams.append({
            'team_id': f'TEAM{team_id:03d}',
            'team_name': team_name,
            'team_leader': leader,
            'member_count': member_count,
            'revenue_target': revenue_target,
            'team_type': 'Support',
            'focus_area': focus
        })
        team_id += 1

        if team_id > TARGET_TEAMS:
            break

    # Trim to exactly 35 teams
    teams = teams[:TARGET_TEAMS]

    print(f"  ✓ Generated {len(teams)} sales teams")
    print(f"    - By type:")
    team_types = defaultdict(int)
    for team in teams:
        team_types[team['team_type']] += 1
    for ttype, count in sorted(team_types.items()):
        print(f"      • {ttype}: {count}")

    return teams

# ============================================================================
# CUSTOMER GENERATION (3000 CUSTOMERS)
# ============================================================================

# Company name components (Vietnamese businesses)
COMPANY_PREFIXES = [
    'Công ty', 'Công ty TNHH', 'Công ty Cổ phần', 'Tập đoàn', 'Chi nhánh',
    'Doanh nghiệp', 'Xí nghiệp', 'Trung tâm'
]

COMPANY_NAMES = [
    'Thương mại Hùng Vương', 'Đầu tư Bảo Việt', 'Xây dựng Hoàng Long',
    'Vật liệu xây dựng Đại Phát', 'Thép Việt Ý', 'Điện lạnh Bách Khoa',
    'May mặc Hoa Sen', 'Dệt may Việt Tiến', 'Thời trang Nam Phong',
    'Trang sức Bảo Tín', 'Đồng hồ Đăng Quang', 'Điện tử Sài Gòn',
    'Máy tính Phương Nam', 'Phần mềm Trí Tuệ', 'Công nghệ Việt Nam',
    'Giải pháp số FPT', 'Viễn thông Viettel', 'Điện thoại Thế Giới Di Động',
    'Bán lẻ Vinmart', 'Siêu thị BigC', 'Thực phẩm Á Châu',
    'Nước giải khát Tân Hiệp Phát', 'Bánh kẹo Kinh Đô', 'Trà Phúc Long',
    'Café Highlands', 'Nhà hàng Ngọc Mai', 'Khách sạn Mường Thanh',
    'Du lịch Saigon Tourist', 'Vận tải Phương Trang', 'Logistics Hải Vân',
    'Thủy sản Minh Hải', 'Nông sản sạch Đà Lạt', 'Chế biến thực phẩm Vissan',
    'Dược phẩm Hà Nội', 'Bệnh viện Quốc tế', 'Giáo dục Nguyễn Hoàng',
    'Anh ngữ ILA', 'Đào tạo FPT', 'Nhà xuất bản Trẻ',
    'In ấn Thành Công', 'Quảng cáo Việt Nam', 'Truyền thông Sáng Tạo',
    'Marketing Đỉnh Cao', 'Tư vấn McKinsey', 'Tư vấn Ernst & Young',
    'Bất động sản Vinhomes', 'Xây dựng Coteccons', 'Nội thất Hoàng Gia',
    'Gỗ Minh Phương', 'Sơn Jotun', 'Kính Việt Nhật',
    'Ô tô Toyota', 'Xe máy Honda', 'Cơ khí Đông Á'
]

STATUSES = ['Client', 'Potential', 'Lost']

def generate_tax_id():
    """Generate Vietnamese tax ID (10-13 digits)"""
    return f"{random.randint(1000000000, 9999999999)}"

def generate_address(region):
    """Generate Vietnamese address"""
    streets = ['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo', 'Hai Bà Trưng',
              'Lý Thường Kiệt', 'Hoàng Diệu', 'Điện Biên Phủ', 'Phan Chu Trinh',
              'Láng Hạ', 'Trường Chinh']

    districts = {
        'North': ['Ba Đình', 'Hoàn Kiếm', 'Đống Đa', 'Hai Bà Trưng', 'Thanh Xuân'],
        'Central': ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5'],
        'South': ['Quận 1', 'Quận 3', 'Quận 5', 'Quận 7', 'Quận 10', 'Bình Thạnh', 'Tân Bình']
    }

    street = random.choice(streets)
    number = random.randint(1, 999)
    district = random.choice(districts.get(region, districts['South']))

    city = random.choice(REGIONS[region]['cities'])

    return f"{number} {street}, {district}, {city}"

def generate_customer_email(company_name, index):
    """Generate customer email (ASCII only)"""
    domains = ['gmail.com', 'yahoo.com', 'company.vn', 'business.com.vn', 'outlook.com']
    ascii_name = remove_vietnamese_accents(company_name)
    simple_name = ascii_name.lower().replace('cong ty', '').replace('tnhh', '').replace('co phan', '').strip()
    simple_name = simple_name.replace(' ', '')[:12]
    return f"contact{index}@{simple_name}.{random.choice(domains)}"

def generate_creation_date():
    """Generate customer creation date (last 2 years)"""
    days = random.randint(0, 730)
    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")

def generate_purchase_revenue(customer_type):
    """Generate total purchase revenue based on customer type"""
    ranges = {
        'Enterprise': (500000000, 5000000000),
        'SME': (50000000, 500000000),
        'Startup': (10000000, 100000000)
    }
    return random.randint(*ranges.get(customer_type, (10000000, 1000000000)))

def generate_order_value_range(customer_type):
    """Typical order value range by customer type"""
    ranges = {
        'Enterprise': ['100M - 500M', '> 500M'],
        'SME': ['10M - 50M', '50M - 100M', '100M - 500M'],
        'Startup': ['< 10M', '10M - 50M']
    }
    return random.choice(ranges.get(customer_type, ['10M - 50M']))

def generate_customers_enterprise(salespeople, count=TARGET_CUSTOMERS):
    """Generate 3000 customers with proper distribution"""
    print(f"Generating {count} customers...")
    customers = []
    used_tax_ids = set()
    used_company_names = set()

    # Extract sales executive names for assignment
    salesperson_names = [sp['name'] for sp in salespeople if sp['user_type'] == 'Sales']

    # Calculate regional distribution
    regional_weights = [(r, REGIONS[r]['weight']) for r in REGIONS]

    for i in range(1, count + 1):
        # Progress indicator every 500 customers
        if i % 500 == 0:
            print(f"  ... generating customer {i}/{count}")

        # Generate unique tax ID
        while True:
            tax_id = generate_tax_id()
            if tax_id not in used_tax_ids:
                used_tax_ids.add(tax_id)
                break

        # Generate unique company name
        max_attempts = 10
        for attempt in range(max_attempts):
            company_prefix = random.choice(COMPANY_PREFIXES)
            company_suffix = random.choice(COMPANY_NAMES)
            company_name = f"{company_prefix} {company_suffix}"

            if company_name not in used_company_names:
                used_company_names.add(company_name)
                break
            elif attempt == max_attempts - 1:
                # Add number if can't generate unique
                company_name = f"{company_name} {i}"
                used_company_names.add(company_name)

        # Status with weights: 60% Client, 30% Potential, 10% Lost
        status = random.choices(STATUSES, weights=[60, 30, 10])[0]

        # Select region based on weights
        region = random.choices(
            [r[0] for r in regional_weights],
            [r[1] for r in regional_weights]
        )[0]

        # Select customer type with distribution: 40% SME, 35% Enterprise, 25% Startup
        customer_type = random.choices(CUSTOMER_TYPES, weights=[35, 40, 25])[0]

        # Select industry
        industry = random.choice(INDUSTRIES)

        customer = {
            'customer_code': f"CUST{i:04d}",
            'company_name': company_name,
            'tax_id': tax_id,
            'contact_person': generate_person_name(),
            'phone': generate_phone(),
            'email': generate_customer_email(company_suffix, i),
            'status': status,
            'salesperson': random.choice(salesperson_names),
            'entity_type': random.choice(['Company', 'Individual Business']),
            'terms': random.choice(['Net 15', 'Net 30', 'Net 60', 'Net 90', 'COD', 'Prepaid']),
            'industry': industry,
            'region': region,
            'customer_type': customer_type,
            'order_value_range': generate_order_value_range(customer_type),
            'purchase_revenue': generate_purchase_revenue(customer_type),
            'sales_policy': random.choice(['Basic', 'Standard', 'Premium', 'VIP']),
            'parent_company': f"CUST{random.randint(1, max(1, i-1)):04d}" if i > 20 and random.random() < 0.15 else "",
            'delivery_address': generate_address(region),
            'invoice_email': generate_customer_email(company_suffix, i + 10000),
            'creation_date': generate_creation_date(),
            'notes': f"Enterprise demo customer {i}"
        }

        customers.append(customer)

    print(f"  ✓ Generated {len(customers)} customers")

    # Stats
    status_dist = defaultdict(int)
    type_dist = defaultdict(int)
    region_dist = defaultdict(int)

    for c in customers:
        status_dist[c['status']] += 1
        type_dist[c['customer_type']] += 1
        region_dist[c['region']] += 1

    print(f"    - By status:")
    for status, count in sorted(status_dist.items()):
        print(f"      • {status}: {count}")
    print(f"    - By type:")
    for ctype, count in sorted(type_dist.items()):
        print(f"      • {ctype}: {count}")
    print(f"    - By region:")
    for region, count in sorted(region_dist.items()):
        print(f"      • {region}: {count}")

    return customers

# ============================================================================
# FILE WRITING
# ============================================================================

def write_csv(filename, data, fieldnames):
    """Write data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✓ Written {len(data)} records to {filename}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("STARTING DATA GENERATION")
    print("=" * 80 + "\n")

    # Generate staff
    staff, staff_dict = generate_staff_enterprise()

    # Generate sales teams
    teams = generate_sales_teams_enterprise(staff_dict)

    # Generate customers
    customers = generate_customers_enterprise(staff, TARGET_CUSTOMERS)

    print("\n" + "=" * 80)
    print("WRITING CSV FILES")
    print("=" * 80 + "\n")

    # Write staff CSV
    staff_fields = [
        'employee_code', 'name', 'login', 'email', 'phone', 'job_title',
        'department', 'manager', 'region_territory', 'industry_specialization',
        'customer_type_focus', 'active', 'hire_date', 'monthly_sales_target',
        'user_type', 'sales_team'
    ]
    write_csv('staff_sprint1_enterprise.csv', staff, staff_fields)

    # Write sales teams CSV
    team_fields = [
        'team_id', 'team_name', 'team_leader', 'member_count',
        'revenue_target', 'team_type', 'focus_area'
    ]
    write_csv('sales_teams_sprint1_enterprise.csv', teams, team_fields)

    # Write customers CSV
    customer_fields = [
        'customer_code', 'company_name', 'tax_id', 'contact_person', 'phone',
        'email', 'status', 'salesperson', 'entity_type', 'terms', 'industry',
        'region', 'customer_type', 'order_value_range', 'purchase_revenue',
        'sales_policy', 'parent_company', 'delivery_address', 'invoice_email',
        'creation_date', 'notes'
    ]
    write_csv('customers_sprint1_enterprise.csv', customers, customer_fields)

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE - SUMMARY")
    print("=" * 80 + "\n")

    print(f"📊 STAFF ({len(staff)} members):")
    print(f"  • Directors: {len(staff_dict['directors'])}")
    print(f"  • Managers: {len(staff_dict['managers'])}")
    print(f"  • Sales Executives: {len(staff_dict['sales_execs'])}")
    print(f"  • Telesales: {len(staff_dict['telesales'])}")
    print(f"  • Support Staff: {len(staff_dict['support'])}")

    print(f"\n📊 SALES TEAMS ({len(teams)} teams):")
    team_types = defaultdict(int)
    for team in teams:
        team_types[team['team_type']] += 1
    for ttype, count in sorted(team_types.items()):
        print(f"  • {ttype}: {count}")

    total_target = sum([t['revenue_target'] for t in teams])
    print(f"\n  Total monthly revenue target: {total_target/1000000000:.1f}B VND")

    print(f"\n📊 CUSTOMERS ({len(customers)} records):")
    print(f"  • Enterprise: {sum(1 for c in customers if c['customer_type'] == 'Enterprise')}")
    print(f"  • SME: {sum(1 for c in customers if c['customer_type'] == 'SME')}")
    print(f"  • Startup: {sum(1 for c in customers if c['customer_type'] == 'Startup')}")

    print("\n" + "=" * 80)
    print("✅ All enterprise demo data files generated successfully!")
    print("=" * 80 + "\n")

    print("📁 Generated files:")
    print("  • staff_sprint1_enterprise.csv")
    print("  • sales_teams_sprint1_enterprise.csv")
    print("  • customers_sprint1_enterprise.csv")

    print("\nNext steps:")
    print("  1. Review the generated CSV files")
    print("  2. Run the import scripts to populate Odoo")
    print("  3. Generate CRM demo data (leads, opportunities, activities)")

if __name__ == "__main__":
    main()
