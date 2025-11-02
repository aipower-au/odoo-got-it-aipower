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
            'view_mode': 'list,form',
            'domain': domain,
        }
