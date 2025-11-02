#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assign Users to Sales Teams
Reads staff CSV and assigns each user to their designated sales team

Usage: python3 assign_users_to_teams.py [--csv FILENAME]
"""

import xmlrpc.client
import csv
import sys
import argparse
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


def get_user_id(uid, models, login):
    """Get user ID by login"""
    try:
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['login', '=', login]]]
        )
        return user_ids[0] if user_ids else None
    except Exception as e:
        return None


def assign_users_to_teams(uid, models, csv_file):
    """Assign users to their sales teams based on CSV data"""
    print("=" * 80)
    print("ASSIGNING USERS TO SALES TEAMS")
    print("=" * 80)

    print(f"\n📄 Reading staff data from: {csv_file}")

    # Cache for team IDs
    team_cache = {}

    stats = {
        'assigned': 0,
        'skipped': 0,
        'user_not_found': 0,
        'team_not_found': 0,
        'errors': 0
    }

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            staff_records = list(reader)

        total = len(staff_records)
        print(f"📊 Found {total} staff members\n")

        for idx, row in enumerate(staff_records, 1):
            login = row['login']
            team_name = row.get('sales_team', '').strip()
            name = row['name']

            # Skip if no team assigned
            if not team_name:
                stats['skipped'] += 1
                continue

            try:
                # Get user ID
                user_id = get_user_id(uid, models, login)
                if not user_id:
                    print(f"  ⚠️  User not found: {login:15} ({name})")
                    stats['user_not_found'] += 1
                    continue

                # Get team ID (use cache)
                if team_name not in team_cache:
                    team_id = get_team_id(uid, models, team_name)
                    team_cache[team_name] = team_id
                else:
                    team_id = team_cache[team_name]

                if not team_id:
                    print(f"  ⚠️  Team not found: {team_name} for {login}")
                    stats['team_not_found'] += 1
                    continue

                # Assign user to team
                # Add user to team's member_ids
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.team', 'write',
                    [[team_id], {
                        'member_ids': [(4, user_id)]  # (4, id) means add to many2many
                    }]
                )

                stats['assigned'] += 1
                print(f"  ✓ Assigned: {login:15} ({name:25}) → {team_name}")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ Error: {login}: {e}")

            # Show progress every 25 records
            if idx % 25 == 0:
                print(f"   Progress: {idx}/{total} ({100*idx//total}%)")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Print summary
    print("\n" + "=" * 80)
    print("ASSIGNMENT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Assigned:         {stats['assigned']} users")
    print(f"⊘ Skipped (no team): {stats['skipped']} users")
    print(f"⚠️  User not found:   {stats['user_not_found']} users")
    print(f"⚠️  Team not found:   {stats['team_not_found']} teams")
    print(f"❌ Errors:           {stats['errors']} users")

    if stats['errors'] == 0 and stats['assigned'] > 0:
        print(f"\n✅ Successfully assigned {stats['assigned']} users to their teams!")
    elif stats['errors'] > 0:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Assign users to sales teams')
    parser.add_argument('--csv', default='../test_data/staff_sprint1_enterprise.csv',
                       help='Path to staff CSV file')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    assign_users_to_teams(uid, models, args.csv)


if __name__ == "__main__":
    main()
