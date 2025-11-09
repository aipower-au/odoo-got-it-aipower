# -*- coding: utf-8 -*-
from odoo import models


class CrmCustomerMatcher(models.AbstractModel):
    """
    Service class for customer duplicate detection with confidence scoring.
    REQ: Customer Duplicate Detection - Multi-Identifier Customer Matching
    """
    _name = 'crm.customer.matcher'
    _description = 'Customer Duplicate Matcher Service'

    def find_matches(self, lead):
        """
        Find matching customers using multi-identifier search.

        Args:
            lead: crm.lead record to match

        Returns:
            dict|False: Match result with customer_id, confidence, match_fields, reason
                       or False if no match found
        """
        if not lead:
            return False

        # Collect all potential matches
        matches = []

        # Search by MST (strongest identifier)
        if lead.normalized_mst:
            mst_matches = self._search_by_mst(lead.normalized_mst, lead.id)
            for customer in mst_matches:
                matches.append({
                    'customer': customer,
                    'match_fields': ['mst'],
                })

        # Search by phone
        if lead.normalized_phone:
            phone_matches = self._search_by_phone(lead.normalized_phone, lead.id)
            for customer in phone_matches:
                # Check if already in matches
                existing = next((m for m in matches if m['customer'].id == customer.id), None)
                if existing:
                    existing['match_fields'].append('phone')
                else:
                    matches.append({
                        'customer': customer,
                        'match_fields': ['phone'],
                    })

        # Search by email
        if lead.normalized_email:
            email_matches = self._search_by_email(lead.normalized_email, lead.id)
            for customer in email_matches:
                # Check if already in matches
                existing = next((m for m in matches if m['customer'].id == customer.id), None)
                if existing:
                    existing['match_fields'].append('email')
                else:
                    matches.append({
                        'customer': customer,
                        'match_fields': ['email'],
                    })

        if not matches:
            return False

        # Calculate confidence scores for all matches
        for match in matches:
            match['confidence'] = self._calculate_confidence(match['match_fields'])
            match['score'] = self._get_confidence_score(match['confidence'])

        # Select primary match using tie-breaking logic
        primary_match = self._select_primary_match(matches)

        if primary_match:
            return {
                'customer_id': primary_match['customer'].id,
                'confidence': primary_match['confidence'],
                'match_fields': primary_match['match_fields'],
                'reason': f"{', '.join(primary_match['match_fields'])} exact match",
            }

        return False

    def _search_by_mst(self, mst, exclude_lead_partner_id=None):
        """Search customers by normalized MST."""
        domain = [('vat', '=', mst)]
        if exclude_lead_partner_id:
            domain.append(('id', '!=', exclude_lead_partner_id))
        return self.env['res.partner'].search(domain)

    def _search_by_phone(self, phone, exclude_lead_partner_id=None):
        """Search customers by normalized phone."""
        domain = ['|', ('phone', '=', phone), ('mobile', '=', phone)]
        if exclude_lead_partner_id:
            domain.append(('id', '!=', exclude_lead_partner_id))
        return self.env['res.partner'].search(domain)

    def _search_by_email(self, email, exclude_lead_partner_id=None):
        """Search customers by normalized email."""
        domain = [('email', '=', email)]
        if exclude_lead_partner_id:
            domain.append(('id', '!=', exclude_lead_partner_id))
        return self.env['res.partner'].search(domain)

    def _calculate_confidence(self, match_fields):
        """
        Calculate confidence level based on matched fields.

        Confidence Levels:
        - Very High (95%+): Multiple identifiers match (MST + phone + email, or MST + phone)
        - High (85-95%): MST exact match only
        - Medium (70-85%): Phone or email exact match only
        - Low (<70%): Partial matches (not used in Sprint 1)

        Args:
            match_fields (list): List of matched field names

        Returns:
            str: Confidence level (very_high, high, medium, low)
        """
        score = self._get_confidence_score_from_fields(match_fields)

        if score >= 95:
            return 'very_high'
        elif score >= 85:
            return 'high'
        elif score >= 70:
            return 'medium'
        else:
            return 'low'

    def _get_confidence_score_from_fields(self, match_fields):
        """Calculate numerical confidence score from matched fields."""
        score = 0

        if 'mst' in match_fields:
            score += 60  # MST is strongest identifier

        if 'phone' in match_fields:
            score += 25

        if 'email' in match_fields:
            score += 15

        # Bonus for multiple matches
        if len(match_fields) >= 2:
            score += 10

        return min(score, 100)

    def _get_confidence_score(self, confidence_level):
        """Convert confidence level to numerical score for comparison."""
        scores = {
            'very_high': 100,
            'high': 90,
            'medium': 75,
            'low': 60,
            'none': 0,
        }
        return scores.get(confidence_level, 0)

    def _select_primary_match(self, matches):
        """
        Select primary match from multiple matches using tie-breaking logic.

        Business Rules:
        1. Highest confidence score wins
        2. If tied, prefer customer with assigned salesperson
        3. If still tied, prefer most recently updated customer

        Args:
            matches (list): List of match dictionaries

        Returns:
            dict: Primary match dictionary
        """
        if not matches:
            return None

        if len(matches) == 1:
            return matches[0]

        # Sort by confidence score (descending)
        sorted_matches = sorted(matches, key=lambda m: m['score'], reverse=True)

        # Get all matches with highest score
        highest_score = sorted_matches[0]['score']
        top_matches = [m for m in sorted_matches if m['score'] == highest_score]

        if len(top_matches) == 1:
            return top_matches[0]

        # Tie-breaker 1: Prefer customer with assigned salesperson
        matches_with_sales = [m for m in top_matches if m['customer'].user_id]
        if matches_with_sales:
            # If multiple have salespeople, use most recently updated
            return max(matches_with_sales, key=lambda m: m['customer'].write_date or m['customer'].create_date)

        # Tie-breaker 2: Most recently updated customer
        return max(top_matches, key=lambda m: m['customer'].write_date or m['customer'].create_date)
