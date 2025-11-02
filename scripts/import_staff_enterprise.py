#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import enterprise staff from CSV as Odoo users (150+ users)
Supports batch processing for large datasets

Usage: python3 import_staff_enterprise.py [--csv FILENAME] [--batch-size SIZE]
"""

import xmlrpc.client
import csv
import sys
import argparse
from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    DEFAULT_USER_PASSWORD
)

# Batch size for API calls
BATCH_SIZE = 50

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
        print(f"  ⚠️  Warning: Could not find group {module}.{group_name}: {e}")
        return None


def get_team_id(uid, models, team_name):
    """Get sales team ID by name"""
    try:
        team_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.team', 'search',
            [[['name', '=', team_name]]]
        )
        return team_ids[0] if team_ids else None
    except Exception as e:
        return None


def import_staff_batch(uid, models, csv_file, batch_size=BATCH_SIZE):
    """Import staff from CSV as users with batch processing"""
    print("=" * 80)
    print("IMPORTING ENTERPRISE STAFF")
    print("=" * 80)

    print(f"\n📄 Reading staff data from: {csv_file}")

    # Get group IDs
    print("\n📦 Getting group IDs...")
    base_user_group = get_group_id(uid, models, 'base', 'group_user')
    sales_group = get_group_id(uid, models, 'sales_team', 'group_sale_salesman')
    sales_manager_group = get_group_id(uid, models, 'sales_team', 'group_sale_manager')

    print(f"   base.group_user: {base_user_group}")
    print(f"   sales_team.group_sale_salesman: {sales_group}")
    print(f"   sales_team.group_sale_manager: {sales_manager_group}")

    if not base_user_group:
        print("\n❌ Could not find base user group! Aborting.")
        return

    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'teams_assigned': 0
    }

    # Cache for team IDs
    team_cache = {}

    try:
        # Read all staff first
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            staff_records = list(reader)

        total = len(staff_records)
        print(f"\n📊 Found {total} staff members to import")
        print(f"   Batch size: {batch_size}")
        print(f"   Batches: {(total + batch_size - 1) // batch_size}\n")

        # Process in batches
        for batch_num in range(0, total, batch_size):
            batch = staff_records[batch_num:batch_num + batch_size]
            batch_end = min(batch_num + batch_size, total)

            print(f"👥 Processing batch {batch_num//batch_size + 1}: records {batch_num+1}-{batch_end}")

            for row in batch:
                try:
                    # Check if user exists
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.users', 'search',
                        [[['login', '=', row['login']]]]
                    )

                    # Determine groups based on job title
                    user_groups = [base_user_group]

                    # Add sales group for sales roles
                    if row.get('user_type') in ['Sales', 'Manager', 'Director'] and sales_group:
                        user_groups.append(sales_group)

                    # Add manager group for managers and directors
                    if row.get('job_title') in ['Sales Manager', 'Sales Director', 'Regional Director'] and sales_manager_group:
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

                    user_id = None
                    if existing_ids:
                        # Update existing user
                        user_id = existing_ids[0]
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.users', 'write',
                            [[user_id], user_data]
                        )
                        stats['updated'] += 1
                        print(f"  ✓ Updated: {row['login']:20} ({row['name']})")
                    else:
                        # Create new user
                        user_data['password'] = DEFAULT_USER_PASSWORD
                        user_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.users', 'create',
                            [user_data]
                        )
                        stats['created'] += 1
                        print(f"  + Created: {row['login']:20} ({row['name']})")

                    # Assign user to sales team if specified
                    team_name = row.get('sales_team', '').strip()
                    if team_name and user_id:
                        # Get team ID (use cache)
                        if team_name not in team_cache:
                            team_id = get_team_id(uid, models, team_name)
                            team_cache[team_name] = team_id
                        else:
                            team_id = team_cache[team_name]

                        if team_id:
                            try:
                                # Add user to team's member_ids
                                models.execute_kw(
                                    ODOO_DB, uid, ODOO_PASSWORD,
                                    'crm.team', 'write',
                                    [[team_id], {
                                        'member_ids': [(4, user_id)]
                                    }]
                                )
                                stats['teams_assigned'] += 1
                            except Exception as e:
                                print(f"    ⚠️  Could not assign to team '{team_name}': {e}")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error: {row.get('login', 'unknown')}: {e}")

            # Show batch progress
            processed = batch_end
            print(f"   Progress: {processed}/{total} ({100*processed//total}%)\n")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Print summary
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} users")
    print(f"✓ Updated:  {stats['updated']} users")
    print(f"✓ Teams Assigned: {stats['teams_assigned']} users")
    print(f"⊘ Skipped:  {stats['skipped']} users")
    print(f"❌ Errors:   {stats['errors']} users")
    print(f"\nTotal processed: {stats['created'] + stats['updated'] + stats['errors']}/{total}")

    if stats['errors'] == 0 and (stats['created'] + stats['updated']) == total:
        print("\n✅ All staff imported successfully!")
        if stats['teams_assigned'] > 0:
            print(f"✅ {stats['teams_assigned']} users assigned to their sales teams!")
    elif stats['errors'] > 0:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import enterprise staff into Odoo')
    parser.add_argument('--csv', default='../test_data/staff_sprint1_enterprise.csv',
                       help='Path to staff CSV file')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Batch size for processing (default: {BATCH_SIZE})')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    import_staff_batch(uid, models, args.csv, args.batch_size)


if __name__ == "__main__":
    main()
