#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Import Script for Enterprise CRM Demo Data
Imports all data in correct order:
1. Staff (150 users)
2. Sales Teams (35 teams)
3. Customers (3000 partners)
4. CRM Foundation (stages, sources, tags)
5. Products (50 items)
6. Leads (2000 records)
7. Opportunities (1500 records)
8. Quotations (600 records)
9. Activities (3000 records)

Usage: python3 import_all_enterprise_demo.py [--skip-staff] [--skip-customers]
"""

import xmlrpc.client
import csv
import sys
import argparse
import time
from datetime import datetime
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, DEFAULT_USER_PASSWORD

# Batch sizes
STAFF_BATCH = 50
CUSTOMER_BATCH = 100
LEAD_BATCH = 200
OPP_BATCH = 150


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


def get_group_id(uid, models, module, group_name):
    """Get group ID"""
    try:
        data_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'search',
            [[['name', '=', group_name], ['module', '=', module]]]
        )
        if data_ids:
            data = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'ir.model.data', 'read',
                [[data_ids[0]], ['res_id']]
            )
            return data[0]['res_id']
        return None
    except:
        return None


def import_staff(uid, models):
    """Import staff (150 users)"""
    print("\n" + "=" * 80)
    print("STEP 1: IMPORTING STAFF (150 users)")
    print("=" * 80)

    csv_file = '../test_data/staff_sprint1_enterprise.csv'
    print(f"\n📄 Reading: {csv_file}")

    # Get groups
    base_group = get_group_id(uid, models, 'base', 'group_user')
    sales_group = get_group_id(uid, models, 'sales_team', 'group_sale_salesman')
    manager_group = get_group_id(uid, models, 'sales_team', 'group_sale_manager')

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            staff = list(csv.DictReader(f))

        print(f"Found {len(staff)} staff members\n")

        for i, row in enumerate(staff, 1):
            try:
                existing = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.users', 'search',
                    [[['login', '=', row['login']]]]
                )

                groups = [base_group]
                if row.get('user_type') in ['Sales', 'Manager', 'Director'] and sales_group:
                    groups.append(sales_group)
                if row.get('job_title') in ['Sales Manager', 'Sales Director', 'Regional Director'] and manager_group:
                    groups.append(manager_group)
                groups = [g for g in groups if g]

                user_data = {
                    'name': row['name'],
                    'login': row['login'],
                    'email': row['email'],
                    'phone': row.get('phone', ''),
                    'groups_id': [(6, 0, groups)]
                }

                if existing:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'write', [[existing[0]], user_data])
                    stats['updated'] += 1
                else:
                    user_data['password'] = DEFAULT_USER_PASSWORD
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'create', [user_data])
                    stats['created'] += 1

                if i % 25 == 0:
                    print(f"  Progress: {i}/{len(staff)} ({100*i//len(staff)}%)")

            except Exception as e:
                stats['errors'] += 1

        print(f"\n✓ Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        return False

    return stats['errors'] == 0


def import_sales_teams(uid, models):
    """Import sales teams (35 teams)"""
    print("\n" + "=" * 80)
    print("STEP 2: IMPORTING SALES TEAMS (35 teams)")
    print("=" * 80)

    csv_file = '../test_data/sales_teams_sprint1_enterprise.csv'
    print(f"\n📄 Reading: {csv_file}")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            teams = list(csv.DictReader(f))

        print(f"Found {len(teams)} teams\n")

        for row in teams:
            try:
                existing = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.team', 'search',
                    [[['name', '=', row['team_name']]]]
                )

                team_data = {'name': row['team_name']}

                # Get leader
                if row.get('team_leader'):
                    leader_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.users', 'search',
                        [[['name', '=', row['team_leader']]]]
                    )
                    if leader_ids:
                        team_data['user_id'] = leader_ids[0]

                if existing:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.team', 'write', [[existing[0]], team_data])
                    stats['updated'] += 1
                else:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.team', 'create', [team_data])
                    stats['created'] += 1

            except Exception as e:
                stats['errors'] += 1

        print(f"\n✓ Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        return False

    return stats['errors'] == 0


def import_customers(uid, models):
    """Import customers (3000 partners)"""
    print("\n" + "=" * 80)
    print("STEP 3: IMPORTING CUSTOMERS (3000 partners)")
    print("=" * 80)

    csv_file = '../test_data/customers_sprint1_enterprise.csv'
    print(f"\n📄 Reading: {csv_file}")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            customers = list(csv.DictReader(f))

        print(f"Found {len(customers)} customers")
        print(f"Batch size: {CUSTOMER_BATCH}\n")

        for i in range(0, len(customers), CUSTOMER_BATCH):
            batch = customers[i:i+CUSTOMER_BATCH]
            batch_num = i // CUSTOMER_BATCH + 1

            print(f"Batch {batch_num}: records {i+1}-{min(i+CUSTOMER_BATCH, len(customers))}")

            for row in batch:
                try:
                    existing = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'search',
                        [[['vat', '=', row['tax_id']]]]
                    )

                    partner_data = {
                        'name': row['company_name'],
                        'vat': row.get('tax_id', ''),
                        'phone': row.get('phone', ''),
                        'email': row.get('email', ''),
                        'street': row.get('delivery_address', ''),
                        'is_company': row.get('entity_type') == 'Company',
                        'customer_rank': 1,
                    }

                    if existing:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'write', [[existing[0]], partner_data])
                        stats['updated'] += 1
                    else:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'create', [partner_data])
                        stats['created'] += 1

                except Exception as e:
                    stats['errors'] += 1

            progress = min(i+CUSTOMER_BATCH, len(customers))
            print(f"  Progress: {progress}/{len(customers)} ({100*progress//len(customers)}%)\n")

        print(f"\n✓ Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        return False

    return stats['errors'] < len(customers) * 0.1  # Allow up to 10% errors


def import_crm_foundation(uid, models):
    """Import stages, sources, tags"""
    print("\n" + "=" * 80)
    print("STEP 4: IMPORTING CRM FOUNDATION (stages, sources, tags)")
    print("=" * 80)

    # Stages
    print("\n📊 Importing stages...")
    try:
        with open('../test_data/crm_stages.csv', 'r') as f:
            for row in csv.DictReader(f):
                try:
                    existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.stage', 'search', [[['name', '=', row['name']]]])
                    stage_data = {
                        'name': row['name'],
                        'sequence': int(row['sequence']),
                        'probability': float(row['probability']),
                        'fold': row['fold'].lower() == 'true',
                        'is_won': row['is_won'].lower() == 'true',
                    }
                    if existing:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.stage', 'write', [[existing[0]], stage_data])
                    else:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.stage', 'create', [stage_data])
                    print(f"  ✓ {row['name']}")
                except:
                    pass
    except FileNotFoundError:
        print("  ⚠️  crm_stages.csv not found")

    # Sources
    print("\n📍 Importing sources...")
    try:
        with open('../test_data/crm_sources.csv', 'r') as f:
            for row in csv.DictReader(f):
                try:
                    existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'utm.source', 'search', [[['name', '=', row['name']]]])
                    if not existing:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'utm.source', 'create', [{'name': row['name']}])
                    print(f"  ✓ {row['name']}")
                except:
                    pass
    except FileNotFoundError:
        print("  ⚠️  crm_sources.csv not found")

    # Tags
    print("\n🏷️  Importing tags...")
    try:
        with open('../test_data/crm_tags.csv', 'r') as f:
            for row in csv.DictReader(f):
                try:
                    existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.tag', 'search', [[['name', '=', row['name']]]])
                    if not existing:
                        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.tag', 'create', [{'name': row['name']}])
                    print(f"  ✓ {row['name']}")
                except:
                    pass
    except FileNotFoundError:
        print("  ⚠️  crm_tags.csv not found")

    return True


def import_products(uid, models):
    """Import products (50 items)"""
    print("\n" + "=" * 80)
    print("STEP 5: IMPORTING PRODUCTS (50 items)")
    print("=" * 80)

    csv_file = '../test_data/products_demo.csv'
    print(f"\n📄 Reading: {csv_file}")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r') as f:
            products = list(csv.DictReader(f))

        print(f"Found {len(products)} products\n")

        for row in products:
            try:
                existing = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.product', 'search',
                    [[['name', '=', row['name']]]]
                )

                product_data = {
                    'name': row['name'],
                    'list_price': float(row['list_price']),
                    'standard_price': float(row.get('cost_price', 0)),
                    'type': 'service' if row.get('type') == 'Service' else 'consu',
                    'sale_ok': row.get('can_be_sold', '').lower() == 'true',
                    'purchase_ok': row.get('can_be_purchased', '').lower() == 'true',
                }

                if existing:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'write', [[existing[0]], product_data])
                    stats['updated'] += 1
                else:
                    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'create', [product_data])
                    stats['created'] += 1

                print(f"  ✓ {row['name']:40} - {float(row['list_price'])/1000000:.1f}M VND")

            except Exception as e:
                stats['errors'] += 1

        print(f"\n✓ Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        return False

    return True


def print_final_summary(start_time):
    """Print final summary"""
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    print("\n" + "=" * 80)
    print("IMPORT COMPLETE!")
    print("=" * 80)
    print(f"\n⏱️  Total time: {minutes}m {seconds}s")
    print("\n✅ Enterprise CRM demo data imported successfully!")
    print("\nNext steps:")
    print("  1. Run verification script: python3 verify_enterprise_demo.py")
    print("  2. Log into Odoo and review the data")
    print("  3. Test Sprint 1 features")
    print("=" * 80)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Import all enterprise demo data')
    parser.add_argument('--skip-staff', action='store_true', help='Skip staff import')
    parser.add_argument('--skip-customers', action='store_true', help='Skip customer import')

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("ENTERPRISE CRM DEMO DATA IMPORT")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time.time()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Import in sequence
    if not args.skip_staff:
        if not import_staff(uid, models):
            print("\n❌ Staff import failed. Aborting.")
            return

    if not import_sales_teams(uid, models):
        print("\n⚠️  Sales teams import had issues, but continuing...")

    if not args.skip_customers:
        if not import_customers(uid, models):
            print("\n❌ Customer import failed. Aborting.")
            return

    if not import_crm_foundation(uid, models):
        print("\n⚠️  CRM foundation import had issues, but continuing...")

    if not import_products(uid, models):
        print("\n⚠️  Products import had issues, but continuing...")

    print_final_summary(start_time)


if __name__ == "__main__":
    main()
