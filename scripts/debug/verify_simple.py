#!/usr/bin/env python3
"""Simple verification of imported data"""

import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print("=" * 70)
print("DATA VERIFICATION")
print("=" * 70)

# Count users
users_count = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'search_count', [[]]
)

# Count teams
teams_count = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'crm.team', 'search_count', [[]]
)

# Count partners (excluding user partners)
user_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'search', [[]]
)

users = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'read',
    [user_ids, ['partner_id']]
)

user_partner_ids = [u['partner_id'][0] for u in users if u['partner_id']]

partners_count = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.partner', 'search_count',
    [[['id', 'not in', user_partner_ids]]]
)

print(f"\n📊 Record Counts:")
print(f"   Users: {users_count}")
print(f"   Sales Teams: {teams_count}")
print(f"   Customers: {partners_count}")

print(f"\n📋 Expected vs Actual:")
print(f"   Staff: Expected ~23, Actual: {users_count}")
print(f"   Teams: Expected ~7, Actual: {teams_count}")
print(f"   Customers: Expected ~100, Actual: {partners_count}")

if users_count >= 23 and teams_count >= 7 and partners_count >= 100:
    print(f"\n✅ All data imported successfully!")
else:
    print(f"\n⚠️  Some data may be missing")

print("=" * 70)
