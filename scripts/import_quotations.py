#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Quotations and Quotation Lines from CSV

Imports quotations (sale.order) and their line items (sale.order.line) from CSV files.

CSV Columns Required:
    Quotations:
        - quotation_id: Unique reference (e.g., QUOT0001)
        - name: Quotation name
        - partner_name: Customer name (must exist in res.partner)
        - assigned_to: Salesperson login or name
        - team: Sales team name (optional)
        - opportunity_id: Linked opportunity name (optional)
        - date_order: Order date (YYYY-MM-DD)
        - amount_total: Total amount
        - state: draft, sent, sale, or cancel

    Quotation Lines:
        - quotation_id: Reference to parent quotation
        - product_id or product_name: Product name (must exist)
        - quantity: Quantity
        - unit_price or price_unit: Unit price
        - discount: Discount percentage (optional)

Usage:
    python3 import_quotations.py
    python3 import_quotations.py --quotations custom_quotes.csv --lines custom_lines.csv
"""

import xmlrpc.client
import csv
import argparse
from datetime import datetime
from config import ODOO_DB, ODOO_PASSWORD
from odoo_utils import (
    connect_odoo,
    get_partner_id,
    get_user_id,
    get_team_id,
    get_opportunity_id,
    get_product_id,
    print_stats
)

BATCH_SIZE = 100


def get_order_id_by_ref(uid, models, client_order_ref):
    """
    Get sale order ID by client_order_ref.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        client_order_ref: Client order reference (e.g., QUOT0001)

    Returns:
        Order ID if found, None otherwise
    """
    try:
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[['client_order_ref', '=', client_order_ref]]]
        )
        return order_ids[0] if order_ids else None
    except (xmlrpc.client.Fault, Exception):
        return None


def import_quotations_batch(uid, models, csv_file, batch_size=BATCH_SIZE):
    """Import quotations from CSV in batches"""
    print("=" * 80)
    print("IMPORTING QUOTATIONS")
    print("=" * 80)

    print(f"\n📄 Reading quotations data from: {csv_file}")

    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'partner_not_found': 0,
        'user_not_found': 0,
        'team_not_found': 0,
        'opportunity_not_found': 0
    }

    # Build a mapping of quotation_id -> order_id for later line import
    quotation_id_map = {}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            quotations = list(reader)

        total = len(quotations)
        print(f"\n📊 Found {total} quotations to import")
        print(f"Batch size: {batch_size}\n")

        for i in range(0, total, batch_size):
            batch = quotations[i:i+batch_size]
            batch_num = i // batch_size + 1

            print(f"Batch {batch_num}: records {i+1}-{min(i+batch_size, total)}")

            for row in batch:
                try:
                    quotation_ref = row.get('quotation_id', '')

                    # Check if quotation exists
                    existing_id = get_order_id_by_ref(uid, models, quotation_ref)

                    # Prepare quotation data
                    order_data = {
                        'client_order_ref': quotation_ref,
                    }

                    # Get partner (customer) - REQUIRED
                    partner_name = row.get('partner_name') or row.get('customer')
                    if partner_name:
                        partner_id = get_partner_id(uid, models, partner_name)
                        if partner_id:
                            order_data['partner_id'] = partner_id
                        else:
                            stats['partner_not_found'] += 1
                            stats['errors'] += 1
                            continue  # Skip if no customer

                    # Get user (salesperson)
                    user_name = row.get('assigned_to') or row.get('salesperson')
                    if user_name:
                        user_id = get_user_id(uid, models, user_name)
                        if user_id:
                            order_data['user_id'] = user_id
                        else:
                            stats['user_not_found'] += 1

                    # Get team
                    if row.get('team'):
                        team_id = get_team_id(uid, models, row['team'])
                        if team_id:
                            order_data['team_id'] = team_id
                        else:
                            stats['team_not_found'] += 1

                    # Get opportunity
                    opp_name = row.get('opportunity_id') or row.get('opportunity')
                    if opp_name:
                        opp_id = get_opportunity_id(uid, models, opp_name)
                        if opp_id:
                            order_data['opportunity_id'] = opp_id
                        else:
                            stats['opportunity_not_found'] += 1

                    # State
                    if row.get('state'):
                        order_data['state'] = row['state']

                    # Date order
                    if row.get('date_order'):
                        try:
                            order_data['date_order'] = row['date_order']
                        except:
                            pass

                    # Validity date
                    if row.get('validity_date'):
                        try:
                            order_data['validity_date'] = row['validity_date']
                        except:
                            pass

                    if existing_id:
                        # Update existing quotation
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'sale.order', 'write',
                            [[existing_id], order_data]
                        )
                        stats['updated'] += 1
                        quotation_id_map[quotation_ref] = existing_id
                    else:
                        # Create new quotation
                        new_id = models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'sale.order', 'create',
                            [order_data]
                        )
                        stats['created'] += 1
                        quotation_id_map[quotation_ref] = new_id

                except Exception as e:
                    stats['errors'] += 1

            progress = min(i+batch_size, total)
            print(f"  Progress: {progress}/{total} ({100*progress//total}%)\n")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return None
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None

    # Print summary
    print("=" * 80)
    print("QUOTATIONS IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} quotations")
    print(f"✓ Updated:  {stats['updated']} quotations")
    print(f"❌ Errors:   {stats['errors']} quotations")

    if stats['partner_not_found'] > 0:
        print(f"⚠️  Customer not found: {stats['partner_not_found']} quotations")
    if stats['user_not_found'] > 0:
        print(f"⚠️  Salesperson not found: {stats['user_not_found']} quotations")
    if stats['team_not_found'] > 0:
        print(f"⚠️  Team not found: {stats['team_not_found']} quotations")
    if stats['opportunity_not_found'] > 0:
        print(f"⚠️  Opportunity not found: {stats['opportunity_not_found']} quotations")

    print(f"\nTotal processed: {stats['created'] + stats['updated'] + stats['errors']}/{total}")

    if stats['errors'] == 0:
        print("\n✅ All quotations imported successfully!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)

    return quotation_id_map


def import_quotation_lines_batch(uid, models, csv_file, quotation_id_map, batch_size=BATCH_SIZE):
    """Import quotation lines from CSV in batches"""
    print("\n" + "=" * 80)
    print("IMPORTING QUOTATION LINES")
    print("=" * 80)

    print(f"\n📄 Reading quotation lines data from: {csv_file}")

    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'order_not_found': 0,
        'product_not_found': 0
    }

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            lines = list(reader)

        total = len(lines)
        print(f"\n📊 Found {total} quotation lines to import")
        print(f"Batch size: {batch_size}\n")

        for i in range(0, total, batch_size):
            batch = lines[i:i+batch_size]
            batch_num = i // batch_size + 1

            print(f"Batch {batch_num}: records {i+1}-{min(i+batch_size, total)}")

            for row in batch:
                try:
                    quotation_ref = row.get('quotation_id', '')

                    # Get order ID from map
                    order_id = quotation_id_map.get(quotation_ref)
                    if not order_id:
                        stats['order_not_found'] += 1
                        stats['errors'] += 1
                        continue

                    # Prepare line data
                    line_data = {
                        'order_id': order_id,
                    }

                    # Get product - REQUIRED
                    # Support both 'product' and 'product_id'/'product_name' column names
                    product_name = row.get('product') or row.get('product_id') or row.get('product_name')
                    if product_name:
                        product_id = get_product_id(uid, models, product_name)
                        if product_id:
                            line_data['product_id'] = product_id
                        else:
                            stats['product_not_found'] += 1
                            stats['errors'] += 1
                            continue
                    else:
                        stats['product_not_found'] += 1
                        stats['errors'] += 1
                        continue

                    # Quantity
                    if row.get('quantity'):
                        try:
                            line_data['product_uom_qty'] = float(row['quantity'])
                        except:
                            line_data['product_uom_qty'] = 1.0

                    # Price unit - support both 'price_unit' and 'unit_price'
                    price = row.get('price_unit') or row.get('unit_price')
                    if price:
                        try:
                            line_data['price_unit'] = float(price)
                        except:
                            pass

                    # Discount
                    if row.get('discount'):
                        try:
                            line_data['discount'] = float(row['discount'])
                        except:
                            pass

                    # Create new line (we don't update existing lines)
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'sale.order.line', 'create',
                        [line_data]
                    )
                    stats['created'] += 1

                except Exception as e:
                    stats['errors'] += 1

            progress = min(i+batch_size, total)
            print(f"  Progress: {progress}/{total} ({100*progress//total}%)\n")

    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_file}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Print summary
    print("=" * 80)
    print("QUOTATION LINES IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} quotation lines")
    print(f"❌ Errors:   {stats['errors']} quotation lines")

    if stats['order_not_found'] > 0:
        print(f"⚠️  Order not found: {stats['order_not_found']} lines")
    if stats['product_not_found'] > 0:
        print(f"⚠️  Product not found: {stats['product_not_found']} lines")

    print(f"\nTotal processed: {stats['created'] + stats['errors']}/{total}")

    if stats['errors'] == 0:
        print("\n✅ All quotation lines imported successfully!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import quotations and lines into Odoo')
    parser.add_argument('--quotations', default='../test_data/quotations_demo.csv',
                       help='Path to quotations CSV file')
    parser.add_argument('--lines', default='../test_data/quotation_lines_demo.csv',
                       help='Path to quotation lines CSV file')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    # Import quotations first
    quotation_id_map = import_quotations_batch(uid, models, args.quotations)

    # Then import quotation lines if quotations were imported
    if quotation_id_map:
        import_quotation_lines_batch(uid, models, args.lines, quotation_id_map)
    else:
        print("\n❌ Skipping quotation lines import due to quotations import failure")


if __name__ == "__main__":
    main()
