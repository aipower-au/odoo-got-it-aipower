#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import sales teams from CSV
Creates crm.team records with team leaders and members

Usage: python3 import_sales_teams.py
"""

import xmlrpc.client
import csv
import sys
from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    SALES_TEAMS_CSV
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


def import_sales_teams(uid, models):
    """Import sales teams from CSV"""
    print(f"\n📄 Reading sales teams data from: {SALES_TEAMS_CSV}")

    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }

    try:
        with open(SALES_TEAMS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = 0

            for row in reader:
                total += 1
                try:
                    team_name = row['team_name']

                    # Check if team exists
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.team', 'search',
                        [[['name', '=', team_name]]]
                    )

                    # Find team leader
                    leader_id = find_user_by_name(uid, models, row['team_leader'])
                    if not leader_id:
                        print(f"  ⚠️  Warning: Team leader '{row['team_leader']}' not found for team '{team_name}'")

                    # Find team members
                    member_names = [m.strip() for m in row['team_members'].split(',')]
                    member_ids = []

                    for member_name in member_names:
                        member_id = find_user_by_name(uid, models, member_name)
                        if member_id:
                            member_ids.append(member_id)
                        else:
                            print(f"  ⚠️  Warning: Member '{member_name}' not found for team '{team_name}'")

                    # Prepare team data
                    team_data = {
                        'name': team_name,
                        'user_id': leader_id if leader_id else False,
                    }

                    # Add members (many2many field)
                    if member_ids:
                        team_data['member_ids'] = [(6, 0, member_ids)]

                    if existing_ids:
                        # Update existing team
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.team', 'write',
                            [existing_ids, team_data]
                        )
                        stats['updated'] += 1
                        print(f"  ↻ Updated: {team_name} ({len(member_ids)} members)")
                    else:
                        # Create new team
                        team_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.team', 'create',
                            [team_data]
                        )
                        stats['created'] += 1
                        print(f"  ✓ Created: {team_name} ({len(member_ids)} members)")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error with {row.get('team_name', 'unknown')}: {e}")

            print(f"\n📊 Processed {total} sales teams")

    except FileNotFoundError:
        print(f"❌ Error: File not found: {SALES_TEAMS_CSV}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)

    return stats


def main():
    """Main execution"""
    print("=" * 70)
    print("ODOO SALES TEAMS IMPORT SCRIPT")
    print("=" * 70)

    print(f"\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    print(f"\n👥 Importing sales teams...")
    stats = import_sales_teams(uid, models)

    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"\n✓ Created: {stats['created']} teams")
    print(f"↻ Updated: {stats['updated']} teams")
    print(f"⊘ Skipped: {stats['skipped']} teams")
    print(f"❌ Errors: {stats['errors']} teams")

    total_success = stats['created'] + stats['updated']
    print(f"\n✅ Successfully processed: {total_success} teams")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
