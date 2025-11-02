# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

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
                new_user_id = vals['user_id']
                new_user = self.env['res.users'].browse(new_user_id).name if new_user_id else 'None'

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
