#!/usr/bin/env python3
"""
Fix user groups for imported staff
Assigns proper Sales and Sales Manager groups to users
"""

import xmlrpc.client
import csv
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, STAFF_CSV

def connect_odoo():
    """Connect to Odoo"""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def get_group_id(uid, models, module, group_name):
    """Get group ID using ir.model.data search"""
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
    except Exception as e:
        print(f"  ⚠️  Error getting group {module}.{group_name}: {e}")
        return None

def main():
    print("=" * 70)
    print("FIXING USER GROUPS")
    print("=" * 70)

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Get group IDs
    print("\n📦 Getting group IDs...")
    base_user_group = get_group_id(uid, models, 'base', 'group_user')
    sales_group = get_group_id(uid, models, 'sales_team', 'group_sale_salesman')
    sales_manager_group = get_group_id(uid, models, 'sales_team', 'group_sale_manager')

    print(f"   base.group_user: {base_user_group}")
    print(f"   sales_team.group_sale_salesman: {sales_group}")
    print(f"   sales_team.group_sale_manager: {sales_manager_group}")

    if not all([base_user_group, sales_group, sales_manager_group]):
        print("\n❌ Could not find all required groups!")
        return

    # Read staff CSV to know job titles
    print(f"\n📄 Reading staff data from: {STAFF_CSV}")

    staff_data = {}
    with open(STAFF_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            staff_data[row['login']] = row['job_title']

    # Get all users
    print("\n👥 Updating user groups...")

    stats = {'updated': 0, 'skipped': 0, 'errors': 0}

    for login, job_title in staff_data.items():
        try:
            # Find user
            user_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'search',
                [[['login', '=', login]]]
            )

            if not user_ids:
                print(f"  ⊘ User not found: {login}")
                stats['skipped'] += 1
                continue

            user_id = user_ids[0]

            # Determine which groups to assign
            groups = [base_user_group, sales_group]

            if job_title in ['Sales Manager', 'Sales Director']:
                groups.append(sales_manager_group)

            # Update user groups (replace existing groups)
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'write',
                [[user_id], {'groups_id': [(6, 0, groups)]}]
            )

            stats['updated'] += 1
            title_short = job_title[:20]
            print(f"  ✓ {login:15} - {title_short:20} - {len(groups)} groups")

        except Exception as e:
            stats['errors'] += 1
            print(f"  ❌ Error updating {login}: {e}")

    print("\n" + "=" * 70)
    print("UPDATE SUMMARY")
    print("=" * 70)
    print(f"\n✓ Updated: {stats['updated']} users")
    print(f"⊘ Skipped: {stats['skipped']} users")
    print(f"❌ Errors: {stats['errors']} users")

    print("\n✅ User groups updated successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
