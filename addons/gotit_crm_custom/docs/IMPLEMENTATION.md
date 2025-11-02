# GotIt CRM Custom - Technical Implementation Guide

**Module:** `gotit_crm_custom`
**Odoo Version:** 18.0
**Document Version:** 1.0.0
**Last Updated:** 2025-11-02

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Module Setup](#2-module-setup)
3. [Model Extensions](#3-model-extensions)
4. [Duplicate Checking Implementation](#4-duplicate-checking-implementation)
5. [Assignment Rules Engine](#5-assignment-rules-engine)
6. [Tax ID Lookup Service](#6-tax-id-lookup-service)
7. [Status Automation](#7-status-automation)
8. [Bulk Operations](#8-bulk-operations)
9. [REST API Implementation](#9-rest-api-implementation)
10. [Security Configuration](#10-security-configuration)
11. [Views and UI](#11-views-and-ui)
12. [Data Migration](#12-data-migration)
13. [Testing](#13-testing)
14. [Deployment](#14-deployment)

---

## 1. Architecture Overview

### 1.1 Design Principles

The `gotit_crm_custom` module follows Odoo 18 best practices:

- **Extension Pattern:** Uses `_inherit` to extend existing models (`res.partner`, `crm.lead`) without creating new tables
- **Mixins:** Leverages `mail.thread` and `mail.activity.mixin` for communication features
- **Security First:** Implements constraints, record rules, and API authentication
- **Separation of Concerns:** Models, views, controllers, wizards in separate directories
- **RESTful API:** HTTP controllers with JSON responses for external integration

### 1.2 Module Dependencies

```python
# __manifest__.py
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
```

### 1.3 Directory Structure

```
gotit_crm_custom/
├── __init__.py
├── __manifest__.py
├── README.md
├── docs/
│   └── IMPLEMENTATION.md (this file)
├── models/
│   ├── __init__.py
│   ├── res_partner.py          # Customer extensions
│   ├── crm_lead.py             # Lead extensions
│   ├── assignment_rule.py      # Assignment rules
│   ├── tax_id_service.py       # MST lookup
│   └── api_key.py              # API authentication
├── views/
│   ├── res_partner_views.xml
│   ├── crm_lead_views.xml
│   ├── assignment_rule_views.xml
│   └── menu_items.xml
├── wizards/
│   ├── __init__.py
│   ├── bulk_change_salesperson.py
│   └── bulk_change_salesperson_views.xml
├── controllers/
│   ├── __init__.py
│   └── api.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── data/
    └── assignment_rules_demo.xml
```

---

## 2. Module Setup

### 2.1 Root __init__.py

```python
# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import controllers

def _post_init_hook(cr, registry):
    """Called after module installation"""
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create default assignment rules if none exist
    if not env['gotit.assignment.rule'].search([]):
        env['gotit.assignment.rule'].create({
            'name': 'Default Rule',
            'sequence': 100,
            'active': True,
        })
```

### 2.2 models/__init__.py

```python
# -*- coding: utf-8 -*-

from . import res_partner
from . import crm_lead
from . import assignment_rule
from . import tax_id_service
from . import api_key
```

### 2.3 wizards/__init__.py

```python
# -*- coding: utf-8 -*-

from . import bulk_change_salesperson
```

### 2.4 controllers/__init__.py

```python
# -*- coding: utf-8 -*-

from . import api
```

---

## 3. Model Extensions

### 3.1 res.partner Extension (Customer/Partner)

**File:** `models/res_partner.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class ResPartner(models.Model):
    """
    Extend res.partner with GotIt-specific fields and business logic
    Uses EXTENSION pattern - adds fields to existing model
    """
    _inherit = 'res.partner'

    # ========== CUSTOM FIELDS ==========

    # Payment Terms (GotIt-specific)
    terms = fields.Selection([
        ('cod', 'Cash on Delivery'),
        ('net7', 'Net 7 Days'),
        ('net15', 'Net 15 Days'),
        ('net30', 'Net 30 Days'),
        ('net45', 'Net 45 Days'),
        ('net60', 'Net 60 Days'),
        ('custom', 'Custom Terms'),
    ], string='Payment Terms',
       tracking=True,
       help="Payment terms for this customer")

    # Entity Type (extends is_company)
    entity_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('government', 'Government'),
        ('ngo', 'NGO'),
    ], string='Entity Type',
       compute='_compute_entity_type',
       store=True,
       readonly=False,
       tracking=True)

    # Revenue Tracking
    purchase_revenue = fields.Monetary(
        string='Purchase Revenue',
        currency_field='currency_id',
        help="Total revenue from this customer",
        tracking=True
    )

    # Sales Policy
    sales_policy = fields.Selection([
        ('standard', 'Standard'),
        ('vip', 'VIP'),
        ('strategic', 'Strategic Partner'),
        ('government', 'Government'),
    ], string='Sales Policy',
       default='standard',
       tracking=True,
       help="Policy level for this customer")

    # Contracts relationship
    contract_ids = fields.One2many(
        'sale.order',  # Simplified - use sale.order as contracts
        'partner_id',
        string='Contracts',
        domain=[('state', 'in', ['sale', 'done'])],
        help="Active contracts for this customer"
    )

    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count'
    )

    # Multiple invoice accounts
    invoice_account_ids = fields.Many2many(
        'res.partner',
        'partner_invoice_account_rel',
        'partner_id',
        'invoice_account_id',
        string='Invoice Accounts',
        domain=[('type', '=', 'invoice')],
        help="Multiple contacts for invoicing"
    )

    # Customer categorization for assignment rules
    industry_group = fields.Selection([
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('government', 'Government'),
        ('other', 'Other'),
    ], string='Industry Group',
       help="Industry group for assignment rules")

    region = fields.Selection([
        ('north', 'North Vietnam'),
        ('central', 'Central Vietnam'),
        ('south', 'South Vietnam'),
    ], string='Region',
       compute='_compute_region',
       store=True,
       readonly=False,
       help="Geographic region for assignment rules")

    customer_type = fields.Selection([
        ('sme', 'Small/Medium Enterprise'),
        ('enterprise', 'Enterprise'),
        ('government', 'Government'),
        ('individual', 'Individual'),
    ], string='Customer Type',
       help="Customer type for assignment rules")

    order_value_range = fields.Selection([
        ('0-10m', '0 - 10M VND'),
        ('10m-50m', '10M - 50M VND'),
        ('50m-100m', '50M - 100M VND'),
        ('100m-500m', '100M - 500M VND'),
        ('500m+', '500M+ VND'),
    ], string='Order Value Range',
       compute='_compute_order_value_range',
       store=True,
       help="Expected order value range")

    # Status enhancement
    customer_status = fields.Selection([
        ('potential', 'Potential'),
        ('client', 'Client'),
        ('lost', 'Lost'),
    ], string='Customer Status',
       default='potential',
       tracking=True,
       help="Customer lifecycle status")

    # ========== COMPUTED METHODS ==========

    @api.depends('is_company')
    def _compute_entity_type(self):
        """Compute entity type based on is_company"""
        for partner in self:
            if not partner.entity_type:
                partner.entity_type = 'company' if partner.is_company else 'individual'

    @api.depends('contract_ids')
    def _compute_contract_count(self):
        """Count active contracts"""
        for partner in self:
            partner.contract_count = len(partner.contract_ids)

    @api.depends('city', 'state_id')
    def _compute_region(self):
        """Compute region based on city/state"""
        # Simplified mapping - extend based on actual Vietnamese provinces
        north_cities = ['Hanoi', 'Ha Noi', 'Hai Phong', 'Quang Ninh']
        central_cities = ['Da Nang', 'Hue', 'Quang Nam']
        south_cities = ['Ho Chi Minh', 'Saigon', 'Binh Duong', 'Dong Nai']

        for partner in self:
            if not partner.region and partner.city:
                city = partner.city.strip()
                if any(nc in city for nc in north_cities):
                    partner.region = 'north'
                elif any(cc in city for cc in central_cities):
                    partner.region = 'central'
                elif any(sc in city for sc in south_cities):
                    partner.region = 'south'

    @api.depends('purchase_revenue')
    def _compute_order_value_range(self):
        """Compute order value range from revenue"""
        for partner in self:
            revenue = partner.purchase_revenue
            if revenue == 0:
                partner.order_value_range = '0-10m'
            elif revenue < 10000000:
                partner.order_value_range = '0-10m'
            elif revenue < 50000000:
                partner.order_value_range = '10m-50m'
            elif revenue < 100000000:
                partner.order_value_range = '50m-100m'
            elif revenue < 500000000:
                partner.order_value_range = '100m-500m'
            else:
                partner.order_value_range = '500m+'

    # ========== CONSTRAINTS ==========

    _sql_constraints = [
        ('vat_unique',
         'UNIQUE(vat)',
         'Tax ID must be unique! This Tax ID already exists in the system.'),
    ]

    @api.constrains('vat', 'phone', 'email', 'user_id')
    def _check_duplicate_contact_info(self):
        """
        Enforce business rule: Duplicate contact info must have same salesperson
        Checks phone/email duplication and ensures same user_id
        """
        for partner in self:
            if not partner.user_id:
                continue

            # Check for duplicate phone
            if partner.phone:
                duplicates = self.search([
                    ('id', '!=', partner.id),
                    ('phone', '=', partner.phone),
                    ('user_id', '!=', False),
                    ('user_id', '!=', partner.user_id.id),
                ], limit=1)

                if duplicates:
                    raise ValidationError(_(
                        "Phone number %(phone)s is already used by %(partner)s "
                        "with salesperson %(user)s. Duplicate contacts must have "
                        "the same salesperson.",
                        phone=partner.phone,
                        partner=duplicates[0].name,
                        user=duplicates[0].user_id.name
                    ))

            # Check for duplicate email
            if partner.email:
                duplicates = self.search([
                    ('id', '!=', partner.id),
                    ('email', '=', partner.email),
                    ('user_id', '!=', False),
                    ('user_id', '!=', partner.user_id.id),
                ], limit=1)

                if duplicates:
                    raise ValidationError(_(
                        "Email %(email)s is already used by %(partner)s "
                        "with salesperson %(user)s. Duplicate contacts must have "
                        "the same salesperson.",
                        email=partner.email,
                        partner=duplicates[0].name,
                        user=duplicates[0].user_id.name
                    ))

    # ========== ONCHANGE METHODS ==========

    @api.onchange('vat')
    def _onchange_vat_check_duplicate(self):
        """Warn user if Tax ID already exists"""
        if self.vat:
            existing = self.search([
                ('id', '!=', self.id or 0),
                ('vat', '=', self.vat)
            ], limit=1)

            if existing:
                return {
                    'warning': {
                        'title': _("Duplicate Tax ID"),
                        'message': _(
                            "Tax ID %(vat)s already exists for %(partner)s. "
                            "You cannot create a duplicate.",
                            vat=self.vat,
                            partner=existing.name
                        )
                    }
                }

    # ========== CRUD OVERRIDES ==========

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to apply auto-assignment and status logic"""
        partners = super().create(vals_list)

        for partner in partners:
            # Auto-assign salesperson if not set
            if not partner.user_id and partner.is_company:
                partner._auto_assign_salesperson()

            # Set initial status
            if not partner.customer_status:
                partner.customer_status = 'potential'

        return partners

    def write(self, vals):
        """Override write to handle status transitions"""
        result = super().write(vals)

        # Auto-transition to client status when conditions met
        for partner in self:
            if partner.customer_status == 'potential':
                if partner._check_client_conditions():
                    partner.customer_status = 'client'

        return result

    # ========== BUSINESS METHODS ==========

    def _auto_assign_salesperson(self):
        """
        Auto-assign salesperson based on assignment rules
        Called during partner creation
        """
        self.ensure_one()

        AssignmentRule = self.env['gotit.assignment.rule']
        rule = AssignmentRule._find_matching_rule(self)

        if rule and rule.assigned_user_id:
            self.user_id = rule.assigned_user_id
            self.message_post(
                body=_("Salesperson auto-assigned to %s based on rule: %s") % (
                    rule.assigned_user_id.name,
                    rule.name
                )
            )

    def _check_client_conditions(self):
        """
        Check if partner should be transitioned to 'client' status
        Conditions: Has at least one confirmed sale order
        """
        self.ensure_one()
        return bool(self.sale_order_count > 0)

    def action_lookup_tax_id(self):
        """
        Trigger Tax ID lookup service
        Called from button in form view
        """
        self.ensure_one()

        if not self.vat:
            raise UserError(_("Please enter a Tax ID before lookup"))

        TaxIDService = self.env['gotit.tax.id.service']
        company_data = TaxIDService.lookup_company_by_vat(self.vat)

        if company_data:
            self.write(company_data)
            self.message_post(
                body=_("Company information updated from Tax ID: %s") % self.vat
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Company information loaded from Tax ID'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Not Found'),
                    'message': _('No information found for Tax ID: %s') % self.vat,
                    'type': 'warning',
                    'sticky': False,
                }
            }

    def action_view_contracts(self):
        """Open contract list for this partner"""
        self.ensure_one()
        return {
            'name': _('Contracts'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id), ('state', 'in', ['sale', 'done'])],
            'context': {'default_partner_id': self.id},
        }
```

### 3.2 crm.lead Extension (Lead Management)

**File:** `models/crm_lead.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    """
    Extend crm.lead with lead caretaker and auto-assignment
    """
    _inherit = 'crm.lead'

    # Lead caretaker (pre-identification assignment)
    lead_caretaker_id = fields.Many2one(
        'res.users',
        string='Lead Caretaker',
        tracking=True,
        help="Temporary caretaker before customer/salesperson identified"
    )

    # Assignment history
    assignment_history = fields.Text(
        string='Assignment History',
        readonly=True,
        help="Track salesperson changes"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-assign based on rules"""
        leads = super().create(vals_list)

        for lead in leads:
            # Check if partner already exists with assigned salesperson
            if lead.partner_id and lead.partner_id.user_id:
                # Return lead to customer's salesperson
                lead.user_id = lead.partner_id.user_id
                lead.message_post(
                    body=_("Lead assigned to customer's salesperson: %s") %
                    lead.user_id.name
                )
            elif not lead.user_id:
                # Auto-assign based on rules
                lead._auto_assign_lead()

        return leads

    def write(self, vals):
        """Track assignment changes"""
        # Track user_id changes
        if 'user_id' in vals:
            for lead in self:
                old_user = lead.user_id.name if lead.user_id else 'None'
                new_user = self.env['res.users'].browse(vals['user_id']).name if vals['user_id'] else 'None'

                history = lead.assignment_history or ''
                history += f"\n{fields.Datetime.now()}: {old_user} → {new_user}"
                vals['assignment_history'] = history

        return super().write(vals)

    def _auto_assign_lead(self):
        """Auto-assign lead based on assignment rules"""
        self.ensure_one()

        AssignmentRule = self.env['gotit.assignment.rule']

        # Create temporary partner object for rule matching
        temp_partner = self.env['res.partner'].new({
            'industry_group': self._infer_industry(),
            'region': self._infer_region(),
            'customer_type': self._infer_customer_type(),
            'order_value_range': self._infer_value_range(),
        })

        rule = AssignmentRule._find_matching_rule(temp_partner)

        if rule:
            if not self.partner_id or not self.partner_id.user_id:
                # Assign to caretaker first
                self.lead_caretaker_id = rule.assigned_user_id
                self.message_post(
                    body=_("Lead caretaker assigned: %s (Rule: %s)") % (
                        rule.assigned_user_id.name,
                        rule.name
                    )
                )
            else:
                # Direct assignment
                self.user_id = rule.assigned_user_id

    def _infer_industry(self):
        """Infer industry from lead data"""
        # Simplified - extend with keyword matching
        return 'other'

    def _infer_region(self):
        """Infer region from lead data"""
        # Use city/state if available
        if self.city:
            north_cities = ['Hanoi', 'Ha Noi', 'Hai Phong']
            central_cities = ['Da Nang', 'Hue']
            south_cities = ['Ho Chi Minh', 'Saigon']

            if any(nc in self.city for nc in north_cities):
                return 'north'
            elif any(cc in self.city for cc in central_cities):
                return 'central'
            elif any(sc in self.city for sc in south_cities):
                return 'south'
        return False

    def _infer_customer_type(self):
        """Infer customer type from lead data"""
        # Simplified logic
        if self.type == 'opportunity' and self.expected_revenue > 100000000:
            return 'enterprise'
        return 'sme'

    def _infer_value_range(self):
        """Infer value range from expected revenue"""
        if not self.expected_revenue:
            return '0-10m'

        revenue = self.expected_revenue
        if revenue < 10000000:
            return '0-10m'
        elif revenue < 50000000:
            return '10m-50m'
        elif revenue < 100000000:
            return '50m-100m'
        elif revenue < 500000000:
            return '100m-500m'
        else:
            return '500m+'
```

---

## 4. Duplicate Checking Implementation

### 4.1 SQL Constraint (Database Level)

Already implemented in `res_partner.py`:

```python
_sql_constraints = [
    ('vat_unique',
     'UNIQUE(vat)',
     'Tax ID must be unique! This Tax ID already exists in the system.'),
]
```

This creates a PostgreSQL unique constraint on the `vat` column.

### 4.2 Python Constraint (Application Level)

```python
@api.constrains('vat', 'phone', 'email', 'user_id')
def _check_duplicate_contact_info(self):
    """
    Multi-field duplicate checking with salesperson enforcement
    """
    for partner in self:
        if not partner.user_id:
            continue

        # Build dynamic domain for checking
        domains = []

        if partner.phone:
            domains.append([
                ('id', '!=', partner.id),
                ('phone', '=', partner.phone),
                ('user_id', '!=', False),
                ('user_id', '!=', partner.user_id.id),
            ])

        if partner.email:
            domains.append([
                ('id', '!=', partner.id),
                ('email', '=', partner.email),
                ('user_id', '!=', False),
                ('user_id', '!=', partner.user_id.id),
            ])

        for domain in domains:
            duplicates = self.search(domain, limit=1)
            if duplicates:
                field_name = 'phone' if 'phone' in str(domain) else 'email'
                field_value = partner.phone if field_name == 'phone' else partner.email

                raise ValidationError(_(
                    "%(field)s '%(value)s' is already used by %(partner)s "
                    "with salesperson %(user)s. Duplicate contacts must have "
                    "the same salesperson.",
                    field=field_name.title(),
                    value=field_value,
                    partner=duplicates[0].name,
                    user=duplicates[0].user_id.name
                ))
```

### 4.3 UI Warning (User Experience)

```python
@api.onchange('vat')
def _onchange_vat_check_duplicate(self):
    """Show warning before save"""
    if self.vat:
        existing = self.search([
            ('id', '!=', self.id or 0),
            ('vat', '=', self.vat)
        ], limit=1)

        if existing:
            return {
                'warning': {
                    'title': _("Duplicate Tax ID"),
                    'message': _("Tax ID %(vat)s already exists for %(partner)s"),
                }
            }
```

---

## 5. Assignment Rules Engine

### 5.1 Assignment Rule Model

**File:** `models/assignment_rule.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AssignmentRule(models.Model):
    """
    Configurable rules for salesperson assignment
    Rules are evaluated by sequence (priority)
    """
    _name = 'gotit.assignment.rule'
    _description = 'Salesperson Assignment Rule'
    _order = 'sequence, id'

    name = fields.Char(
        string='Rule Name',
        required=True,
        help="Descriptive name for this rule"
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help="Inactive rules are not evaluated"
    )

    sequence = fields.Integer(
        string='Priority',
        default=10,
        help="Lower number = higher priority. Rules evaluated in order."
    )

    # Matching criteria (all must match if set)
    industry_group = fields.Selection([
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('government', 'Government'),
        ('other', 'Other'),
    ], string='Industry Group',
       help="Match this industry (leave empty to match any)")

    region = fields.Selection([
        ('north', 'North Vietnam'),
        ('central', 'Central Vietnam'),
        ('south', 'South Vietnam'),
    ], string='Region',
       help="Match this region (leave empty to match any)")

    customer_type = fields.Selection([
        ('sme', 'Small/Medium Enterprise'),
        ('enterprise', 'Enterprise'),
        ('government', 'Government'),
        ('individual', 'Individual'),
    ], string='Customer Type',
       help="Match this customer type (leave empty to match any)")

    order_value_range = fields.Selection([
        ('0-10m', '0 - 10M VND'),
        ('10m-50m', '10M - 50M VND'),
        ('50m-100m', '50M - 100M VND'),
        ('100m-500m', '100M - 500M VND'),
        ('500m+', '500M+ VND'),
    ], string='Order Value Range',
       help="Match this value range (leave empty to match any)")

    # Assignment target
    assigned_user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        required=True,
        domain=[('share', '=', False)],  # Only internal users
        help="Salesperson to assign when rule matches"
    )

    # Statistics
    assignment_count = fields.Integer(
        string='Assignments',
        readonly=True,
        help="Number of times this rule has been applied"
    )

    last_assignment_date = fields.Datetime(
        string='Last Assignment',
        readonly=True,
        help="Last time this rule was used"
    )

    @api.model
    def _find_matching_rule(self, partner):
        """
        Find first matching rule for a partner
        Returns: gotit.assignment.rule record or False
        """
        rules = self.search([('active', '=', True)], order='sequence, id')

        for rule in rules:
            if rule._matches(partner):
                # Update statistics
                rule.write({
                    'assignment_count': rule.assignment_count + 1,
                    'last_assignment_date': fields.Datetime.now(),
                })
                return rule

        return False

    def _matches(self, partner):
        """
        Check if partner matches this rule
        All non-empty criteria must match
        """
        self.ensure_one()

        # Industry check
        if self.industry_group and partner.industry_group != self.industry_group:
            return False

        # Region check
        if self.region and partner.region != self.region:
            return False

        # Customer type check
        if self.customer_type and partner.customer_type != self.customer_type:
            return False

        # Order value range check
        if self.order_value_range and partner.order_value_range != self.order_value_range:
            return False

        # All criteria matched
        return True

    def action_view_assignments(self):
        """View partners assigned by this rule"""
        self.ensure_one()

        # Find partners assigned to this rule's user with matching criteria
        domain = [('user_id', '=', self.assigned_user_id.id)]

        if self.industry_group:
            domain.append(('industry_group', '=', self.industry_group))
        if self.region:
            domain.append(('region', '=', self.region))
        if self.customer_type:
            domain.append(('customer_type', '=', self.customer_type))

        return {
            'name': _('Assigned Partners'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': domain,
        }
```

---

## 6. Tax ID Lookup Service

### 6.1 Mock Implementation

**File:** `models/tax_id_service.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, models, _
import random

class TaxIDService(models.AbstractModel):
    """
    Mock service for Vietnamese Tax ID (MST) lookup
    Replace with real API integration in production
    """
    _name = 'gotit.tax.id.service'
    _description = 'Tax ID Lookup Service'

    @api.model
    def lookup_company_by_vat(self, vat):
        """
        Lookup company information by Tax ID

        Args:
            vat (str): Vietnamese Tax ID (MST)

        Returns:
            dict: Company information or False if not found
        """
        # Mock implementation - returns dummy data
        # TODO: Replace with real API call to Vietnamese MST database

        if not vat or len(vat) < 10:
            return False

        # Simulate API call
        company_data = self._mock_api_call(vat)

        return company_data

    def _mock_api_call(self, vat):
        """
        Simulate third-party API response
        Returns realistic Vietnamese company data
        """
        # Mock company names
        company_names = [
            'Công ty TNHH %s Việt Nam' % ('Technology', 'Solutions', 'Innovations'),
            'Công ty Cổ phần %s' % ('Phát triển Phần mềm', 'Thương mại', 'Dịch vụ'),
            '%s Co., Ltd.' % ('Vietnam Tech', 'Saigon Solutions', 'Hanoi Innovations'),
        ]

        # Mock addresses
        addresses = [
            {'street': 'Số 123 Đường Lê Lợi', 'city': 'Hanoi', 'zip': '100000'},
            {'street': '456 Nguyễn Huệ', 'city': 'Ho Chi Minh', 'zip': '700000'},
            {'street': '789 Trần Phú', 'city': 'Da Nang', 'zip': '550000'},
        ]

        # Select random data
        company_name = random.choice(company_names)
        address = random.choice(addresses)

        return {
            'name': company_name,
            'street': address['street'],
            'city': address['city'],
            'zip': address['zip'],
            'country_id': self.env.ref('base.vn').id,  # Vietnam
            'phone': '+84 %d %d %d' % (
                random.randint(20, 99),
                random.randint(100, 999),
                random.randint(1000, 9999)
            ),
            'email': 'info@%s.vn' % vat.lower(),
            'is_company': True,
        }

    @api.model
    def integrate_real_api(self, api_url, api_key):
        """
        Template method for real API integration

        Args:
            api_url (str): API endpoint URL
            api_key (str): API authentication key

        Example:
            import requests

            response = requests.get(
                f"{api_url}/lookup",
                params={'vat': vat},
                headers={'Authorization': f'Bearer {api_key}'}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('company_name'),
                    'street': data.get('address'),
                    'city': data.get('city'),
                    ...
                }
        """
        pass
```

---

## 7. Status Automation

### 7.1 Auto-transition Logic

Already implemented in `res_partner.py`:

```python
def write(self, vals):
    """Override write to handle status transitions"""
    result = super().write(vals)

    # Auto-transition to client status when conditions met
    for partner in self:
        if partner.customer_status == 'potential':
            if partner._check_client_conditions():
                partner.customer_status = 'client'
                partner.message_post(
                    body=_("Status automatically changed to Client")
                )

    return result

def _check_client_conditions(self):
    """
    Check if partner should be transitioned to 'client' status
    Condition: Has at least one confirmed sale order (account created)
    """
    self.ensure_one()
    return bool(self.sale_order_count > 0)
```

### 7.2 Scheduled Action (Optional)

For batch status updates, create a scheduled action:

**File:** `data/ir_cron.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="ir_cron_update_customer_status" model="ir.cron">
        <field name="name">Update Customer Status</field>
        <field name="model_id" ref="base.model_res_partner"/>
        <field name="state">code</field>
        <field name="code">model._cron_update_customer_status()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

**Python method:**

```python
@api.model
def _cron_update_customer_status(self):
    """Batch update customer statuses"""
    potential_customers = self.search([
        ('customer_status', '=', 'potential'),
        ('sale_order_count', '>', 0)
    ])

    for customer in potential_customers:
        customer.customer_status = 'client'
```

---

## 8. Bulk Operations

### 8.1 Bulk Change Salesperson Wizard

**File:** `wizards/bulk_change_salesperson.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BulkChangeSalesperson(models.TransientModel):
    """
    Wizard for bulk changing salesperson on partners or leads
    """
    _name = 'wizard.bulk.change.salesperson'
    _description = 'Bulk Change Salesperson'

    model_name = fields.Selection([
        ('res.partner', 'Customers'),
        ('crm.lead', 'Leads'),
    ], string='Apply To',
       required=True,
       default='res.partner')

    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        help="Customers to update"
    )

    lead_ids = fields.Many2many(
        'crm.lead',
        string='Leads',
        help="Leads to update"
    )

    new_user_id = fields.Many2one(
        'res.users',
        string='New Salesperson',
        required=True,
        domain=[('share', '=', False)],
        help="Salesperson to assign to selected records"
    )

    @api.model
    def default_get(self, fields_list):
        """Load selected records from context"""
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'res.partner':
            res['model_name'] = 'res.partner'
            res['partner_ids'] = [(6, 0, active_ids)]
        elif active_model == 'crm.lead':
            res['model_name'] = 'crm.lead'
            res['lead_ids'] = [(6, 0, active_ids)]

        return res

    def action_apply(self):
        """Apply salesperson change to selected records"""
        self.ensure_one()

        if self.model_name == 'res.partner':
            if not self.partner_ids:
                raise UserError(_("Please select at least one customer"))

            self.partner_ids.write({'user_id': self.new_user_id.id})

            # Post message on each partner
            for partner in self.partner_ids:
                partner.message_post(
                    body=_("Salesperson changed to %s via bulk operation") %
                    self.new_user_id.name
                )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Salesperson updated for %d customers') % len(self.partner_ids),
                    'type': 'success',
                    'sticky': False,
                }
            }

        elif self.model_name == 'crm.lead':
            if not self.lead_ids:
                raise UserError(_("Please select at least one lead"))

            self.lead_ids.write({'user_id': self.new_user_id.id})

            for lead in self.lead_ids:
                lead.message_post(
                    body=_("Salesperson changed to %s via bulk operation") %
                    self.new_user_id.name
                )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Salesperson updated for %d leads') % len(self.lead_ids),
                    'type': 'success',
                    'sticky': False,
                }
            }
```

### 8.2 Wizard View

**File:** `wizards/bulk_change_salesperson_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_bulk_change_salesperson_form" model="ir.ui.view">
        <field name="name">wizard.bulk.change.salesperson.form</field>
        <field name="model">wizard.bulk.change.salesperson</field>
        <field name="arch" type="xml">
            <form string="Bulk Change Salesperson">
                <group>
                    <field name="model_name" invisible="1"/>
                    <field name="partner_ids" widget="many2many_tags"
                           invisible="model_name != 'res.partner'"/>
                    <field name="lead_ids" widget="many2many_tags"
                           invisible="model_name != 'crm.lead'"/>
                    <field name="new_user_id" options="{'no_create': True}"/>
                </group>
                <footer>
                    <button string="Apply" name="action_apply" type="object"
                            class="btn-primary" data-hotkey="q"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"
                            data-hotkey="z"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_bulk_change_salesperson" model="ir.actions.act_window">
        <field name="name">Change Salesperson</field>
        <field name="res_model">wizard.bulk.change.salesperson</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="base.model_res_partner"/>
        <field name="binding_view_types">list</field>
    </record>

    <record id="action_wizard_bulk_change_salesperson_leads" model="ir.actions.act_window">
        <field name="name">Change Salesperson</field>
        <field name="res_model">wizard.bulk.change.salesperson</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="crm.model_crm_lead"/>
        <field name="binding_view_types">list</field>
    </record>
</odoo>
```

---

## 9. REST API Implementation

### 9.1 API Key Model

**File:** `models/api_key.py`

```python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied
import secrets

class APIKey(models.Model):
    """
    API keys for external system authentication
    """
    _name = 'gotit.api.key'
    _description = 'API Key'

    name = fields.Char(
        string='Name',
        required=True,
        help="Descriptive name for this API key"
    )

    key = fields.Char(
        string='API Key',
        required=True,
        readonly=True,
        default=lambda self: self._generate_key(),
        help="API key for authentication"
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help="Inactive keys cannot be used"
    )

    allowed_ips = fields.Text(
        string='Allowed IPs',
        help="Comma-separated list of allowed IP addresses (leave empty for any)"
    )

    last_used_date = fields.Datetime(
        string='Last Used',
        readonly=True
    )

    usage_count = fields.Integer(
        string='Usage Count',
        readonly=True,
        default=0
    )

    @api.model
    def _generate_key(self):
        """Generate secure random API key"""
        return secrets.token_urlsafe(32)

    @api.model
    def authenticate(self, key, ip_address=None):
        """
        Validate API key

        Args:
            key (str): API key to validate
            ip_address (str): Client IP address

        Returns:
            gotit.api.key record if valid, raises AccessDenied otherwise
        """
        api_key = self.search([('key', '=', key), ('active', '=', True)], limit=1)

        if not api_key:
            raise AccessDenied(_("Invalid API key"))

        # Check IP whitelist if configured
        if api_key.allowed_ips and ip_address:
            allowed_ips = [ip.strip() for ip in api_key.allowed_ips.split(',')]
            if ip_address not in allowed_ips:
                raise AccessDenied(_("IP address not allowed"))

        # Update usage statistics
        api_key.write({
            'last_used_date': fields.Datetime.now(),
            'usage_count': api_key.usage_count + 1,
        })

        return api_key
```

### 9.2 API Controller

**File:** `controllers/api.py`

```python
# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import AccessDenied, ValidationError, UserError
import json
import logging

_logger = logging.getLogger(__name__)

class GotItAPI(http.Controller):
    """
    REST API endpoints for external systems
    """

    def _authenticate_request(self):
        """
        Authenticate API request using Bearer token
        Returns: True if authenticated, raises AccessDenied otherwise
        """
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied(_("Missing or invalid Authorization header"))

        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        client_ip = request.httprequest.remote_addr

        # Validate API key
        APIKey = request.env['gotit.api.key'].sudo()
        APIKey.authenticate(api_key, client_ip)

        return True

    def _json_response(self, data, status=200):
        """Helper to return JSON response"""
        return Response(
            json.dumps(data, default=str, ensure_ascii=False),
            status=status,
            mimetype='application/json'
        )

    def _error_response(self, error, message, status=400, field=None):
        """Helper to return error response"""
        response_data = {
            'error': error,
            'message': message,
        }
        if field:
            response_data['field'] = field

        return self._json_response(response_data, status=status)

    @http.route('/api/customer/create', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def api_create_customer(self):
        """
        Create a new customer via API

        POST /api/customer/create
        Headers:
            Authorization: Bearer YOUR_API_KEY
            Content-Type: application/json

        Body:
            {
                "name": "Company Name",
                "vat": "0123456789",
                "phone": "+84912345678",
                "email": "contact@company.com",
                "street": "123 Main St",
                "city": "Hanoi",
                "customer_type": "enterprise",
                "industry_group": "technology"
            }

        Response:
            {
                "success": true,
                "partner_id": 123,
                "name": "Company Name",
                "assigned_salesperson": "John Doe",
                "message": "Customer created successfully"
            }
        """
        try:
            # Authenticate
            self._authenticate_request()

            # Parse request body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return self._error_response(
                    'Invalid JSON',
                    'Request body must be valid JSON',
                    status=400
                )

            # Validate required fields
            required_fields = ['name']
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return self._error_response(
                    'Missing Fields',
                    f"Required fields missing: {', '.join(missing_fields)}",
                    status=400
                )

            # Create partner
            Partner = request.env['res.partner'].sudo()

            # Map API fields to Odoo fields
            partner_vals = {
                'name': data.get('name'),
                'vat': data.get('vat'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'street': data.get('street'),
                'city': data.get('city'),
                'zip': data.get('zip'),
                'is_company': True,
                'customer_type': data.get('customer_type'),
                'industry_group': data.get('industry_group'),
                'region': data.get('region'),
                'terms': data.get('terms'),
                'sales_policy': data.get('sales_policy'),
            }

            # Remove None values
            partner_vals = {k: v for k, v in partner_vals.items() if v is not None}

            try:
                partner = Partner.create(partner_vals)

                response_data = {
                    'success': True,
                    'partner_id': partner.id,
                    'name': partner.name,
                    'assigned_salesperson': partner.user_id.name if partner.user_id else None,
                    'message': 'Customer created successfully'
                }

                _logger.info(f"Customer created via API: {partner.name} (ID: {partner.id})")

                return self._json_response(response_data, status=201)

            except ValidationError as e:
                return self._error_response(
                    'Validation Error',
                    str(e),
                    status=400
                )

        except AccessDenied as e:
            return self._error_response(
                'Authentication Failed',
                str(e),
                status=401
            )

        except Exception as e:
            _logger.exception("API error creating customer")
            return self._error_response(
                'Server Error',
                'An unexpected error occurred',
                status=500
            )

    @http.route('/api/lead/create', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def api_create_lead(self):
        """
        Create a new lead via API

        POST /api/lead/create
        Headers:
            Authorization: Bearer YOUR_API_KEY
            Content-Type: application/json

        Body:
            {
                "name": "Lead Name",
                "contact_name": "Contact Person",
                "email": "contact@example.com",
                "phone": "+84987654321",
                "description": "Lead description",
                "source": "website"
            }

        Response:
            {
                "success": true,
                "lead_id": 456,
                "lead_name": "Lead Name",
                "assigned_to": "Jane Smith",
                "message": "Lead created successfully"
            }
        """
        try:
            # Authenticate
            self._authenticate_request()

            # Parse request body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return self._error_response(
                    'Invalid JSON',
                    'Request body must be valid JSON',
                    status=400
                )

            # Validate required fields
            required_fields = ['name']
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return self._error_response(
                    'Missing Fields',
                    f"Required fields missing: {', '.join(missing_fields)}",
                    status=400
                )

            # Create lead
            Lead = request.env['crm.lead'].sudo()

            lead_vals = {
                'name': data.get('name'),
                'contact_name': data.get('contact_name'),
                'email_from': data.get('email'),
                'phone': data.get('phone'),
                'description': data.get('description'),
                'source_id': self._get_source_id(data.get('source')),
                'type': 'lead',
            }

            # Remove None values
            lead_vals = {k: v for k, v in lead_vals.items() if v is not None}

            try:
                lead = Lead.create(lead_vals)

                response_data = {
                    'success': True,
                    'lead_id': lead.id,
                    'lead_name': lead.name,
                    'assigned_to': lead.user_id.name if lead.user_id else (
                        lead.lead_caretaker_id.name if lead.lead_caretaker_id else None
                    ),
                    'message': 'Lead created successfully'
                }

                _logger.info(f"Lead created via API: {lead.name} (ID: {lead.id})")

                return self._json_response(response_data, status=201)

            except ValidationError as e:
                return self._error_response(
                    'Validation Error',
                    str(e),
                    status=400
                )

        except AccessDenied as e:
            return self._error_response(
                'Authentication Failed',
                str(e),
                status=401
            )

        except Exception as e:
            _logger.exception("API error creating lead")
            return self._error_response(
                'Server Error',
                'An unexpected error occurred',
                status=500
            )

    def _get_source_id(self, source_name):
        """Get or create lead source"""
        if not source_name:
            return False

        Source = request.env['utm.source'].sudo()
        source = Source.search([('name', '=ilike', source_name)], limit=1)

        if not source:
            source = Source.create({'name': source_name})

        return source.id

    @http.route('/api/health', type='http', auth='public', methods=['GET'], csrf=False)
    def api_health_check(self):
        """
        Health check endpoint
        GET /api/health
        """
        return self._json_response({
            'status': 'healthy',
            'service': 'GotIt CRM API',
            'version': '1.0.0'
        })
```

---

## 10. Security Configuration

### 10.1 Access Rights (CSV)

**File:** `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_assignment_rule_user,gotit.assignment.rule.user,model_gotit_assignment_rule,sales_team.group_sale_salesman,1,0,0,0
access_assignment_rule_manager,gotit.assignment.rule.manager,model_gotit_assignment_rule,sales_team.group_sale_manager,1,1,1,1
access_api_key_manager,gotit.api.key.manager,model_gotit_api_key,base.group_system,1,1,1,1
```

### 10.2 Record Rules (XML)

**File:** `security/security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <!-- Partner: Users see own customers -->
        <record id="res_partner_rule_own" model="ir.rule">
            <field name="name">Partners: Own Customers Only</field>
            <field name="model_id" ref="base.model_res_partner"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Partner: Managers see all -->
        <record id="res_partner_rule_manager" model="ir.rule">
            <field name="name">Partners: Managers See All</field>
            <field name="model_id" ref="base.model_res_partner"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
        </record>

        <!-- Lead: Users see own leads -->
        <record id="crm_lead_rule_own" model="ir.rule">
            <field name="name">Leads: Own Leads Only</field>
            <field name="model_id" ref="crm.model_crm_lead"/>
            <field name="domain_force">['|', ('user_id', '=', user.id), ('lead_caretaker_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>

    </data>
</odoo>
```

---

## 11. Views and UI

### 11.1 Partner Form View

**File:** `views/res_partner_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Partner Form View Extension -->
    <record id="view_partner_form_gotit" model="ir.ui.view">
        <field name="name">res.partner.form.gotit</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">

            <!-- Add button in header -->
            <header position="inside">
                <button name="action_lookup_tax_id" string="Lookup by MST"
                        type="object" class="btn-primary"
                        invisible="not vat or not is_company"/>
            </header>

            <!-- Add status bar -->
            <xpath expr="//sheet" position="before">
                <header>
                    <field name="customer_status" widget="statusbar"
                           options="{'clickable': '1'}"
                           invisible="not is_company"/>
                </header>
            </xpath>

            <!-- Add GotIt custom fields in Sales & Purchases tab -->
            <xpath expr="//notebook/page[@name='sales_purchases']" position="inside">
                <group string="GotIt Information" name="gotit_info">
                    <group>
                        <field name="terms"/>
                        <field name="entity_type"/>
                        <field name="sales_policy"/>
                        <field name="purchase_revenue" widget="monetary"/>
                    </group>
                    <group>
                        <field name="industry_group"/>
                        <field name="region"/>
                        <field name="customer_type"/>
                        <field name="order_value_range"/>
                    </group>
                </group>

                <group string="Contracts" name="contracts">
                    <field name="contract_count"/>
                    <button name="action_view_contracts" string="View Contracts"
                            type="object" class="oe_link"
                            invisible="contract_count == 0"/>
                </group>

                <group string="Invoice Accounts" name="invoice_accounts">
                    <field name="invoice_account_ids" widget="many2many_tags"/>
                </group>
            </xpath>

        </field>
    </record>

</odoo>
```

### 11.2 Assignment Rules Views

**File:** `views/assignment_rule_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Assignment Rule Tree View -->
    <record id="view_assignment_rule_tree" model="ir.ui.view">
        <field name="name">gotit.assignment.rule.tree</field>
        <field name="model">gotit.assignment.rule</field>
        <field name="arch" type="xml">
            <tree string="Assignment Rules" default_order="sequence">
                <field name="sequence" widget="handle"/>
                <field name="name"/>
                <field name="industry_group"/>
                <field name="region"/>
                <field name="customer_type"/>
                <field name="order_value_range"/>
                <field name="assigned_user_id"/>
                <field name="assignment_count"/>
                <field name="active" widget="boolean_toggle"/>
            </tree>
        </field>
    </record>

    <!-- Assignment Rule Form View -->
    <record id="view_assignment_rule_form" model="ir.ui.view">
        <field name="name">gotit.assignment.rule.form</field>
        <field name="model">gotit.assignment.rule</field>
        <field name="arch" type="xml">
            <form string="Assignment Rule">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_assignments" type="object"
                                class="oe_stat_button" icon="fa-users">
                            <field name="assignment_count" widget="statinfo"
                                   string="Assignments"/>
                        </button>
                    </div>

                    <widget name="web_ribbon" title="Archived"
                            bg_color="bg-danger"
                            invisible="active"/>

                    <group>
                        <group>
                            <field name="name"/>
                            <field name="sequence"/>
                            <field name="active" widget="boolean_toggle"/>
                        </group>
                        <group>
                            <field name="assigned_user_id"/>
                            <field name="last_assignment_date"/>
                        </group>
                    </group>

                    <notebook>
                        <page string="Matching Criteria" name="criteria">
                            <group>
                                <group string="Customer Profile">
                                    <field name="industry_group"/>
                                    <field name="region"/>
                                    <field name="customer_type"/>
                                </group>
                                <group string="Order Information">
                                    <field name="order_value_range"/>
                                </group>
                            </group>

                            <div class="alert alert-info" role="alert">
                                <strong>Note:</strong> All specified criteria must match for this rule to apply.
                                Leave fields empty to match any value.
                            </div>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Assignment Rule Action -->
    <record id="action_assignment_rule" model="ir.actions.act_window">
        <field name="name">Assignment Rules</field>
        <field name="res_model">gotit.assignment.rule</field>
        <field name="view_mode">tree,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first assignment rule
            </p>
            <p>
                Assignment rules automatically assign salespersons based on
                customer characteristics like industry, region, and order value.
            </p>
        </field>
    </record>

</odoo>
```

### 11.3 Menu Items

**File:** `views/menu_items.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Configuration Menu -->
    <menuitem id="menu_gotit_crm_configuration"
              name="GotIt CRM"
              parent="sales_team.menu_sale_config"
              sequence="100"/>

    <menuitem id="menu_assignment_rules"
              name="Assignment Rules"
              parent="menu_gotit_crm_configuration"
              action="action_assignment_rule"
              sequence="10"/>

</odoo>
```

---

## 12. Data Migration

### 12.1 Update Import Scripts

**Update:** `scripts/import_customers_enterprise.py`

Add the following field mappings:

```python
# After line 115 (where partner_vals is defined)

partner_vals = {
    'name': row['company_name'],
    'vat': row['tax_id'],
    'phone': row['phone'],
    'email': row['email'],
    'street': row['delivery_address'],
    'ref': row['customer_code'],
    'is_company': True,
    'user_id': salesperson_id,

    # NEW FIELDS - Sprint 1
    'terms': row.get('terms'),
    'entity_type': 'company' if row.get('entity_type') == 'company' else 'individual',
    'purchase_revenue': float(row.get('purchase_revenue', 0)),
    'sales_policy': row.get('sales_policy', 'standard'),
    'industry_group': row.get('industry'),
    'region': row.get('region'),
    'customer_type': row.get('customer_type'),
    'customer_status': row.get('status', 'potential').lower(),
}
```

### 12.2 Update CSV Schema

**Update:** `test_data/customers_sprint1_enterprise.csv`

Ensure CSV has these columns:
```
customer_code,company_name,tax_id,contact_person,phone,email,status,salesperson,
entity_type,terms,industry,region,customer_type,order_value_range,purchase_revenue,
sales_policy,parent_company,delivery_address,invoice_email,creation_date,notes
```

---

## 13. Testing

### 13.1 Manual Testing Checklist

**Duplicate Checking:**
- [ ] Create customer with Tax ID → Save → Try create another with same Tax ID → Should fail
- [ ] Create customer with phone → Create another with same phone but different salesperson → Should fail
- [ ] Create customer with email → Create another with same email but same salesperson → Should succeed

**Assignment Rules:**
- [ ] Create rule: Industry=Technology, Region=North → Assign to User A
- [ ] Create customer: Industry=Technology, Region=North → Should auto-assign to User A
- [ ] Check assignment_count on rule → Should increment

**Tax ID Lookup:**
- [ ] Open customer → Enter Tax ID → Click "Lookup by MST" → Should populate fields

**Status Automation:**
- [ ] Create customer with status=Potential
- [ ] Create and confirm a sale order for that customer
- [ ] Customer status should change to "Client"

**Bulk Operations:**
- [ ] Select 5 customers → Action → Change Salesperson → Select User B → Apply
- [ ] All 5 customers should have User B as salesperson

**REST API:**
```bash
# Test customer creation
curl -X POST http://localhost:8069/api/customer/create \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Company",
    "vat": "9999999999",
    "phone": "+84999999999",
    "email": "api@test.com"
  }'

# Test lead creation
curl -X POST http://localhost:8069/api/lead/create \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Lead",
    "contact_name": "Test Contact",
    "email": "lead@test.com"
  }'
```

### 13.2 Automated Testing (Optional)

**File:** `tests/__init__.py`

```python
from . import test_assignment_rules
from . import test_duplicate_checking
from . import test_api
```

**File:** `tests/test_assignment_rules.py`

```python
from odoo.tests import TransactionCase

class TestAssignmentRules(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user_a = self.env['res.users'].create({
            'name': 'User A',
            'login': 'user_a',
        })
        self.user_b = self.env['res.users'].create({
            'name': 'User B',
            'login': 'user_b',
        })

    def test_assignment_rule_matching(self):
        """Test that assignment rules correctly match and assign"""
        rule = self.env['gotit.assignment.rule'].create({
            'name': 'Test Rule',
            'industry_group': 'technology',
            'region': 'north',
            'assigned_user_id': self.user_a.id,
        })

        partner = self.env['res.partner'].create({
            'name': 'Test Company',
            'is_company': True,
            'industry_group': 'technology',
            'region': 'north',
        })

        self.assertEqual(partner.user_id, self.user_a)
        self.assertEqual(rule.assignment_count, 1)
```

---

## 14. Deployment

### 14.1 Module Installation

```bash
# 1. Copy module to addons directory
cp -r gotit_crm_custom /path/to/odoo/addons/

# 2. Restart Odoo
docker-compose restart odoo

# 3. Update module list (via Odoo UI or command)
./odoo-bin -d your_database -u gotit_crm_custom

# Or via Docker:
docker-compose exec odoo odoo -d your_database -u gotit_crm_custom
```

### 14.2 Post-Installation Configuration

1. **Create Assignment Rules:**
   - Navigate to Sales → Configuration → GotIt CRM → Assignment Rules
   - Create rules based on business requirements

2. **Generate API Keys:**
   - Navigate to Settings → Technical → API Keys
   - Create keys for each external system

3. **Import Data:**
   ```bash
   cd scripts/
   python3 import_all_enterprise_demo.py
   ```

4. **Verify Installation:**
   - Check custom fields appear on customer forms
   - Test assignment rules
   - Test API endpoints

### 14.3 Production Checklist

- [ ] Module installed successfully
- [ ] Assignment rules configured
- [ ] API keys created and documented
- [ ] Data migrated successfully
- [ ] Duplicate checking working
- [ ] Status automation working
- [ ] Bulk operations working
- [ ] API endpoints tested
- [ ] Security rules verified
- [ ] User training completed
- [ ] Documentation distributed

---

## Appendix

### A. Field Reference

| Field Name | Model | Type | Description |
|------------|-------|------|-------------|
| terms | res.partner | Selection | Payment terms |
| entity_type | res.partner | Selection | Entity type |
| purchase_revenue | res.partner | Monetary | Revenue tracking |
| sales_policy | res.partner | Selection | Policy level |
| contract_ids | res.partner | One2many | Contracts |
| invoice_account_ids | res.partner | Many2many | Invoice accounts |
| industry_group | res.partner | Selection | Industry for assignment |
| region | res.partner | Selection | Geographic region |
| customer_type | res.partner | Selection | Customer type |
| order_value_range | res.partner | Selection | Order value range |
| customer_status | res.partner | Selection | Lifecycle status |
| lead_caretaker_id | crm.lead | Many2one | Pre-identification caretaker |

### B. API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /api/health | GET | Public | Health check |
| /api/customer/create | POST | API Key | Create customer |
| /api/lead/create | POST | API Key | Create lead |

### C. Assignment Rule Logic

```
FOR each active rule (ordered by sequence):
    IF all rule criteria match partner:
        ASSIGN partner.user_id = rule.assigned_user_id
        INCREMENT rule.assignment_count
        BREAK
```

### D. Glossary

- **MST:** Mã số thuế (Vietnamese Tax ID)
- **Assignment Rule:** Configurable rule for auto-assigning salespersons
- **Lead Caretaker:** Temporary owner of lead before identification
- **Entity Type:** Type of business entity (company, individual, etc.)

---

**End of Implementation Guide**

For support, contact the GotIt development team.
