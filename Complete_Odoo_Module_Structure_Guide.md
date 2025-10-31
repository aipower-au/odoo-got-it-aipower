# Complete Odoo Module Structure Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Module Directory Structure](#module-directory-structure)
3. [Essential Module Components](#essential-module-components)
4. [Real Estate Module Example](#real-estate-module-example)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Development Workflow](#development-workflow)

## Architecture Overview

Odoo follows a **three-tier architecture**:

- **Presentation Tier**: HTML5, JavaScript, CSS (transitioning to OWL framework)
- **Logic Tier**: Python with custom ORM
- **Data Tier**: PostgreSQL database

```
┌─────────────────────────────────────────────────┐
│                Presentation Tier                │
│            HTML5 + JavaScript + CSS            │
│                (OWL Framework)                  │
├─────────────────────────────────────────────────┤
│                 Logic Tier                      │
│              Python + Custom ORM               │
├─────────────────────────────────────────────────┤
│                 Data Tier                       │
│                PostgreSQL                       │
└─────────────────────────────────────────────────┘
```

## Module Directory Structure

### Complete Module Structure
```bash
estate/                              # Module root directory
├── __init__.py                      # Main Python package init
├── __manifest__.py                  # Module manifest/descriptor
├── models/                          # Business logic models
│   ├── __init__.py                 # Models package init
│   ├── estate_property.py          # Main model
│   ├── estate_property_type.py     # Related model
│   ├── estate_property_tag.py      # Related model
│   └── estate_property_offer.py    # Related model
├── views/                          # User interface definitions
│   ├── estate_property_views.xml   # Main views
│   ├── estate_property_type_views.xml
│   ├── estate_property_tag_views.xml
│   ├── estate_property_offer_views.xml
│   └── estate_menus.xml           # Menu structure
├── security/                       # Access control
│   ├── ir.model.access.csv        # Basic access rights
│   └── estate_security.xml        # Advanced security rules
├── data/                          # Configuration data
│   ├── estate_data.xml           # Initial/demo data
│   └── estate_sequence.xml       # Sequences and numbering
├── demo/                          # Demo data for testing
│   └── estate_demo.xml
├── wizard/                        # Transient models (wizards)
│   ├── __init__.py
│   └── estate_wizard.py
├── report/                        # Reports and documents
│   ├── __init__.py
│   ├── estate_report.py
│   └── estate_report_template.xml
├── controllers/                   # Web controllers
│   ├── __init__.py
│   └── estate_controller.py
├── static/                        # Static web assets
│   ├── description/               # Module description
│   │   ├── icon.png              # Module icon (128x128)
│   │   └── index.html            # Module description page
│   ├── src/
│   │   ├── css/                  # Custom stylesheets
│   │   │   └── estate.css
│   │   ├── js/                   # JavaScript files
│   │   │   └── estate.js
│   │   └── xml/                  # QWeb templates
│   │       └── estate_templates.xml
│   └── img/                      # Images
├── tests/                         # Unit tests
│   ├── __init__.py
│   └── test_estate.py
└── i18n/                         # Internationalization
    ├── estate.pot                # Translation template
    ├── fr.po                     # French translations
    └── es.po                     # Spanish translations
```

### Minimal Module Structure
```bash
minimal_module/
├── __init__.py                    # Required: Package init
├── __manifest__.py               # Required: Module manifest
├── models/
│   ├── __init__.py
│   └── model_name.py
└── views/
    └── view_name.xml
```

## Essential Module Components

### 1. Module Manifest (`__manifest__.py`)

```python
# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management',
    'version': '17.0.1.0.0',
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
    'author': 'Your Company Name',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',           # Always required
        'mail',           # For messaging features
        'web',            # For web interface
        'account',        # If using accounting features
    ],
    'data': [
        # Security files (load first)
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        
        # Data files
        'data/estate_sequence.xml',
        'data/estate_data.xml',
        
        # View files
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',
        
        # Report files
        'report/estate_report.xml',
        'report/estate_report_template.xml',
        
        # Wizard files
        'wizard/estate_wizard_views.xml',
    ],
    'demo': [
        'demo/estate_demo.xml',
    ],
    'qweb': [
        'static/src/xml/estate_templates.xml',
    ],
    'installable': True,
    'application': True,              # True if this is a main application
    'auto_install': False,           # Don't auto-install
    'external_dependencies': {
        'python': ['requests', 'lxml'],  # Python dependencies
        'bin': ['wkhtmltopdf'],          # Binary dependencies
    },
    'images': ['static/description/banner.png'],
    'price': 0.00,
    'currency': 'EUR',
}
```

### 2. Python Package Init (`__init__.py`)

```python
# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import wizard
from . import report
```

### 3. Models Package Init (`models/__init__.py`)

```python
# -*- coding: utf-8 -*-
from . import estate_property
from . import estate_property_type
from . import estate_property_tag
from . import estate_property_offer
```

## Real Estate Module Example

### Main Property Model (`models/estate_property.py`)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import date, timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Add messaging features
    
    # ========== FIELDS ==========
    
    # Basic Information
    name = fields.Char(
        string="Title", 
        required=True, 
        tracking=True,
        help="Property title or name"
    )
    description = fields.Text(
        string="Description",
        tracking=True
    )
    postcode = fields.Char(
        string="Postcode",
        tracking=True
    )
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: date.today() + timedelta(days=90),
        tracking=True
    )
    
    # Financial Information
    expected_price = fields.Float(
        string="Expected Price",
        required=True,
        tracking=True,
        help="Expected selling price"
    )
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False,
        tracking=True
    )
    
    # Property Details
    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2
    )
    living_area = fields.Integer(
        string="Living Area (sqm)"
    )
    facades = fields.Integer(
        string="Facades"
    )
    garage = fields.Boolean(
        string="Garage",
        default=False
    )
    garden = fields.Boolean(
        string="Garden",
        default=False
    )
    garden_area = fields.Integer(
        string="Garden Area (sqm)"
    )
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ]
    )
    
    # Status and Workflow
    state = fields.Selection(
        string="Status",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        copy=False,
        default='new',
        tracking=True
    )
    
    # Relationships
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
        required=True
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
        tracking=True
    )
    buyer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Buyer",
        readonly=True,
        copy=False,
        tracking=True
    )
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        string="Tags"
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers"
    )
    
    # Computed Fields
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area",
        store=True
    )
    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_price"
    )
    offer_count = fields.Integer(
        string="Offer Count",
        compute="_compute_offer_count"
    )
    
    # ========== COMPUTED METHODS ==========
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0
    
    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
    
    # ========== CONSTRAINTS ==========
    
    @api.constrains("expected_price")
    def _check_expected_price(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError(_("Expected price must be positive"))
    
    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price and record.selling_price < 0:
                raise ValidationError(_("Selling price cannot be negative"))
    
    # ========== ONCHANGE METHODS ==========
    
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False
    
    # ========== ACTION METHODS ==========
    
    def action_sold(self):
        """Mark property as sold"""
        if "canceled" in self.mapped("state"):
            raise UserError(_("Canceled properties cannot be sold."))
        
        for record in self:
            if not record.offer_ids:
                raise UserError(_("Cannot sell property without offers."))
            
            # Find accepted offer
            accepted_offers = record.offer_ids.filtered(lambda o: o.status == 'accepted')
            if not accepted_offers:
                raise UserError(_("No accepted offers found."))
            
            record.selling_price = accepted_offers[0].price
            record.buyer_id = accepted_offers[0].partner_id
        
        return self.write({"state": "sold"})
    
    def action_cancel(self):
        """Cancel property"""
        if "sold" in self.mapped("state"):
            raise UserError(_("Sold properties cannot be canceled."))
        return self.write({"state": "canceled"})
    
    def action_view_offers(self):
        """View property offers"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Property Offers'),
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
    
    # ========== CRUD OVERRIDES ==========
    
    @api.model
    def create(self, vals):
        """Override create to add custom logic"""
        # Set sequence number if not provided
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('estate.property') or _('New')
        return super().create(vals)
    
    def write(self, vals):
        """Override write to add custom logic"""
        # Add message when state changes
        if 'state' in vals:
            for record in self:
                record.message_post(
                    body=_("Property status changed to %s") % dict(self._fields['state'].selection)[vals['state']]
                )
        return super().write(vals)
    
    def unlink(self):
        """Override unlink to add constraints"""
        if any(prop.state in ['sold', 'offer_accepted'] for prop in self):
            raise UserError(_("Cannot delete sold or accepted properties."))
        return super().unlink()
    
    # ========== BUSINESS METHODS ==========
    
    def _get_property_report_data(self):
        """Get data for property reports"""
        self.ensure_one()
        return {
            'property': self,
            'offers': self.offer_ids.sorted('price', reverse=True),
            'best_offer': self.offer_ids.filtered(lambda o: o.price == self.best_price),
        }
```

### Property Type Model (`models/estate_property_type.py`)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "name"
    
    name = fields.Char(
        string="Name",
        required=True,
        translate=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Used to order property types"
    )
    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id",
        string="Properties"
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_type_id",
        string="Offers"
    )
    offer_count = fields.Integer(
        string="Offers Count",
        compute="_compute_offer_count"
    )
    
    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
    
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Property type name must be unique.'),
    ]
```

### Property Tags Model (`models/estate_property_tag.py`)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"
    
    name = fields.Char(
        string="Name",
        required=True,
        translate=True
    )
    color = fields.Integer(
        string="Color",
        default=0
    )
    
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]
```

### Property Offers Model (`models/estate_property_offer.py`)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import date, timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"
    
    price = fields.Float(
        string="Price",
        required=True
    )
    status = fields.Selection(
        string="Status",
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy=False
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True
    )
    property_id = fields.Many2one(
        comodel_name="estate.property",
        string="Property",
        required=True
    )
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        string="Property Type",
        store=True
    )
    validity = fields.Integer(
        string="Validity (days)",
        default=7
    )
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline"
    )
    
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + timedelta(days=record.validity)
            else:
                record.date_deadline = date.today() + timedelta(days=record.validity)
    
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
    
    @api.constrains("price")
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError(_("Offer price must be positive"))
    
    def action_accept(self):
        """Accept the offer"""
        if self.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
            raise ValidationError(_("Only one offer can be accepted per property"))
        
        self.status = 'accepted'
        self.property_id.state = 'offer_accepted'
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        
        # Refuse other offers
        other_offers = self.property_id.offer_ids.filtered(lambda o: o.id != self.id)
        other_offers.write({'status': 'refused'})
    
    def action_refuse(self):
        """Refuse the offer"""
        self.status = 'refused'
    
    @api.model
    def create(self, vals):
        """Override create to update property state"""
        offer = super().create(vals)
        offer.property_id.state = 'offer_received'
        return offer
```

### Views Definition (`views/estate_property_views.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        
        <!-- ========== SEARCH VIEW ========== -->
        <record id="estate_property_view_search" model="ir.ui.view">
            <field name="name">estate.property.search</field>
            <field name="model">estate.property</field>
            <field name="arch" type="xml">
                <search>
                    <field name="name" string="Title"/>
                    <field name="postcode"/>
                    <field name="expected_price"/>
                    <field name="bedrooms"/>
                    <field name="living_area" filter_domain="[('living_area', '>=', self)]"/>
                    <field name="facades"/>
                    <field name="property_type_id"/>
                    <field name="tag_ids"/>
                    <separator/>
                    <filter string="Available" name="available" domain="[('state', 'in', ['new', 'offer_received'])]"/>
                    <filter string="Current User" name="my_properties" domain="[('user_id', '=', uid)]"/>
                    <separator/>
                    <group expand="1" string="Group By">
                        <filter string="Status" name="group_state" context="{'group_by': 'state'}"/>
                        <filter string="Property Type" name="group_property_type" context="{'group_by': 'property_type_id'}"/>
                        <filter string="Salesperson" name="group_user" context="{'group_by': 'user_id'}"/>
                    </group>
                </search>
            </field>
        </record>

        <!-- ========== LIST VIEW ========== -->
        <record id="estate_property_view_tree" model="ir.ui.view">
            <field name="name">estate.property.tree</field>
            <field name="model">estate.property</field>
            <field name="arch" type="xml">
                <tree 
                    decoration-success="state in ('offer_received','offer_accepted')" 
                    decoration-bf="state=='offer_accepted'" 
                    decoration-muted="state=='sold'"
                    sample="1">
                    <field name="name"/>
                    <field name="property_type_id"/>
                    <field name="postcode"/>
                    <field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
                    <field name="bedrooms"/>
                    <field name="living_area"/>
                    <field name="expected_price" widget="monetary"/>
                    <field name="selling_price" widget="monetary"/>
                    <field name="date_availability" optional="hide"/>
                    <field name="state" decoration-success="state in ('offer_received','offer_accepted')" decoration-danger="state=='canceled'" widget="badge"/>
                </tree>
            </field>
        </record>

        <!-- ========== FORM VIEW ========== -->
        <record id="estate_property_view_form" model="ir.ui.view">
            <field name="name">estate.property.form</field>
            <field name="model">estate.property</field>
            <field name="arch" type="xml">
                <form string="Property">
                    <header>
                        <button name="action_sold" type="object" string="Sold" 
                                class="btn-primary" states="new,offer_received,offer_accepted"/>
                        <button name="action_cancel" type="object" string="Cancel" 
                                states="new,offer_received,offer_accepted"/>
                        <field name="state" widget="statusbar" 
                               statusbar_visible="new,offer_received,offer_accepted,sold"/>
                    </header>
                    <sheet>
                        <div class="oe_button_box" name="button_box">
                            <button name="action_view_offers" type="object" class="oe_stat_button" icon="fa-handshake-o">
                                <field name="offer_count" widget="statinfo" string="Offers"/>
                            </button>
                        </div>
                        <div class="oe_title">
                            <h1>
                                <field name="name" class="mb16" placeholder="Property Title"/>
                            </h1>
                            <field name="tag_ids" widget="many2many_tags" 
                                   options="{'color_field': 'color'}" placeholder="Tags..."/>
                        </div>
                        <group>
                            <group>
                                <field name="property_type_id" options="{'no_create': True, 'no_edit': True}"/>
                                <field name="postcode"/>
                                <field name="date_availability"/>
                            </group>
                            <group>
                                <field name="expected_price" widget="monetary"/>
                                <field name="best_price" widget="monetary"/>
                                <field name="selling_price" widget="monetary"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Description">
                                <group>
                                    <group>
                                        <field name="description"/>
                                        <field name="bedrooms"/>
                                        <field name="living_area"/>
                                        <field name="facades"/>
                                        <field name="garage"/>
                                        <field name="garden"/>
                                        <field name="garden_area" attrs="{'invisible': [('garden', '=', False)]}"/>
                                        <field name="garden_orientation" attrs="{'invisible': [('garden', '=', False)]}"/>
                                        <field name="total_area"/>
                                    </group>
                                </group>
                            </page>
                            <page string="Offers">
                                <field name="offer_ids" 
                                       attrs="{'readonly': [('state', 'in', ('offer_accepted', 'sold', 'canceled'))]}">
                                    <tree editable="bottom" decoration-success="status=='accepted'" decoration-danger="status=='refused'">
                                        <field name="price" widget="monetary"/>
                                        <field name="partner_id"/>
                                        <field name="validity"/>
                                        <field name="date_deadline"/>
                                        <field name="status"/>
                                        <button name="action_accept" type="object" string="Accept" 
                                                icon="fa-check" attrs="{'invisible': [('status', '!=', False)]}"/>
                                        <button name="action_refuse" type="object" string="Refuse" 
                                                icon="fa-times" attrs="{'invisible': [('status', '!=', False)]}"/>
                                    </tree>
                                </field>
                            </page>
                            <page string="Other Info">
                                <group>
                                    <field name="user_id"/>
                                    <field name="buyer_id"/>
                                </group>
                            </page>
                        </notebook>
                    </sheet>
                    <div class="oe_chatter">
                        <field name="message_follower_ids"/>
                        <field name="activity_ids"/>
                        <field name="message_ids"/>
                    </div>
                </form>
            </field>
        </record>

        <!-- ========== KANBAN VIEW ========== -->
        <record id="estate_property_view_kanban" model="ir.ui.view">
            <field name="name">estate.property.kanban</field>
            <field name="model">estate.property</field>
            <field name="arch" type="xml">
                <kanban default_group_by="property_type_id" records_draggable="false" sample="1">
                    <field name="state"/>
                    <field name="property_type_id"/>
                    <field name="expected_price"/>
                    <field name="best_price"/>
                    <field name="selling_price"/>
                    <field name="tag_ids"/>
                    <templates>
                        <t t-name="kanban-card">
                            <div class="oe_kanban_card oe_kanban_global_click">
                                <div class="o_kanban_record_top mb16">
                                    <div class="o_kanban_record_headings">
                                        <strong class="o_kanban_record_title">
                                            <field name="name"/>
                                        </strong>
                                    </div>
                                    <div class="o_kanban_manage_button_section">
                                        <a class="o_kanban_manage_toggle_button" href="#" data-bs-toggle="dropdown" role="button" aria-label="Dropdown manage" aria-haspopup="true" aria-expanded="false">
                                            <i class="fa fa-ellipsis-v" role="img" aria-label="Manage" title="Manage"/>
                                        </a>
                                        <div class="dropdown-menu" role="menu">
                                            <a role="menuitem" type="edit" class="dropdown-item">Edit</a>
                                            <a role="menuitem" type="delete" class="dropdown-item">Delete</a>
                                        </div>
                                    </div>
                                </div>
                                <div class="o_kanban_record_body">
                                    <field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
                                    <div class="text-muted">
                                        Expected Price: <field name="expected_price" widget="monetary"/>
                                    </div>
                                    <div t-if="record.state.raw_value == 'offer_received'" class="text-info">
                                        Best Offer: <field name="best_price" widget="monetary"/>
                                    </div>
                                    <div t-if="record.state.raw_value == 'offer_accepted'" class="text-success">
                                        Selling Price: <field name="selling_price" widget="monetary"/>
                                    </div>
                                </div>
                                <div class="o_kanban_record_bottom">
                                    <div class="oe_kanban_bottom_left">
                                        <field name="state" widget="label_selection" 
                                               options="{'classes': {'new': 'default', 'offer_received': 'info', 'offer_accepted': 'success', 'sold': 'success', 'canceled': 'danger'}}"/>
                                    </div>
                                    <div class="oe_kanban_bottom_right">
                                        <field name="activity_ids" widget="kanban_activity"/>
                                        <img t-att-src="kanban_image('res.users', 'avatar_128', record.user_id.raw_value)" 
                                             t-att-title="record.user_id.value" t-att-alt="record.user_id.value" 
                                             class="oe_kanban_avatar"/>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </templates>
                </kanban>
            </field>
        </record>

        <!-- ========== ACTIONS ========== -->
        <record id="estate_property_action" model="ir.actions.act_window">
            <field name="name">Properties</field>
            <field name="res_model">estate.property</field>
            <field name="view_mode">kanban,tree,form</field>
            <field name="search_view_id" ref="estate_property_view_search"/>
            <field name="context">{
                'search_default_available': 1,
                'search_default_group_property_type': 1
            }</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Create a new property
                </p>
                <p>
                    Let's create your first property and manage your real estate portfolio.
                </p>
            </field>
        </record>

    </data>
</odoo>
```

### Security Configuration (`security/ir.model.access.csv`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_estate_property_user,estate.property.user,model_estate_property,base.group_user,1,1,1,1
access_estate_property_type_user,estate.property.type.user,model_estate_property_type,base.group_user,1,1,1,1
access_estate_property_tag_user,estate.property.tag.user,model_estate_property_tag,base.group_user,1,1,1,1
access_estate_property_offer_user,estate.property.offer.user,model_estate_property_offer,base.group_user,1,1,1,1
access_estate_property_manager,estate.property.manager,model_estate_property,base.group_system,1,1,1,1
access_estate_property_type_manager,estate.property.type.manager,model_estate_property_type,base.group_system,1,1,1,1
access_estate_property_tag_manager,estate.property.tag.manager,model_estate_property_tag,base.group_system,1,1,1,1
access_estate_property_offer_manager,estate.property.offer.manager,model_estate_property_offer,base.group_system,1,1,1,1
```

### Menu Structure (`views/estate_menus.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        
        <!-- ========== MAIN MENU ========== -->
        <menuitem id="estate_menu_root" 
                  name="Real Estate" 
                  sequence="10" 
                  web_icon="estate,static/description/icon.png"/>

        <!-- ========== FIRST LEVEL MENUS ========== -->
        <menuitem id="estate_first_level_menu" 
                  name="Advertisements" 
                  parent="estate_menu_root" 
                  sequence="10"/>
        
        <menuitem id="estate_settings_menu" 
                  name="Settings" 
                  parent="estate_menu_root" 
                  sequence="90"/>

        <!-- ========== PROPERTY MENUS ========== -->
        <menuitem id="estate_property_menu_action" 
                  name="Properties" 
                  action="estate_property_action" 
                  parent="estate_first_level_menu" 
                  sequence="10"/>

        <!-- ========== CONFIGURATION MENUS ========== -->
        <menuitem id="estate_property_type_menu_action" 
                  name="Property Types" 
                  action="estate_property_type_action" 
                  parent="estate_settings_menu" 
                  sequence="10"/>
        
        <menuitem id="estate_property_tag_menu_action" 
                  name="Property Tags" 
                  action="estate_property_tag_action" 
                  parent="estate_settings_menu" 
                  sequence="20"/>

    </data>
</odoo>
```

## Advanced Features

### 1. Wizards (`wizard/estate_wizard.py`)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EstatePropertyWizard(models.TransientModel):
    _name = 'estate.property.wizard'
    _description = 'Property Mass Update Wizard'
    
    property_ids = fields.Many2many(
        'estate.property',
        string='Properties'
    )
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='New Property Type'
    )
    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Add Tags'
    )
    
    def action_update_properties(self):
        """Update selected properties"""
        vals = {}
        if self.property_type_id:
            vals['property_type_id'] = self.property_type_id.id
        if self.tag_ids:
            vals['tag_ids'] = [(4, tag.id) for tag in self.tag_ids]
        
        if vals:
            self.property_ids.write(vals)
        
        return {'type': 'ir.actions.act_window_close'}
```

### 2. Controllers (`controllers/estate_controller.py`)

```python
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class EstateController(http.Controller):
    
    @http.route('/estate/properties', type='http', auth='public', website=True)
    def estate_properties(self, **kwargs):
        """Public page showing properties"""
        properties = request.env['estate.property'].sudo().search([
            ('state', 'in', ['new', 'offer_received'])
        ])
        return request.render('estate.property_list_template', {
            'properties': properties
        })
    
    @http.route('/estate/api/properties', type='json', auth='user')
    def api_properties(self, **kwargs):
        """JSON API for properties"""
        properties = request.env['estate.property'].search([])
        return [{
            'id': prop.id,
            'name': prop.name,
            'price': prop.expected_price,
            'state': prop.state,
        } for prop in properties]
```

### 3. Reports (`report/estate_report.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        
        <!-- Report Action -->
        <record id="estate_property_report" model="ir.actions.report">
            <field name="name">Property Report</field>
            <field name="model">estate.property</field>
            <field name="report_type">qweb-pdf</field>
            <field name="report_name">estate.property_report_template</field>
            <field name="report_file">estate.property_report_template</field>
            <field name="binding_model_id" ref="model_estate_property"/>
            <field name="binding_type">report</field>
        </record>

        <!-- Report Template -->
        <template id="property_report_template">
            <t t-call="web.html_container">
                <t t-foreach="docs" t-as="doc">
                    <t t-call="web.external_layout">
                        <div class="page">
                            <h2>Property Report</h2>
                            <div class="row">
                                <div class="col-6">
                                    <strong>Property:</strong> <span t-field="doc.name"/><br/>
                                    <strong>Type:</strong> <span t-field="doc.property_type_id"/><br/>
                                    <strong>Postcode:</strong> <span t-field="doc.postcode"/><br/>
                                </div>
                                <div class="col-6">
                                    <strong>Expected Price:</strong> <span t-field="doc.expected_price" t-options="{'widget': 'monetary'}"/><br/>
                                    <strong>Living Area:</strong> <span t-field="doc.living_area"/> sqm<br/>
                                    <strong>Status:</strong> <span t-field="doc.state"/><br/>
                                </div>
                            </div>
                            
                            <t t-if="doc.offer_ids">
                                <h3>Offers</h3>
                                <table class="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Partner</th>
                                            <th>Price</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <t t-foreach="doc.offer_ids" t-as="offer">
                                            <tr>
                                                <td><span t-field="offer.partner_id"/></td>
                                                <td><span t-field="offer.price" t-options="{'widget': 'monetary'}"/></td>
                                                <td><span t-field="offer.status"/></td>
                                            </tr>
                                        </t>
                                    </tbody>
                                </table>
                            </t>
                        </div>
                    </t>
                </t>
            </t>
        </template>
        
    </data>
</odoo>
```

## Best Practices

### 1. Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable and method names
- Add docstrings to all methods
- Use proper field ordering in models
- Implement proper error handling

### 2. Security Best Practices
- Always define access rights
- Use record rules for row-level security
- Validate user inputs
- Use sudo() carefully
- Implement proper field permissions

### 3. Performance Optimization
- Use computed fields with store=True when appropriate
- Implement proper indexes on frequently queried fields
- Use read_group for aggregated data
- Minimize database queries in loops
- Use prefetch for related fields

### 4. User Experience
- Provide meaningful help text
- Use proper field widgets
- Implement smart defaults
- Add proper search filters
- Use status bars for workflows

## Development Workflow

### 1. Development Environment Setup
```bash
# Clone Odoo source
git clone https://github.com/odoo/odoo.git
cd odoo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create addon directory
mkdir custom_addons
```

### 2. Module Development Process
1. **Plan**: Define requirements and data model
2. **Create**: Set up basic module structure
3. **Model**: Implement business objects
4. **Views**: Create user interface
5. **Security**: Configure access rights
6. **Test**: Write and run tests
7. **Deploy**: Install and configure

### 3. Testing
```python
# tests/test_estate.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestEstate(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.property_type = self.env['estate.property.type'].create({
            'name': 'House'
        })
    
    def test_property_creation(self):
        """Test property creation"""
        property_vals = {
            'name': 'Test Property',
            'expected_price': 100000,
            'property_type_id': self.property_type.id,
        }
        prop = self.env['estate.property'].create(property_vals)
        self.assertEqual(prop.state, 'new')
    
    def test_price_validation(self):
        """Test price validation"""
        with self.assertRaises(ValidationError):
            self.env['estate.property'].create({
                'name': 'Test Property',
                'expected_price': -100,
                'property_type_id': self.property_type.id,
            })
```

### 4. Deployment Commands
```bash
# Install module
./odoo-bin -d database_name -i estate

# Update module
./odoo-bin -d database_name -u estate

# Run with custom addons path
./odoo-bin -d database_name --addons-path=addons,custom_addons

# Debug mode
./odoo-bin -d database_name --dev=all
```

This comprehensive guide provides everything needed to understand and create complete Odoo modules following best practices and industry standards.
