#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Utility Functions
Common functions used across import/export/verification scripts
Provides connection management, lookup helpers, and error handling
"""

import sys
import xmlrpc.client
from typing import Optional, List, Dict, Tuple, Any
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================

def connect_odoo() -> Tuple[int, Any]:
    """
    Connect to Odoo and authenticate.

    Returns:
        Tuple of (uid, models_proxy)

    Raises:
        SystemExit: If connection or authentication fails

    Example:
        >>> uid, models = connect_odoo()
        >>> print(f"Connected as UID: {uid}")
    """
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication failed - invalid credentials")

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models

    except xmlrpc.client.Fault as e:
        print(f"❌ Odoo XML-RPC Error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print(f"   Check that Odoo is running at {ODOO_URL}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


# ============================================================================
# LOOKUP FUNCTIONS
# ============================================================================

def get_user_id(uid: int, models: Any, user_name_or_login: str) -> Optional[int]:
    """
    Get user ID by name or login (with multiple fallback strategies).

    Tries in order:
    1. Login with @gotit.vn suffix (e.g., son.p@gotit.vn)
    2. Login without suffix (e.g., son.p)
    3. By full name (e.g., Nguyễn Văn Sơn)

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        user_name_or_login: User login (e.g., 'son.p') or full name

    Returns:
        User ID if found, None otherwise

    Example:
        >>> user_id = get_user_id(uid, models, 'son.p')
        >>> if user_id:
        >>>     print(f"Found user: {user_id}")
    """
    try:
        # Try 1: Login with @gotit.vn suffix
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['login', '=', f"{user_name_or_login}@gotit.vn"]]]
        )
        if user_ids:
            return user_ids[0]

        # Try 2: Login without @gotit.vn suffix
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['login', '=', user_name_or_login]]]
        )
        if user_ids:
            return user_ids[0]

        # Try 3: By full name
        user_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users', 'search',
            [[['name', '=', user_name_or_login]]]
        )
        if user_ids:
            return user_ids[0]

        return None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up user '{user_name_or_login}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_user_id: {e}")
        return None


def get_partner_id(uid: int, models: Any, partner_name: str) -> Optional[int]:
    """
    Get partner (customer/company) ID by name.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        partner_name: Partner/company name

    Returns:
        Partner ID if found, None otherwise

    Example:
        >>> partner_id = get_partner_id(uid, models, 'Công ty ABC')
    """
    try:
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['name', '=', partner_name]]]
        )
        return partner_ids[0] if partner_ids else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up partner '{partner_name}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_partner_id: {e}")
        return None


def get_team_id(uid: int, models: Any, team_name: str) -> Optional[int]:
    """
    Get sales team ID by name.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        team_name: Sales team name

    Returns:
        Team ID if found, None otherwise

    Example:
        >>> team_id = get_team_id(uid, models, 'North Regional Team')
    """
    try:
        team_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.team', 'search',
            [[['name', '=', team_name]]]
        )
        return team_ids[0] if team_ids else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up team '{team_name}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_team_id: {e}")
        return None


def get_product_id(uid: int, models: Any, product_name: str) -> Optional[int]:
    """
    Get product ID by name.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        product_name: Product name

    Returns:
        Product ID if found, None otherwise

    Example:
        >>> product_id = get_product_id(uid, models, 'CRM System')
    """
    try:
        product_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'product.product', 'search',
            [[['name', '=', product_name]]]
        )
        return product_ids[0] if product_ids else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up product '{product_name}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_product_id: {e}")
        return None


def get_opportunity_id(uid: int, models: Any, opportunity_name: str) -> Optional[int]:
    """
    Get opportunity (crm.lead with type='opportunity') ID by name.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        opportunity_name: Opportunity name

    Returns:
        Opportunity ID if found, None otherwise

    Example:
        >>> opp_id = get_opportunity_id(uid, models, 'Công ty ABC - Software Solution')
    """
    try:
        opp_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search',
            [[['name', '=', opportunity_name], ['type', '=', 'opportunity']]]
        )
        return opp_ids[0] if opp_ids else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up opportunity '{opportunity_name}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_opportunity_id: {e}")
        return None


def get_lead_id(uid: int, models: Any, lead_name: str) -> Optional[int]:
    """
    Get lead (crm.lead with type='lead') ID by name.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        lead_name: Lead name

    Returns:
        Lead ID if found, None otherwise

    Example:
        >>> lead_id = get_lead_id(uid, models, 'Cần hỗ trợ kỹ thuật - Nguyễn Văn A')
    """
    try:
        lead_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search',
            [[['name', '=', lead_name], ['type', '=', 'lead']]]
        )
        return lead_ids[0] if lead_ids else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up lead '{lead_name}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_lead_id: {e}")
        return None


def get_group_id(uid: int, models: Any, group_xmlid: str) -> Optional[int]:
    """
    Get security group ID by XML ID.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        group_xmlid: XML ID (e.g., 'sales_team.group_sale_salesman')

    Returns:
        Group ID if found, None otherwise

    Example:
        >>> group_id = get_group_id(uid, models, 'sales_team.group_sale_salesman')
    """
    try:
        # Split module and name
        if '.' in group_xmlid:
            module, name = group_xmlid.split('.', 1)
        else:
            # If no module specified, assume base
            module = 'base'
            name = group_xmlid

        # Look up by module and name
        data_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'search',
            [[['name', '=', name], ['module', '=', module]]]
        )

        if not data_ids:
            return None

        # Get the res_id
        data = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'read',
            [data_ids[0], ['res_id']]
        )

        return data['res_id'] if data else None

    except xmlrpc.client.Fault as e:
        print(f"⚠️  Error looking up group '{group_xmlid}': {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error in get_group_id: {e}")
        return None


# ============================================================================
# RECORD OPERATIONS
# ============================================================================

def create_or_update_record(
    uid: int,
    models: Any,
    model: str,
    search_domain: List,
    values: Dict,
    update_if_exists: bool = True
) -> Tuple[Optional[int], str]:
    """
    Create or update a record in Odoo.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        model: Model name (e.g., 'res.partner')
        search_domain: Search criteria (e.g., [['name', '=', 'ABC']])
        values: Field values to create/update
        update_if_exists: If True, update existing records; if False, skip

    Returns:
        Tuple of (record_id, action) where action is 'created', 'updated', or 'skipped'

    Example:
        >>> record_id, action = create_or_update_record(
        >>>     uid, models, 'res.partner',
        >>>     [['name', '=', 'Công ty ABC']],
        >>>     {'name': 'Công ty ABC', 'email': 'abc@example.com'}
        >>> )
        >>> print(f"Record {record_id} was {action}")
    """
    try:
        # Check if record exists
        existing_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search',
            [search_domain]
        )

        if existing_ids:
            existing_id = existing_ids[0]
            if update_if_exists:
                # Update existing record
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    model, 'write',
                    [[existing_id], values]
                )
                return existing_id, 'updated'
            else:
                return existing_id, 'skipped'
        else:
            # Create new record
            new_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                model, 'create',
                [values]
            )
            return new_id, 'created'

    except xmlrpc.client.Fault as e:
        print(f"❌ Error in create_or_update_record for {model}: {e}")
        return None, 'error'
    except Exception as e:
        print(f"❌ Unexpected error in create_or_update_record: {e}")
        return None, 'error'


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def count_records(uid: int, models: Any, model: str, domain: Optional[List] = None) -> int:
    """
    Count records in a model.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        model: Model name (e.g., 'res.partner')
        domain: Optional search domain (default: all records)

    Returns:
        Number of records

    Example:
        >>> total = count_records(uid, models, 'res.partner')
        >>> customers = count_records(uid, models, 'res.partner', [['customer_rank', '>', 0]])
    """
    try:
        search_domain = domain if domain is not None else []
        return models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search_count',
            [search_domain]
        )
    except (xmlrpc.client.Fault, Exception):
        return 0


def record_exists(uid: int, models: Any, model: str, domain: List) -> bool:
    """
    Check if a record exists.

    Args:
        uid: Authenticated user ID
        models: Odoo models proxy
        model: Model name
        domain: Search criteria

    Returns:
        True if record exists, False otherwise

    Example:
        >>> if record_exists(uid, models, 'res.partner', [['name', '=', 'ABC']]):
        >>>     print("Partner ABC exists")
    """
    try:
        record_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            model, 'search',
            [domain], {'limit': 1}
        )
        return len(record_ids) > 0
    except (xmlrpc.client.Fault, Exception):
        return False


# ============================================================================
# PROGRESS REPORTING
# ============================================================================

def print_progress(current: int, total: int, prefix: str = "Progress") -> None:
    """
    Print progress bar for batch operations.

    Args:
        current: Current record number
        total: Total records
        prefix: Optional prefix text

    Example:
        >>> for i, record in enumerate(records, 1):
        >>>     print_progress(i, len(records))
    """
    percentage = int(100 * current / total)
    print(f"  {prefix}: {current}/{total} ({percentage}%)")


def print_stats(stats: Dict[str, int]) -> None:
    """
    Print import/export statistics in a consistent format.

    Args:
        stats: Dictionary with keys like 'created', 'updated', 'errors', 'skipped'

    Example:
        >>> stats = {'created': 100, 'updated': 50, 'errors': 5}
        >>> print_stats(stats)
    """
    if 'created' in stats:
        print(f"✓ Created:  {stats['created']}")
    if 'updated' in stats:
        print(f"✓ Updated:  {stats['updated']}")
    if 'skipped' in stats:
        print(f"⊙ Skipped:  {stats['skipped']}")
    if 'errors' in stats:
        symbol = '❌' if stats['errors'] > 0 else '✓'
        print(f"{symbol} Errors:   {stats['errors']}")
