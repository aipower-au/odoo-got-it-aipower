# Spec: Automated Sales Assignment

## ADDED Requirements

### Requirement: Assign to Existing Salesperson for Duplicate Customers

The system SHALL automatically assign leads to the existing salesperson when a duplicate customer is detected with an assigned sales representative. If the matched customer has an assigned salesperson, the lead is assigned to the same salesperson. If the matched customer has no assigned salesperson, the lead is routed to the manual assignment workflow. All duplicate customers must maintain consistent sales ownership.

#### Scenario: Assign to existing salesperson
- **WHEN** an existing customer ID 12345 with assigned salesperson "John Doe" (User ID 100) is in the database and a new lead matches customer ID 12345 via MST and the system processes sales assignment
- **THEN** the lead is assigned to "John Doe" (User ID 100)
- **AND** assignment reason is "existing_customer_ownership"
- **AND** assignment is marked as "automatic"

#### Scenario: No salesperson assigned to existing customer
- **WHEN** an existing customer ID 12345 with NO assigned salesperson is in the database and a new lead matches customer ID 12345 and the system processes sales assignment
- **THEN** the lead is NOT automatically assigned
- **AND** a notification is sent to Sales Manager
- **AND** the lead status is "Pending Assignment"
- **AND** assignment reason is "existing_customer_no_owner"

### Requirement: Auto-Assign New Customers via Sales Rules

The system SHALL automatically assign leads for new customers (no duplicates found) using configurable sales assignment rules. Rules are executed in priority order with the first matching rule winning. If no rules match, the lead is routed to the default assignment queue. All rule applications are logged.

#### Scenario: Assign based on industry group rule
- **WHEN** sales assignment rules are configured with Rule 1 "Industry=Technology assigns to Tech Sales Team" and Rule 2 "Region=Hanoi assigns to North Sales Team" and a new lead has Industry="Technology", Region="Hanoi" and auto-assignment rules are evaluated
- **THEN** the lead is assigned to "Tech Sales Team"
- **AND** assignment reason is "rule_match: Industry=Technology"
- **AND** Rule 1 is logged as the applied rule

#### Scenario: No matching rules
- **WHEN** sales assignment rules exist but none match the lead criteria and a default assignment queue is configured and auto-assignment rules are evaluated
- **THEN** the lead is added to the default assignment queue
- **AND** assignment reason is "no_rule_match"
- **AND** a notification is sent to Sales Manager

#### Scenario: Auto-assign to round-robin queue
- **WHEN** no specific rules match and round-robin assignment is enabled for "General Sales Team" and auto-assignment processes the lead
- **THEN** the lead is assigned to the next salesperson in rotation
- **AND** assignment reason is "round_robin"
- **AND** the rotation counter is incremented

### Requirement: Handle Assignment Conflicts

The system SHALL prevent and detect assignment conflicts where multiple salespeople might claim the same customer. The system uses database-level locking when assigning leads, ensures atomicity of duplicate detection plus assignment, and prevents concurrent assignments to the same customer.

#### Scenario: Prevent concurrent assignment
- **WHEN** two leads for the same customer (MST "0123456789") arrive simultaneously and both leads trigger assignment processing at the same time and the system processes assignments
- **THEN** only ONE lead is assigned to a salesperson
- **AND** the second lead is marked as duplicate of the first
- **AND** both leads reference the same customer record
- **AND** both leads show the same assigned salesperson

#### Scenario: Detect existing assignment conflict
- **WHEN** a customer with existing assigned salesperson A is in the database and a lead attempts assignment to salesperson B and the system validates the assignment
- **THEN** the conflict is detected
- **AND** the assignment is rejected
- **AND** an alert is sent to Sales Manager
- **AND** the lead is assigned to existing salesperson A

### Requirement: Notify Stakeholders of Assignments

The system SHALL notify relevant stakeholders when leads are assigned. Notification recipients include the assigned salesperson (for new assignments), Sales Manager (for manual assignment requests and conflicts), and Telesales Team (for incomplete information). Notification methods include Odoo activity/task creation, email notification (optional, configurable), and in-app notification.

#### Scenario: Notify salesperson of new lead assignment
- **WHEN** a lead is automatically assigned to salesperson "Jane Smith" and the assignment is completed
- **THEN** an Odoo activity is created for "Jane Smith"
- **AND** the activity type is "Lead Assignment"
- **AND** the activity includes lead name, customer info, and assignment reason
- **AND** the activity due date is today

#### Scenario: Notify Sales Manager for manual assignment
- **WHEN** a lead matches existing customer with no assigned salesperson and the system routes to manual assignment
- **THEN** an Odoo activity is created for "Sales Manager"
- **AND** the activity type is "Manual Assignment Required"
- **AND** the activity includes lead details, customer match info, and reason for manual review
- **AND** the activity priority is "high"

### Requirement: Log All Assignment Operations

The system SHALL log all assignment operations for audit and performance tracking. Log information includes lead identifier, customer identifier (if matched), assignment timestamp, assigned salesperson (if any), assignment method (automatic/manual), assignment reason/rule applied, and processing duration.

#### Scenario: Log automatic assignment
- **WHEN** a lead is automatically assigned to salesperson ID 100 via rule "Industry=Technology" and the assignment is completed
- **THEN** an audit log is created with lead ID, customer ID (if duplicate), assigned to User ID 100, method "automatic", reason "rule_match: Industry=Technology", timestamp, and processing time in milliseconds

#### Scenario: Log manual assignment trigger
- **WHEN** a lead requires manual assignment (no owner for existing customer) and the manual assignment workflow is triggered
- **THEN** an audit log is created with lead ID, customer ID, assigned to null, method "manual_required", reason "existing_customer_no_owner", and timestamp
