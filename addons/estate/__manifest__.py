# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management',
    'version': '19.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties, offers, and sales',
    'description': """
Real Estate Management
======================

This module allows you to:
* Manage real estate properties
* Track property offers and negotiations
* Handle property sales and documentation
* Generate property reports
* Manage property types and tags

Key Features:
* Property lifecycle management
* Offer management system
* Advanced search and filtering
* Kanban and calendar views
* Automated workflows
* PDF reports generation
    """,
    'author': 'AI Power',
    'website': 'https://www.aipower.com.au',
    'license': 'LGPL-3',
    'depends': [
        'base',           # Always required
        'mail',           # For messaging features
        'web',            # For web interface
    ],
    'data': [
        # Security files (load first)
        'security/ir.model.access.csv',

        # View files
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',
    ],
    'demo': [
        # Demo data files (load in order)
        'demo/estate_property_type_demo.xml',
        'demo/estate_property_tag_demo.xml',
        'demo/estate_property_demo.xml',
        'demo/estate_property_offer_demo.xml',
    ],
    'installable': True,
    'application': True,              # True if this is a main application
    'auto_install': False,           # Don't auto-install
}
