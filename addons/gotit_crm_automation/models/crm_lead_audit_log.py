# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CrmLeadAuditLog(models.Model):
    """Audit log for CRM lead automation operations."""
    _name = 'crm.lead.audit.log'
    _description = 'CRM Lead Audit Log'
    _order = 'timestamp desc'
    _rec_name = 'operation_type'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead',
        required=True,
        ondelete='cascade',
        index=True
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        ondelete='set null',
        index=True
    )

    operation_type = fields.Selection([
        ('validation', 'Validation'),
        ('duplicate_detection', 'Duplicate Detection'),
        ('assignment', 'Assignment'),
        ('verification', 'Verification'),
    ], string='Operation Type', required=True, index=True)

    operation_result = fields.Text(
        string='Operation Result',
        help='Summary of the operation result'
    )

    processing_time_ms = fields.Integer(
        string='Processing Time (ms)',
        help='Time taken to process this operation in milliseconds'
    )

    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        readonly=True,
        index=True
    )

    details = fields.Json(
        string='Details',
        help='Flexible JSON field for storing operation-specific details'
    )

    @api.model
    def create(self, vals):
        """Override create to make logs read-only after creation."""
        # Ensure timestamp is set
        if 'timestamp' not in vals:
            vals['timestamp'] = fields.Datetime.now()
        return super(CrmLeadAuditLog, self).create(vals)

    def write(self, vals):
        """Prevent modification of audit logs."""
        # Audit logs should be immutable
        return False

    def unlink(self):
        """Prevent deletion of audit logs."""
        # Only allow deletion by system admin in very specific cases
        if not self.env.user.has_group('base.group_system'):
            return False
        return super(CrmLeadAuditLog, self).unlink()
