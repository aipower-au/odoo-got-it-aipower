# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import AccessDenied, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class GotItAPI(http.Controller):
    """
    REST API endpoints for external systems
    """

    def _authenticate_request(self):
        """
        Authenticate API request using Bearer token
        Returns: True if authenticated, raises AccessDenied otherwise
        """
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied(_("Missing or invalid Authorization header"))

        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        client_ip = request.httprequest.remote_addr

        # Validate API key
        APIKey = request.env['gotit.api.key'].sudo()
        APIKey.authenticate(api_key, client_ip)

        return True

    def _json_response(self, data, status=200):
        """Helper to return JSON response"""
        return Response(
            json.dumps(data, default=str, ensure_ascii=False),
            status=status,
            mimetype='application/json'
        )

    def _error_response(self, error, message, status=400, field=None):
        """Helper to return error response"""
        response_data = {
            'error': error,
            'message': message,
        }
        if field:
            response_data['field'] = field

        return self._json_response(response_data, status=status)

    @http.route('/api/customer/create', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def api_create_customer(self):
        """
        Create a new customer via API

        POST /api/customer/create
        Headers:
            Authorization: Bearer YOUR_API_KEY
            Content-Type: application/json

        Body:
            {
                "name": "Company Name",
                "vat": "0123456789",
                "phone": "+84912345678",
                "email": "contact@company.com",
                "street": "123 Main St",
                "city": "Hanoi",
                "customer_type": "enterprise",
                "industry_group": "technology"
            }

        Response:
            {
                "success": true,
                "partner_id": 123,
                "name": "Company Name",
                "assigned_salesperson": "John Doe",
                "message": "Customer created successfully"
            }
        """
        try:
            # Authenticate
            self._authenticate_request()

            # Parse request body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return self._error_response(
                    'Invalid JSON',
                    'Request body must be valid JSON',
                    status=400
                )

            # Validate required fields
            required_fields = ['name']
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return self._error_response(
                    'Missing Fields',
                    f"Required fields missing: {', '.join(missing_fields)}",
                    status=400
                )

            # Create partner
            Partner = request.env['res.partner'].sudo()

            # Map API fields to Odoo fields
            partner_vals = {
                'name': data.get('name'),
                'vat': data.get('vat'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'street': data.get('street'),
                'city': data.get('city'),
                'zip': data.get('zip'),
                'is_company': True,
                'customer_type': data.get('customer_type'),
                'industry_group': data.get('industry_group'),
                'region': data.get('region'),
                'terms': data.get('terms'),
                'sales_policy': data.get('sales_policy'),
            }

            # Remove None values
            partner_vals = {k: v for k, v in partner_vals.items() if v is not None}

            try:
                partner = Partner.create(partner_vals)

                response_data = {
                    'success': True,
                    'partner_id': partner.id,
                    'name': partner.name,
                    'assigned_salesperson': partner.user_id.name if partner.user_id else None,
                    'message': 'Customer created successfully'
                }

                _logger.info(f"Customer created via API: {partner.name} (ID: {partner.id})")

                return self._json_response(response_data, status=201)

            except ValidationError as e:
                return self._error_response(
                    'Validation Error',
                    str(e),
                    status=400
                )

        except AccessDenied as e:
            return self._error_response(
                'Authentication Failed',
                str(e),
                status=401
            )

        except Exception as e:
            _logger.exception("API error creating customer")
            return self._error_response(
                'Server Error',
                'An unexpected error occurred',
                status=500
            )

    @http.route('/api/lead/create', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def api_create_lead(self):
        """
        Create a new lead via API

        POST /api/lead/create
        Headers:
            Authorization: Bearer YOUR_API_KEY
            Content-Type: application/json

        Body:
            {
                "name": "Lead Name",
                "contact_name": "Contact Person",
                "email": "contact@example.com",
                "phone": "+84987654321",
                "description": "Lead description",
                "source": "website"
            }

        Response:
            {
                "success": true,
                "lead_id": 456,
                "lead_name": "Lead Name",
                "assigned_to": "Jane Smith",
                "message": "Lead created successfully"
            }
        """
        try:
            # Authenticate
            self._authenticate_request()

            # Parse request body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return self._error_response(
                    'Invalid JSON',
                    'Request body must be valid JSON',
                    status=400
                )

            # Validate required fields
            required_fields = ['name']
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                return self._error_response(
                    'Missing Fields',
                    f"Required fields missing: {', '.join(missing_fields)}",
                    status=400
                )

            # Create lead
            Lead = request.env['crm.lead'].sudo()

            lead_vals = {
                'name': data.get('name'),
                'contact_name': data.get('contact_name'),
                'email_from': data.get('email'),
                'phone': data.get('phone'),
                'description': data.get('description'),
                'source_id': self._get_source_id(data.get('source')),
                'type': 'lead',
            }

            # Remove None values
            lead_vals = {k: v for k, v in lead_vals.items() if v is not None}

            try:
                lead = Lead.create(lead_vals)

                response_data = {
                    'success': True,
                    'lead_id': lead.id,
                    'lead_name': lead.name,
                    'assigned_to': lead.user_id.name if lead.user_id else (
                        lead.lead_caretaker_id.name if lead.lead_caretaker_id else None
                    ),
                    'message': 'Lead created successfully'
                }

                _logger.info(f"Lead created via API: {lead.name} (ID: {lead.id})")

                return self._json_response(response_data, status=201)

            except ValidationError as e:
                return self._error_response(
                    'Validation Error',
                    str(e),
                    status=400
                )

        except AccessDenied as e:
            return self._error_response(
                'Authentication Failed',
                str(e),
                status=401
            )

        except Exception as e:
            _logger.exception("API error creating lead")
            return self._error_response(
                'Server Error',
                'An unexpected error occurred',
                status=500
            )

    def _get_source_id(self, source_name):
        """Get or create lead source"""
        if not source_name:
            return False

        Source = request.env['utm.source'].sudo()
        source = Source.search([('name', '=ilike', source_name)], limit=1)

        if not source:
            source = Source.create({'name': source_name})

        return source.id

    @http.route('/api/health', type='http', auth='public', methods=['GET'], csrf=False)
    def api_health_check(self):
        """
        Health check endpoint
        GET /api/health
        """
        return self._json_response({
            'status': 'healthy',
            'service': 'GotIt CRM API',
            'version': '1.0.0'
        })
