#!/usr/bin/env python3
"""
Clean Demo Data Script for GotIt CRM
Safely removes all demo data from Odoo to start fresh
"""

import xmlrpc.client
import argparse
import sys

# Import local modules
import config


class OdooDataCleaner:
    """Clean demo data from Odoo"""

    def __init__(self, url, db, username, password):
        """Initialize connection to Odoo"""
        self.url = url
        self.db = db
        self.username = username
        self.password = password

        print(f"Connecting to Odoo at {url}...")
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(db, username, password, {})

        if not self.uid:
            raise Exception("Authentication failed!")

        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        print(f"✓ Connected as user ID: {self.uid}\n")

        self.stats = {}

    def execute(self, model, method, args_list, kwargs_dict=None):
        """Execute a method on an Odoo model"""
        if kwargs_dict is None:
            kwargs_dict = {}
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args_list, kwargs_dict
        )

    def search_records(self, model, domain, limit=None):
        """Search for records"""
        kwargs_dict = {}
        if limit:
            kwargs_dict['limit'] = limit
        return self.execute(model, 'search', [domain], kwargs_dict)

    def count_records(self, model, domain):
        """Count records matching domain"""
        return self.execute(model, 'search_count', [domain])

    def delete_records(self, model, record_ids):
        """Delete records by IDs"""
        if not record_ids:
            return 0

        try:
            self.execute(model, 'unlink', [record_ids])
            return len(record_ids)
        except Exception as e:
            print(f"  ⚠ Error deleting {model}: {str(e)[:100]}")
            return 0

    def clean_activities(self):
        """Delete all activities"""
        print("Cleaning Activities...")

        # Delete all activities (they're usually demo/test data)
        activity_ids = self.search_records('mail.activity', [])
        deleted = self.delete_records('mail.activity', activity_ids)

        self.stats['mail.activity'] = deleted
        print(f"  → Deleted {deleted} activities")

        return deleted

    def clean_quotations(self):
        """Delete all quotations/sale orders"""
        print("\nCleaning Quotations/Sale Orders...")

        # Get all sale orders
        order_ids = self.search_records('sale.order', [])

        if order_ids:
            # First, try to cancel confirmed orders by setting state
            print(f"  → Cancelling {len(order_ids)} sale orders...")
            try:
                # Set state to 'cancel' for all orders
                self.execute('sale.order', 'write', [order_ids, {'state': 'cancel'}])
                print(f"  → Cancelled {len(order_ids)} orders")
            except Exception as e:
                print(f"  ⚠ Could not cancel all orders: {str(e)[:80]}")
                # Try to delete draft orders only
                draft_ids = self.search_records('sale.order', [('state', 'in', ['draft', 'cancel'])])
                if draft_ids:
                    order_ids = draft_ids
                    print(f"  → Will delete {len(draft_ids)} draft/cancelled orders only")

            # Now delete the orders (this will cascade delete lines)
            deleted_orders = self.delete_records('sale.order', order_ids)
            self.stats['sale.order'] = deleted_orders
            print(f"  → Deleted {deleted_orders} sale orders")

            return deleted_orders
        else:
            self.stats['sale.order'] = 0
            print(f"  → No sale orders to delete")
            return 0

    def clean_products(self):
        """Delete all products (except system defaults)"""
        print("\nCleaning Products...")

        # Only delete products without module reference (demo products)
        # Keep system products that came with Odoo installation
        product_ids = self.search_records('product.product', [
            ('create_uid', '!=', 1)  # Not created by system
        ])

        deleted = self.delete_records('product.product', product_ids)

        self.stats['product.product'] = deleted
        print(f"  → Deleted {deleted} products")

        return deleted

    def clean_opportunities(self):
        """Delete all opportunities (keeping leads separate)"""
        print("\nCleaning Opportunities...")

        # Delete only opportunities (type=opportunity)
        opp_ids = self.search_records('crm.lead', [('type', '=', 'opportunity')])
        deleted = self.delete_records('crm.lead', opp_ids)

        self.stats['crm.lead (opportunities)'] = deleted
        print(f"  → Deleted {deleted} opportunities")

        return deleted

    def clean_leads(self):
        """Delete all leads"""
        print("\nCleaning Leads...")

        # Delete only leads (type=lead)
        lead_ids = self.search_records('crm.lead', [('type', '=', 'lead')])
        deleted = self.delete_records('crm.lead', lead_ids)

        self.stats['crm.lead (leads)'] = deleted
        print(f"  → Deleted {deleted} leads")

        return deleted

    def clean_customers(self, keep_admin=True):
        """Delete all customers/partners"""
        print("\nCleaning Customers/Partners...")

        # Build domain to exclude system users
        domain = [('is_company', '=', True)]

        if keep_admin:
            # Don't delete the admin's partner or system users
            domain.append(('id', '>', 3))  # Usually first 3 are system records

        customer_ids = self.search_records('res.partner', domain)
        deleted = self.delete_records('res.partner', customer_ids)

        self.stats['res.partner'] = deleted
        print(f"  → Deleted {deleted} customers/partners")

        return deleted

    def clean_sales_teams(self, keep_defaults=True):
        """Delete sales teams"""
        print("\nCleaning Sales Teams...")

        if keep_defaults:
            # Only delete teams without module reference (demo teams)
            team_ids = self.search_records('crm.team', [
                ('create_uid', '!=', 1)  # Not created by system
            ])
        else:
            team_ids = self.search_records('crm.team', [])

        deleted = self.delete_records('crm.team', team_ids)

        self.stats['crm.team'] = deleted
        print(f"  → Deleted {deleted} sales teams")

        return deleted

    def clean_stages(self, keep_defaults=True):
        """Delete custom CRM stages"""
        print("\nCleaning CRM Stages...")

        if keep_defaults:
            # Only delete stages created by demo script
            stage_ids = self.search_records('crm.stage', [
                ('create_uid', '!=', 1)  # Not created by system
            ])
        else:
            stage_ids = self.search_records('crm.stage', [])

        deleted = self.delete_records('crm.stage', stage_ids)

        self.stats['crm.stage'] = deleted
        print(f"  → Deleted {deleted} CRM stages")

        return deleted

    def show_summary(self):
        """Show summary of what will be cleaned"""
        print("=" * 70)
        print("DATA CLEANUP PREVIEW")
        print("=" * 70)
        print(f"\nConnection: {self.url}")
        print(f"Database: {self.db}")

        print("\n📊 RECORDS TO BE DELETED:")
        print("-" * 70)

        counts = {
            'Activities': self.count_records('mail.activity', []),
            'Sale Orders (& lines)': self.count_records('sale.order', []),
            'Products (demo)': self.count_records('product.product', [('create_uid', '!=', 1)]),
            'Opportunities': self.count_records('crm.lead', [('type', '=', 'opportunity')]),
            'Leads': self.count_records('crm.lead', [('type', '=', 'lead')]),
            'Customers/Partners': self.count_records('res.partner', [('is_company', '=', True), ('id', '>', 3)]),
            'Sales Teams (demo)': self.count_records('crm.team', [('create_uid', '!=', 1)]),
            'CRM Stages (demo)': self.count_records('crm.stage', [('create_uid', '!=', 1)]),
        }

        total = 0
        for name, count in counts.items():
            print(f"  {name:.<50} {count:>4} records")
            total += count

        print("-" * 70)
        print(f"  {'TOTAL':.<50} {total:>4} records")
        print("-" * 70)

        return total

    def clean_all(self, skip_confirmation=False):
        """Clean all demo data"""
        total = self.show_summary()

        if total == 0:
            print("\n✓ No demo data found to clean.")
            return

        if not skip_confirmation:
            print("\n⚠️  WARNING: This will permanently delete all the records listed above!")
            print("This action cannot be undone.")
            response = input("\nType 'yes' to confirm deletion: ")

            if response.lower() != 'yes':
                print("Cleanup cancelled.")
                return

        print("\n" + "=" * 70)
        print("CLEANING DEMO DATA")
        print("=" * 70 + "\n")

        # Clean in order (dependencies first)
        self.clean_activities()
        self.clean_quotations()
        self.clean_opportunities()
        self.clean_leads()
        self.clean_customers(keep_admin=True)
        self.clean_products()
        self.clean_sales_teams(keep_defaults=True)
        self.clean_stages(keep_defaults=True)

        self.show_cleanup_report()

    def show_cleanup_report(self):
        """Show final cleanup report"""
        print("\n" + "=" * 70)
        print("CLEANUP REPORT")
        print("=" * 70)

        print("\n📊 RECORDS DELETED:")
        print("-" * 70)

        total_deleted = 0
        for model, count in self.stats.items():
            model_name = model.replace('_', ' ').replace('.', ' ').title()
            print(f"  {model_name:.<50} {count:>4} records")
            total_deleted += count

        print("-" * 70)
        print(f"  {'TOTAL DELETED':.<50} {total_deleted:>4} records")

        print("\n" + "=" * 70)
        print("✓ Cleanup completed successfully!")
        print("=" * 70 + "\n")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Clean Demo Data from GotIt CRM')
    parser.add_argument('--url', default=config.ODOO_URL, help='Odoo URL')
    parser.add_argument('--db', default=config.ODOO_DB, help='Database name')
    parser.add_argument('--user', default=config.ODOO_USERNAME, help='Username')
    parser.add_argument('--password', default=config.ODOO_PASSWORD, help='Password')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--preview', action='store_true', help='Preview only, do not delete')

    args = parser.parse_args()

    print("=" * 70)
    print("GOTIT CRM - DEMO DATA CLEANUP")
    print("=" * 70 + "\n")

    try:
        cleaner = OdooDataCleaner(args.url, args.db, args.user, args.password)

        if args.preview:
            cleaner.show_summary()
            print("\n(Preview mode - no data was deleted)")
        else:
            cleaner.clean_all(skip_confirmation=args.yes)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
