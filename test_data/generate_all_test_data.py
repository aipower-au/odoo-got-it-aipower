#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master script to generate all Sprint 1 test data
Generates: staff, customers, and sales teams CSV files

Usage: python3 generate_all_test_data.py
"""

import csv
import random
from datetime import datetime, timedelta

print("=" * 70)
print("SPRINT 1 TEST DATA GENERATOR")
print("=" * 70)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Main Sales Team - these will be the 8 salespeople in customer CSV
MAIN_SALES_TEAM = [
    {
        'name': 'Nguyễn Văn Thành',
        'region': 'South',
        'industry': ['F&B', 'Logistics'],
        'customer_type': 'Enterprise'
    },
    {
        'name': 'Phạm Thu Hà',
        'region': 'South',
        'industry': ['Technology', 'Hospitality'],
        'customer_type': 'SME'
    },
    {
        'name': 'Trần Thị Hồng',
        'region': 'North',
        'industry': ['F&B', 'Manufacturing'],
        'customer_type': 'Enterprise'
    },
    {
        'name': 'Võ Thị Lan',
        'region': 'Central',
        'industry': ['Retail', 'Fashion'],
        'customer_type': 'Startup'
    },
    {
        'name': 'Hoàng Đức Long',
        'region': 'South',
        'industry': ['Education', 'Technology'],
        'customer_type': 'SME'
    },
    {
        'name': 'Phan Quốc Anh',
        'region': 'Central',
        'industry': ['Hospitality', 'Logistics'],
        'customer_type': 'Enterprise'
    },
    {
        'name': 'Lê Minh Tuấn',
        'region': 'North',
        'industry': ['Education', 'Healthcare'],
        'customer_type': 'SME'
    },
    {
        'name': 'Đặng Minh Phương',
        'region': 'Central',
        'industry': ['Construction', 'Manufacturing'],
        'customer_type': 'Startup'
    }
]

SALES_MANAGERS = [
    {'name': 'Lê Quốc Bảo', 'region': 'North', 'manages': ['Trần Thị Hồng', 'Lê Minh Tuấn']},
    {'name': 'Nguyễn Thị Mai', 'region': 'South', 'manages': ['Nguyễn Văn Thành', 'Phạm Thu Hà', 'Hoàng Đức Long']},
    {'name': 'Trần Văn Hải', 'region': 'Central', 'manages': ['Võ Thị Lan', 'Phan Quốc Anh', 'Đặng Minh Phương']}
]

SALES_DIRECTOR = {'name': 'Phạm Minh Tuấn', 'region': 'All Vietnam'}

TELESALES_STAFF = [
    {'name': 'Nguyễn Thu Hằng', 'region': 'North'},
    {'name': 'Trần Văn Đạt', 'region': 'North'},
    {'name': 'Lê Thị Hương', 'region': 'South'},
    {'name': 'Hoàng Minh Khoa', 'region': 'South'},
    {'name': 'Võ Thị Ngọc', 'region': 'Central'}
]

ADDITIONAL_SALES = [
    {'name': 'Bùi Văn Tài', 'region': 'North', 'industry': ['Technology', 'Retail']},
    {'name': 'Đỗ Thị Phương', 'region': 'South', 'industry': ['F&B', 'Healthcare']},
    {'name': 'Phan Thị Tuyết', 'region': 'Central', 'industry': ['Construction', 'Logistics']},
    {'name': 'Ngô Văn Hùng', 'region': 'North', 'industry': ['Manufacturing', 'Fashion']},
    {'name': 'Huỳnh Thị Lan', 'region': 'South', 'industry': ['Education', 'Hospitality']}
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

PHONE_PREFIXES = ['091', '094', '088', '083', '084', '085', '081', '082', '090', '093']

# Vietnamese to ASCII character mapping
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
        # Convert to lowercase and check if it's a Vietnamese character
        result.append(VIETNAMESE_TO_ASCII.get(char.lower(), char.lower()))
    return ''.join(result)

def generate_phone():
    """Generate Vietnamese phone number"""
    prefix = random.choice(PHONE_PREFIXES)
    return f"+84{prefix[1:]}{random.randint(1000000, 9999999)}"

def generate_login(name):
    """Generate login from name (ASCII only)"""
    # Remove Vietnamese accents first
    ascii_name = remove_vietnamese_accents(name)
    parts = ascii_name.lower().split()
    if len(parts) >= 2:
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
        'telesales': (90, 730)
    }
    days = random.randint(*ranges.get(seniority, (180, 545)))
    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")

def generate_sales_target(job_title):
    """Generate monthly sales target in VND"""
    targets = {
        'Sales Director': (2000000000, 3000000000),
        'Sales Manager': (500000000, 1000000000),
        'Sales Executive': (100000000, 300000000),
        'Telesales Executive': (0, 0)
    }
    range_selected = targets.get(job_title, (50000000, 150000000))
    if range_selected[0] == 0:
        return 0
    return random.randint(range_selected[0], range_selected[1])

def get_sales_team(region, job_title):
    """Determine sales team based on region and job title"""
    if job_title == 'Sales Director':
        return 'Leadership'
    elif job_title == 'Sales Manager':
        return f'{region} Regional Team' if region != 'All Vietnam' else 'Management'
    elif job_title == 'Telesales Executive':
        return 'Telesales Team'
    else:
        return f'{region} Regional Team'

# ============================================================================
# STAFF GENERATION
# ============================================================================

def generate_staff():
    """Generate all staff records"""
    print("Generating staff data...")
    staff = []
    emp_id = 1

    # Sales Director
    director = SALES_DIRECTOR
    staff.append({
        'employee_code': f'EMP{emp_id:03d}',
        'name': director['name'],
        'login': generate_login(director['name']),
        'email': generate_email(director['name']),
        'phone': generate_phone(),
        'job_title': 'Sales Director',
        'department': 'Sales',
        'manager': '',
        'region_territory': director['region'],
        'industry_specialization': 'All',
        'customer_type_focus': 'All',
        'active': 'True',
        'hire_date': generate_hire_date('director'),
        'monthly_sales_target': generate_sales_target('Sales Director'),
        'user_type': 'Director',
        'sales_team': get_sales_team('All', 'Sales Director')
    })
    emp_id += 1

    # Sales Managers
    for manager in SALES_MANAGERS:
        staff.append({
            'employee_code': f'EMP{emp_id:03d}',
            'name': manager['name'],
            'login': generate_login(manager['name']),
            'email': generate_email(manager['name']),
            'phone': generate_phone(),
            'job_title': 'Sales Manager',
            'department': 'Sales',
            'manager': SALES_DIRECTOR['name'],
            'region_territory': manager['region'],
            'industry_specialization': 'All',
            'customer_type_focus': 'All',
            'active': 'True',
            'hire_date': generate_hire_date('manager'),
            'monthly_sales_target': generate_sales_target('Sales Manager'),
            'user_type': 'Manager',
            'sales_team': get_sales_team(manager['region'], 'Sales Manager')
        })
        emp_id += 1

    # Main Sales Executives
    manager_mapping = {
        'North': 'Lê Quốc Bảo',
        'South': 'Nguyễn Thị Mai',
        'Central': 'Trần Văn Hải'
    }

    for sales in MAIN_SALES_TEAM:
        staff.append({
            'employee_code': f'EMP{emp_id:03d}',
            'name': sales['name'],
            'login': generate_login(sales['name']),
            'email': generate_email(sales['name']),
            'phone': generate_phone(),
            'job_title': 'Sales Executive',
            'department': 'Sales',
            'manager': manager_mapping[sales['region']],
            'region_territory': sales['region'],
            'industry_specialization': ', '.join(sales['industry']),
            'customer_type_focus': sales['customer_type'],
            'active': 'True',
            'hire_date': generate_hire_date('sales'),
            'monthly_sales_target': generate_sales_target('Sales Executive'),
            'user_type': 'Sales',
            'sales_team': get_sales_team(sales['region'], 'Sales Executive')
        })
        emp_id += 1

    # Additional Sales Executives
    for sales in ADDITIONAL_SALES:
        staff.append({
            'employee_code': f'EMP{emp_id:03d}',
            'name': sales['name'],
            'login': generate_login(sales['name']),
            'email': generate_email(sales['name']),
            'phone': generate_phone(),
            'job_title': 'Sales Executive',
            'department': 'Sales',
            'manager': manager_mapping[sales['region']],
            'region_territory': sales['region'],
            'industry_specialization': ', '.join(sales['industry']),
            'customer_type_focus': 'Mixed',
            'active': 'True',
            'hire_date': generate_hire_date('sales'),
            'monthly_sales_target': generate_sales_target('Sales Executive'),
            'user_type': 'Sales',
            'sales_team': get_sales_team(sales['region'], 'Sales Executive')
        })
        emp_id += 1

    # Telesales Team
    for tele in TELESALES_STAFF:
        staff.append({
            'employee_code': f'EMP{emp_id:03d}',
            'name': tele['name'],
            'login': generate_login(tele['name']),
            'email': generate_email(tele['name']),
            'phone': generate_phone(),
            'job_title': 'Telesales Executive',
            'department': 'Telesales',
            'manager': 'Lê Quốc Bảo',
            'region_territory': tele['region'],
            'industry_specialization': 'All',
            'customer_type_focus': 'Lead Qualification',
            'active': 'True',
            'hire_date': generate_hire_date('telesales'),
            'monthly_sales_target': generate_sales_target('Telesales Executive'),
            'user_type': 'Telesales',
            'sales_team': get_sales_team('All', 'Telesales Executive')
        })
        emp_id += 1

    print(f"  ✓ Generated {len(staff)} staff members")
    return staff

def write_staff_csv(staff, filename):
    """Write staff to CSV file"""
    fieldnames = [
        'employee_code', 'name', 'login', 'email', 'phone', 'job_title',
        'department', 'manager', 'region_territory', 'industry_specialization',
        'customer_type_focus', 'active', 'hire_date', 'monthly_sales_target',
        'user_type', 'sales_team'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(staff)

# ============================================================================
# CUSTOMER GENERATION
# ============================================================================

# Vietnamese company data
COMPANY_PREFIXES = [
    "Công ty TNHH", "Công ty Cổ phần", "Công ty", "Tập đoàn",
    "Doanh nghiệp", "Chi nhánh", "Xí nghiệp"
]

COMPANY_NAMES = [
    "Thương mại Hùng Vương", "Công nghệ Việt Nam", "Thực phẩm Á Châu",
    "Điện tử Sài Gòn", "Xây dựng Hoàng Long", "Dược phẩm Hà Nội",
    "Vật liệu xây dựng Đại Phát", "Thời trang Nam Phong", "May mặc Hoa Sen",
    "Nhựa Thiên Long", "Cơ khí Đông Á", "Thép Việt Ý", "Gỗ Minh Phương",
    "Nội thất Hoàng Gia", "Điện lạnh Bách Khoa", "Máy tính Phương Nam",
    "Phần mềm Trí Tuệ", "Giải pháp số FPT", "Marketing Đỉnh Cao",
    "Truyền thông Sáng Tạo", "In ấn Thành Công", "Bao bì Tân Tiến",
    "Logistics Hải Vân", "Vận tải Phương Trang", "Khách sạn Mường Thanh",
    "Nhà hàng Ngọc Mai", "Café Highlands", "Siêu thị BigC", "Bán lẻ Vinmart",
    "Dệt may Việt Tiến", "Da giày Huế", "Mỹ phẩm Phương Đông",
    "Trang sức Bảo Tín", "Đồng hồ Đăng Quang", "Điện thoại Thế Giới Di Động",
    "Thiết bị y tế Hà Nội", "Công nghệ sinh học", "Nông sản sạch Đà Lạt",
    "Thủy sản Minh Hải", "Chế biến thực phẩm Vissan", "Bia Hà Nội",
    "Nước giải khát Tân Hiệp Phát", "Sữa TH True Milk", "Bánh kẹo Kinh Đô",
    "Cà phê Trung Nguyên", "Trà Phúc Long", "Nhà xuất bản Trẻ",
    "Giáo dục Nguyễn Hoàng", "Anh ngữ ILA", "Đào tạo FPT", "Tư vấn Ernst & Young"
]

PERSON_FIRST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Mai", "Trương", "Tô"
]

PERSON_MIDDLE_NAMES = [
    "Văn", "Thị", "Đức", "Minh", "Hữu", "Quốc", "Anh", "Thanh", "Hoàng", "Phương",
    "Hồng", "Thu", "Xuân", "Hạ", "Thu", "Đông", "Kim", "Ngọc", "Bảo", "Gia"
]

PERSON_LAST_NAMES = [
    "Anh", "Hùng", "Dũng", "Mạnh", "Tuấn", "Tùng", "Hải", "Nam", "Long", "Quân",
    "Hương", "Lan", "Linh", "Nga", "Nhung", "Phương", "Quỳnh", "Trang", "Vy", "Yến",
    "Khoa", "Đạt", "Thành", "Vương", "Hiếu", "Khánh", "Phúc", "Tâm", "Trí", "Bình"
]

INDUSTRIES = [
    "Technology", "F&B", "Retail", "Manufacturing", "Healthcare",
    "Education", "Construction", "Logistics", "Hospitality", "Fashion"
]

REGIONS = [
    "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng",
    "Biên Hòa", "Nha Trang", "Huế", "Vũng Tàu", "Quy Nhơn"
]

DISTRICTS_HANOI = [
    "Hoàn Kiếm", "Ba Đình", "Đống Đa", "Hai Bà Trưng", "Cầu Giấy",
    "Tây Hồ", "Thanh Xuân", "Hoàng Mai", "Long Biên", "Nam Từ Liêm"
]

DISTRICTS_HCMC = [
    "Quận 1", "Quận 3", "Quận 5", "Quận 7", "Quận 10",
    "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Gò Vấp", "Thủ Đức"
]

STREETS = [
    "Lê Lợi", "Nguyễn Huệ", "Trần Hưng Đạo", "Hai Bà Trưng", "Lý Thường Kiệt",
    "Điện Biên Phủ", "Hoàng Diệu", "Phan Chu Trinh", "Trường Chinh", "Láng Hạ"
]

STATUSES = ["Potential", "Client", "Lost"]
CUSTOMER_TYPES = ["Enterprise", "SME", "Startup"]
ENTITY_TYPES = ["Company", "Individual Business"]
TERMS = ["Net 30", "Net 60", "Net 90", "COD", "Prepaid", "Net 15"]
SALES_POLICIES = ["Standard", "VIP", "Premium", "Basic"]

def generate_tax_id():
    """Generate unique 10-digit Vietnamese tax ID"""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def generate_person_name():
    """Generate Vietnamese person name"""
    first = random.choice(PERSON_FIRST_NAMES)
    middle = random.choice(PERSON_MIDDLE_NAMES)
    last = random.choice(PERSON_LAST_NAMES)
    return f"{first} {middle} {last}"

def generate_address(region):
    """Generate Vietnamese address"""
    if region == "Hà Nội":
        district = random.choice(DISTRICTS_HANOI)
    elif region == "Hồ Chí Minh":
        district = random.choice(DISTRICTS_HCMC)
    else:
        district = f"Quận {random.randint(1, 5)}"

    street_number = random.randint(1, 999)
    street = random.choice(STREETS)
    return f"{street_number} {street}, {district}, {region}"

def generate_revenue():
    """Generate purchase revenue in VND"""
    ranges = [
        (10000000, 50000000),
        (50000000, 200000000),
        (200000000, 1000000000),
        (1000000000, 5000000000),
    ]
    range_selected = random.choice(ranges)
    return random.randint(range_selected[0], range_selected[1])

def generate_order_value():
    """Generate order value range"""
    ranges = ["< 10M", "10M - 50M", "50M - 100M", "100M - 500M", "> 500M"]
    return random.choice(ranges)

def generate_creation_date():
    """Generate random date in past 6 months"""
    days_ago = random.randint(0, 180)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")

def generate_parent_company(index):
    """Generate parent company for some customers"""
    if random.random() < 0.3 and index > 10:
        parent_index = random.randint(1, index - 1)
        return f"CUST{parent_index:03d}"
    return ""

def generate_customer_email(company_name, index):
    """Generate email address (ASCII only)"""
    domains = ['gmail.com', 'yahoo.com', 'company.vn', 'business.com.vn', 'outlook.com']
    # Remove Vietnamese accents and convert to ASCII
    ascii_name = remove_vietnamese_accents(company_name)
    simple_name = ascii_name.lower().replace('cong ty', '').replace('tnhh', '').replace('co phan', '').strip()
    simple_name = simple_name.replace(' ', '')[:10]
    return f"contact{index}@{simple_name}.{random.choice(domains)}"

def generate_customers(salespeople, count=100):
    """Generate customer data"""
    print("Generating customer data...")
    customers = []
    used_tax_ids = set()

    # Extract salesperson names
    salesperson_names = [sp['name'] for sp in salespeople if sp['user_type'] == 'Sales']

    for i in range(1, count + 1):
        # Generate unique tax ID
        while True:
            tax_id = generate_tax_id()
            if tax_id not in used_tax_ids:
                used_tax_ids.add(tax_id)
                break

        # Generate company name
        company_prefix = random.choice(COMPANY_PREFIXES)
        company_suffix = random.choice(COMPANY_NAMES)
        company_name = f"{company_prefix} {company_suffix}"

        # Status with weights: 60% Client, 30% Potential, 10% Lost
        status = random.choices(STATUSES, weights=[30, 60, 10])[0]
        region = random.choice(REGIONS)

        customer = {
            'customer_code': f"CUST{i:03d}",
            'company_name': company_name,
            'tax_id': tax_id,
            'contact_person': generate_person_name(),
            'phone': generate_phone(),
            'email': generate_customer_email(company_suffix, i),
            'status': status,
            'salesperson': random.choice(salesperson_names),
            'entity_type': random.choice(ENTITY_TYPES),
            'terms': random.choice(TERMS),
            'industry': random.choice(INDUSTRIES),
            'region': region,
            'customer_type': random.choice(CUSTOMER_TYPES),
            'order_value_range': generate_order_value(),
            'purchase_revenue': generate_revenue(),
            'sales_policy': random.choice(SALES_POLICIES),
            'parent_company': generate_parent_company(i),
            'delivery_address': generate_address(region),
            'invoice_email': generate_customer_email(company_suffix, i + 1000),
            'creation_date': generate_creation_date(),
            'notes': f"Test customer {i} for Sprint 1"
        }

        customers.append(customer)

    print(f"  ✓ Generated {len(customers)} customers")
    return customers

def write_customers_csv(customers, filename):
    """Write customers to CSV file"""
    fieldnames = [
        'customer_code', 'company_name', 'tax_id', 'contact_person', 'phone',
        'email', 'status', 'salesperson', 'entity_type', 'terms', 'industry',
        'region', 'customer_type', 'order_value_range', 'purchase_revenue',
        'sales_policy', 'parent_company', 'delivery_address', 'invoice_email',
        'creation_date', 'notes'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(customers)

# ============================================================================
# SALES TEAMS GENERATION
# ============================================================================

def generate_sales_teams():
    """Generate sales teams"""
    print("Generating sales teams data...")

    teams = [
        {
            'team_code': 'TEAM001',
            'team_name': 'North Regional Team',
            'team_leader': 'Lê Quốc Bảo',
            'team_members': 'Trần Thị Hồng, Lê Minh Tuấn, Bùi Văn Tài, Ngô Văn Hùng',
            'region_coverage': 'Hà Nội, Hải Phòng, Huế',
            'industry_focus': 'All',
            'customer_type_target': 'All',
            'monthly_revenue_target': 800000000,
            'team_type': 'Regional',
            'description': 'Covers all sales activities in Northern Vietnam'
        },
        {
            'team_code': 'TEAM002',
            'team_name': 'South Regional Team',
            'team_leader': 'Nguyễn Thị Mai',
            'team_members': 'Nguyễn Văn Thành, Phạm Thu Hà, Hoàng Đức Long, Đỗ Thị Phương, Huỳnh Thị Lan',
            'region_coverage': 'Hồ Chí Minh, Biên Hòa, Vũng Tàu',
            'industry_focus': 'All',
            'customer_type_target': 'All',
            'monthly_revenue_target': 1200000000,
            'team_type': 'Regional',
            'description': 'Covers all sales activities in Southern Vietnam'
        },
        {
            'team_code': 'TEAM003',
            'team_name': 'Central Regional Team',
            'team_leader': 'Trần Văn Hải',
            'team_members': 'Võ Thị Lan, Phan Quốc Anh, Đặng Minh Phương, Phan Thị Tuyết',
            'region_coverage': 'Đà Nẵng, Nha Trang, Quy Nhơn, Cần Thơ',
            'industry_focus': 'All',
            'customer_type_target': 'All',
            'monthly_revenue_target': 700000000,
            'team_type': 'Regional',
            'description': 'Covers all sales activities in Central Vietnam'
        },
        {
            'team_code': 'TEAM004',
            'team_name': 'Technology & Digital Team',
            'team_leader': 'Phạm Thu Hà',
            'team_members': 'Phạm Thu Hà, Hoàng Đức Long, Bùi Văn Tài',
            'region_coverage': 'All Vietnam',
            'industry_focus': 'Technology, Education',
            'customer_type_target': 'Enterprise, SME',
            'monthly_revenue_target': 500000000,
            'team_type': 'Industry-based',
            'description': 'Specialized team for technology and digital transformation clients'
        },
        {
            'team_code': 'TEAM005',
            'team_name': 'F&B & Retail Team',
            'team_leader': 'Nguyễn Văn Thành',
            'team_members': 'Nguyễn Văn Thành, Trần Thị Hồng, Võ Thị Lan, Đỗ Thị Phương',
            'region_coverage': 'All Vietnam',
            'industry_focus': 'F&B, Retail, Fashion',
            'customer_type_target': 'All',
            'monthly_revenue_target': 600000000,
            'team_type': 'Industry-based',
            'description': 'Specialized team for food & beverage and retail sectors'
        },
        {
            'team_code': 'TEAM006',
            'team_name': 'Enterprise Sales Team',
            'team_leader': 'Nguyễn Thị Mai',
            'team_members': 'Nguyễn Văn Thành, Trần Thị Hồng, Phan Quốc Anh',
            'region_coverage': 'All Vietnam',
            'industry_focus': 'All',
            'customer_type_target': 'Enterprise',
            'monthly_revenue_target': 1000000000,
            'team_type': 'Customer-type based',
            'description': 'High-value enterprise accounts with order value > 100M VND'
        },
        {
            'team_code': 'TEAM007',
            'team_name': 'Telesales Team',
            'team_leader': 'Lê Quốc Bảo',
            'team_members': 'Nguyễn Thu Hằng, Trần Văn Đạt, Lê Thị Hương, Hoàng Minh Khoa, Võ Thị Ngọc',
            'region_coverage': 'All Vietnam',
            'industry_focus': 'All',
            'customer_type_target': 'Lead Qualification',
            'monthly_revenue_target': 0,
            'team_type': 'Support',
            'description': 'Handles initial lead qualification and customer identification'
        }
    ]

    print(f"  ✓ Generated {len(teams)} sales teams")
    return teams

def write_teams_csv(teams, filename):
    """Write sales teams to CSV file"""
    fieldnames = [
        'team_code', 'team_name', 'team_leader', 'team_members',
        'region_coverage', 'industry_focus', 'customer_type_target',
        'monthly_revenue_target', 'team_type', 'description'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(teams)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def print_statistics(staff, customers, teams):
    """Print comprehensive statistics"""
    print()
    print("=" * 70)
    print("GENERATION COMPLETE - STATISTICS")
    print("=" * 70)

    # Staff statistics
    print("\n📊 STAFF (22 members):")
    by_title = {}
    for s in staff:
        by_title[s['job_title']] = by_title.get(s['job_title'], 0) + 1
    for title, count in sorted(by_title.items()):
        print(f"  • {title}: {count}")

    print("\n  Main Salespeople (in customer CSV):")
    for s in staff:
        if s['name'] in [m['name'] for m in MAIN_SALES_TEAM]:
            print(f"    - {s['name']} ({s['employee_code']}) - {s['region_territory']}")

    # Customer statistics
    print(f"\n📊 CUSTOMERS (100 records):")
    statuses = {}
    regions = {}
    for c in customers:
        statuses[c['status']] = statuses.get(c['status'], 0) + 1
        regions[c['region']] = regions.get(c['region'], 0) + 1

    print("  Status distribution:")
    for status, count in sorted(statuses.items()):
        print(f"    • {status}: {count}")

    print(f"\n  Regional distribution: {len(regions)} regions")

    # Teams statistics
    print(f"\n📊 SALES TEAMS (7 teams):")
    by_type = {}
    total_target = 0
    for team in teams:
        by_type[team['team_type']] = by_type.get(team['team_type'], 0) + 1
        total_target += team['monthly_revenue_target']

    print("  By type:")
    for ttype, count in sorted(by_type.items()):
        print(f"    • {ttype}: {count}")
    print(f"\n  Total monthly revenue target: {total_target/1000000000:.1f}B VND")

    print("\n" + "=" * 70)
    print("✅ All test data files generated successfully!")
    print("=" * 70)

def main():
    """Main execution"""
    # Generate in order: staff → customers → teams
    staff = generate_staff()
    write_staff_csv(staff, "staff_sprint1.csv")

    customers = generate_customers(staff, count=100)
    write_customers_csv(customers, "customers_sprint1.csv")

    teams = generate_sales_teams()
    write_teams_csv(teams, "sales_teams_sprint1.csv")

    # Print statistics
    print_statistics(staff, customers, teams)

    print("\n📁 Generated files:")
    print("  • staff_sprint1.csv")
    print("  • customers_sprint1.csv")
    print("  • sales_teams_sprint1.csv")
    print()

if __name__ == "__main__":
    main()
