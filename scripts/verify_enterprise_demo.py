#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Enterprise CRM Demo Data
Checks all imported data and provides detailed statistics

Usage: python3 verify_enterprise_demo.py
"""

import xmlrpc.client
import sys
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


def connect_odoo():
    """Connect to Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            raise Exception("Authentication failed")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)


def count_records(uid, models, model, domain=[]):
    """Count records in a model"""
    try:
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search_count', [domain]
        )
    except:
        return 0


def verify_staff(uid, models):
    """Verify staff/users"""
    print("\n👥 STAFF VERIFICATION")
    print("─" * 80)

    # Total users (excluding admin/public)
    total = count_records(uid, models, 'res.users', [['id', '>', 2]])
    print(f"   Total staff: {total}")

    # Expected: 150
    if total >= 150:
        print("   ✅ Staff count looks good (expected ~150)")
    elif total > 0:
        print(f"   ⚠️  Staff count lower than expected ({total} vs 150)")
    else:
        print("   ❌ No staff found!")

    # Check groups
    sales_users = count_records(uid, models, 'res.users', [['groups_id', 'in', [get_group_id_by_name(uid, models, 'Sales / User')]]])
    print(f"   Sales users: {sales_users}")

    return total


def verify_customers(uid, models):
    """Verify customers"""
    print("\n🏢 CUSTOMER VERIFICATION")
    print("─" * 80)

    # Get user partner IDs to exclude
    users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search_read',
        [[]], {'fields': ['partner_id']}
    )
    user_partner_ids = [u['partner_id'][0] for u in users if u.get('partner_id')]

    total = count_records(uid, models, 'res.partner', [['id', 'not in', user_partner_ids]])
    print(f"   Total customers: {total}")

    # Expected: 3000
    if total >= 3000:
        print("   ✅ Customer count looks good (expected ~3000)")
    elif total > 0:
        print(f"   ⚠️  Customer count lower than expected ({total} vs 3000)")
    else:
        print("   ❌ No customers found!")

    # By customer rank
    customers = count_records(uid, models, 'res.partner', [['customer_rank', '>', 0]])
    print(f"   Marked as customers: {customers}")

    return total


def verify_sales_teams(uid, models):
    """Verify sales teams"""
    print("\n👔 SALES TEAMS VERIFICATION")
    print("─" * 80)

    total = count_records(uid, models, 'crm.team')
    print(f"   Total teams: {total}")

    # Expected: 32-35
    if total >= 30:
        print("   ✅ Teams count looks good (expected ~35)")
    elif total > 0:
        print(f"   ⚠️  Teams count lower than expected ({total} vs 35)")
    else:
        print("   ❌ No teams found!")

    return total


def verify_crm_foundation(uid, models):
    """Verify CRM foundation"""
    print("\n📊 CRM FOUNDATION VERIFICATION")
    print("─" * 80)

    stages = count_records(uid, models, 'crm.stage')
    sources = count_records(uid, models, 'utm.source')
    tags = count_records(uid, models, 'crm.tag')

    print(f"   Stages: {stages} (expected 7+)")
    print(f"   Sources: {sources} (expected 9+)")
    print(f"   Tags: {tags} (expected 24+)")

    if stages >= 7 and sources >= 9 and tags >= 24:
        print("   ✅ CRM foundation looks good")
    else:
        print("   ⚠️  Some CRM foundation data may be missing")

    return stages + sources + tags


def verify_products(uid, models):
    """Verify products"""
    print("\n📦 PRODUCTS VERIFICATION")
    print("─" * 80)

    total = count_records(uid, models, 'product.product')
    print(f"   Total products: {total}")

    # Saleable products
    saleable = count_records(uid, models, 'product.product', [['sale_ok', '=', True]])
    print(f"   Saleable products: {saleable}")

    # Expected: 50+
    if saleable >= 50:
        print("   ✅ Products count looks good (expected ~50)")
    elif saleable > 0:
        print(f"   ⚠️  Products count lower than expected ({saleable} vs 50)")
    else:
        print("   ⚠️  No custom products found (may be using defaults)")

    return saleable


def verify_leads(uid, models):
    """Verify leads"""
    print("\n🎯 LEADS VERIFICATION")
    print("─" * 80)

    # Leads (type='lead')
    leads = count_records(uid, models, 'crm.lead', [['type', '=', 'lead']])
    print(f"   Total leads: {leads}")

    # Expected: ~2000
    if leads >= 1800:
        print("   ✅ Leads count looks good (expected ~2000)")
    elif leads > 0:
        print(f"   ⚠️  Leads count lower than expected ({leads} vs 2000)")
    else:
        print("   ❌ No leads found!")

    return leads


