# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied
import secrets

class APIKey(models.Model):
    """
    API keys for external system authentication
    """
    _name = 'gotit.api.key'
    _description = 'API Key'

    name = fields.Char(
        string='Name',
        required=True,
        help="Descriptive name for this API key"
    )

    key = fields.Char(
        string='API Key',
        required=True,
        readonly=True,
        default=lambda self: self._generate_key(),
        help="API key for authentication",
        copy=False
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help="Inactive keys cannot be used"
    )

    allowed_ips = fields.Text(
        string='Allowed IPs',
        help="Comma-separated list of allowed IP addresses (leave empty for any)"
    )

    last_used_date = fields.Datetime(
        string='Last Used',
        readonly=True
    )

    usage_count = fields.Integer(
        string='Usage Count',
        readonly=True,
        default=0
    )

    @api.model
    def _generate_key(self):
        """Generate secure random API key"""
        return secrets.token_urlsafe(32)

    @api.model
    def authenticate(self, key, ip_address=None):
        """
        Validate API key

        Args:
            key (str): API key to validate
            ip_address (str): Client IP address

        Returns:
            gotit.api.key record if valid, raises AccessDenied otherwise
        """
        api_key = self.search([('key', '=', key), ('active', '=', True)], limit=1)

        if not api_key:
            raise AccessDenied(_("Invalid API key"))

        # Check IP whitelist if configured
        if api_key.allowed_ips and ip_address:
            allowed_ips = [ip.strip() for ip in api_key.allowed_ips.split(',')]
            if ip_address not in allowed_ips:
                raise AccessDenied(_("IP address not allowed"))

        # Update usage statistics
        api_key.write({
            'last_used_date': fields.Datetime.now(),
            'usage_count': api_key.usage_count + 1,
        })

        return api_key
