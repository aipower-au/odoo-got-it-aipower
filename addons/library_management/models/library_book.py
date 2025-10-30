# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Title',
        required=True,
        tracking=True,
        help='Book title'
    )
    isbn = fields.Char(
        string='ISBN',
        copy=False,
        tracking=True,
        help='International Standard Book Number'
    )
    author = fields.Char(
        string='Author',
        required=True,
        tracking=True
    )
    publisher = fields.Char(
        string='Publisher',
        tracking=True
    )
    publication_date = fields.Date(
        string='Publication Date',
        tracking=True
    )
    category = fields.Selection([
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('other', 'Other')
    ], string='Category', default='other', tracking=True)

    pages = fields.Integer(
        string='Number of Pages',
        tracking=True
    )
    description = fields.Text(
        string='Description',
        help='Book summary or description'
    )
    cover_image = fields.Binary(
        string='Cover Image',
        attachment=True
    )

    # Inventory fields
    total_copies = fields.Integer(
        string='Total Copies',
        default=1,
        required=True,
        tracking=True
    )
    available_copies = fields.Integer(
        string='Available Copies',
        compute='_compute_available_copies',
        store=True
    )
    borrowed_copies = fields.Integer(
        string='Borrowed Copies',
        compute='_compute_available_copies',
        store=True
    )

    # Related fields
    borrowing_ids = fields.One2many(
        'library.borrowing',
        'book_id',
        string='Borrowing Records'
    )
    active_borrowing_ids = fields.One2many(
        'library.borrowing',
        'book_id',
        string='Active Borrowings',
        domain=[('state', '=', 'borrowed')]
    )

    # Status
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'All Borrowed'),
        ('unavailable', 'Unavailable')
    ], string='Status', compute='_compute_state', store=True)

    _sql_constraints = [
        ('isbn_unique', 'UNIQUE(isbn)', 'ISBN must be unique!'),
    ]

    @api.depends('total_copies', 'active_borrowing_ids')
    def _compute_available_copies(self):
        """Compute available and borrowed copies"""
        for book in self:
            borrowed = len(book.active_borrowing_ids)
            book.borrowed_copies = borrowed
            book.available_copies = book.total_copies - borrowed

    @api.depends('available_copies', 'active')
    def _compute_state(self):
        """Compute book availability state"""
        for book in self:
            if not book.active:
                book.state = 'unavailable'
            elif book.available_copies <= 0:
                book.state = 'borrowed'
            else:
                book.state = 'available'

    @api.constrains('total_copies')
    def _check_total_copies(self):
        """Ensure total copies is positive"""
        for book in self:
            if book.total_copies < 0:
                raise ValidationError('Total copies must be a positive number!')

    @api.constrains('pages')
    def _check_pages(self):
        """Ensure pages is positive"""
        for book in self:
            if book.pages and book.pages < 0:
                raise ValidationError('Number of pages must be positive!')

    def action_view_borrowings(self):
        """Open borrowing records for this book"""
        self.ensure_one()
        return {
            'name': 'Borrowing Records',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing',
            'view_mode': 'list,form',
            'domain': [('book_id', '=', self.id)],
            'context': {'default_book_id': self.id}
        }
