#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM Demo Data Generator for Odoo 18
Generates: leads (2000), opportunities (1500), activities (3000), products (50), quotations (600)

Usage:
  python3 generate_crm_demo_data.py                    # Full enterprise scale
  python3 generate_crm_demo_data.py --test              # Small test (20/15/30/10/10)
  python3 generate_crm_demo_data.py --leads 100 --opportunities 50 --activities 100 --products 20 --quotations 30

Requires: staff_sprint1_enterprise.csv and customers_sprint1_enterprise.csv
"""

import csv
import random
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

# ============================================================================
# PARSE COMMAND LINE ARGUMENTS
# ============================================================================

parser = argparse.ArgumentParser(description='Generate CRM demo data for Odoo')
parser.add_argument('--test', action='store_true', help='Generate small test dataset (20 leads, 15 opps, 30 activities, 10 products, 10 quotations)')
parser.add_argument('--leads', type=int, help='Number of leads (default: 2000)')
parser.add_argument('--opportunities', type=int, help='Number of opportunities (default: 1500)')
parser.add_argument('--activities', type=int, help='Number of activities (default: 3000)')
parser.add_argument('--products', type=int, help='Number of products (default: 50)')
parser.add_argument('--quotations', type=int, help='Number of quotations (default: 600)')
args = parser.parse_args()

# ============================================================================
# CONFIGURATION
# ============================================================================

if args.test:
    TARGET_LEADS = 20
    TARGET_OPPORTUNITIES = 15
    TARGET_ACTIVITIES = 30
    TARGET_PRODUCTS = 10
    TARGET_QUOTATIONS = 10
else:
    TARGET_LEADS = args.leads or 2000
    TARGET_OPPORTUNITIES = args.opportunities or 1500
    TARGET_ACTIVITIES = args.activities or 3000
    TARGET_PRODUCTS = args.products or 50
    TARGET_QUOTATIONS = args.quotations or 600

print("=" * 80)
print("CRM DEMO DATA GENERATOR")
print("=" * 80)
print(f"Configuration: {TARGET_LEADS} leads, {TARGET_OPPORTUNITIES} opportunities, {TARGET_ACTIVITIES} activities")
print(f"               {TARGET_PRODUCTS} products, {TARGET_QUOTATIONS} quotations")
print("=" * 80)
print()

# ============================================================================
# CRM STAGES (PIPELINE)
# ============================================================================

CRM_STAGES = [
    {'stage_id': 'STAGE01', 'name': 'New', 'sequence': 1, 'probability': 5, 'fold': False, 'is_won': False},
    {'stage_id': 'STAGE02', 'name': 'Qualified', 'sequence': 2, 'probability': 20, 'fold': False, 'is_won': False},
    {'stage_id': 'STAGE03', 'name': 'Meeting Scheduled', 'sequence': 3, 'probability': 40, 'fold': False, 'is_won': False},
    {'stage_id': 'STAGE04', 'name': 'Proposal', 'sequence': 4, 'probability': 60, 'fold': False, 'is_won': False},
    {'stage_id': 'STAGE05', 'name': 'Negotiation', 'sequence': 5, 'probability': 75, 'fold': False, 'is_won': False},
    {'stage_id': 'STAGE06', 'name': 'Won', 'sequence': 6, 'probability': 100, 'fold': False, 'is_won': True},
    {'stage_id': 'STAGE07', 'name': 'Lost', 'sequence': 7, 'probability': 0, 'fold': True, 'is_won': False},
]

# ============================================================================
# LEAD SOURCES
# ============================================================================

LEAD_SOURCES = [
    {'source_id': 'SRC01', 'name': 'Website Form', 'weight': 0.35},
    {'source_id': 'SRC02', 'name': 'Hotline', 'weight': 0.25},
    {'source_id': 'SRC03', 'name': 'Referral', 'weight': 0.15},
    {'source_id': 'SRC04', 'name': 'Trade Show', 'weight': 0.10},
    {'source_id': 'SRC05', 'name': 'Cold Calling', 'weight': 0.05},
    {'source_id': 'SRC06', 'name': 'LinkedIn', 'weight': 0.04},
    {'source_id': 'SRC07', 'name': 'Partner Network', 'weight': 0.03},
    {'source_id': 'SRC08', 'name': 'Email Campaign', 'weight': 0.02},
    {'source_id': 'SRC09', 'name': 'Google Ads', 'weight': 0.01},
]

# ============================================================================
# CRM TAGS
# ============================================================================

CRM_TAGS = [
    # Source tags
    {'tag_id': 'TAG01', 'name': 'Website', 'category': 'Source'},
    {'tag_id': 'TAG02', 'name': 'Hotline', 'category': 'Source'},
    {'tag_id': 'TAG03', 'name': 'Referral', 'category': 'Source'},
    # Industry tags
    {'tag_id': 'TAG04', 'name': 'Technology', 'category': 'Industry'},
    {'tag_id': 'TAG05', 'name': 'F&B', 'category': 'Industry'},
    {'tag_id': 'TAG06', 'name': 'Manufacturing', 'category': 'Industry'},
    {'tag_id': 'TAG07', 'name': 'Retail', 'category': 'Industry'},
    {'tag_id': 'TAG08', 'name': 'Healthcare', 'category': 'Industry'},
    {'tag_id': 'TAG09', 'name': 'Education', 'category': 'Industry'},
    # Product tags
    {'tag_id': 'TAG10', 'name': 'Software License', 'category': 'Product'},
    {'tag_id': 'TAG11', 'name': 'Training', 'category': 'Product'},
    {'tag_id': 'TAG12', 'name': 'Support Contract', 'category': 'Product'},
    {'tag_id': 'TAG13', 'name': 'Hardware', 'category': 'Product'},
    {'tag_id': 'TAG14', 'name': 'Consulting', 'category': 'Product'},
    # Priority tags
    {'tag_id': 'TAG15', 'name': 'Hot Lead', 'category': 'Priority'},
    {'tag_id': 'TAG16', 'name': 'Warm Lead', 'category': 'Priority'},
    {'tag_id': 'TAG17', 'name': 'Cold Lead', 'category': 'Priority'},
    {'tag_id': 'TAG18', 'name': 'VIP', 'category': 'Priority'},
    {'tag_id': 'TAG19', 'name': 'Urgent', 'category': 'Priority'},
    # Status tags
    {'tag_id': 'TAG20', 'name': 'Follow-up Needed', 'category': 'Status'},
    {'tag_id': 'TAG21', 'name': 'Decision Pending', 'category': 'Status'},
    {'tag_id': 'TAG22', 'name': 'Budget Approved', 'category': 'Status'},
    {'tag_id': 'TAG23', 'name': 'Contract Review', 'category': 'Status'},
    {'tag_id': 'TAG24', 'name': 'Technical Evaluation', 'category': 'Status'},
]

# ============================================================================
# VIETNAMESE NAME & ADDRESS DATA
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
    """Convert Vietnamese characters to ASCII"""
    result = []
    for char in text:
        result.append(VIETNAMESE_TO_ASCII.get(char.lower(), char.lower()))
    return ''.join(result)

FAMILY_NAMES = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
                'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Trương']

MIDDLE_NAMES_MALE = ['Văn', 'Đức', 'Minh', 'Quốc', 'Hữu', 'Xuân', 'Hoàng', 'Thanh']
MIDDLE_NAMES_FEMALE = ['Thị', 'Thu', 'Hồng', 'Kim', 'Phương', 'Ngọc', 'Bảo', 'Hạ']

GIVEN_NAMES_MALE = ['Thành', 'Long', 'Hùng', 'Tài', 'Tuấn', 'Anh', 'Khoa', 'Phúc', 'Bình']
GIVEN_NAMES_FEMALE = ['Lan', 'Hà', 'Mai', 'Hương', 'Trang', 'Nga', 'Yến', 'Nhung', 'Vy']

def generate_person_name(gender='random'):
    """Generate Vietnamese person name"""
    if gender == 'random':
        gender = random.choice(['male', 'female'])

    family = random.choice(FAMILY_NAMES)
    if gender == 'male':
        middle = random.choice(MIDDLE_NAMES_MALE)
        given = random.choice(GIVEN_NAMES_MALE)
    else:
        middle = random.choice(MIDDLE_NAMES_FEMALE)
        given = random.choice(GIVEN_NAMES_FEMALE)

    return f"{family} {middle} {given}"

PHONE_PREFIXES = ['091', '094', '088', '083', '084', '085', '081', '082', '090', '093']

def generate_phone():
    """Generate Vietnamese phone number"""
    prefix = random.choice(PHONE_PREFIXES)
    return f"+84{prefix[1:]}{random.randint(1000000, 9999999)}"

def generate_email(name, company=None):
    """Generate email (ASCII only)"""
    ascii_name = remove_vietnamese_accents(name)
    parts = ascii_name.lower().split()

    if company:
        ascii_company = remove_vietnamese_accents(company).replace(' ', '').lower()[:10]
        domain = f"{ascii_company}.vn"
    else:
        domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])

    if len(parts) >= 2:
        username = f"{parts[-1]}.{parts[0][0]}"
    else:
        username = parts[0]

    return f"{username}@{domain}"

CITIES = ['Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'Huế', 'Cần Thơ', 'Hải Phòng', 'Nha Trang', 'Biên Hòa']

def generate_address():
    """Generate Vietnamese address"""
    streets = ['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo', 'Hai Bà Trưng']
    return f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(CITIES)}"

# ============================================================================
# LEAD GENERATION
# ============================================================================

LEAD_TITLES = [
    "Quan tâm giải pháp CRM",
    "Yêu cầu báo giá phần mềm",
    "Tìm hiểu dịch vụ tư vấn",
    "Đăng ký demo sản phẩm",
    "Cần hỗ trợ kỹ thuật",
    "Nâng cấp hệ thống",
    "Liên hệ về partnership",
    "Hỏi về training course",
    "Yêu cầu thông tin sản phẩm",
    "Quan tâm giải pháp đám mây"
]

INDUSTRIES = ['Technology', 'F&B', 'Manufacturing', 'Retail', 'Healthcare',
              'Education', 'Construction', 'Logistics', 'Hospitality', 'Finance']

def generate_leads(staff_list, count=TARGET_LEADS):
    """Generate leads assigned to telesales team"""
    print(f"Generating {count} leads...")
    leads = []

    # Get telesales staff
    telesales = [s for s in staff_list if s['user_type'] == 'Telesales']
    if not telesales:
        print("  ⚠️  No telesales staff found! Using all staff.")
        telesales = staff_list

    # Lead stage distribution for telesales qualification
    # 40% New, 30% Qualified (ready to convert), 20% In Contact, 10% Lost
    stage_dist = {
        'New': ('STAGE01', 0.40),
        'Qualified': ('STAGE02', 0.30),
        'New': ('STAGE01', 0.20),  # Additional new leads
        'Lost': ('STAGE07', 0.10)
    }

    stages = []
    for stage_name, (stage_id, weight) in stage_dist.items():
        stages.extend([stage_id] * int(count * weight))

    # Ensure we have exactly count stages
    while len(stages) < count:
        stages.append('STAGE01')
    stages = stages[:count]
    random.shuffle(stages)

    for i in range(1, count + 1):
        if i % 500 == 0:
            print(f"  ... generating lead {i}/{count}")

        contact_name = generate_person_name()
        company_name = random.choice([
            None,  # 30% don't have company name yet
            f"Công ty {random.choice(['TNHH', 'Cổ phần'])} {random.choice(['An Phát', 'Bảo Minh', 'Cát Tường', 'Đại Phát', 'Gia Hưng'])}"
        ]) if random.random() > 0.30 else None

        stage_id = stages[i-1]
        priority = random.choices(['0', '1', '2', '3'], weights=[50, 30, 15, 5])[0]  # Normal, Medium, High, Urgent

        # Select source
        source_choices = [s['source_id'] for s in LEAD_SOURCES]
        source_weights = [s['weight'] for s in LEAD_SOURCES]
        source = random.choices(source_choices, source_weights)[0]

        # Select tags
        tag_count = random.randint(1, 3)
        tags = ','.join(random.sample([t['tag_id'] for t in CRM_TAGS[:20]], tag_count))

        # Date created (last 6 months)
        date_created = datetime.now() - timedelta(days=random.randint(0, 180))

        # Date open (contacted) - some leads not contacted yet
        date_open = ""
        if stage_id != 'STAGE01' or random.random() > 0.4:
            date_open = (date_created + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")

        # Date closed (qualified or lost)
        date_closed = ""
        if stage_id in ['STAGE02', 'STAGE07']:
            if date_open:
                base_date = datetime.strptime(date_open, "%Y-%m-%d")
            else:
                base_date = date_created
            date_closed = (base_date + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")

        lead = {
            'lead_id': f'LEAD{i:04d}',
            'name': f"{random.choice(LEAD_TITLES)} - {company_name or contact_name}",
            'type': 'lead',
            'partner_name': company_name or "",
            'contact_name': contact_name,
            'email_from': generate_email(contact_name, company_name),
            'phone': generate_phone(),
            'street': generate_address() if random.random() > 0.3 else "",
            'city': random.choice(CITIES) if random.random() > 0.5 else "",
            'assigned_to': random.choice(telesales)['login'],
            'team': random.choice(telesales)['sales_team'],
            'stage_id': stage_id,
            'priority': priority,
            'source_id': source,
            'tag_ids': tags,
            'description': f"Lead generated from {source}. Industry: {random.choice(INDUSTRIES)}",
            'date_created': date_created.strftime("%Y-%m-%d"),
            'date_open': date_open,
            'date_closed': date_closed,
        }

        leads.append(lead)

    print(f"  ✓ Generated {len(leads)} leads")

    # Stats
    stage_dist = defaultdict(int)
    source_dist = defaultdict(int)
    priority_dist = defaultdict(int)

    for lead in leads:
        stage_dist[lead['stage_id']] += 1
        source_dist[lead['source_id']] += 1
        priority_dist[lead['priority']] += 1

    print(f"    - By stage:")
    for stage_id, count in sorted(stage_dist.items()):
        stage_name = next((s['name'] for s in CRM_STAGES if s['stage_id'] == stage_id), stage_id)
        print(f"      • {stage_name}: {count}")

    print(f"    - By source:")
    for src_id, count in sorted(source_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
        src_name = next((s['name'] for s in LEAD_SOURCES if s['source_id'] == src_id), src_id)
        print(f"      • {src_name}: {count}")

    return leads

# ============================================================================
# OPPORTUNITY GENERATION
# ============================================================================

def generate_opportunities(staff_list, customer_list, count=TARGET_OPPORTUNITIES):
    """Generate opportunities assigned to sales executives"""
    print(f"Generating {count} opportunities...")
    opportunities = []

    # Get sales executives
    sales_execs = [s for s in staff_list if s['user_type'] == 'Sales']
    if not sales_execs:
        print("  ⚠️  No sales executives found! Using all staff.")
        sales_execs = staff_list

    # Opportunity stage distribution (realistic pipeline)
    # 25% New, 20% Qualified, 15% Meeting, 20% Proposal, 10% Negotiation, 5% Won, 5% Lost
    stage_weights = {
        'STAGE01': 0.25,
        'STAGE02': 0.20,
        'STAGE03': 0.15,
        'STAGE04': 0.20,
        'STAGE05': 0.10,
        'STAGE06': 0.05,
        'STAGE07': 0.05
    }

    stages = []
    for stage_id, weight in stage_weights.items():
        stages.extend([stage_id] * int(count * weight))

    while len(stages) < count:
        stages.append('STAGE01')
    stages = stages[:count]
    random.shuffle(stages)

    for i in range(1, count + 1):
        if i % 500 == 0:
            print(f"  ... generating opportunity {i}/{count}")

        # Link to customer (always use real customers from list)
        if customer_list:
            customer = random.choice(customer_list)
            partner_name = customer['company_name']
            email = customer['email']
            phone = customer['phone']
        else:
            # Fallback if no customers loaded (shouldn't happen)
            partner_name = f"Công ty {random.choice(['TNHH', 'Cổ phần'])} Khách hàng Tiềm năng {i}"
            contact_name = generate_person_name()
            email = generate_email(contact_name)
            phone = generate_phone()

        stage_id = stages[i-1]
        priority = random.choices(['0', '1', '2', '3'], weights=[40, 35, 20, 5])[0]

        # Expected revenue based on customer type and stage
        if stage_id in ['STAGE06', 'STAGE05', 'STAGE04']:  # Advanced stages = higher value
            revenue_range = (100000000, 800000000)
        elif stage_id in ['STAGE03', 'STAGE02']:
            revenue_range = (50000000, 300000000)
        else:
            revenue_range = (10000000, 200000000)

        expected_revenue = random.randint(*revenue_range)

        # Probability from stage
        probability = next((s['probability'] for s in CRM_STAGES if s['stage_id'] == stage_id), 20)

        # Deadline (expected close date)
        date_created = datetime.now() - timedelta(days=random.randint(0, 120))
        days_to_close = random.randint(30, 90)
        deadline = (date_created + timedelta(days=days_to_close)).strftime("%Y-%m-%d")

        # Date open
        date_open = (date_created + timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d")

        # Select source
        source = random.choice([s['source_id'] for s in LEAD_SOURCES])

        # Select tags (2-4 tags)
        tag_count = random.randint(2, 4)
        tags = ','.join(random.sample([t['tag_id'] for t in CRM_TAGS], tag_count))

        # Assign to sales exec
        sales_exec = random.choice(sales_execs)

        opportunity = {
            'opportunity_id': f'OPP{i:04d}',
            'name': f"{partner_name} - {random.choice(['Software Solution', 'Services Contract', 'Product License', 'Consulting Project'])}",
            'type': 'opportunity',
            'partner_name': partner_name,
            'email_from': email,
            'phone': phone,
            'assigned_to': sales_exec['login'],
            'team': sales_exec['sales_team'],
            'stage_id': stage_id,
            'priority': priority,
            'expected_revenue': expected_revenue,
            'probability': probability,
            'date_deadline': deadline,
            'date_created': date_created.strftime("%Y-%m-%d"),
            'date_open': date_open,
            'tag_ids': tags,
            'source_id': source,
            'description': f"Opportunity for {partner_name}. Industry: {random.choice(INDUSTRIES)}. Value: {expected_revenue:,} VND"
        }

        opportunities.append(opportunity)

    print(f"  ✓ Generated {len(opportunities)} opportunities")

    # Stats
    stage_dist = defaultdict(int)
    revenue_by_stage = defaultdict(int)

    for opp in opportunities:
        stage_dist[opp['stage_id']] += 1
        revenue_by_stage[opp['stage_id']] += opp['expected_revenue']

    print(f"    - By stage:")
    for stage_id, count in sorted(stage_dist.items()):
        stage_name = next((s['name'] for s in CRM_STAGES if s['stage_id'] == stage_id), stage_id)
        revenue = revenue_by_stage[stage_id] / 1000000000
        print(f"      • {stage_name}: {count} ({revenue:.1f}B VND)")

    total_revenue = sum([o['expected_revenue'] for o in opportunities]) / 1000000000
    print(f"    - Total pipeline value: {total_revenue:.1f}B VND")

    return opportunities

# ============================================================================
# ACTIVITY GENERATION
# ============================================================================

ACTIVITY_TYPES = [
    {'type_id': 'ACT01', 'name': 'Call', 'weight': 0.30},
    {'type_id': 'ACT02', 'name': 'Email', 'weight': 0.25},
    {'type_id': 'ACT03', 'name': 'Meeting', 'weight': 0.20},
    {'type_id': 'ACT04', 'name': 'To Do', 'weight': 0.20},
    {'type_id': 'ACT05', 'name': 'Upload Document', 'weight': 0.05},
]

ACTIVITY_SUMMARIES = {
    'Call': ['Follow-up call', 'Introduction call', 'Demo call', 'Pricing discussion', 'Contract negotiation call'],
    'Email': ['Send proposal', 'Send quotation', 'Follow-up email', 'Send documentation', 'Contract review'],
    'Meeting': ['Product demo', 'Discovery meeting', 'Negotiation meeting', 'Contract signing', 'Kick-off meeting'],
    'To Do': ['Prepare proposal', 'Update CRM', 'Send contract', 'Schedule follow-up', 'Research customer'],
    'Upload Document': ['Upload contract', 'Upload proposal', 'Upload technical docs', 'Upload quotation', 'Upload presentation']
}

def generate_activities(leads, opportunities, count=TARGET_ACTIVITIES):
    """Generate activities linked to leads/opportunities"""
    print(f"Generating {count} activities...")
    activities = []

    # Combine all lead/opportunity names (use actual names instead of IDs)
    all_records = []
    for lead in leads:
        all_records.append(('lead', lead['name'], lead['assigned_to']))
    for opp in opportunities:
        all_records.append(('opportunity', opp['name'], opp['assigned_to']))

    if not all_records:
        print("  ⚠️  No leads or opportunities to link activities to!")
        return []

    # Activity type distribution
    type_choices = [t['type_id'] for t in ACTIVITY_TYPES]
    type_weights = [t['weight'] for t in ACTIVITY_TYPES]

    # Date distribution: 20% overdue, 30% this week, 40% next 2 weeks, 10% future
    today = datetime.now()

    for i in range(1, count + 1):
        if i % 500 == 0:
            print(f"  ... generating activity {i}/{count}")

        # Select related record
        rec_type, rec_id, assigned_to = random.choice(all_records)

        # Select activity type
        activity_type = random.choices(type_choices, type_weights)[0]
        type_name = next((t['name'] for t in ACTIVITY_TYPES if t['type_id'] == activity_type), 'Call')

        # Generate summary
        summary = random.choice(ACTIVITY_SUMMARIES.get(type_name, ['Follow-up']))

        # Generate deadline
        date_option = random.random()
        if date_option < 0.20:  # 20% overdue
            deadline = today - timedelta(days=random.randint(1, 14))
        elif date_option < 0.50:  # 30% this week
            deadline = today + timedelta(days=random.randint(0, 7))
        elif date_option < 0.90:  # 40% next 2 weeks
            deadline = today + timedelta(days=random.randint(8, 21))
        else:  # 10% future
            deadline = today + timedelta(days=random.randint(22, 60))

        activity = {
            'activity_id': f'ACT{i:04d}',
            'res_model': 'crm.lead',  # In Odoo, both leads and opps are crm.lead
            'res_id': rec_id,
            'res_type': rec_type,
            'activity_type_id': activity_type,
            'activity_type_name': type_name,
            'summary': summary,
            'date_deadline': deadline.strftime("%Y-%m-%d"),
            'assigned_to': assigned_to,
            'note': f"Activity for {rec_id}. Type: {type_name}",
        }

        activities.append(activity)

    print(f"  ✓ Generated {len(activities)} activities")

    # Stats
    type_dist = defaultdict(int)
    timeline_dist = {'Overdue': 0, 'This Week': 0, 'Next 2 Weeks': 0, 'Future': 0}

    for act in activities:
        type_dist[act['activity_type_name']] += 1

        act_date = datetime.strptime(act['date_deadline'], "%Y-%m-%d")
        if act_date < today:
            timeline_dist['Overdue'] += 1
        elif act_date <= today + timedelta(days=7):
            timeline_dist['This Week'] += 1
        elif act_date <= today + timedelta(days=21):
            timeline_dist['Next 2 Weeks'] += 1
        else:
            timeline_dist['Future'] += 1

    print(f"    - By type:")
    for atype, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {atype}: {count}")

    print(f"    - By timeline:")
    for timeline, count in timeline_dist.items():
        print(f"      • {timeline}: {count}")

    return activities

# ============================================================================
# PRODUCT GENERATION
# ============================================================================

PRODUCT_CATEGORIES = {
    'Software': ['CRM System', 'ERP Solution', 'Project Management Tool', 'Accounting Software', 'HR Management System'],
    'Services': ['Consulting Services', 'Implementation Services', 'Training Services', 'Support Package', 'Custom Development'],
    'Hardware': ['Server Hardware', 'Network Equipment', 'Workstation', 'Storage Device', 'Security Appliance'],
    'Subscription': ['Cloud Storage', 'SaaS License', 'API Access', 'Premium Support', 'Enterprise Plan']
}

def generate_products(count=TARGET_PRODUCTS):
    """Generate product catalog"""
    print(f"Generating {count} products...")
    products = []

    product_id = 1
    for category, product_names in PRODUCT_CATEGORIES.items():
        for product_name in product_names:
            if product_id > count:
                break

            # Price based on category
            if category == 'Software':
                price = random.randint(10000000, 100000000)
            elif category == 'Services':
                price = random.randint(5000000, 50000000)
            elif category == 'Hardware':
                price = random.randint(15000000, 80000000)
            else:  # Subscription
                price = random.randint(1000000, 20000000)

            product = {
                'product_id': f'PROD{product_id:03d}',
                'name': product_name,
                'category': category,
                'list_price': price,
                'cost_price': int(price * random.uniform(0.4, 0.7)),
                'type': random.choice(['Service', 'Product']),
                'can_be_sold': True,
                'can_be_purchased': category == 'Hardware',
                'description': f"{category} - {product_name}. Enterprise-grade solution."
            }

            products.append(product)
            product_id += 1

            if product_id > count:
                break

    # Add some additional products to reach target
    while len(products) < count:
        category = random.choice(list(PRODUCT_CATEGORIES.keys()))
        product_name = f"{category} Solution {len(products) + 1}"
        price = random.randint(5000000, 50000000)

        products.append({
            'product_id': f'PROD{len(products)+1:03d}',
            'name': product_name,
            'category': category,
            'list_price': price,
            'cost_price': int(price * 0.6),
            'type': 'Product',
            'can_be_sold': True,
            'can_be_purchased': False,
            'description': f"{category} product offering"
        })

    print(f"  ✓ Generated {len(products)} products")

    # Stats
    cat_dist = defaultdict(int)
    for prod in products:
        cat_dist[prod['category']] += 1

    print(f"    - By category:")
    for cat, count in sorted(cat_dist.items()):
        print(f"      • {cat}: {count}")

    avg_price = sum([p['list_price'] for p in products]) / len(products) / 1000000
    print(f"    - Average price: {avg_price:.1f}M VND")

    return products

# ============================================================================
# QUOTATION GENERATION
# ============================================================================

def generate_quotations(opportunities, products, count=TARGET_QUOTATIONS):
    """Generate quotations linked to opportunities"""
    print(f"Generating {count} quotations...")
    quotations = []

    # Select opportunities that should have quotations (40% of opportunities)
    # Prioritize opportunities in Proposal, Negotiation, Won stages
    opportunities_with_quotes = [
        opp for opp in opportunities
        if opp['stage_id'] in ['STAGE04', 'STAGE05', 'STAGE06']
    ]

    # Add some from earlier stages
    other_opps = [opp for opp in opportunities if opp['stage_id'] not in ['STAGE04', 'STAGE05', 'STAGE06']]
    opportunities_with_quotes.extend(random.sample(other_opps, min(len(other_opps), count // 3)))

    # Limit to count
    opportunities_with_quotes = opportunities_with_quotes[:count]

    for i, opp in enumerate(opportunities_with_quotes, 1):
        if i % 200 == 0:
            print(f"  ... generating quotation {i}/{count}")

        # Quote date (after opportunity creation)
        opp_created = datetime.strptime(opp['date_created'], "%Y-%m-%d")
        quote_date = opp_created + timedelta(days=random.randint(7, 45))

        # Validity date (2-4 weeks from quote date)
        validity_date = quote_date + timedelta(days=random.randint(14, 28))

        # State based on opportunity stage
        if opp['stage_id'] == 'STAGE06':  # Won
            state = 'sale'  # Confirmed sales order
        elif opp['stage_id'] == 'STAGE07':  # Lost
            state = random.choice(['cancel', 'draft'])
        elif opp['stage_id'] in ['STAGE04', 'STAGE05']:  # Proposal/Negotiation
            state = random.choice(['sent', 'draft'])
        else:
            state = 'draft'

        # Select 1-5 products for quote lines
        num_products = random.randint(1, 5)
        selected_products = random.sample(products, min(num_products, len(products)))

        # Calculate total
        total_amount = 0
        quote_lines = []
        for j, product in enumerate(selected_products, 1):
            quantity = random.randint(1, 10)
            unit_price = product['list_price']
            # Apply discount 0-20%
            discount = random.choice([0, 0, 0, 5, 10, 15, 20])
            subtotal = quantity * unit_price * (1 - discount/100)
            total_amount += subtotal

            quote_lines.append({
                'line_id': f'QL{i:04d}_{j:02d}',
                'product_id': product['name'],  # Use actual product name instead of ID
                'product_name': product['name'],
                'quantity': quantity,
                'unit_price': unit_price,
                'discount': discount,
                'subtotal': int(subtotal)
            })

        quotation = {
            'quotation_id': f'QUOT{i:04d}',
            'name': f'Q-{quote_date.strftime("%Y%m")}-{i:04d}',
            'opportunity_id': opp['name'],  # Use actual opportunity name instead of ID
            'partner_name': opp['partner_name'],
            'assigned_to': opp['assigned_to'],
            'team': opp['team'],
            'date_order': quote_date.strftime("%Y-%m-%d"),
            'validity_date': validity_date.strftime("%Y-%m-%d"),
            'amount_total': int(total_amount),
            'state': state,
            'num_lines': len(quote_lines),
            'quote_lines': quote_lines,
            'notes': f"Quotation for {opp['partner_name']}"
        }

        quotations.append(quotation)

    print(f"  ✓ Generated {len(quotations)} quotations")

    # Stats
    state_dist = defaultdict(int)
    for quot in quotations:
        state_dist[quot['state']] += 1

    print(f"    - By state:")
    for state, count in sorted(state_dist.items()):
        print(f"      • {state}: {count}")

    total_value = sum([q['amount_total'] for q in quotations]) / 1000000000
    print(f"    - Total quotation value: {total_value:.1f}B VND")

    return quotations

# ============================================================================
# FILE WRITING
# ============================================================================

def write_csv(filename, data, fieldnames):
    """Write data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"  ✓ Written {len(data)} records to {filename}")

