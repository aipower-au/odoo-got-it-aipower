#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import leads from CSV (2000 records)

Usage: python3 import_leads.py [--csv FILENAME]
"""

import xmlrpc.client
import csv
import sys
import argparse
from datetime import datetime
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

BATCH_SIZE = 200


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


def get_or_create_stage(uid, models, stage_name):
    """Get or create CRM stage by name"""
    try:
        stage_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.stage', 'search',
            [[['name', '=', stage_name]]]
        )
        if stage_ids:
            return stage_ids[0]

        # Create if not exists
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.stage', 'create',
            [{'name': stage_name}]
        )
    except:
        return None


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


def get_partner_id(uid, models, partner_name):
    """Get partner ID by name"""
    try:
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['name', '=', partner_name]]]
        )
        return partner_ids[0] if partner_ids else None
    except:
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
    except:
        return None


def get_source_id(uid, models, source_name):
    """Get or create UTM source by name"""
    try:
        source_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'utm.source', 'search',
            [[['name', '=', source_name]]]
        )
        if source_ids:
            return source_ids[0]

        # Create if not exists
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'utm.source', 'create',
            [{'name': source_name}]
        )
    except:
        return None


def get_tag_ids(uid, models, tag_names):
    """Get CRM tag IDs by names (comma-separated)"""
    if not tag_names:
        return []

    try:
        tags = [t.strip() for t in tag_names.split(',')]
        tag_ids = []

        for tag_name in tags:
            existing = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'crm.tag', 'search',
                [[['name', '=', tag_name]]]
            )
            if existing:
                tag_ids.append(existing[0])
            else:
                # Create if not exists
                new_tag = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'crm.tag', 'create',
                    [{'name': tag_name}]
                )
                tag_ids.append(new_tag)

        return tag_ids
    except:
        return []


def import_leads_batch(uid, models, csv_file, batch_size=BATCH_SIZE):
    """Import leads from CSV in batches"""
    print("=" * 80)
    print("IMPORTING LEADS")
    print("=" * 80)

    print(f"\n📄 Reading leads data from: {csv_file}")

    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'stage_not_found': 0,
        'user_not_found': 0,
        'partner_not_found': 0,
        'team_not_found': 0
    }

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            leads = list(reader)

        total = len(leads)
        print(f"\n📊 Found {total} leads to import")
        print(f"Batch size: {batch_size}\n")

        for i in range(0, total, batch_size):
            batch = leads[i:i+batch_size]
            batch_num = i // batch_size + 1

            print(f"Batch {batch_num}: records {i+1}-{min(i+batch_size, total)}")

            for row in batch:
                try:
                    # Check if lead exists
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.lead', 'search',
                        [[['name', '=', row['name']], ['type', '=', 'lead']]]
                    )

                    # Prepare lead data
                    lead_data = {
                        'name': row['name'],
                        'type': 'lead',
                        'contact_name': row.get('contact_name', ''),
                        'email_from': row.get('email', ''),
                        'phone': row.get('phone', ''),
                        'description': row.get('description', ''),
                    }

                    # Get stage
                    if row.get('stage'):
                        stage_id = get_or_create_stage(uid, models, row['stage'])
                        if stage_id:
                            lead_data['stage_id'] = stage_id
                        else:
                            stats['stage_not_found'] += 1

                    # Get user (salesperson)
                    if row.get('salesperson'):
                        user_id = get_user_id(uid, models, row['salesperson'])
                        if user_id:
                            lead_data['user_id'] = user_id
                        else:
                            stats['user_not_found'] += 1

                    # Get partner (customer)
                    if row.get('customer'):
                        partner_id = get_partner_id(uid, models, row['customer'])
                        if partner_id:
                            lead_data['partner_id'] = partner_id
                        else:
                            stats['partner_not_found'] += 1

                    # Get team
                    if row.get('team'):
                        team_id = get_team_id(uid, models, row['team'])
                        if team_id:
                            lead_data['team_id'] = team_id
                        else:
                            stats['team_not_found'] += 1

                    # Get source
                    if row.get('source'):
                        source_id = get_source_id(uid, models, row['source'])
                        if source_id:
                            lead_data['source_id'] = source_id

                    # Get tags
                    if row.get('tags'):
                        tag_ids = get_tag_ids(uid, models, row['tags'])
                        if tag_ids:
                            lead_data['tag_ids'] = [(6, 0, tag_ids)]

                    # Expected revenue
                    if row.get('expected_revenue'):
                        try:
                            lead_data['expected_revenue'] = float(row['expected_revenue'])
                        except:
                            pass

                    # Priority
                    if row.get('priority'):
                        lead_data['priority'] = row['priority']

                    # Date open
                    if row.get('date_open'):
                        try:
                            lead_data['date_open'] = row['date_open']
                        except:
                            pass

                    if existing_ids:
                        # Update existing lead
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.lead', 'write',
                            [[existing_ids[0]], lead_data]
                        )
                        stats['updated'] += 1
                    else:
                        # Create new lead
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.lead', 'create',
                            [lead_data]
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
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Created:  {stats['created']} leads")
    print(f"✓ Updated:  {stats['updated']} leads")
    print(f"❌ Errors:   {stats['errors']} leads")

    if stats['stage_not_found'] > 0:
        print(f"⚠️  Stage not found: {stats['stage_not_found']} leads")
    if stats['user_not_found'] > 0:
        print(f"⚠️  Salesperson not found: {stats['user_not_found']} leads")
    if stats['partner_not_found'] > 0:
        print(f"⚠️  Customer not found: {stats['partner_not_found']} leads")
    if stats['team_not_found'] > 0:
        print(f"⚠️  Team not found: {stats['team_not_found']} leads")

    print(f"\nTotal processed: {stats['created'] + stats['updated'] + stats['errors']}/{total}")

    if stats['errors'] == 0:
        print("\n✅ All leads imported successfully!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import leads into Odoo')
    parser.add_argument('--csv', default='../test_data/leads_demo.csv',
                       help='Path to leads CSV file')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    import_leads_batch(uid, models, args.csv)


if __name__ == "__main__":
    main()
