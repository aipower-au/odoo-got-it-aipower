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
