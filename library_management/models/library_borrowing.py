# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class LibraryBorrowing(models.Model):
    _name = 'library.borrowing'
    _description = 'Library Borrowing Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'borrow_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('library.borrowing') or 'New'
    )

    book_id = fields.Many2one(
        'library.book',
        string='Book',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    member_id = fields.Many2one(
        'library.member',
        string='Member',
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    borrow_date = fields.Date(
        string='Borrow Date',
        default=fields.Date.today,
        required=True,
        tracking=True
    )
    due_date = fields.Date(
        string='Due Date',
        required=True,
        tracking=True,
        compute='_compute_due_date',
        store=True,
        readonly=False
    )
    return_date = fields.Date(
        string='Return Date',
        tracking=True
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    # Computed fields
    duration = fields.Integer(
        string='Borrowed Days',
        compute='_compute_duration',
        help='Number of days the book was/has been borrowed'
    )
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_is_overdue',
        store=True
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_days_overdue'
    )

    # Fine management
    fine_amount = fields.Float(
        string='Fine Amount',
        compute='_compute_fine_amount',
        store=True,
        help='Late return fine'
    )
    fine_paid = fields.Boolean(
        string='Fine Paid',
        default=False,
        tracking=True
    )

    notes = fields.Text(string='Notes')

    @api.depends('borrow_date')
    def _compute_due_date(self):
        """Set due date to 14 days from borrow date"""
        for record in self:
            if record.borrow_date:
                record.due_date = record.borrow_date + timedelta(days=14)

    @api.depends('borrow_date', 'return_date', 'state')
    def _compute_duration(self):
        """Compute borrowing duration"""
        for record in self:
            if record.borrow_date:
                end_date = record.return_date if record.return_date else fields.Date.today()
                if record.state == 'borrowed':
                    record.duration = (end_date - record.borrow_date).days
                elif record.state == 'returned' and record.return_date:
                    record.duration = (record.return_date - record.borrow_date).days
                else:
                    record.duration = 0
            else:
                record.duration = 0

    @api.depends('due_date', 'return_date', 'state')
    def _compute_is_overdue(self):
        """Check if book return is overdue"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'borrowed' and record.due_date:
                record.is_overdue = record.due_date < today
            else:
                record.is_overdue = False

    @api.depends('due_date', 'return_date', 'state')
    def _compute_days_overdue(self):
        """Calculate days overdue"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'borrowed' and record.due_date and record.due_date < today:
                record.days_overdue = (today - record.due_date).days
            elif record.state == 'returned' and record.return_date and record.due_date and record.return_date > record.due_date:
                record.days_overdue = (record.return_date - record.due_date).days
            else:
                record.days_overdue = 0

    @api.depends('days_overdue')
    def _compute_fine_amount(self):
        """Calculate fine based on overdue days (1 USD per day)"""
        for record in self:
            if record.days_overdue > 0:
                record.fine_amount = record.days_overdue * 1.0  # 1 USD per day
            else:
                record.fine_amount = 0.0

    @api.constrains('borrow_date', 'due_date', 'return_date')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.due_date and record.borrow_date and record.due_date < record.borrow_date:
                raise ValidationError('Due date cannot be before borrow date!')
            if record.return_date and record.borrow_date and record.return_date < record.borrow_date:
                raise ValidationError('Return date cannot be before borrow date!')

    @api.constrains('member_id')
    def _check_member_status(self):
        """Check if member can borrow books"""
        for record in self:
            if record.member_id.state != 'active':
                raise ValidationError(f'Member {record.member_id.name} is not active and cannot borrow books!')

    @api.constrains('book_id')
    def _check_book_availability(self):
        """Check if book is available"""
        for record in self:
            if record.state == 'draft' and record.book_id.available_copies <= 0:
                raise ValidationError(f'Book "{record.book_id.name}" is not available for borrowing!')

    def action_borrow(self):
        """Confirm borrowing"""
        for record in self:
            if record.book_id.available_copies <= 0:
                raise UserError(f'Book "{record.book_id.name}" is not available!')
            if record.member_id.state != 'active':
                raise UserError(f'Member "{record.member_id.name}" is not active!')

            record.state = 'borrowed'
            record.message_post(
                body=f'Book borrowed by {record.member_id.name}',
                subject='Book Borrowed'
            )

    def action_return(self):
        """Process book return"""
        for record in self:
            if record.state != 'borrowed':
                raise UserError('Only borrowed books can be returned!')

            record.return_date = fields.Date.today()
            record.state = 'returned'

            msg = f'Book returned by {record.member_id.name}'
            if record.fine_amount > 0:
                msg += f' (Fine: ${record.fine_amount:.2f})'

            record.message_post(
                body=msg,
                subject='Book Returned'
            )

    def action_cancel(self):
        """Cancel borrowing"""
        for record in self:
            if record.state == 'returned':
                raise UserError('Cannot cancel a returned borrowing!')
            record.state = 'cancelled'
            record.message_post(
                body='Borrowing cancelled',
                subject='Borrowing Cancelled'
            )

    def action_pay_fine(self):
        """Mark fine as paid"""
        for record in self:
            if record.fine_amount <= 0:
                raise UserError('No fine to pay!')
            record.fine_paid = True
            record.message_post(
                body=f'Fine of ${record.fine_amount:.2f} paid',
                subject='Fine Paid'
            )
