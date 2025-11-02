#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import CRM foundation data: stages, sources, and tags

Usage: python3 import_crm_foundation.py
"""

import xmlrpc.client
import csv
import sys
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


def import_stages(uid, models, csv_file='../test_data/crm_stages.csv'):
    """Import CRM stages"""
    print("\n📊 Importing CRM Stages...")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.stage', 'search',
                        [[['name', '=', row['name']]]]
                    )

                    stage_data = {
                        'name': row['name'],
                        'sequence': int(row['sequence']),
                        'probability': float(row['probability']),
                        'fold': row['fold'].lower() == 'true',
                        'is_won': row['is_won'].lower() == 'true',
                    }

                    if existing_ids:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.stage', 'write',
                            [[existing_ids[0]], stage_data]
                        )
                        stats['updated'] += 1
                    else:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.stage', 'create',
                            [stage_data]
                        )
                        stats['created'] += 1

                    print(f"  ✓ {row['name']:20} (Probability: {row['probability']}%)")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error: {row.get('name', 'unknown')}: {e}")

        print(f"   Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"  ⚠️  File not found: {csv_file}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    return stats


def import_sources(uid, models, csv_file='../test_data/crm_sources.csv'):
    """Import lead sources (UTM sources)"""
    print("\n📍 Importing Lead Sources...")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'utm.source', 'search',
                        [[['name', '=', row['name']]]]
                    )

                    source_data = {
                        'name': row['name'],
                    }

                    if existing_ids:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'utm.source', 'write',
                            [[existing_ids[0]], source_data]
                        )
                        stats['updated'] += 1
                    else:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'utm.source', 'create',
                            [source_data]
                        )
                        stats['created'] += 1

                    print(f"  ✓ {row['name']}")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error: {row.get('name', 'unknown')}: {e}")

        print(f"   Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"  ⚠️  File not found: {csv_file}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    return stats


def import_tags(uid, models, csv_file='../test_data/crm_tags.csv'):
    """Import CRM tags"""
    print("\n🏷️  Importing CRM Tags...")

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    existing_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'crm.tag', 'search',
                        [[['name', '=', row['name']]]]
                    )

                    tag_data = {
                        'name': row['name'],
                    }

                    if existing_ids:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.tag', 'write',
                            [[existing_ids[0]], tag_data]
                        )
                        stats['updated'] += 1
                    else:
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'crm.tag', 'create',
                            [tag_data]
                        )
                        stats['created'] += 1

                    print(f"  ✓ {row['name']:25} (Category: {row.get('category', 'N/A')})")

                except Exception as e:
                    stats['errors'] += 1
                    print(f"  ❌ Error: {row.get('name', 'unknown')}: {e}")

        print(f"   Created: {stats['created']}, Updated: {stats['updated']}, Errors: {stats['errors']}")

    except FileNotFoundError:
        print(f"  ⚠️  File not found: {csv_file}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    return stats


def main():
    """Main execution function"""
    print("=" * 80)
    print("IMPORTING CRM FOUNDATION DATA")
    print("=" * 80)

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Import in order
    stage_stats = import_stages(uid, models)
    source_stats = import_sources(uid, models)
    tag_stats = import_tags(uid, models)

    # Summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"\n✓ Stages:  {stage_stats['created']} created, {stage_stats['updated']} updated")
    print(f"✓ Sources: {source_stats['created']} created, {source_stats['updated']} updated")
    print(f"✓ Tags:    {tag_stats['created']} created, {tag_stats['updated']} updated")

    total_errors = stage_stats['errors'] + source_stats['errors'] + tag_stats['errors']
    if total_errors == 0:
        print("\n✅ All CRM foundation data imported successfully!")
    else:
        print(f"\n⚠️  Completed with {total_errors} total errors")

    print("=" * 80)


if __name__ == "__main__":
    main()