# ============================================================================
# LOAD STAFF AND CUSTOMERS
# ============================================================================

def load_staff():
    """Load staff from enterprise CSV"""
    print("Loading staff data...")
    staff = []
    try:
        with open('staff_sprint1_enterprise.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            staff = list(reader)
        print(f"  ✓ Loaded {len(staff)} staff members")
    except FileNotFoundError:
        print("  ⚠️  staff_sprint1_enterprise.csv not found! Generate it first.")
    return staff

def load_customers():
    """Load customers from enterprise CSV"""
    print("Loading customer data...")
    customers = []
    try:
        with open('customers_sprint1_enterprise.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            customers = list(reader)
        print(f"  ✓ Loaded {len(customers)} customers")
    except FileNotFoundError:
        print("  ⚠️  customers_sprint1_enterprise.csv not found! Generate it first.")
    return customers

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("STARTING CRM DATA GENERATION")
    print("=" * 80 + "\n")

    # Load prerequisite data
    staff = load_staff()
    customers = load_customers()

    if not staff:
        print("\n❌ Cannot proceed without staff data!")
        print("Please run: python3 generate_enterprise_demo_data.py first")
        return

    # Generate CRM data
    print("\n" + "=" * 80)
    print("GENERATING CRM DATA")
    print("=" * 80 + "\n")

    leads = generate_leads(staff, TARGET_LEADS)
    opportunities = generate_opportunities(staff, customers, TARGET_OPPORTUNITIES)
    activities = generate_activities(leads, opportunities, TARGET_ACTIVITIES)
    products = generate_products(TARGET_PRODUCTS)
    quotations = generate_quotations(opportunities, products, TARGET_QUOTATIONS)

    print("\n" + "=" * 80)
    print("WRITING CSV FILES")
    print("=" * 80 + "\n")

    # Write stages
    write_csv('crm_stages.csv', CRM_STAGES,
              ['stage_id', 'name', 'sequence', 'probability', 'fold', 'is_won'])

    # Write sources
    write_csv('crm_sources.csv', LEAD_SOURCES,
              ['source_id', 'name', 'weight'])

    # Write tags
    write_csv('crm_tags.csv', CRM_TAGS,
              ['tag_id', 'name', 'category'])

    # Write leads
    lead_fields = [
        'lead_id', 'name', 'type', 'partner_name', 'contact_name', 'email_from',
        'phone', 'street', 'city', 'assigned_to', 'team', 'stage_id', 'priority',
        'source_id', 'tag_ids', 'description', 'date_created', 'date_open', 'date_closed'
    ]
    write_csv('leads_demo.csv', leads, lead_fields)

    # Write opportunities
    opp_fields = [
        'opportunity_id', 'name', 'type', 'partner_name', 'email_from', 'phone',
        'assigned_to', 'team', 'stage_id', 'priority', 'expected_revenue', 'probability',
        'date_deadline', 'date_created', 'date_open', 'tag_ids', 'source_id', 'description'
    ]
    write_csv('opportunities_demo.csv', opportunities, opp_fields)

    # Write activities
    activity_fields = [
        'activity_id', 'res_model', 'res_id', 'res_type', 'activity_type_id',
        'activity_type_name', 'summary', 'date_deadline', 'assigned_to', 'note'
    ]
    write_csv('activities_demo.csv', activities, activity_fields)

    # Write products
    product_fields = [
        'product_id', 'name', 'category', 'list_price', 'cost_price', 'type',
        'can_be_sold', 'can_be_purchased', 'description'
    ]
    write_csv('products_demo.csv', products, product_fields)

    # Write quotations (main records)
    quotation_fields = [
        'quotation_id', 'name', 'opportunity_id', 'partner_name', 'assigned_to',
        'team', 'date_order', 'validity_date', 'amount_total', 'state', 'num_lines', 'notes'
    ]
    write_csv('quotations_demo.csv', quotations, quotation_fields)

    # Write quotation lines (separate file)
    all_quote_lines = []
    for quot in quotations:
        for line in quot['quote_lines']:
            line['quotation_id'] = quot['quotation_id']
            all_quote_lines.append(line)

    quote_line_fields = [
        'quotation_id', 'line_id', 'product_id', 'product_name', 'quantity',
        'unit_price', 'discount', 'subtotal'
    ]
    write_csv('quotation_lines_demo.csv', all_quote_lines, quote_line_fields)

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE - SUMMARY")
    print("=" * 80 + "\n")

    print(f"📊 CRM DATA GENERATED:")
    print(f"  • Stages: {len(CRM_STAGES)}")
    print(f"  • Sources: {len(LEAD_SOURCES)}")
    print(f"  • Tags: {len(CRM_TAGS)}")
    print(f"  • Leads: {len(leads)}")
    print(f"  • Opportunities: {len(opportunities)}")
    print(f"  • Activities: {len(activities)}")
    print(f"  • Products: {len(products)}")
    print(f"  • Quotations: {len(quotations)}")
    print(f"  • Quotation Lines: {len(all_quote_lines)}")

    print("\n" + "=" * 80)
    print("✅ All CRM demo data files generated successfully!")
    print("=" * 80 + "\n")

    print("📁 Generated files:")
    print("  • crm_stages.csv")
    print("  • crm_sources.csv")
    print("  • crm_tags.csv")
    print("  • leads_demo.csv")
    print("  • opportunities_demo.csv")
    print("  • activities_demo.csv")
    print("  • products_demo.csv")
    print("  • quotations_demo.csv")
    print("  • quotation_lines_demo.csv")

    print("\nNext steps:")
    print("  1. Review the generated CSV files")
    print("  2. Run the import scripts to populate Odoo CRM")
    print("  3. Verify all data and relationships")

if __name__ == "__main__":
    main()
