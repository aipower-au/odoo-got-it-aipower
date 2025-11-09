# -*- coding: utf-8 -*-
import re
from odoo import models


class CrmLeadNormalizer(models.AbstractModel):
    """
    Service class for normalizing customer identifier data.
    REQ: Lead Information Validation - Sanitize and Normalize Customer Data
    """
    _name = 'crm.lead.normalizer'
    _description = 'Lead Data Normalizer Service'

    def normalize_phone(self, phone_string):
        """
        Normalize Vietnamese phone number to standard format.

        Args:
            phone_string (str): Phone number in any format

        Returns:
            str|bool: Normalized phone number or False if invalid

        Format: 84XXXXXXXXX or 0XXXXXXXXX
        """
        if not phone_string:
            return False

        # Remove all non-digit characters
        phone = re.sub(r'[^\d]', '', str(phone_string))

        if not phone:
            return False

        # Handle Vietnamese phone formats
        # Remove country code prefix if present
        if phone.startswith('84'):
            phone = '0' + phone[2:]
        elif phone.startswith('+84'):
            phone = '0' + phone[3:]

        # Validate Vietnamese mobile number format (10 digits starting with 0)
        if len(phone) == 10 and phone[0] == '0':
            return phone
        elif len(phone) == 9:
            # Add leading 0 if missing
            return '0' + phone

        # If doesn't match expected format, return as-is (cleaned of formatting)
        return phone if len(phone) >= 9 else False

    def normalize_email(self, email_string):
        """
        Normalize email address to standard format.

        Args:
            email_string (str): Email address in any format

        Returns:
            str|bool: Normalized email or False if invalid
        """
        if not email_string:
            return False

        # Convert to lowercase and trim whitespace
        email = str(email_string).lower().strip()

        # Basic email validation
        if '@' not in email or '.' not in email:
            return False

        return email

    def normalize_mst(self, mst_string):
        """
        Normalize Vietnamese Tax ID (MST) to standard format.

        Args:
            mst_string (str): MST in any format

        Returns:
            str|bool: Normalized MST or False if invalid

        Format: 10-13 digits, no formatting
        """
        if not mst_string:
            return False

        # Remove all non-digit characters
        mst = re.sub(r'[^\d]', '', str(mst_string))

        if not mst:
            return False

        # Validate Vietnamese MST length (10-13 digits)
        if 10 <= len(mst) <= 13:
            return mst

        return False
