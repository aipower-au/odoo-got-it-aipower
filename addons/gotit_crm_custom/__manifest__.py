# -*- coding: utf-8 -*-
{
    'name': 'GotIt CRM Custom',
    'version': '1.0.0',
    'category': 'Customer Relationship Management',
    'summary': 'GotIt-specific CRM extensions for Sprint 1',
    'description': """
        GotIt CRM Custom Module
        =======================
        - Enhanced customer/partner management
        - Vietnamese Tax ID (MST) integration
        - Configurable salesperson assignment
        - REST API for external systems

        Sprint 1 Features:
        - Duplicate Tax ID checking
        - Auto-assignment rules engine
        - Lead caretaker functionality
        - Status automation
        - Bulk operations
        - REST API endpoints
    """,
    'author': 'GotIt Team',
    'website': 'https://www.gotit.vn',
    'depends': [
        'base',
        'contacts',
        'crm',
        'sale',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/assignment_rule_views.xml',
        'views/api_key_views.xml',
        'views/menu_items.xml',
        'wizards/bulk_change_salesperson_views.xml',
        'data/assignment_rules_demo.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
