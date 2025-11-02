#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import customers from CSV as partners
Creates res.partner records with salesperson assignments

Usage: python3 import_customers.py
"""

import xmlrpc.client
import csv
import sys
from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    CUSTOMERS_CSV, BATCH_SIZE
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


def import_customers(uid, models):
    """Import customers from CSV"""
    print(f"\n📄 Reading customers data from: {CUSTOMERS_CSV}")

    # Get Vietnam country ID
    vietnam_id = find_country_id(uid, models, 'VN')
    if vietnam_id:
        print(f"   ✓ Found Vietnam country ID: {vietnam_id}")
    else:
        print(f"   ⚠️  Vietnam country not found, addresses may be incomplete")

    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }

    try:
        with open(CUSTOMERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = 0
            batch_count = 0

            for row in reader:
                total += 1
                batch_count += 1

                try:
                    # Check if customer exists by Tax ID
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'search',
                        [[['vat', '=', row['tax_id']]]]
                    )

                    # Find salesperson
                    salesperson_id = find_user_by_name(uid, models, row['salesperson'])
                    if not salesperson_id:
                        print(f"  ⚠️  Salesperson '{row['salesperson']}' not found for {row['company_name']}")

                    # Find parent company if specified
                    parent_id = None
                    if row.get('parent_company') and row['parent_company'].strip():
                        parent_code = row['parent_company']
                        # Try to find parent by customer_code or reference
                        parent_ids = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'search',
                            [[['ref', '=', parent_code]]]
                        )
                        if parent_ids:
                            parent_id = parent_ids[0]

                    # Prepare partner data
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

                    if parent_id:
                        partner_data['parent_id'] = parent_id

                    # Add comment/notes
                    if row.get('notes'):
                        partner_data['comment'] = row['notes']

                    if existing_ids:
                        # Update existing customer
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'write',
                            [existing_ids, partner_data]
                        )
                        stats['updated'] += 1
                        if batch_count % 10 == 0:
                            print(f"  ... {total} customers processed ({stats['created']} created, {stats['updated']} updated)")
                    else:
                        # Create new customer
                        partner_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'create',
                            [partner_data]
                        )
                        stats['created'] += 1
                        if batch_count % 10 == 0:
                            print(f"  ... {total} customers processed ({stats['created']} created, {stats['updated']} updated)")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error with {row.get('company_name', 'unknown')}: {e}")

            print(f"\n📊 Processed {total} customers")

    except FileNotFoundError:
        print(f"❌ Error: File not found: {CUSTOMERS_CSV}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)

    return stats


def main():
    """Main execution"""
    print("=" * 70)
    print("ODOO CUSTOMERS IMPORT SCRIPT")
    print("=" * 70)

    print(f"\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    print(f"\n🏢 Importing customers...")
    stats = import_customers(uid, models)

    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"\n✓ Created: {stats['created']} customers")
    print(f"↻ Updated: {stats['updated']} customers")
    print(f"⊘ Skipped: {stats['skipped']} customers")
    print(f"❌ Errors: {stats['errors']} customers")

    total_success = stats['created'] + stats['updated']
    print(f"\n✅ Successfully processed: {total_success} customers")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
