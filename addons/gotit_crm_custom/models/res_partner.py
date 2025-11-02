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
        'sale.order',
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
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id), ('state', 'in', ['sale', 'done'])],
            'context': {'default_partner_id': self.id},
        }
