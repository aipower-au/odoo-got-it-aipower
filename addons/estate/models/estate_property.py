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
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    # ========== CRUD OVERRIDES ==========

    @api.model
    def create(self, vals):
        """Override create to add custom logic"""
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
