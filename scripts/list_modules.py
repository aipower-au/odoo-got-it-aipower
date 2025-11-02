#!/usr/bin/env python3
"""List all installed modules in Odoo"""

import xmlrpc.client
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print("=" * 70)
print("INSTALLED ODOO MODULES")
print("=" * 70)

# Get all installed modules
module_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.module.module', 'search',
    [[['state', '=', 'installed']]]
)

modules = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.module.module', 'read',
    [module_ids, ['name', 'shortdesc', 'category_id']]
)

# Group by category
from collections import defaultdict
by_category = defaultdict(list)

for module in modules:
    category = module['category_id'][1] if module['category_id'] else 'Uncategorized'
    by_category[category].append({
        'name': module['name'],
        'desc': module['shortdesc']
    })

# Sort categories
for category in sorted(by_category.keys()):
    print(f"\n📦 {category}")
    print("-" * 70)
    for module in sorted(by_category[category], key=lambda x: x['name']):
        print(f"  • {module['name']:30} - {module['desc']}")

print("\n" + "=" * 70)
print(f"Total installed modules: {len(modules)}")
print("=" * 70)
