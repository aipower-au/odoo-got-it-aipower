#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master import script for Sprint 1 test data
Imports staff, sales teams, and customers in the correct order

Usage: python3 import_all_sprint1.py
"""

import xmlrpc.client
import csv
import sys
import time
from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    STAFF_CSV, SALES_TEAMS_CSV, CUSTOMERS_CSV,
    DEFAULT_USER_PASSWORD, USER_GROUPS
)


def connect_odoo():
    """Connect to Odoo and return connection objects"""
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


def get_group_id(uid, models, group_xmlid):
    """Get group ID from XML ID"""
    try:
        group_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'xmlid_to_res_id',
            [group_xmlid]
        )
        return group_id
    except:
        return None


def find_user_by_name(uid, models, name):
    """Find user ID by name"""
    try:
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['name', '=', name]]]
        )
        return user_ids[0] if user_ids else None
    except:
        return None


def find_country_id(uid, models, country_code='VN'):
    """Find country ID by code"""
    try:
        country_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.country', 'search',
            [[['code', '=', country_code]]]
        )
        return country_ids[0] if country_ids else None
    except:
        return None


def import_staff(uid, models):
    """Import staff from CSV as users"""
    print("\n" + "=" * 70)
    print("STEP 1: IMPORTING STAFF")
    print("=" * 70)
    print(f"\n📄 Reading: {STAFF_CSV}")

    # Get group IDs
    base_user_group = get_group_id(uid, models, USER_GROUPS['base'])
    sales_group = get_group_id(uid, models, USER_GROUPS['sales'])
    sales_manager_group = get_group_id(uid, models, USER_GROUPS['sales_manager'])

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    with open(STAFF_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.users', 'search',
                    [[['login', '=', row['login']]]]
                )

                # Determine groups
                user_groups = [g for g in [base_user_group, sales_group] if g]
                if row.get('job_title') in ['Sales Manager', 'Sales Director']:
                    if sales_manager_group:
                        user_groups.append(sales_manager_group)

                user_data = {
                    'name': row['name'],
                    'login': row['login'],
                    'email': row['email'],
                    'phone': row.get('phone', ''),
                    'groups_id': [(6, 0, user_groups)]
                }

                if existing_ids:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.users', 'write',
                        [existing_ids, user_data]
                    )
                    stats['updated'] += 1
                    print(f"  ↻ {row['name']}")
                else:
                    user_data['password'] = DEFAULT_USER_PASSWORD
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.users', 'create',
                        [user_data]
                    )
                    stats['created'] += 1
                    print(f"  ✓ {row['name']}")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ {row.get('name', 'unknown')}: {e}")

    print(f"\n✅ Staff Import: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors")
    return stats


def import_sales_teams(uid, models):
    """Import sales teams from CSV"""
    print("\n" + "=" * 70)
    print("STEP 2: IMPORTING SALES TEAMS")
    print("=" * 70)
    print(f"\n📄 Reading: {SALES_TEAMS_CSV}")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    with open(SALES_TEAMS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                team_name = row['team_name']

                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.team', 'search',
                    [[['name', '=', team_name]]]
                )

                # Find team leader
                leader_id = find_user_by_name(uid, models, row['team_leader'])

                # Find team members
                member_names = [m.strip() for m in row['team_members'].split(',')]
                member_ids = []
                for member_name in member_names:
                    member_id = find_user_by_name(uid, models, member_name)
                    if member_id:
                        member_ids.append(member_id)

                team_data = {
                    'name': team_name,
                    'user_id': leader_id if leader_id else False,
                }

                if member_ids:
                    team_data['member_ids'] = [(6, 0, member_ids)]

                if existing_ids:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.team', 'write',
                        [existing_ids, team_data]
                    )
                    stats['updated'] += 1
                    print(f"  ↻ {team_name} ({len(member_ids)} members)")
                else:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.team', 'create',
                        [team_data]
                    )
                    stats['created'] += 1
                    print(f"  ✓ {team_name} ({len(member_ids)} members)")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ {row.get('team_name', 'unknown')}: {e}")

    print(f"\n✅ Teams Import: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors")
    return stats


def import_customers(uid, models):
    """Import customers from CSV"""
    print("\n" + "=" * 70)
    print("STEP 3: IMPORTING CUSTOMERS")
    print("=" * 70)
    print(f"\n📄 Reading: {CUSTOMERS_CSV}")

    vietnam_id = find_country_id(uid, models, 'VN')

    stats = {'created': 0, 'updated': 0, 'errors': 0}
    count = 0

    with open(CUSTOMERS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            count += 1
            try:
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'search',
                    [[['vat', '=', row['tax_id']]]]
                )

                salesperson_id = find_user_by_name(uid, models, row['salesperson'])

                partner_data = {
                    'name': row['company_name'],
                    'ref': row.get('customer_code', ''),
                    'vat': row['tax_id'],
                    'phone': row['phone'],
                    'email': row['email'],
                    'street': row['delivery_address'],
                    'is_company': True,
                    'company_type': 'company',
                    'user_id': salesperson_id if salesperson_id else False,
                    'country_id': vietnam_id if vietnam_id else False,
                }

                if row.get('notes'):
                    partner_data['comment'] = row['notes']

                if existing_ids:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'write',
                        [existing_ids, partner_data]
                    )
                    stats['updated'] += 1
                else:
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'create',
                        [partner_data]
                    )
                    stats['created'] += 1

                if count % 20 == 0:
                    print(f"  ... {count} processed ({stats['created']} created, {stats['updated']} updated)")

            except Exception as e:
                stats['errors'] += 1
                if count % 20 == 0:
                    print(f"  ... {count} processed ({stats['errors']} errors)")

    print(f"\n✅ Customers Import: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors")
    return stats


def main():
    """Main execution"""
    start_time = time.time()

    print("=" * 70)
    print("SPRINT 1 - COMPLETE DATA IMPORT")
    print("=" * 70)

    print(f"\n🔌 Connecting to Odoo...")
    print(f"   URL: {ODOO_URL}")
    print(f"   Database: {ODOO_DB}")

    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Import in order: Staff → Teams → Customers
    all_stats = {}

    try:
        all_stats['staff'] = import_staff(uid, models)
        time.sleep(1)  # Brief pause between imports

        all_stats['teams'] = import_sales_teams(uid, models)
        time.sleep(1)

        all_stats['customers'] = import_customers(uid, models)

    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        sys.exit(1)

    # Final summary
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(f"\n👥 Staff:")
    print(f"   ✓ Created: {all_stats['staff']['created']}")
    print(f"   ↻ Updated: {all_stats['staff']['updated']}")
    print(f"   ❌ Errors: {all_stats['staff']['errors']}")

    print(f"\n🏆 Sales Teams:")
    print(f"   ✓ Created: {all_stats['teams']['created']}")
    print(f"   ↻ Updated: {all_stats['teams']['updated']}")
    print(f"   ❌ Errors: {all_stats['teams']['errors']}")

    print(f"\n🏢 Customers:")
    print(f"   ✓ Created: {all_stats['customers']['created']}")
    print(f"   ↻ Updated: {all_stats['customers']['updated']}")
    print(f"   ❌ Errors: {all_stats['customers']['errors']}")

    total_created = sum(s['created'] for s in all_stats.values())
    total_updated = sum(s['updated'] for s in all_stats.values())
    total_errors = sum(s['errors'] for s in all_stats.values())

    print(f"\n📊 TOTALS:")
    print(f"   ✓ Total Created: {total_created}")
    print(f"   ↻ Total Updated: {total_updated}")
    print(f"   ❌ Total Errors: {total_errors}")

    print(f"\n⏱️  Time elapsed: {elapsed_time:.2f} seconds")

    if total_errors == 0:
        print("\n🎉 All data imported successfully!")
    else:
        print(f"\n⚠️  Import completed with {total_errors} errors")

    if all_stats['staff']['created'] > 0:
        print(f"\nℹ️  Default password for new users: {DEFAULT_USER_PASSWORD}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