def verify_opportunities(uid, models):
    """Verify opportunities"""
    print("\n💼 OPPORTUNITIES VERIFICATION")
    print("─" * 80)

    # Opportunities (type='opportunity')
    opps = count_records(uid, models, 'crm.lead', [['type', '=', 'opportunity']])
    print(f"   Total opportunities: {opps}")

    # Expected: ~1500
    if opps >= 1400:
        print("   ✅ Opportunities count looks good (expected ~1500)")
    elif opps > 0:
        print(f"   ⚠️  Opportunities count lower than expected ({opps} vs 1500)")
    else:
        print("   ❌ No opportunities found!")

    # By stage
    if opps > 0:
        stages = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.stage', 'search_read',
            [[]], {'fields': ['name'], 'limit': 10}
        )
        print("\n   Distribution by stage:")
        for stage in stages[:5]:  # Show first 5 stages
            count = count_records(uid, models, 'crm.lead', [['type', '=', 'opportunity'], ['stage_id', '=', stage['id']]])
            print(f"     • {stage['name']:20}: {count}")

    return opps


def verify_quotations(uid, models):
    """Verify quotations"""
    print("\n📋 QUOTATIONS VERIFICATION")
    print("─" * 80)

    total = count_records(uid, models, 'sale.order')
    print(f"   Total quotations: {total}")

    # Expected: ~600
    if total >= 500:
        print("   ✅ Quotations count looks good (expected ~600)")
    elif total > 0:
        print(f"   ⚠️  Quotations count lower than expected ({total} vs 600)")
    else:
        print("   ⚠️  No quotations found")

    # By state
    if total > 0:
        draft = count_records(uid, models, 'sale.order', [['state', '=', 'draft']])
        sent = count_records(uid, models, 'sale.order', [['state', '=', 'sent']])
        sale = count_records(uid, models, 'sale.order', [['state', '=', 'sale']])

        print(f"\n   By state:")
        print(f"     • Draft: {draft}")
        print(f"     • Sent: {sent}")
        print(f"     • Confirmed (Sale): {sale}")

    return total


def verify_activities(uid, models):
    """Verify activities"""
    print("\n📅 ACTIVITIES VERIFICATION")
    print("─" * 80)

    total = count_records(uid, models, 'mail.activity')
    print(f"   Total activities: {total}")

    # Expected: ~3000
    if total >= 2500:
        print("   ✅ Activities count looks good (expected ~3000)")
    elif total > 0:
        print(f"   ⚠️  Activities count lower than expected ({total} vs 3000)")
    else:
        print("   ⚠️  No activities found")

    return total


def get_group_id_by_name(uid, models, name):
    """Helper to get group ID by name"""
    try:
        group_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.groups', 'search',
            [[['full_name', 'ilike', name]]]
        )
        return group_ids[0] if group_ids else None
    except:
        return None


def print_summary(counts):
    """Print overall summary"""
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    print("\n📊 Data Overview:")
    print(f"   ✓ Staff: {counts['staff']}")
    print(f"   ✓ Customers: {counts['customers']}")
    print(f"   ✓ Sales Teams: {counts['teams']}")
    print(f"   ✓ CRM Foundation: {counts['foundation']} items")
    print(f"   ✓ Products: {counts['products']}")
    print(f"   ✓ Leads: {counts['leads']}")
    print(f"   ✓ Opportunities: {counts['opportunities']}")
    print(f"   ✓ Quotations: {counts['quotations']}")
    print(f"   ✓ Activities: {counts['activities']}")

    total = sum(counts.values())
    print(f"\n   Total records: {total:,}")

    # Check if core data is present
    if counts['staff'] >= 100 and counts['customers'] >= 2000:
        print("\n✅ Enterprise CRM demo data verification PASSED!")
    elif counts['staff'] > 0 and counts['customers'] > 0:
        print("\n⚠️  Data verification PARTIAL - some data may be missing")
    else:
        print("\n❌ Data verification FAILED - core data is missing")

    print("=" * 80)


def main():
    """Main execution"""
    print("=" * 80)
    print("ENTERPRISE CRM DEMO DATA VERIFICATION")
    print("=" * 80)

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Verify each component
    counts = {
        'staff': verify_staff(uid, models),
        'customers': verify_customers(uid, models),
        'teams': verify_sales_teams(uid, models),
        'foundation': verify_crm_foundation(uid, models),
        'products': verify_products(uid, models),
        'leads': verify_leads(uid, models),
        'opportunities': verify_opportunities(uid, models),
        'quotations': verify_quotations(uid, models),
        'activities': verify_activities(uid, models),
    }

    # Print summary
    print_summary(counts)


if __name__ == "__main__":
    main()
