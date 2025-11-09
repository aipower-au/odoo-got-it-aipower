# -*- coding: utf-8 -*-
{
    'name': 'GotIt CRM Automation',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Automated lead assignment with duplicate detection and sales verification',
    'description': """
        GotIt CRM Automation Module
        ============================

        Features:
        ---------
        * Lead information validation and normalization
        * Customer duplicate detection with confidence scoring
        * Automated sales assignment with configurable rules
        * Sales verification workflow for manual review
        * Comprehensive audit logging

        This module implements intelligent lead routing based on customer duplicate
        detection and sales assignment rules for the Vietnamese market.
    """,
    'author': 'GotIt CRM Team',
    'website': 'https://github.com/aipower-au/odoo-got-it-aipower',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/mail_activity_type_data.xml',

        # Views
        'views/crm_lead_views.xml',
        'views/crm_assignment_rule_views.xml',
        'views/crm_lead_audit_log_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
