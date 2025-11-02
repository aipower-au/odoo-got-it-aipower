#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import enterprise sales teams from CSV (35 teams)

Usage: python3 import_sales_teams_enterprise.py [--csv FILENAME]
"""

import xmlrpc.client
import csv
import sys
import argparse
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


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


def get_user_id(uid, models, user_name):
    """Get user ID by name"""
    try:
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['name', '=', user_name]]]
        )
        return user_ids[0] if user_ids else None
    except:
        return None


def import_sales_teams(uid, models, csv_file):
    """Import sales teams from CSV"""
    print("=" * 80)
    print("IMPORTING SALES TEAMS")
    print("=" * 80)

    print(f"\n📄 Reading teams data from: {csv_file}")

    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'leader_not_found': 0
    }

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            teams = list(reader)

        total = len(teams)
        print(f"\n📊 Found {total} sales teams to import\n")

        for row in teams:
            try:
                # Check if team exists
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.team', 'search',
                    [[['name', '=', row['team_name']]]]
                )

                # Get team leader ID
                leader_id = None
                if row.get('team_leader'):
                    leader_id = get_user_id(uid, models, row['team_leader'])
                    if not leader_id:
                        stats['leader_not_found'] += 1
                        print(f"  ⚠️  Leader not found: {row['team_leader']} for team {row['team_name']}")

                # Prepare team data
                team_data = {
                    'name': row['team_name'],
                }

                if leader_id:
                    team_data['user_id'] = leader_id

                if existing_ids:
                    # Update existing team
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.team', 'write',
                        [[existing_ids[0]], team_data]
                    )
                    stats['updated'] += 1
                    print(f"  ✓ Updated: {row['team_name']:40} (Leader: {row.get('team_leader', 'N/A')[:20]})")
                else:
                    # Create new team
                    team_id = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.team', 'create',
                        [team_data]
                    )
                    stats['created'] += 1
                    print(f"  + Created: {row['team_name']:40} (Leader: {row.get('team_leader', 'N/A')[:20]})")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ Error: {row.get('team_name', 'unknown')}: {e}")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Print summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} teams")
    print(f"✓ Updated:  {stats['updated']} teams")
    print(f"❌ Errors:   {stats['errors']} teams")
    print(f"⚠️  Leader not found: {stats['leader_not_found']} teams")
    print(f"\nTotal processed: {stats['created'] + stats['updated'] + stats['errors']}/{total}")

    if stats['errors'] == 0:
        print("\n✅ All sales teams imported successfully!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import enterprise sales teams into Odoo')
    parser.add_argument('--csv', default='../test_data/sales_teams_sprint1_enterprise.csv',
                       help='Path to sales teams CSV file')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    import_sales_teams(uid, models, args.csv)


if __name__ == "__main__":
    main()
