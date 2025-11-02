#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Activities from CSV

Imports activities (mail.activity) linked to leads or opportunities.

CSV Columns Required:
    - activity_id: Unique reference (optional)
    - res_model: Model name (crm.lead)
    - res_id: Lead or opportunity name
    - res_type: 'lead' or 'opportunity'
    - activity_type_id or activity_type_name: Activity type
    - summary: Activity summary
    - date_deadline or due_date: Due date (YYYY-MM-DD)
    - assigned_to: User login or name
    - note or description: Activity notes (optional)

Usage:
    python3 import_activities.py
    python3 import_activities.py --csv custom_activities.csv
"""

import xmlrpc.client
import csv
import argparse
from datetime import datetime
from config import ODOO_DB, ODOO_PASSWORD
from odoo_utils import (
    connect_odoo,
    get_user_id,
    get_lead_id,
    get_opportunity_id,
    print_stats
)

BATCH_SIZE = 200


def get_activity_type_id(uid, models, activity_type_name):
    """
    Get or map activity type by name to standard Odoo activity types.

    Odoo has standard activity types: Call, Email, Meeting, To Do, Upload Document

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        activity_type_name: Activity type name from CSV

    Returns:
        Activity type ID if found, fallback to first available type
    """
    try:
        # Common activity types mapping to standard Odoo types
        activity_type_mapping = {
            'Call': 'Call',
            'Email': 'Email',
            'Meeting': 'Meeting',
            'To Do': 'To Do',
            'Follow-up': 'To Do',
            'Demo': 'Meeting',
            'Proposal': 'To Do',
            'Upload Document': 'Upload Document'
        }

        # Map to standard Odoo activity type
        mapped_type = activity_type_mapping.get(activity_type_name, 'To Do')

        # Search for activity type
        type_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.activity.type', 'search',
            [[['name', '=', mapped_type]]]
        )

        if type_ids:
            return type_ids[0]

        # If not found, get the first available activity type
        type_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'mail.activity.type', 'search',
            [[]]
        )
        return type_ids[0] if type_ids else None

    except (xmlrpc.client.Fault, Exception):
        return None


def get_model_id(uid, models, model_name):
    """
    Get model ID by model name (for activities linking).

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        model_name: Model name (e.g., 'crm.lead')

    Returns:
        Model ID if found, None otherwise
    """
    try:
        model_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search',
            [[['model', '=', model_name]]]
        )
        return model_ids[0] if model_ids else None
    except (xmlrpc.client.Fault, Exception):
        return None


def import_activities_batch(uid, models, csv_file, batch_size=BATCH_SIZE):
    """Import activities from CSV in batches"""
    print("=" * 80)
    print("IMPORTING ACTIVITIES")
    print("=" * 80)

    print(f"\n📄 Reading activities data from: {csv_file}")

    stats = {
        'created': 0,
        'updated': 0,
        'errors': 0,
        'user_not_found': 0,
        'opportunity_not_found': 0,
        'activity_type_not_found': 0
    }

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            activities = list(reader)

        total = len(activities)
        print(f"\n📊 Found {total} activities to import")
        print(f"Batch size: {batch_size}\n")

        for i in range(0, total, batch_size):
            batch = activities[i:i+batch_size]
            batch_num = i // batch_size + 1

            print(f"Batch {batch_num}: records {i+1}-{min(i+batch_size, total)}")

            for row in batch:
                try:
                    # Prepare activity data
                    activity_data = {
                        'summary': row.get('summary', 'Activity'),
                        'note': row.get('note') or row.get('description', ''),
                    }

                    # Get lead or opportunity - REQUIRED (res_model and res_id)
                    res_ref = row.get('res_id')  # e.g., "LEAD1183" or "OPP1472"
                    res_type = row.get('res_type', 'opportunity')  # lead or opportunity

                    if res_ref:
                        # Look up by name
                        if res_type == 'lead':
                            lead_id = get_lead_id(uid, models, res_ref)
                            if lead_id:
                                activity_data['res_model_id'] = get_model_id(uid, models, 'crm.lead')
                                activity_data['res_id'] = lead_id
                            else:
                                stats['opportunity_not_found'] += 1
                                stats['errors'] += 1
                                continue
                        else:  # opportunity
                            opp_id = get_opportunity_id(uid, models, res_ref)
                            if opp_id:
                                activity_data['res_model_id'] = get_model_id(uid, models, 'crm.lead')
                                activity_data['res_id'] = opp_id
                            else:
                                stats['opportunity_not_found'] += 1
                                stats['errors'] += 1
                                continue
                    else:
                        stats['errors'] += 1
                        continue

                    # Get user (assigned to)
                    if row.get('assigned_to'):
                        user_id = get_user_id(uid, models, row['assigned_to'])
                        if user_id:
                            activity_data['user_id'] = user_id
                        else:
                            stats['user_not_found'] += 1

                    # Get activity type
                    activity_type = row.get('activity_type_name') or row.get('activity_type')
                    if activity_type:
                        type_id = get_activity_type_id(uid, models, activity_type)
                        if type_id:
                            activity_data['activity_type_id'] = type_id
                        else:
                            stats['activity_type_not_found'] += 1

                    # Due date - REQUIRED
                    due_date = row.get('date_deadline') or row.get('due_date')
                    if due_date:
                        try:
                            activity_data['date_deadline'] = due_date
                        except:
                            pass

                    # State
                    if row.get('state'):
                        activity_data['state'] = row['state']

                    # Create new activity (we don't update existing)
                    models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'mail.activity', 'create',
                        [activity_data]
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
    print(f"\n✓ Created:  {stats['created']} activities")
    print(f"❌ Errors:   {stats['errors']} activities")

    if stats['user_not_found'] > 0:
        print(f"⚠️  User not found: {stats['user_not_found']} activities")
    if stats['opportunity_not_found'] > 0:
        print(f"⚠️  Opportunity not found: {stats['opportunity_not_found']} activities")
    if stats['activity_type_not_found'] > 0:
        print(f"⚠️  Activity type not found: {stats['activity_type_not_found']} activities")

    print(f"\nTotal processed: {stats['created'] + stats['errors']}/{total}")

    if stats['errors'] == 0:
        print("\n✅ All activities imported successfully!")
    else:
        print(f"\n⚠️  Completed with {stats['errors']} errors")

    print("=" * 80)


def get_model_id(uid, models, model_name):
    """Get model ID by model name"""
    try:
        model_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search',
            [[['model', '=', model_name]]]
        )
        return model_ids[0] if model_ids else None
    except:
        return None


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Import activities into Odoo')
    parser.add_argument('--csv', default='../test_data/activities_demo.csv',
                       help='Path to activities CSV file')

    args = parser.parse_args()

    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}\n")

    import_activities_batch(uid, models, args.csv)


if __name__ == "__main__":
    main()
