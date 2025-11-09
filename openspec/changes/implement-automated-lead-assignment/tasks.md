# Tasks: Implement Automated Lead Assignment

## Implementation Tasks

### Phase 1: Data Model & Infrastructure (Foundation)

#### Task 1.1: Extend CRM Lead Model
- Add fields to `crm.lead` model:
  - `validation_status` (selection: complete, incomplete, pending_info)
  - `duplicate_match_confidence` (selection: very_high, high, medium, low, none)
  - `duplicate_customer_id` (many2one: res.partner)
  - `assignment_method` (selection: automatic, manual, round_robin, rule_based)
  - `assignment_reason` (text)
  - `verification_status` (selection: pending, in_progress, completed, rejected)
  - `verified_by` (many2one: res.users)
  - `verification_date` (datetime)
- Add computed fields:
  - `normalized_phone` (char)
  - `normalized_email` (char)
  - `normalized_mst` (char)
- Create database indexes on MST, phone, email for performance
- **Validation:** Create test lead records with various data combinations

#### Task 1.2: Create Audit Log Model
- Create new model `crm.lead.audit.log`:
  - `lead_id` (many2one: crm.lead)
  - `customer_id` (many2one: res.partner)
  - `operation_type` (selection: validation, duplicate_detection, assignment, verification)
  - `operation_result` (text)
  - `processing_time_ms` (integer)
  - `created_by` (many2one: res.users)
  - `timestamp` (datetime)
  - `details` (json field for flexible logging)
- Add security access rules
- **Validation:** Test log creation and retrieval queries

#### Task 1.3: Create Sales Assignment Rules Model
- Create new model `crm.assignment.rule`:
  - `name` (char)
  - `sequence` (integer) - for priority ordering
  - `active` (boolean)
  - `condition_type` (selection: industry_group, region, customer_type, order_value)
  - `condition_value` (char)
  - `assign_to_user_id` (many2one: res.users)
  - `assign_to_team_id` (many2one: crm.team)
  - `assignment_method` (selection: direct, round_robin, queue)
- Add methods: `evaluate_rule(lead)`, `get_applicable_rules(lead)`
- **Validation:** Create test rules and verify priority ordering

### Phase 2: Lead Validation & Normalization

#### Task 2.1: Implement Data Normalization Service
- Create `crm.lead.normalizer` service class:
  - `normalize_phone(phone_string)` - Vietnamese phone format
  - `normalize_email(email_string)` - lowercase, trim
  - `normalize_mst(mst_string)` - remove formatting, validate length
- Add validation for normalized data format
- Handle edge cases (null, empty strings, invalid formats)
- **Validation:** Unit tests for all normalization functions with Vietnamese data

#### Task 2.2: Implement Lead Validation Logic
- Create `validate_lead_information()` method on `crm.lead`:
  - Check for at least one identifier (MST, phone, email)
  - Call normalization service
  - Set `validation_status` field
  - Create audit log entry
- Handle incomplete leads → assign to Telesales team
- **Validation:** Test with complete, incomplete, and edge case leads

#### Task 2.3: Add Automatic Validation on Lead Creation
- Override `create()` method on `crm.lead`:
  - Trigger validation automatically on new lead
  - Set validation status before save
- Override `write()` method:
  - Re-validate if MST/phone/email fields change
- **Validation:** Create leads via UI and API, verify auto-validation

### Phase 3: Duplicate Detection

#### Task 3.1: Implement Customer Matching Algorithm
- Create `crm.customer.matcher` service class:
  - `find_matches(lead)` - search by MST, phone, email
  - `calculate_confidence(match_fields)` - scoring algorithm
  - `select_primary_match(matches)` - tie-breaking logic
- Use database queries with indexed fields for performance
- Return match results with confidence scores
- **Validation:** Test with known duplicate scenarios, verify accuracy

#### Task 3.2: Implement Conflict Detection
- Create `detect_conflicts(lead, matched_customer)` method:
  - Compare company name (if MST matched)
  - Compare contact person name
  - Compare address fields
  - Return list of conflicting fields
