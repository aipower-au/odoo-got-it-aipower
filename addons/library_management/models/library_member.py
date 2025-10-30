# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    phone = fields.Char(
        string='Phone',
        tracking=True
    )
    member_id = fields.Char(
        string='Member ID',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('library.member') or 'New',
        tracking=True
    )

    # Address fields
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one(
        'res.country.state',
        string='State'
    )
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one(
        'res.country',
        string='Country'
    )

    # Membership details
    membership_date = fields.Date(
        string='Membership Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    membership_type = fields.Selection([
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('student', 'Student'),
        ('senior', 'Senior')
    ], string='Membership Type', default='basic', required=True, tracking=True)

    expiry_date = fields.Date(
        string='Expiry Date',
        compute='_compute_expiry_date',
        store=True
    )

    # Borrowing related
    borrowing_ids = fields.One2many(
        'library.borrowing',
        'member_id',
        string='Borrowing Records'
    )
    active_borrowing_ids = fields.One2many(
        'library.borrowing',
        'member_id',
        string='Active Borrowings',
        domain=[('state', '=', 'borrowed')]
    )
    borrowed_books_count = fields.Integer(
        string='Currently Borrowed',
        compute='_compute_borrowed_books_count'
    )
    total_borrowed_count = fields.Integer(
        string='Total Books Borrowed',
        compute='_compute_total_borrowed_count'
    )
    overdue_count = fields.Integer(
        string='Overdue Books',
        compute='_compute_overdue_count'
    )

    # Status
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended')
    ], string='Status', compute='_compute_member_state', store=True, tracking=True)

    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique!'),
        ('member_id_unique', 'UNIQUE(member_id)', 'Member ID must be unique!'),
    ]

    @api.depends('membership_date', 'membership_type')
    def _compute_expiry_date(self):
        """Compute membership expiry date based on type"""
        from dateutil.relativedelta import relativedelta

        for member in self:
            if member.membership_date:
                # Different membership durations
                if member.membership_type == 'basic':
                    member.expiry_date = member.membership_date + relativedelta(years=1)
                elif member.membership_type == 'premium':
                    member.expiry_date = member.membership_date + relativedelta(years=2)
                elif member.membership_type == 'student':
                    member.expiry_date = member.membership_date + relativedelta(months=6)
                elif member.membership_type == 'senior':
                    member.expiry_date = member.membership_date + relativedelta(years=3)
            else:
                member.expiry_date = False

    @api.depends('active_borrowing_ids')
    def _compute_borrowed_books_count(self):
        """Count currently borrowed books"""
        for member in self:
            member.borrowed_books_count = len(member.active_borrowing_ids)

    @api.depends('borrowing_ids')
    def _compute_total_borrowed_count(self):
        """Count total books ever borrowed"""
        for member in self:
            member.total_borrowed_count = len(member.borrowing_ids)

    @api.depends('active_borrowing_ids', 'active_borrowing_ids.is_overdue')
    def _compute_overdue_count(self):
        """Count overdue books"""
        for member in self:
            member.overdue_count = len(member.active_borrowing_ids.filtered('is_overdue'))

    @api.depends('expiry_date', 'active', 'overdue_count')
    def _compute_member_state(self):
        """Compute member status"""
        today = fields.Date.today()
        for member in self:
            if not member.active:
                member.state = 'suspended'
            elif member.expiry_date and member.expiry_date < today:
                member.state = 'expired'
            else:
                member.state = 'active'

    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        import re
        for member in self:
            if member.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', member.email):
                raise ValidationError('Please enter a valid email address!')

    def action_view_borrowings(self):
        """Open borrowing records for this member"""
        self.ensure_one()
        return {
            'name': 'Borrowing Records',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing',
            'view_mode': 'list,form',
            'domain': [('member_id', '=', self.id)],
            'context': {'default_member_id': self.id}
        }

    def action_renew_membership(self):
        """Renew membership"""
        for member in self:
            member.membership_date = fields.Date.today()
            member.message_post(
                body='Membership renewed successfully.',
                subject='Membership Renewal'
            )
