#!/usr/bin/env python3
"""Show actual group names for debugging"""

import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Get a sales manager user (Lê Quốc Bảo - Sales Manager)
user_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'res.users', 'search',
    [[['login', '=', 'bảo.l']]]
)

if user_ids:
    user = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'read',
        [user_ids, ['name', 'login', 'groups_id']]
    )[0]

    print(f"\nUser: {user['name']} ({user['login']})")
    print(f"Group IDs: {user['groups_id']}\n")

    # Get group details
    groups = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.groups', 'read',
        [user['groups_id'], ['name', 'full_name']]
    )

    print("Groups:")
    for g in groups:
        print(f"  - {g['name']}")
        if g.get('full_name'):
            print(f"    Full: {g['full_name']}")
