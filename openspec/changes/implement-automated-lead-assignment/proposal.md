# Proposal: Implement Automated Lead Assignment

## Why

Implement an automated lead assignment system for Odoo CRM that intelligently routes incoming leads from landing pages based on customer duplicate detection and sales assignment rules. The system will verify customer information completeness, detect duplicates across multiple identifiers (MST, phone, email), and automatically assign leads to the appropriate salesperson or request manual assignment when needed.

## Motivation

Currently, the GotIt CRM receives leads from multiple landing pages but lacks an automated system to:
- Validate customer information completeness before processing
- Detect duplicate customers using MST (Tax ID), phone numbers (SDT), and email addresses
- Automatically route leads to existing salespeople when customer matches are found
- Handle new vs. existing customer scenarios with appropriate verification workflows
- Ensure consistent sales assignment to prevent customer confusion and data conflicts

This manual process leads to:
- Delayed lead response times
- Inconsistent customer assignments across sales team
- Risk of multiple salespeople contacting the same customer
- Difficulty tracking customer history across multiple lead submissions

## Goals

1. **Automate lead intake validation** - Check completeness of customer information (MST, SDT, Email) before processing
2. **Implement duplicate detection** - Match incoming leads against existing customers using multiple identifiers
3. **Intelligent assignment routing** - Automatically assign leads based on customer status and existing sales relationships
4. **Sales verification workflow** - Enable sales team to verify and claim customer ownership
5. **Notification system** - Alert relevant parties when manual assignment is required

## Non-Goals

- Product selection or quotation automation (handled separately)
- Integration with external marketing automation platforms (future enhancement)
- Lead scoring or prioritization algorithms (out of scope for Sprint 1)
- Multi-language support beyond Vietnamese (not required)

## Capabilities Affected

This change introduces new capabilities:

1. **Lead Information Validation** (`lead-information-validation`)
   - Validate incoming lead data completeness
   - Check for required fields (MST, SDT, Email)

2. **Customer Duplicate Detection** (`customer-duplicate-detection`)
   - Match customers across MST, phone, and email identifiers
   - Handle existing customer identification

3. **Automated Sales Assignment** (`automated-sales-assignment`)
   - Route leads to existing salespeople based on customer ownership
   - Auto-assign new customers via configurable rules
   - Handle unassigned customer scenarios

4. **Sales Verification Workflow** (`sales-verification-workflow`)
   - Enable sales to verify customer information
   - Confirm or update customer ownership
   - Process new customer creation

## Dependencies

- Requires existing CRM customer database with MST, phone, email fields
- Depends on sales assignment rules configuration (from existing project context)
- Needs notification system for assignment alerts (can use Odoo's built-in activity/notification system)

## Risks & Mitigations

**Risk 1: Duplicate detection false positives**
- Mitigation: Implement multi-factor matching (require 2+ identifier matches for high-confidence duplicates)
- Mitigation: Provide manual review interface for sales verification

**Risk 2: Performance impact with large customer database**
- Mitigation: Use database indexing on MST, phone, email fields
- Mitigation: Implement asynchronous processing for non-urgent assignments

**Risk 3: Race conditions with concurrent lead submissions**
- Mitigation: Use database transactions and row-level locking
- Mitigation: Implement idempotent assignment operations

## Open Questions

1. Should the system allow multiple salespeople to handle the same customer for different product lines?
   - Current assumption: No, one salesperson per customer for consistency

2. What happens when a duplicate is found but the existing customer has no assigned salesperson?
   - Proposed: Trigger manual assignment notification to sales manager

3. How should the system handle leads with incomplete information (missing MST/phone/email)?
   - Proposed: Route to telesales team for information collection (per existing business rules)

4. What is the expected response time for sales verification steps?
   - Need clarification: Should there be auto-escalation if no response within X hours?

## Success Criteria

- ✅ 100% of complete leads are automatically validated and routed
- ✅ Duplicate customer detection accuracy > 95% (measured against manual review)
- ✅ Average lead-to-assignment time reduced from manual baseline
- ✅ Zero cases of multiple salespeople assigned to same customer
- ✅ All assignment decisions are auditable with timestamps and reasoning