- **Validation:** Test with matching MST but different company names

#### Task 3.3: Add Duplicate Detection to Lead Workflow
- Create `detect_duplicates()` method on `crm.lead`:
  - Call customer matcher service
  - Update `duplicate_match_confidence` and `duplicate_customer_id`
  - Log results to audit log
  - Trigger appropriate workflow (assignment vs. verification)
- **Validation:** Process leads through full workflow, verify correct routing

### Phase 4: Automated Assignment

#### Task 4.1: Implement Assignment for Duplicate Customers
- Create `assign_to_existing_owner(matched_customer)` method:
  - Get salesperson from matched customer
  - Assign lead to same salesperson
  - Set assignment_method = 'automatic'
  - Set assignment_reason = 'existing_customer_ownership'
  - Create notification activity for salesperson
- Handle case where matched customer has no owner → manual assignment
- **Validation:** Test with customers having/not having assigned salespeople

#### Task 4.2: Implement Rule-Based Assignment
- Create `apply_assignment_rules()` method:
  - Get applicable rules ordered by sequence
  - Evaluate each rule against lead data
  - Assign to first matching rule
  - Log which rule was applied
- Handle no-match scenario → default queue or round-robin
- **Validation:** Create test rules, verify correct rule selection

#### Task 4.3: Implement Round-Robin Assignment
- Create `assign_round_robin(team)` method:
  - Get team members
  - Track last assigned member (using sequence or dedicated model)
  - Assign to next member in rotation
  - Update rotation counter
- **Validation:** Assign multiple leads, verify even distribution

#### Task 4.4: Add Assignment Conflict Prevention
- Implement database locking in assignment operations:
  - Use `WITH FOR UPDATE` or Odoo's locking mechanisms
  - Ensure atomic duplicate detection + assignment
- Create `validate_assignment(lead, salesperson)` method:
  - Check for existing conflicting assignments
  - Prevent assigning same customer to different salespeople
- **Validation:** Test concurrent lead submissions for same customer

#### Task 4.5: Implement Assignment Notifications
- Create notification templates:
  - "New Lead Assignment" for salespeople
  - "Manual Assignment Required" for managers
  - "Assignment Conflict Detected" for escalation
- Create Odoo activities with appropriate priority and due dates
- **Validation:** Trigger assignments, verify notifications are created

### Phase 5: Sales Verification Workflow

#### Task 5.1: Create Verification Interface View
- Design form view for lead verification:
  - Display lead information
  - Show matched customer details (if duplicate)
  - Highlight conflicting fields
  - Buttons: "Confirm Match", "Reject Match", "Create New Customer", "Update Customer"
- Add smart buttons to navigate between lead and customer
- **Validation:** Open verification view with various lead scenarios

#### Task 5.2: Implement Customer Confirmation Logic
- Create `confirm_customer_match()` method:
  - Link lead to confirmed customer
  - Convert lead to opportunity
  - Update verification_status = 'completed'
  - Log verification in audit log
- **Validation:** Confirm matches, verify opportunity creation

#### Task 5.3: Implement New Customer Creation Workflow
- Create `create_new_customer_from_lead()` method:
  - Pre-fill customer form with lead data
  - Trigger MST API enrichment (if MST present)
  - Set creating salesperson as customer owner
  - Link lead to new customer
  - Log as new customer creation
- **Validation:** Create new customers from leads, verify data flow

#### Task 5.4: Implement Customer Ownership Claiming
- Create tree/kanban view for unassigned customers
- Create `claim_customer_ownership(justification)` method:
  - Assign salesperson to customer
  - Assign related leads to salesperson
  - Log claim with justification
  - Create notification
- Add manager approval workflow for high-value customers (optional)
- **Validation:** Claim unassigned customers, verify assignment

#### Task 5.5: Implement Conflict Resolution
- Create conflict detection on claim attempts:
  - Check if customer already has owner
  - Prevent duplicate claims
  - Provide escalation option
