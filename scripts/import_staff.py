#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import staff from CSV as Odoo users
Creates res.users records with proper groups and permissions

Usage: python3 import_staff.py
"""

import xmlrpc.client
import csv
import sys
from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    STAFF_CSV, DEFAULT_USER_PASSWORD, USER_GROUPS
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
        print(f"  ⚠️  Warning: Could not find group {group_xmlid}")
        return None


def import_staff(uid, models):
    """Import staff from CSV as users"""
    print(f"\n📄 Reading staff data from: {STAFF_CSV}")

    # Get group IDs
    base_user_group = get_group_id(uid, models, USER_GROUPS['base'])
    sales_group = get_group_id(uid, models, USER_GROUPS['sales'])
    sales_manager_group = get_group_id(uid, models, USER_GROUPS['sales_manager'])

    groups = [base_user_group, sales_group]

    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }

    try:
        with open(STAFF_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = 0

            for row in reader:
                total += 1
                try:
                    # Check if user exists
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.users', 'search',
                        [[['login', '=', row['login']]]]
                    )

                    # Determine groups based on job title
                    user_groups = list(groups)
                    if row.get('job_title') in ['Sales Manager', 'Sales Director']:
                        if sales_manager_group:
                            user_groups.append(sales_manager_group)

                    # Filter out None values
                    user_groups = [g for g in user_groups if g]

                    user_data = {
                        'name': row['name'],
                        'login': row['login'],
                        'email': row['email'],
                        'phone': row.get('phone', ''),
                        'groups_id': [(6, 0, user_groups)]
                    }

                    if existing_ids:
                        # Update existing user
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.users', 'write',
                            [existing_ids, user_data]
                        )
                        stats['updated'] += 1
                        print(f"  ↻ Updated: {row['name']} ({row['login']})")
                    else:
                        # Create new user
                        user_data['password'] = DEFAULT_USER_PASSWORD

                        user_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.users', 'create',
                            [user_data]
                        )
                        stats['created'] += 1
                        print(f"  ✓ Created: {row['name']} ({row['login']})")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error with {row.get('name', 'unknown')}: {e}")

            print(f"\n📊 Processed {total} staff records")

    except FileNotFoundError:
        print(f"❌ Error: File not found: {STAFF_CSV}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)

    return stats


def main():
    """Main execution"""
    print("=" * 70)
    print("ODOO STAFF IMPORT SCRIPT")
    print("=" * 70)

    print(f"\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    print(f"\n👥 Importing staff as users...")
    stats = import_staff(uid, models)

    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"\n✓ Created: {stats['created']} users")
    print(f"↻ Updated: {stats['updated']} users")
    print(f"⊘ Skipped: {stats['skipped']} users")
    print(f"❌ Errors: {stats['errors']} users")

    total_success = stats['created'] + stats['updated']
    print(f"\n✅ Successfully processed: {total_success} users")

    if stats['created'] > 0:
        print(f"\nℹ️  Default password for new users: {DEFAULT_USER_PASSWORD}")
        print("   Users should change their password on first login")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
