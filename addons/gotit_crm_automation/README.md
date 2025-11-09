# GotIt CRM Automation

Automated lead assignment system for Odoo 18 CRM with intelligent duplicate detection and sales verification workflows.

## Features

### 1. Lead Information Validation
- Automatic validation of lead completeness
- Normalization of identifiers (MST, phone, email)
- Vietnamese phone number format standardization
- Incomplete leads routed to Telesales team

### 2. Customer Duplicate Detection
- Multi-identifier matching (MST + phone + email)
- Confidence-based scoring:
  - Very High (95%+): Multiple identifiers match
  - High (85-95%): MST exact match
  - Medium (70-85%): Phone or email match
- Intelligent tie-breaking for multiple matches
- Comprehensive audit logging

### 3. Automated Sales Assignment
- Automatic assignment to existing customer owners
- Configurable rule-based assignment for new customers
- Manual assignment workflow for edge cases
- Activity notifications to salespeople and managers
- Conflict prevention with database locking

### 4. Sales Verification Workflow
- Customer match confirmation interface
- False positive rejection with new customer creation
- MST API integration ready (enrichment placeholder)
- Verification tracking and audit trail

### 5. Audit Logging
- Complete operation history for all leads
- Processing time metrics
- Operation details in JSON format
- Read-only logs for compliance

## Installation

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r gotit_crm_automation /path/to/odoo/addons/
   ```

2. Update the addons list:
   ```bash
   odoo-bin -u all -d your_database
   ```

3. Install the module from Apps menu or via command line:
   ```bash
   odoo-bin -i gotit_crm_automation -d your_database
   ```

## Configuration

### 1. Assignment Rules
Navigate to: **CRM > Configuration > Automation > Assignment Rules**

Create rules with:
- **Sequence**: Priority order (lower = higher priority)
- **Condition Type**: Industry, Region, Customer Type, Country
- **Condition Value**: Value to match (e.g., "Technology", "Hanoi")
- **Assignment Method**: Direct, Round Robin, or Queue
- **Assign To**: User and/or Team

### 2. Activity Types
The module creates three activity types automatically:
- **Lead Assignment**: Notifies salespeople of new assignments
- **Manual Assignment Required**: Alerts managers to assign leads manually
- **Customer Verification Needed**: Requests verification of duplicate matches

### 3. Access Rights
- **Sales Users**: Can view audit logs and assignment rules (read-only)
- **Sales Managers**: Full access to configure rules and view/delete logs

## Usage

### Automatic Processing
When a new lead is created (via UI, API, or import):
1. Lead is automatically validated for completeness
2. If complete, duplicate detection runs immediately
3. If duplicate found with owner, lead is auto-assigned
4. If new customer, assignment rules are applied
5. Activity created to notify assigned salesperson

### Manual Verification
For leads with duplicate matches:
1. Open the lead form
2. Go to "Automation" tab
3. Review duplicate customer information
4. Click one of:
   - **Confirm Match**: Link lead to existing customer
   - **Reject Match**: Create new customer instead
   - **Create New Customer**: Manually create from lead data

### Viewing Audit Logs
Navigate to: **CRM > Configuration > Automation > Audit Logs**

Filter by:
- Operation Type (Validation, Duplicate Detection, Assignment, Verification)
- Date range
- Specific lead or customer

## Technical Details

### Models
- `crm.lead` (extended): Added validation, duplicate, and assignment fields
- `crm.lead.audit.log`: Immutable audit trail
- `crm.assignment.rule`: Configurable assignment rules
- `crm.lead.normalizer`: Data normalization service (AbstractModel)
- `crm.customer.matcher`: Duplicate detection service (AbstractModel)

### Key Methods
- `validate_lead_information()`: Check lead completeness
- `detect_duplicates()`: Find matching customers
- `apply_assignment_rules()`: Evaluate and apply rules
- `action_confirm_customer_match()`: Verify duplicate
- `action_create_new_customer()`: Create new from lead

### Database Indexes
The module creates indexes on:
- `crm_lead.normalized_phone`
- `crm_lead.normalized_email`
- `crm_lead.normalized_mst`
- `res_partner.vat` (MST)

### Performance
- Lead validation: <100ms
- Duplicate detection: <500ms
- Total processing: <2 seconds (90th percentile)

## Dependencies
- `base`: Odoo base module
- `crm`: Odoo CRM module
- `mail`: Mail and activity management

## Roadmap
See `openspec/changes/implement-automated-lead-assignment/` for:
- Remaining phases (Phase 2-7)
- Detailed implementation tasks
- Success criteria

## License
LGPL-3

## Support
For issues and questions, refer to the project repository:
https://github.com/aipower-au/odoo-got-it-aipower
