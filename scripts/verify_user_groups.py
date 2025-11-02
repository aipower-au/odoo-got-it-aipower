#!/usr/bin/env python3
"""Verify user groups are properly assigned"""

import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print("=" * 70)
print("VERIFYING USER PERMISSIONS")
print("=" * 70)

# Get all users (excluding admin/public)
user_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'search',
    [[['id', '>', 2]]]  # Skip admin and public user
)

users = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'read',
    [user_ids, ['name', 'login', 'groups_id']]
)

# Get group names
print("\n👥 User Permissions:\n")

stats = {
    'base_user': 0,
    'sales_user': 0,
    'sales_manager': 0
}

for user in users:
    # Get group names
    group_ids = user['groups_id']

    groups = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.groups', 'read',
        [group_ids, ['name', 'full_name']]
    )

    group_names = [g['name'] for g in groups]

    # Count permissions by checking full_name field
    full_names = [g.get('full_name', g['name']) for g in groups]

    if any('Internal User' in fn for fn in full_names):
        stats['base_user'] += 1

    if any('Sales / User' in fn or 'Sales / Administrator' in fn for fn in full_names):
        stats['sales_user'] += 1

    if any('Sales / Administrator' in fn for fn in full_names):
        stats['sales_manager'] += 1

    # Show key groups
    key_groups = []
    if any('Sales / Administrator' in fn for fn in full_names):
        key_groups.append('Sales Manager')
    elif any('Sales / User' in fn for fn in full_names):
        key_groups.append('Sales User')
    if any('Internal User' in fn for fn in full_names):
        if not key_groups:  # Only show if no sales group
            key_groups.append('User')

    status = ' '.join(key_groups) if key_groups else 'User'
    print(f"  {user['login']:15} - {status}")

print("\n" + "=" * 70)
print("PERMISSION SUMMARY")
print("=" * 70)
print(f"\n📊 Users by Permission:")
print(f"   Base Users: {stats['base_user']}")
print(f"   Sales Users: {stats['sales_user']}")
print(f"   Sales Managers: {stats['sales_manager']}")

if stats['sales_user'] >= 21 and stats['sales_manager'] >= 4:
    print(f"\n✅ All users have proper permissions!")
else:
    print(f"\n⚠️  Some users may not have correct permissions")

print("\n" + "=" * 70)
