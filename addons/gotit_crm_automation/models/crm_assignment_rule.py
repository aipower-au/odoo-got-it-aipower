# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmAssignmentRule(models.Model):
    """Configurable sales assignment rules for automated lead routing."""
    _name = 'crm.assignment.rule'
    _description = 'CRM Assignment Rule'
    _order = 'sequence, id'

    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Descriptive name for this assignment rule'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Priority order - lower numbers are evaluated first'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Disable rule without deleting it'
    )

    condition_type = fields.Selection([
        ('industry', 'Industry'),
        ('region', 'Region'),
        ('customer_type', 'Customer Type'),
        ('country', 'Country'),
        ('team', 'Sales Team'),
    ], string='Condition Type', required=True)

    condition_value = fields.Char(
        string='Condition Value',
        required=True,
        help='Value to match against (e.g., "Technology", "Hanoi", "Merchant")'
    )

    assignment_method = fields.Selection([
        ('direct', 'Direct Assignment'),
        ('round_robin', 'Round Robin'),
        ('queue', 'Queue'),
    ], string='Assignment Method', required=True, default='direct')

    assign_to_user_id = fields.Many2one(
        'res.users',
        string='Assign To User',
        domain=[('share', '=', False)],
        help='User to assign leads to (for direct assignment)'
    )

    assign_to_team_id = fields.Many2one(
        'crm.team',
        string='Assign To Team',
        help='Team to assign leads to'
    )

    _sql_constraints = [
        ('sequence_positive', 'CHECK(sequence > 0)', 'Sequence must be positive'),
    ]

    def evaluate_rule(self, lead):
        """
        Evaluate if this rule matches the given lead.

        Args:
            lead: crm.lead record to evaluate

        Returns:
            bool: True if rule conditions match the lead
        """
        self.ensure_one()

        if not self.active:
            return False

        # Evaluate based on condition type
        if self.condition_type == 'industry':
            # Check if lead's industry matches
            if lead.partner_id and lead.partner_id.industry_id:
                return lead.partner_id.industry_id.name == self.condition_value
            return False

        elif self.condition_type == 'region':
            # Check if lead's city/state matches
            region_match = (
                (lead.city and self.condition_value.lower() in lead.city.lower()) or
                (lead.state_id and self.condition_value.lower() in lead.state_id.name.lower())
            )
            return region_match

        elif self.condition_type == 'customer_type':
            # Check if customer type matches (assuming it's stored in lead.type or partner)
            if lead.partner_id:
                return getattr(lead.partner_id, 'company_type', False) == self.condition_value.lower()
            return False

        elif self.condition_type == 'country':
            # Check if country matches
            if lead.country_id:
                return lead.country_id.name == self.condition_value
            return False

        elif self.condition_type == 'team':
            # Check if lead already belongs to a specific team
            if lead.team_id:
                return lead.team_id.name == self.condition_value
            return False

        return False

    @api.model
    def get_applicable_rules(self, lead):
        """
        Get all active rules ordered by sequence.

        Args:
            lead: crm.lead record

        Returns:
            recordset: Ordered list of applicable rules
        """
        return self.search([('active', '=', True)], order='sequence')
