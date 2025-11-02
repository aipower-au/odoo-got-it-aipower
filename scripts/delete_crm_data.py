#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Delete all CRM data from Odoo database
Safely removes leads, opportunities, sales teams, and partners while preserving system users

Usage: python3 delete_crm_data.py [--no-confirm]
"""

import xmlrpc.client
import sys
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


def connect_odoo():
    """Connect to Odoo and return connection objects"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication failed. Check credentials in config.py")

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print(f"\nConnection details:")
        print(f"  URL: {ODOO_URL}")
        print(f"  Database: {ODOO_DB}")
        print(f"  Username: {ODOO_USERNAME}")
        sys.exit(1)


def delete_leads(uid, models):
    """Delete all CRM leads and opportunities"""
    print("\n📋 Deleting CRM leads...")

    try:
        lead_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search',
            [[]]
        )

        if lead_ids:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'crm.lead', 'unlink',
                [lead_ids]
            )
            print(f"  ✓ Deleted {len(lead_ids)} leads/opportunities")
        else:
            print("  ⊘ No leads to delete")

        return len(lead_ids) if lead_ids else 0

    except Exception as e:
        print(f"  ❌ Error deleting leads: {e}")
        return 0


def delete_sales_teams(uid, models):
    """Delete all sales teams"""
    print("\n👥 Deleting sales teams...")

    try:
        team_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.team', 'search',
            [[]]
        )

        if team_ids:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'crm.team', 'unlink',
                [team_ids]
            )
            print(f"  ✓ Deleted {len(team_ids)} sales teams")
        else:
            print("  ⊘ No sales teams to delete")

        return len(team_ids) if team_ids else 0

    except Exception as e:
        print(f"  ❌ Error deleting sales teams: {e}")
        return 0


def delete_partners_safe(uid, models):
    """Delete partners except those linked to system users"""
    print("\n🏢 Deleting partners (customers)...")

    try:
        # Get user partner IDs to exclude
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[]]
        )

        users = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'read',
            [user_ids, ['partner_id']]
        )

        user_partner_ids = [u['partner_id'][0] for u in users if u['partner_id']]
        print(f"  ℹ️  Protecting {len(user_partner_ids)} user-linked partners")

        # Search for partners to delete
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['id', 'not in', user_partner_ids]]]
        )

        if partner_ids:
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'unlink',
                [partner_ids]
            )
            print(f"  ✓ Deleted {len(partner_ids)} partners")
        else:
            print("  ⊘ No partners to delete")

        return len(partner_ids) if partner_ids else 0

    except Exception as e:
        print(f"  ❌ Error deleting partners: {e}")
        return 0


def delete_non_admin_users(uid, models):
    """Delete non-admin users (optional - use with caution)"""
    print("\n👤 Deleting non-admin users...")

    try:
        # Get admin user ID
        admin_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['login', '=', ODOO_USERNAME]]]
        )

        admin_id = admin_ids[0] if admin_ids else uid

        # Search for non-admin users
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['id', '!=', admin_id], ['id', '!=', 1]]]  # Exclude admin and system admin
        )

        if user_ids:
            # Filter out the default internal user and public user
            users = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'read',
                [user_ids, ['login']]
            )

            users_to_delete = [
                u['id'] for u in users
                if u['login'] not in ['__system__', 'public']
            ]

            if users_to_delete:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.users', 'unlink',
                    [users_to_delete]
                )
                print(f"  ✓ Deleted {len(users_to_delete)} users")
            else:
                print("  ⊘ No users to delete")

            return len(users_to_delete)
        else:
            print("  ⊘ No users to delete")
            return 0

    except Exception as e:
        print(f"  ❌ Error deleting users: {e}")
        return 0


def show_current_stats(uid, models):
    """Show current database statistics"""
    try:
        leads_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search_count',
            [[]]
        )

        teams_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.team', 'search_count',
            [[]]
        )

        partners_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_count',
            [[]]
        )

        users_count = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search_count',
            [[]]
        )

        print(f"\nCurrent Database Statistics:")
        print(f"  • Leads/Opportunities: {leads_count}")
        print(f"  • Sales Teams: {teams_count}")
        print(f"  • Partners: {partners_count}")
        print(f"  • Users: {users_count}")

        return leads_count + teams_count + partners_count

    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return 0


def main():
    """Main execution"""
    print("=" * 70)
    print("ODOO CRM DATA DELETION SCRIPT")
    print("=" * 70)

    # Check for --no-confirm flag
    skip_confirm = '--no-confirm' in sys.argv or '-y' in sys.argv

    # Connect to Odoo
    print(f"\n🔌 Connecting to Odoo...")
    print(f"   URL: {ODOO_URL}")
    print(f"   Database: {ODOO_DB}")

    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Show current stats
    total_records = show_current_stats(uid, models)

    if total_records == 0:
        print("\n✅ Database is already clean!")
        sys.exit(0)

    # Confirmation
    if not skip_confirm:
        print("\n" + "⚠️ " * 20)
        print("WARNING: This will delete:")
        print("  • All CRM leads and opportunities")
        print("  • All sales teams")
        print("  • All partners (except user-linked partners)")
        print("  • (Optional) All non-admin users")
        print("⚠️ " * 20)

        response = input("\nDo you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Operation cancelled by user")
            sys.exit(0)

        # Ask about users
        delete_users = input("\nDelete non-admin users too? (yes/no): ").strip().lower()
    else:
        print("\n⚠️  Running in no-confirm mode!")
        delete_users = 'no'

    # Execute deletions
    print("\n" + "=" * 70)
    print("STARTING DELETION PROCESS")
    print("=" * 70)

    deleted_counts = {
        'leads': 0,
        'teams': 0,
        'partners': 0,
        'users': 0
    }

    # Delete in order (to avoid foreign key constraints)
    deleted_counts['leads'] = delete_leads(uid, models)
    deleted_counts['teams'] = delete_sales_teams(uid, models)
    deleted_counts['partners'] = delete_partners_safe(uid, models)

    if delete_users in ['yes', 'y']:
        deleted_counts['users'] = delete_non_admin_users(uid, models)

    # Show results
    print("\n" + "=" * 70)
    print("DELETION SUMMARY")
    print("=" * 70)
    print(f"\n✓ Deleted {deleted_counts['leads']} leads/opportunities")
    print(f"✓ Deleted {deleted_counts['teams']} sales teams")
    print(f"✓ Deleted {deleted_counts['partners']} partners")
    print(f"✓ Deleted {deleted_counts['users']} users")

    total_deleted = sum(deleted_counts.values())
    print(f"\n✅ Total records deleted: {total_deleted}")

    # Show final stats
    show_current_stats(uid, models)

    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
