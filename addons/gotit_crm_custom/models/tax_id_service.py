# -*- coding: utf-8 -*-

from odoo import api, models, _
import random

class TaxIDService(models.AbstractModel):
    """
    Mock service for Vietnamese Tax ID (MST) lookup
    Replace with real API integration in production
    """
    _name = 'gotit.tax.id.service'
    _description = 'Tax ID Lookup Service'

    @api.model
    def lookup_company_by_vat(self, vat):
        """
        Lookup company information by Tax ID

        Args:
            vat (str): Vietnamese Tax ID (MST)

        Returns:
            dict: Company information or False if not found
        """
        # Mock implementation - returns dummy data
        # TODO: Replace with real API call to Vietnamese MST database

        if not vat or len(vat) < 10:
            return False

        # Simulate API call
        company_data = self._mock_api_call(vat)

        return company_data

    def _mock_api_call(self, vat):
        """
        Simulate third-party API response
        Returns realistic Vietnamese company data
        """
        # Mock company names
        company_names = [
            'Công ty TNHH Technology Việt Nam',
            'Công ty Cổ phần Phát triển Phần mềm',
            'Vietnam Tech Solutions Co., Ltd.',
            'Công ty TNHH Thương mại Dịch vụ',
            'Saigon Innovations Ltd.',
        ]

        # Mock addresses
        addresses = [
            {'street': 'Số 123 Đường Lê Lợi', 'city': 'Hanoi', 'zip': '100000'},
            {'street': '456 Nguyễn Huệ', 'city': 'Ho Chi Minh', 'zip': '700000'},
            {'street': '789 Trần Phú', 'city': 'Da Nang', 'zip': '550000'},
        ]

        # Select random data
        company_name = random.choice(company_names)
        address = random.choice(addresses)

        return {
            'name': company_name,
            'street': address['street'],
            'city': address['city'],
            'zip': address['zip'],
            'country_id': self.env.ref('base.vn').id,  # Vietnam
            'phone': '+84 %d %d %d' % (
                random.randint(20, 99),
                random.randint(100, 999),
                random.randint(1000, 9999)
            ),
            'email': 'info@%s.vn' % vat.lower(),
            'is_company': True,
        }

    @api.model
    def integrate_real_api(self, api_url, api_key):
        """
        Template method for real API integration

        Args:
            api_url (str): API endpoint URL
            api_key (str): API authentication key

        Example:
            import requests

            response = requests.get(
                f"{api_url}/lookup",
                params={'vat': vat},
                headers={'Authorization': f'Bearer {api_key}'}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('company_name'),
                    'street': data.get('address'),
                    'city': data.get('city'),
                    ...
                }
        """
        pass