- Create `escalate_ownership_dispute()` method:
  - Create escalation ticket for manager
  - Notify both salespeople
  - Freeze customer assignment
- **Validation:** Test concurrent claim attempts, verify conflict handling

### Phase 6: Monitoring & Reporting

#### Task 6.1: Create Verification Dashboard
- Create dashboard view showing:
  - Leads by verification status (pending, in_progress, completed)
  - Average verification time
  - Overdue verifications (>24 hours)
  - Salespeople verification workload
- Use Odoo dashboard/reporting features or custom view
- **Validation:** Generate test data, verify dashboard accuracy

#### Task 6.2: Implement Overdue Verification Alerts
- Create scheduled action (cron job):
  - Run every 6 hours
  - Find leads in verification >24 hours
  - Send reminders to assigned salespeople
  - Escalate to manager after 48 hours
- **Validation:** Manually trigger cron, verify alerts sent

#### Task 6.3: Create Assignment Performance Reports
- Create report showing:
  - Assignment method distribution (automatic vs. manual)
  - Average time from lead creation to assignment
  - Duplicate detection accuracy (false positives tracking)
  - Most frequently triggered assignment rules
- **Validation:** Generate reports with historical data

### Phase 7: Integration & Testing

#### Task 7.1: Create End-to-End Test Scenarios
- Test scenario 1: Complete lead → no duplicate → auto-assign via rule
- Test scenario 2: Complete lead → duplicate found → assign to existing owner
- Test scenario 3: Complete lead → duplicate found → no owner → manual assignment
- Test scenario 4: Incomplete lead → assign to Telesales
- Test scenario 5: Duplicate with conflicts → sales verification → confirm match
- Test scenario 6: False positive duplicate → sales verification → create new customer
- **Validation:** All scenarios complete successfully with correct outcomes

#### Task 7.2: Performance Testing
- Test with large customer database (10,000+ records)
- Measure duplicate detection query performance
- Verify database indexes are being used
- Test concurrent lead processing (10+ simultaneous leads)
- **Validation:** All operations complete within acceptable time (<2 seconds)

#### Task 7.3: Create User Documentation
- Document verification workflow for salespeople
- Document assignment rule configuration for managers
- Create troubleshooting guide for common scenarios
- **Validation:** User testing with documentation

#### Task 7.4: Deploy to Test Environment
- Package custom module with proper manifest
- Deploy to test Odoo instance
- Configure initial assignment rules
- Load test data
- **Validation:** Full workflow testing in test environment

## Dependencies

- **Task Dependencies:**
  - Phase 2 depends on Phase 1 (data models must exist)
  - Phase 3 depends on Phase 2 (validation before duplicate detection)
  - Phase 4 depends on Phase 3 (assignment uses duplicate detection results)
  - Phase 5 depends on Phase 4 (verification handles assignment outcomes)
  - Phase 6 can run in parallel with Phase 5
  - Phase 7 depends on all previous phases

- **Parallel Work Opportunities:**
  - Tasks within same phase can often be parallelized
  - Phase 6 (monitoring) can be built alongside Phase 5
  - Documentation (7.3) can start during Phase 5-6

## Estimated Timeline

- Phase 1: 2-3 days (foundation work)
- Phase 2: 2 days (validation & normalization)
- Phase 3: 3 days (duplicate detection algorithm)
- Phase 4: 4 days (assignment logic - most complex)
- Phase 5: 4 days (verification workflows)
- Phase 6: 2 days (monitoring & reporting)
- Phase 7: 3 days (testing & deployment)

**Total Estimate:** 20-22 days (approximately 4 weeks for single developer)

## Success Criteria

- ✅ All automated tests pass (unit tests for each component)
- ✅ End-to-end scenarios complete successfully
- ✅ Duplicate detection accuracy >95% measured against manual review
- ✅ Performance: Lead processing <2 seconds for 90% of cases
- ✅ Zero assignment conflicts in test scenarios
- ✅ All audit logs capture required information
- ✅ User acceptance testing completed by sales team
