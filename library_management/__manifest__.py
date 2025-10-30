# -*- coding: utf-8 -*-
{
    'name': 'Library Management',
    'version': '19.0.1.0.0',
    'category': 'Services/Library',
    'summary': 'Manage library books, members, and borrowing operations',
    'description': """
Library Management System
=========================
This module provides complete library management functionality including:
    * Book catalog management
    * Member registration and management
    * Book borrowing and return tracking
    * Due date monitoring
    * Book availability status
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail'],
    'data': [
        # Security
        'security/library_security.xml',
        'security/ir.model.access.csv',

        # Views
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_borrowing_views.xml',
        'views/library_menus.xml',

        # Data
        'data/library_data.xml',
    ],
    'demo': [
        'data/library_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
