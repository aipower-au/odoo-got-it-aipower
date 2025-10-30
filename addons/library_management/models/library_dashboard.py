# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class LibraryDashboard(models.Model):
    _name = 'library.dashboard'
    _description = 'Library Dashboard'

    name = fields.Char(string='Dashboard Name', default='Library Dashboard')

    # Statistics Fields
    total_books = fields.Integer(string='Total Books', compute='_compute_statistics')
    available_books = fields.Integer(string='Available Books', compute='_compute_statistics')
    borrowed_books = fields.Integer(string='Borrowed Books', compute='_compute_statistics')
    total_members = fields.Integer(string='Total Members', compute='_compute_statistics')
    active_members = fields.Integer(string='Active Members', compute='_compute_statistics')
    total_borrowings = fields.Integer(string='Total Borrowings', compute='_compute_statistics')
    active_borrowings = fields.Integer(string='Active Borrowings', compute='_compute_statistics')
    overdue_borrowings = fields.Integer(string='Overdue Borrowings', compute='_compute_statistics')
    total_fines = fields.Float(string='Total Fines', compute='_compute_statistics')

    # Recent Activities
    recent_borrowings_ids = fields.Many2many(
        'library.borrowing',
        compute='_compute_recent_activities',
        string='Recent Borrowings'
    )
    recent_returns_ids = fields.Many2many(
        'library.borrowing',
        compute='_compute_recent_activities',
        string='Recent Returns',
        relation='library_dashboard_recent_returns_rel'
    )

    @api.depends_context('uid')
    def _compute_statistics(self):
        for record in self:
            # Books statistics
            all_books = self.env['library.book'].search([])
            record.total_books = len(all_books)
            record.available_books = len(all_books.filtered(lambda b: b.state == 'available'))
            record.borrowed_books = len(all_books.filtered(lambda b: b.state == 'borrowed'))

            # Members statistics
            all_members = self.env['library.member'].search([])
            record.total_members = len(all_members)
            record.active_members = len(all_members.filtered(lambda m: m.state == 'active'))

            # Borrowings statistics
            all_borrowings = self.env['library.borrowing'].search([])
            record.total_borrowings = len(all_borrowings)
            record.active_borrowings = len(all_borrowings.filtered(lambda b: b.state == 'borrowed'))
            record.overdue_borrowings = len(all_borrowings.filtered(lambda b: b.is_overdue and b.state == 'borrowed'))

            # Fines statistics
            record.total_fines = sum(all_borrowings.mapped('fine_amount'))

    @api.depends_context('uid')
    def _compute_recent_activities(self):
        for record in self:
            # Recent borrowings (last 10)
            record.recent_borrowings_ids = self.env['library.borrowing'].search(
                [('state', '=', 'borrowed')],
                order='borrow_date desc',
                limit=10
            )

            # Recent returns (last 10)
            record.recent_returns_ids = self.env['library.borrowing'].search(
                [('state', '=', 'returned')],
                order='return_date desc',
                limit=10
            )

    def action_view_all_books(self):
        """Open all books view"""
        return {
            'name': 'All Books',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'view_mode': 'kanban,list,form',
            'target': 'current',
        }

    def action_view_available_books(self):
        """Open available books view"""
        return {
            'name': 'Available Books',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'view_mode': 'kanban,list,form',
            'domain': [('state', '=', 'available')],
            'target': 'current',
        }

    def action_view_borrowed_books(self):
        """Open borrowed books view"""
        return {
            'name': 'Borrowed Books',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'borrowed')],
            'target': 'current',
        }

    def action_view_all_members(self):
        """Open all members view"""
        return {
            'name': 'All Members',
            'type': 'ir.actions.act_window',
            'res_model': 'library.member',
            'view_mode': 'kanban,list,form',
            'target': 'current',
        }

    def action_view_active_members(self):
        """Open active members view"""
        return {
            'name': 'Active Members',
            'type': 'ir.actions.act_window',
            'res_model': 'library.member',
            'view_mode': 'kanban,list,form',
            'domain': [('state', '=', 'active')],
            'target': 'current',
        }

    def action_view_active_borrowings(self):
        """Open active borrowings view"""
        return {
            'name': 'Active Borrowings',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing',
            'view_mode': 'list,kanban,form',
            'domain': [('state', '=', 'borrowed')],
            'target': 'current',
        }

    def action_view_overdue_borrowings(self):
        """Open overdue borrowings view"""
        return {
            'name': 'Overdue Borrowings',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing',
            'view_mode': 'list,form',
            'domain': [('is_overdue', '=', True), ('state', '=', 'borrowed')],
            'target': 'current',
        }

    def action_new_borrowing(self):
        """Create new borrowing"""
        return {
            'name': 'New Borrowing',
            'type': 'ir.actions.act_window',
            'res_model': 'library.borrowing',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_state': 'draft'},
        }

    def action_new_member(self):
        """Create new member"""
        return {
            'name': 'New Member',
            'type': 'ir.actions.act_window',
            'res_model': 'library.member',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_new_book(self):
        """Create new book"""
        return {
            'name': 'New Book',
            'type': 'ir.actions.act_window',
            'res_model': 'library.book',
            'view_mode': 'form',
            'target': 'new',
        }
