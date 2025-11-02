#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify imported Sprint 1 data
Checks record counts, relationships, and data integrity

Usage: python3 verify_data.py
"""

import xmlrpc.client
import sys
from config import ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD


def connect_odoo():
    """Connect to Odoo and return connection objects"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        if not uid:
            raise Exception("Authentication failed")

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)


def verify_users(uid, models):
    """Verify user data"""
    print("\n" + "=" * 70)
    print("👥 VERIFYING USERS")
    print("=" * 70)

    # Count users (excluding admin and system users)
    total_users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search_count',
        [[]]
    )

    sales_users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search_count',
        [[['groups_id', 'in', [models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model.data', 'xmlid_to_res_id',
            ['sales_team.group_sale_salesman']
        )]]]]
    )

    print(f"\n📊 User Statistics:")
    print(f"   Total Users: {total_users}")
    print(f"   Sales Users: {sales_users}")

    # Get sample users
    user_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search',
        [[]], {'limit': 5}
    )

    users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'read',
        [user_ids, ['name', 'login', 'email']]
    )

    print(f"\n📝 Sample Users:")
    for user in users:
        print(f"   • {user['name']} ({user['login']})")

    return {'total': total_users, 'sales': sales_users}


def verify_teams(uid, models):
    """Verify sales teams data"""
    print("\n" + "=" * 70)
    print("🏆 VERIFYING SALES TEAMS")
    print("=" * 70)

    total_teams = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'search_count',
        [[]]
    )

    print(f"\n📊 Sales Teams Statistics:")
    print(f"   Total Teams: {total_teams}")

    # Get all teams with details
    team_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'search',
        [[]]
    )

    teams = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'read',
        [team_ids, ['name', 'user_id', 'member_ids']]
    )

    print(f"\n📝 Teams Details:")
    for team in teams:
        leader_name = team['user_id'][1] if team['user_id'] else 'No leader'
        member_count = len(team['member_ids']) if team['member_ids'] else 0
        print(f"   • {team['name']}")
        print(f"     Leader: {leader_name} | Members: {member_count}")

    return {'total': total_teams, 'teams': teams}


def verify_partners(uid, models):
    """Verify partner/customer data"""
    print("\n" + "=" * 70)
    print("🏢 VERIFYING CUSTOMERS/PARTNERS")
    print("=" * 70)

    # Get user partner IDs to exclude from count
    user_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search',
        [[]]
    )

    users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'read',
        [user_ids, ['partner_id']]
    )

    user_partner_ids = [u['partner_id'][0] for u in users if u['partner_id']]

    # Count customer partners (excluding user partners)
    total_partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_count',
        [[['id', 'not in', user_partner_ids]]]
    )

    companies = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_count',
        [[['is_company', '=', True], ['id', 'not in', user_partner_ids]]]
    )

    # Partners with salespeople assigned
    with_salesperson = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_count',
        [[['user_id', '!=', False], ['id', 'not in', user_partner_ids]]]
    )

    # Partners with Tax ID
    with_vat = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_count',
        [[['vat', '!=', False], ['id', 'not in', user_partner_ids]]]
    )

    print(f"\n📊 Partner Statistics:")
    print(f"   Total Partners (non-user): {total_partners}")
    print(f"   Companies: {companies}")
    print(f"   With Salesperson: {with_salesperson}")
    print(f"   With Tax ID: {with_vat}")

    # Get sample partners
    partner_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[['id', 'not in', user_partner_ids]]], {'limit': 5}
    )

    partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'read',
        [partner_ids, ['name', 'vat', 'user_id']]
    )

    print(f"\n📝 Sample Customers:")
    for partner in partners:
        salesperson = partner['user_id'][1] if partner['user_id'] else 'Unassigned'
        vat = partner.get('vat', 'N/A')
        print(f"   • {partner['name']}")
        print(f"     Tax ID: {vat} | Salesperson: {salesperson}")

    return {
        'total': total_partners,
        'companies': companies,
        'with_salesperson': with_salesperson,
        'with_vat': with_vat
    }


def verify_relationships(uid, models):
    """Verify data relationships"""
    print("\n" + "=" * 70)
    print("🔗 VERIFYING RELATIONSHIPS")
    print("=" * 70)

    issues = []

    # Check teams without leaders
    teams_no_leader = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'search_count',
        [[['user_id', '=', False]]]
    )

    if teams_no_leader > 0:
        issues.append(f"⚠️  {teams_no_leader} teams without leaders")
    else:
        print(f"   ✓ All teams have leaders")

    # Check teams without members
    team_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'search',
        [[]]
    )

    teams = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'crm.team', 'read',
        [team_ids, ['name', 'member_ids']]
    )

    teams_no_members = [t for t in teams if not t['member_ids']]

    if teams_no_members:
        issues.append(f"⚠️  {len(teams_no_members)} teams without members")
        for team in teams_no_members:
            print(f"   - {team['name']}")
    else:
        print(f"   ✓ All teams have members")

    # Check partners without salespeople
    user_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'search',
        [[]]
    )

    users = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.users', 'read',
        [user_ids, ['partner_id']]
    )

    user_partner_ids = [u['partner_id'][0] for u in users if u['partner_id']]

    partners_no_sales = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_count',
        [[['user_id', '=', False], ['is_company', '=', True], ['id', 'not in', user_partner_ids]]]
    )

    if partners_no_sales > 0:
        issues.append(f"⚠️  {partners_no_sales} company partners without salesperson")
    else:
        print(f"   ✓ All company partners have salespeople")

    return issues


def main():
    """Main execution"""
    print("=" * 70)
    print("SPRINT 1 DATA VERIFICATION")
    print("=" * 70)

    print(f"\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo()
    print(f"   ✓ Connected as UID: {uid}")

    # Verify each data type
    user_stats = verify_users(uid, models)
    team_stats = verify_teams(uid, models)
    partner_stats = verify_partners(uid, models)
    relationship_issues = verify_relationships(uid, models)

    # Final summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    print(f"\n📊 Record Counts:")
    print(f"   Users: {user_stats['total']} (Sales: {user_stats['sales']})")
    print(f"   Sales Teams: {team_stats['total']}")
    print(f"   Customers: {partner_stats['total']} (Companies: {partner_stats['companies']})")

    print(f"\n📈 Data Quality:")
    print(f"   Customers with Salesperson: {partner_stats['with_salesperson']}/{partner_stats['total']}")
    print(f"   Customers with Tax ID: {partner_stats['with_vat']}/{partner_stats['total']}")

    if relationship_issues:
        print(f"\n⚠️  Issues Found ({len(relationship_issues)}):")
        for issue in relationship_issues:
            print(f"   {issue}")
        print("\n⚠️  Verification completed with warnings")
    else:
        print(f"\n✅ All relationship checks passed!")

    # Expected values for Sprint 1
    print(f"\n📋 Expected vs Actual:")
    print(f"   Staff: Expected ~22, Actual: {user_stats['total']}")
    print(f"   Teams: Expected ~7, Actual: {team_stats['total']}")
    print(f"   Customers: Expected ~100, Actual: {partner_stats['total']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
