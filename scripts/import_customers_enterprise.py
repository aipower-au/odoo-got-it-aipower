#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import enterprise customers from CSV (3000+ customers)
Supports batch processing for large datasets

Usage: python3 import_customers_enterprise.py [--csv FILENAME] [--batch-size SIZE]
"""

import xmlrpc.client
import csv
import sys
import argparse
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Batch size for API calls
BATCH_SIZE = 100

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


def get_salesperson_id(uid, models, login):
    """Get user ID by login"""
    try:
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['login', '=', login]]]
        )
        return user_ids[0] if user_ids else None
    except:
        return None


def import_customers_batch(uid, models, csv_file, batch_size=BATCH_SIZE):
    """Import customers from CSV with batch processing"""
    print("=" * 80)
    print("IMPORTING ENTERPRISE CUSTOMERS")
    print("=" * 80)

    print(f"\n📄 Reading customer data from: {csv_file}")

    # Build salesperson lookup cache
    print("\n👥 Building salesperson lookup cache...")
    salesperson_cache = {}

    stats = {
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'salesperson_not_found': 0
    }

    try:
        # Read all customers first
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            customer_records = list(reader)

        total = len(customer_records)
        print(f"\n📊 Found {total} customers to import")
        print(f"   Batch size: {batch_size}")
        print(f"   Batches: {(total + batch_size - 1) // batch_size}\n")

        # Process in batches
        for batch_num in range(0, total, batch_size):
            batch = customer_records[batch_num:batch_num + batch_size]
            batch_end = min(batch_num + batch_size, total)

            print(f"🏢 Processing batch {batch_num//batch_size + 1}: records {batch_num+1}-{batch_end}")

            for row in batch:
                try:
                    # Check if customer exists by tax_id
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'search',
                        [[['vat', '=', row['tax_id']]]]
                    )

                    # Get salesperson ID
                    salesperson_login = row.get('salesperson', '')
                    user_id = None

                    if salesperson_login:
                        # Check cache first
                        if salesperson_login in salesperson_cache:
                            user_id = salesperson_cache[salesperson_login]
                        else:
                            user_id = get_salesperson_id(uid, models, salesperson_login)
                            if user_id:
                                salesperson_cache[salesperson_login] = user_id
                            else:
                                stats['salesperson_not_found'] += 1

                    # Prepare customer data
                    customer_data = {
                        'name': row['company_name'],
                        'vat': row.get('tax_id', ''),
                        'phone': row.get('phone', ''),
                        'email': row.get('email', ''),
                        'street': row.get('delivery_address', ''),
                        'is_company': row.get('entity_type') == 'Company',
                        'customer_rank': 1,  # Mark as customer
                    }

                    if user_id:
                        customer_data['user_id'] = user_id

                    # Add optional fields
                    if row.get('invoice_email'):
                        customer_data['invoice_email'] = row['invoice_email']

                    if existing_ids:
                        # Update existing customer
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'write',
                            [[existing_ids[0]], customer_data]
                        )
                        stats['updated'] += 1
                    else:
                        # Create new customer
                        partner_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'res.partner', 'create',
                            [customer_data]
                        )
                        stats['created'] += 1

                except Exception as e:
                    stats['errors'] += 1
                    if (stats['created'] + stats['updated'] + stats['errors']) % 100 == 0:
                        print(f"  ❌ Error: {row.get('customer_code', 'unknown')}: {e}")

            # Show batch progress
            processed = batch_end
            print(f"   Progress: {processed}/{total} ({100*processed//total}%)")
            print(f"   Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}\n")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        import traceback
        traceback.print_exc()
        return

    # Print summary
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} customers")
    print(f"✓ Updated:  {stats['updated']} customers")
    print(f"⊘ Skipped:  {stats['skipped']} customers")
    print(f"❌ Errors:   {stats['errors']} customers")
    print(f"⚠️  Salesperson not found: {stats['salesperson_not_found']} customers")
    print(f"\nTotal processed: {stats['created'] + stats['updated'] + stats['errors']}/{total}")

    if stats['errors'] == 0 and (stats['created'] + stats['updated']) == total:
        print("\n✅ All customers imported successfully!")
    elif stats['errors'] > 0:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import enterprise customers into Odoo')
    parser.add_argument('--csv', default='../test_data/customers_sprint1_enterprise.csv',
                       help='Path to customers CSV file')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Batch size for processing (default: {BATCH_SIZE})')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    import_customers_batch(uid, models, args.csv, args.batch_size)


if __name__ == "__main__":
    main()
