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
