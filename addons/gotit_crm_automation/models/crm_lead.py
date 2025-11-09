# -*- coding: utf-8 -*-
import re
import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    """Extended CRM Lead model with automation features."""
    _inherit = 'crm.lead'

    # Validation fields
    validation_status = fields.Selection([
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete'),
        ('pending_info', 'Pending Information'),
    ], string='Validation Status', default='incomplete', tracking=True)

    # Duplicate detection fields
    duplicate_match_confidence = fields.Selection([
        ('very_high', 'Very High (95%+)'),
        ('high', 'High (85-95%)'),
        ('medium', 'Medium (70-85%)'),
        ('low', 'Low (<70%)'),
        ('none', 'No Match'),
    ], string='Duplicate Match Confidence', default='none', tracking=True)

    duplicate_customer_id = fields.Many2one(
        'res.partner',
        string='Duplicate Customer',
        help='Matched existing customer if duplicate detected',
        tracking=True
    )

    # Assignment fields
    assignment_method = fields.Selection([
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('round_robin', 'Round Robin'),
        ('rule_based', 'Rule Based'),
    ], string='Assignment Method', tracking=True)

    assignment_reason = fields.Text(
        string='Assignment Reason',
        help='Explanation of why lead was assigned to this salesperson'
    )

    # Verification fields
    verification_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ], string='Verification Status', default='pending', tracking=True)

    verified_by = fields.Many2one(
        'res.users',
        string='Verified By',
        tracking=True
    )

    verification_date = fields.Datetime(
        string='Verification Date',
        tracking=True
    )

    # Normalized fields (computed and stored for indexing)
    normalized_phone = fields.Char(
        string='Normalized Phone',
        compute='_compute_normalized_fields',
        store=True,
        index=True
    )

    normalized_email = fields.Char(
        string='Normalized Email',
        compute='_compute_normalized_fields',
        store=True,
        index=True
    )

    normalized_mst = fields.Char(
        string='Normalized MST',
        compute='_compute_normalized_fields',
        store=True,
        index=True
    )

    # MST field (Vietnamese Tax ID)
    vat = fields.Char(string='Tax ID (MST)', index=True)

    @api.depends('phone', 'mobile', 'email_from', 'vat')
    def _compute_normalized_fields(self):
        """Compute normalized identifier fields."""
        normalizer = self.env['crm.lead.normalizer']
        for lead in self:
            # Normalize phone (prefer mobile over phone)
            phone_value = lead.mobile or lead.phone
            lead.normalized_phone = normalizer.normalize_phone(phone_value) if phone_value else False

            # Normalize email
            lead.normalized_email = normalizer.normalize_email(lead.email_from) if lead.email_from else False

            # Normalize MST
            lead.normalized_mst = normalizer.normalize_mst(lead.vat) if lead.vat else False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger automatic validation and duplicate detection."""
        leads = super(CrmLead, self).create(vals_list)
        for lead in leads:
            # Trigger validation automatically
            lead.validate_lead_information()
            # If validation passes, trigger duplicate detection
            if lead.validation_status == 'complete':
                lead.detect_duplicates()
        return leads

    def write(self, vals):
        """Override write to re-validate if identifier fields change."""
        result = super(CrmLead, self).write(vals)

        # Re-validate if critical fields changed
        critical_fields = {'phone', 'mobile', 'email_from', 'vat'}
        if critical_fields & set(vals.keys()):
            for lead in self:
                lead.validate_lead_information()
                if lead.validation_status == 'complete':
                    lead.detect_duplicates()

        return result

    def validate_lead_information(self):
        """
        Validate lead has at least one identifier (MST, phone, email).
        REQ: Lead Information Validation - Validate Lead Data Completeness
        """
        self.ensure_one()
        start_time = time.time()

        # Check for at least one identifier
        has_mst = bool(self.normalized_mst)
        has_phone = bool(self.normalized_phone)
        has_email = bool(self.normalized_email)

        if has_mst or has_phone or has_email:
            # Lead is complete
            self.validation_status = 'complete'
            status = 'complete'
            fields_present = []
            if has_mst:
                fields_present.append('MST')
            if has_phone:
                fields_present.append('phone')
            if has_email:
                fields_present.append('email')
        else:
            # Lead is incomplete - assign to Telesales
            self.validation_status = 'incomplete'
            status = 'incomplete'
            fields_present = []
            self._assign_to_telesales()

        # Log validation result
        processing_time = int((time.time() - start_time) * 1000)
        self.env['crm.lead.audit.log'].create({
            'lead_id': self.id,
            'operation_type': 'validation',
            'operation_result': status,
            'processing_time_ms': processing_time,
            'details': {
                'fields_present': fields_present,
                'validation_status': status,
            }
        })

        return status == 'complete'

    def _assign_to_telesales(self):
        """Assign incomplete lead to Telesales team."""
        self.ensure_one()
        # Find Telesales team
        telesales_team = self.env['crm.team'].search([('name', 'ilike', 'telesales')], limit=1)
        if telesales_team:
            self.team_id = telesales_team.id
        self.validation_status = 'pending_info'

    def detect_duplicates(self):
        """
        Detect duplicate customers using multi-identifier matching.
        REQ: Customer Duplicate Detection - Multi-Identifier Customer Matching
        """
        self.ensure_one()
        start_time = time.time()

        # Use customer matcher service
        matcher = self.env['crm.customer.matcher']
        match_result = matcher.find_matches(self)

        if match_result:
            # Update lead with match information
            self.duplicate_customer_id = match_result['customer_id']
            self.duplicate_match_confidence = match_result['confidence']

            # Log the match
            processing_time = int((time.time() - start_time) * 1000)
            self.env['crm.lead.audit.log'].create({
                'lead_id': self.id,
                'customer_id': match_result['customer_id'],
                'operation_type': 'duplicate_detection',
                'operation_result': 'match_found',
                'processing_time_ms': processing_time,
                'details': {
                    'confidence': match_result['confidence'],
                    'match_fields': match_result['match_fields'],
                    'match_reason': match_result['reason'],
                }
            })

            # Trigger assignment based on duplicate
            self._assign_to_existing_owner()
        else:
            # No match - new customer
            self.duplicate_match_confidence = 'none'

            # Log no match
            processing_time = int((time.time() - start_time) * 1000)
            self.env['crm.lead.audit.log'].create({
                'lead_id': self.id,
                'operation_type': 'duplicate_detection',
                'operation_result': 'no_match',
                'processing_time_ms': processing_time,
                'details': {
                    'result': 'new_customer'
                }
            })

            # Apply assignment rules for new customer
            self.apply_assignment_rules()

    def _assign_to_existing_owner(self):
        """
        Assign lead to existing customer owner.
        REQ: Automated Sales Assignment - Assign to Existing Salesperson for Duplicate Customers
        """
        self.ensure_one()

        if not self.duplicate_customer_id:
            return

        # Get salesperson from matched customer
        customer = self.duplicate_customer_id
        if customer.user_id:
            # Customer has assigned salesperson
            self.user_id = customer.user_id
            self.team_id = customer.team_id if customer.team_id else self.team_id
            self.assignment_method = 'automatic'
            self.assignment_reason = f'Existing customer ownership: {customer.name} (ID: {customer.id})'

            # Create notification activity
            self._create_assignment_activity(customer.user_id, 'existing_customer')

            # Log assignment
            self.env['crm.lead.audit.log'].create({
                'lead_id': self.id,
                'customer_id': customer.id,
                'operation_type': 'assignment',
                'operation_result': 'automatic',
                'details': {
                    'method': 'automatic',
                    'reason': 'existing_customer_ownership',
                    'assigned_to': customer.user_id.name,
                }
            })
        else:
            # Customer has no owner - trigger manual assignment
            self.assignment_method = 'manual'
            self.assignment_reason = f'Existing customer without owner: {customer.name} (ID: {customer.id})'

            # Notify sales manager
            self._notify_manual_assignment_required()

            # Log manual assignment trigger
            self.env['crm.lead.audit.log'].create({
                'lead_id': self.id,
                'customer_id': customer.id,
                'operation_type': 'assignment',
                'operation_result': 'manual_required',
                'details': {
                    'method': 'manual',
                    'reason': 'existing_customer_no_owner',
                }
            })

    def apply_assignment_rules(self):
        """
        Apply configured assignment rules for new customers.
        REQ: Automated Sales Assignment - Auto-Assign New Customers via Sales Rules
        """
        self.ensure_one()

        # Get applicable rules ordered by sequence
        rules = self.env['crm.assignment.rule'].search([('active', '=', True)], order='sequence')

        for rule in rules:
            if rule.evaluate_rule(self):
                # Rule matches - assign according to rule
                if rule.assignment_method == 'direct' and rule.assign_to_user_id:
                    self.user_id = rule.assign_to_user_id
                    self.team_id = rule.assign_to_team_id if rule.assign_to_team_id else self.team_id
                    self.assignment_method = 'rule_based'
                    self.assignment_reason = f'Rule match: {rule.name}'

                    # Create notification
                    self._create_assignment_activity(rule.assign_to_user_id, 'rule_based')

                    # Log assignment
                    self.env['crm.lead.audit.log'].create({
                        'lead_id': self.id,
                        'operation_type': 'assignment',
                        'operation_result': 'automatic',
                        'details': {
                            'method': 'rule_based',
                            'rule_id': rule.id,
                            'rule_name': rule.name,
                            'assigned_to': rule.assign_to_user_id.name,
                        }
                    })
                    return True

        # No matching rules - log and notify manager
        self.assignment_method = 'manual'
        self.assignment_reason = 'No matching assignment rules'
        self._notify_manual_assignment_required()

        self.env['crm.lead.audit.log'].create({
            'lead_id': self.id,
            'operation_type': 'assignment',
            'operation_result': 'no_rule_match',
            'details': {
                'method': 'manual',
                'reason': 'no_matching_rules',
            }
        })
        return False

    def _create_assignment_activity(self, user, assignment_type):
        """Create Odoo activity to notify salesperson of lead assignment."""
        self.ensure_one()

        activity_type = self.env.ref('gotit_crm_automation.mail_activity_type_lead_assignment', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Lead Assignment')], limit=1)

        if activity_type:
            self.activity_schedule(
                activity_type_id=activity_type.id,
                user_id=user.id,
                summary=f'New Lead Assignment: {self.name}',
                note=f'Lead assigned via {assignment_type}. Customer: {self.partner_name or "Unknown"}. Reason: {self.assignment_reason}',
            )

    def _notify_manual_assignment_required(self):
        """Notify sales manager that manual assignment is required."""
        self.ensure_one()

        # Find sales manager(s)
        sales_managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('sales_team.group_sale_manager').id)])

        activity_type = self.env.ref('gotit_crm_automation.mail_activity_type_manual_assignment', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Manual Assignment Required')], limit=1)

        if activity_type and sales_managers:
            for manager in sales_managers[:1]:  # Assign to first manager only
                self.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=manager.id,
                    summary=f'Manual Assignment Required: {self.name}',
                    note=f'Lead requires manual assignment. Reason: {self.assignment_reason}',
                )

    def action_confirm_customer_match(self):
        """
        Confirm duplicate customer match and convert lead to opportunity.
        REQ: Sales Verification Workflow - Enable Sales to Verify Customer Information
        """
        self.ensure_one()

        if not self.duplicate_customer_id:
            raise ValidationError(_('No duplicate customer found to confirm.'))

        # Link lead to confirmed customer
        self.partner_id = self.duplicate_customer_id
        self.verification_status = 'completed'
        self.verified_by = self.env.user
        self.verification_date = fields.Datetime.now()

        # Convert to opportunity if not already
        if self.type != 'opportunity':
            self.convert_opportunity(self.partner_id.id)

        # Log verification
        self.env['crm.lead.audit.log'].create({
            'lead_id': self.id,
            'customer_id': self.duplicate_customer_id.id,
            'operation_type': 'verification',
            'operation_result': 'confirmed_match',
            'details': {
                'verified_by': self.env.user.name,
                'decision': 'confirmed_match',
            }
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Customer match confirmed and lead converted to opportunity.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reject_match_create_new(self):
        """
        Reject duplicate match and create new customer.
        REQ: Sales Verification Workflow - Handle New Customer Creation
        """
        self.ensure_one()

        # Mark match as false positive
        if self.duplicate_customer_id:
            old_match = self.duplicate_customer_id
            self.env['crm.lead.audit.log'].create({
                'lead_id': self.id,
                'customer_id': old_match.id,
                'operation_type': 'verification',
                'operation_result': 'false_positive',
                'details': {
                    'verified_by': self.env.user.name,
                    'decision': 'rejected_match',
                    'original_match': old_match.name,
                }
            })

        # Clear duplicate match
        self.duplicate_customer_id = False
        self.duplicate_match_confidence = 'none'
        self.verification_status = 'completed'
        self.verified_by = self.env.user
        self.verification_date = fields.Datetime.now()

        # Prepare to create new customer
        return self.action_create_new_customer()

    def action_create_new_customer(self):
        """Open form to create new customer from lead data."""
        self.ensure_one()

        # Prepare customer data
        customer_vals = {
            'name': self.partner_name or self.contact_name,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email_from,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
            'country_id': self.country_id.id if self.country_id else False,
            'state_id': self.state_id.id if self.state_id else False,
            'vat': self.vat,  # MST
            'user_id': self.env.user.id,  # Set creating salesperson as owner
        }

        # Create customer
        new_customer = self.env['res.partner'].create(customer_vals)

        # Link to lead
        self.partner_id = new_customer
        self.user_id = self.env.user

        # Log new customer creation
        self.env['crm.lead.audit.log'].create({
            'lead_id': self.id,
            'customer_id': new_customer.id,
            'operation_type': 'verification',
            'operation_result': 'new_customer_created',
            'details': {
                'created_by': self.env.user.name,
                'decision': 'new_customer_created',
                'customer_name': new_customer.name,
            }
        })

        # Convert to opportunity
        if self.type != 'opportunity':
            self.convert_opportunity(new_customer.id)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('New customer created and lead converted to opportunity.'),
                'type': 'success',
                'sticky': False,
            }
        }
