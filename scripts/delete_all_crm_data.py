#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced CRM Data Deletion Script
Deletes all CRM-related data in the correct order to avoid foreign key constraints

Usage: python3 delete_all_crm_data.py [--no-confirm] [--keep-users]
"""

import xmlrpc.client
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


def count_records(uid, models, model):
    """Count records in a model"""
    try:
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search_count', [[]]
        )
    except:
        return 0


def delete_records(uid, models, model, name, batch_size=100):
    """Delete all records from a model in batches"""
    print(f"\n🗑️  Deleting {name}...")

    try:
        # Get all IDs
        all_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search', [[]]
        )

        total = len(all_ids)
        if total == 0:
            print(f"   No records to delete")
            return 0

        print(f"   Found {total} records")

        # Delete in batches
        deleted = 0
        for i in range(0, total, batch_size):
            batch = all_ids[i:i+batch_size]
            try:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    model, 'unlink', [batch]
                )
                deleted += len(batch)

                if total > 100 and i % 500 == 0:
                    print(f"   Progress: {deleted}/{total} ({100*deleted//total}%)")

            except Exception as e:
                print(f"   ⚠️  Batch error: {e}")

        print(f"   ✓ Deleted {deleted} records")
        return deleted

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def delete_users(uid, models, keep_admin=True):
    """Delete imported users (keep admin and system users)"""
    print(f"\n🗑️  Deleting users...")

    try:
        # Get users to delete (ID > 2 to skip admin and public)
        if keep_admin:
            user_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'search',
                [[['id', '>', 2]]]  # Skip admin (1) and public (2)
            )
        else:
            user_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.users', 'search',
                [[['id', '!=', uid]]]  # Only keep current user
            )

        total = len(user_ids)
        if total == 0:
            print(f"   No users to delete")
            return 0

        print(f"   Found {total} users to delete")

        # Delete in batches
        deleted = 0
        batch_size = 50
        for i in range(0, total, batch_size):
            batch = user_ids[i:i+batch_size]
            try:
                # First deactivate
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.users', 'write',
                    [batch, {'active': False}]
                )

                # Then delete
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.users', 'unlink', [batch]
                )
                deleted += len(batch)

            except Exception as e:
                print(f"   ⚠️  Batch error: {e}")

        print(f"   ✓ Deleted {deleted} users")
        return deleted

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def delete_customers(uid, models):
    """Delete customer partners (non-user partners)"""
    print(f"\n🗑️  Deleting customers...")

    try:
        # Get all user partner IDs
        users = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search_read',
            [[]], {'fields': ['partner_id']}
        )
        user_partner_ids = [u['partner_id'][0] for u in users if u.get('partner_id')]

        # Get all partners except user partners
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['id', 'not in', user_partner_ids]]]
        )

        total = len(partner_ids)
        if total == 0:
            print(f"   No customers to delete")
            return 0

        print(f"   Found {total} customer records")

        # Delete in batches
        deleted = 0
        batch_size = 100
        for i in range(0, total, batch_size):
            batch = partner_ids[i:i+batch_size]
            try:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'unlink', [batch]
                )
                deleted += len(batch)

                if total > 100 and i % 500 == 0:
                    print(f"   Progress: {deleted}/{total} ({100*deleted//total}%)")

            except Exception as e:
                print(f"   ⚠️  Batch error: {e}")

        print(f"   ✓ Deleted {deleted} customers")
        return deleted

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Delete all CRM data')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation')
    parser.add_argument('--keep-users', action='store_true', help='Keep imported users')

    args = parser.parse_args()

    print("=" * 80)
    print("DELETE ALL CRM DATA")
    print("=" * 80)

    if not args.no_confirm:
        print("\n⚠️  WARNING: This will delete ALL CRM data including:")
        print("   - Activities")
        print("   - Quotations and quote lines")
        print("   - Leads and Opportunities")
        print("   - Products")
        print("   - Sales Teams")
        print("   - Customers (partners)")
        if not args.keep_users:
            print("   - Users (except admin)")
        print()
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("\n❌ Operation cancelled")
            return

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Check current counts
    print("\n" + "=" * 80)
    print("CURRENT DATA COUNTS")
    print("=" * 80)
    print(f"   Users: {count_records(uid, models, 'res.users')}")
    print(f"   Customers: {count_records(uid, models, 'res.partner')}")
    print(f"   Sales Teams: {count_records(uid, models, 'crm.team')}")
    print(f"   Leads/Opportunities: {count_records(uid, models, 'crm.lead')}")
    print(f"   Products: {count_records(uid, models, 'product.product')}")
    print(f"   Quotations: {count_records(uid, models, 'sale.order')}")

    # Delete in correct order (reverse of import)
    print("\n" + "=" * 80)
    print("DELETING DATA")
    print("=" * 80)

    total_deleted = 0

    # 1. Activities
    total_deleted += delete_records(uid, models, 'mail.activity', 'Activities')

    # 2. Quotations and lines
    total_deleted += delete_records(uid, models, 'sale.order.line', 'Quotation Lines')
    total_deleted += delete_records(uid, models, 'sale.order', 'Quotations')

    # 3. Leads and Opportunities (same model)
    total_deleted += delete_records(uid, models, 'crm.lead', 'Leads & Opportunities', batch_size=200)

    # 4. Products (only if they exist)
    total_deleted += delete_records(uid, models, 'product.product', 'Products')

    # 5. CRM Foundation (optional - these are usually kept)
    # total_deleted += delete_records(uid, models, 'crm.tag', 'CRM Tags')
    # total_deleted += delete_records(uid, models, 'utm.source', 'Lead Sources')
    # total_deleted += delete_records(uid, models, 'crm.stage', 'CRM Stages')

    # 6. Sales Teams
    total_deleted += delete_records(uid, models, 'crm.team', 'Sales Teams')

    # 7. Customers (partners that are not user partners)
    total_deleted += delete_customers(uid, models)

    # 8. Users (if not keeping)
    if not args.keep_users:
        total_deleted += delete_users(uid, models, keep_admin=True)

    # Final summary
    print("\n" + "=" * 80)
    print("DELETION COMPLETE")
    print("=" * 80)
    print(f"\n✓ Total records deleted: {total_deleted}")
    print("\n✅ All CRM data has been deleted!")
    print("=" * 80)


if __name__ == "__main__":
    main()
