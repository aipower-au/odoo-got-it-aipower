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
