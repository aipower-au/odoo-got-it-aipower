#!/usr/bin/env python3
"""Check which modules are installed in Odoo"""

import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print("=" * 70)
print("CHECKING INSTALLED ODOO MODULES")
print("=" * 70)

# Check for CRM-related modules
modules_to_check = ['crm', 'sales_team', 'sale', 'sale_management', 'base']

print("\n📦 Module Status:\n")

for module_name in modules_to_check:
    module_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.module.module', 'search',
        [[['name', '=', module_name]]]
    )

    if module_ids:
        module = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'read',
            [module_ids, ['name', 'state']]
        )[0]

        status = module['state']
        icon = "✅" if status == 'installed' else "❌"
        print(f"  {icon} {module['name']:20} - {status}")
    else:
        print(f"  ❌ {module_name:20} - not found")

print("\n" + "=" * 70)

# Check if we can access groups
print("\nChecking User Groups:\n")

groups_to_check = [
    'base.group_user',
    'sales_team.group_sale_salesman',
    'sales_team.group_sale_manager'
]

for group_xml_id in groups_to_check:
    try:
        # Try the newer method first
        group_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'search',
            [[['name', '=', group_xml_id.split('.')[1]],
              ['module', '=', group_xml_id.split('.')[0]]]]
        )

        if group_ids:
            print(f"  ✅ {group_xml_id}")
        else:
            print(f"  ❌ {group_xml_id} - not found")
    except Exception as e:
        print(f"  ❌ {group_xml_id} - error: {e}")

print("\n" + "=" * 70)
