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
