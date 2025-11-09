# Spec: Sales Verification Workflow

## ADDED Requirements

### Requirement: Enable Sales to Verify Customer Information

The system SHALL provide a verification interface for salespeople to review and confirm customer information when matches or conflicts are detected. Verification tasks include reviewing matched customer details, confirming customer identity (same vs. different customer), updating customer information if needed, and claiming or rejecting customer ownership.

#### Scenario: Sales verifies matching customer is correct
- **WHEN** a lead is matched to existing customer ID 12345 and the lead is assigned to salesperson "John Doe" for verification and "John Doe" opens the verification interface and reviews the customer information and confirms the match is correct
- **THEN** the customer record is confirmed as same
- **AND** the lead is converted to opportunity under customer ID 12345
- **AND** "John Doe" is confirmed as the assigned salesperson
- **AND** the verification status is "confirmed"

#### Scenario: Sales rejects match - different customer
- **WHEN** a lead is matched to existing customer ID 12345 based on phone number and salesperson reviews the customer details and determines this is a DIFFERENT customer (wrong match) and selects "Create New Customer"
- **THEN** a new customer record is created
- **AND** the lead is linked to the new customer
- **AND** the original match is logged as "false_positive"
- **AND** duplicate detection algorithm is flagged for review

#### Scenario: Sales updates customer information
- **WHEN** a lead has conflicting company name with matched customer where existing customer shows "ABC Company" and lead shows "ABC Company Ltd" and salesperson reviews the conflict and updates customer company name to "ABC Company Ltd" and confirms the match
- **THEN** the customer record is updated with new company name
- **AND** the change is logged in customer history
- **AND** the lead is converted to opportunity

### Requirement: Handle New Customer Creation

The system SHALL allow salespeople to create new customer records when leads don't match existing customers or matches are rejected. The new customer creation process pre-fills the form with lead information, validates required fields, enriches with MST API data (if MST provided), and assigns the creating salesperson as customer owner.

#### Scenario: Create new customer from verified lead
- **WHEN** a lead has no duplicate matches (new customer) and the lead contains MST "0123456789", phone "0901234567", email "new@example.com" and salesperson initiates new customer creation
- **THEN** a customer form is opened pre-filled with MST "0123456789", phone "0901234567", and email "new@example.com"
- **AND** MST API lookup is triggered for company details
- **AND** the salesperson is set as customer owner

#### Scenario: MST enrichment during customer creation
- **WHEN** salesperson is creating a new customer with MST "0123456789" and the customer form loads
- **THEN** MST API is called with MST "0123456789"
- **AND** company name, legal name, registration date are auto-filled
- **AND** company status is validated (active/suspended/dissolved)
- **AND** if status is "dissolved", a warning is displayed

### Requirement: Claim Customer Ownership

The system SHALL allow salespeople to claim ownership of customers that have no assigned salesperson. Ownership claiming displays customers pending ownership assignment, allows sales to claim based on their expertise/territory, requires manager approval for high-value customers (optional), and logs ownership claims with justification.

#### Scenario: Sales claims unassigned customer
- **WHEN** an existing customer ID 12345 has no assigned salesperson and a new lead for this customer triggers manual assignment and salesperson "Jane Smith" is notified and "Jane Smith" reviews the customer and lead and clicks "Claim Customer" and provides justification "Customer in my territory - Hanoi region"
- **THEN** "Jane Smith" is assigned as customer owner
- **AND** the lead is assigned to "Jane Smith"
- **AND** the claim is logged with justification and timestamp

#### Scenario: Manager approval required for high-value customer
- **WHEN** an existing customer ID 12345 has estimated annual value greater than $100,000 and the customer has no assigned salesperson and salesperson "John Doe" attempts to claim the customer
- **THEN** a manager approval request is created
- **AND** the customer is in "Pending Approval" status
- **AND** "John Doe" receives notification that approval is required
- **AND** Sales Manager receives approval request

### Requirement: Handle Conflicting Ownership Claims

The system SHALL resolve conflicts when multiple salespeople attempt to claim the same customer. Conflict resolution gives first claim priority (timestamp-based), notifies later claimers of existing assignment, provides escalation path to manager for disputes, and logs all claim attempts for audit.

#### Scenario: Second salesperson attempts claim on already-assigned customer
- **WHEN** customer ID 12345 was claimed by "Jane Smith" at 10:00 AM and salesperson "John Doe" attempts to claim same customer at 10:05 AM and "John Doe" submits the claim
- **THEN** the claim is rejected
- **AND** "John Doe" is notified that customer is already assigned to "Jane Smith"
- **AND** an option to "Request Manager Review" is provided
- **AND** the rejected claim is logged

#### Scenario: Escalate ownership dispute to manager
- **WHEN** "John Doe" was rejected when claiming customer ID 12345 (already assigned to "Jane Smith") and "John Doe" clicks "Request Manager Review" and provides justification "I have existing relationship with this customer"
- **THEN** an escalation ticket is created for Sales Manager
- **AND** both "Jane Smith" and "John Doe" are notified of the review
- **AND** the customer assignment is frozen until manager decision

### Requirement: Track Verification Workflow Progress

The system SHALL track and display progress of leads through the verification workflow. Tracking information includes verification status (pending, in_progress, completed, rejected), salesperson assigned for verification, verification start and completion timestamps, actions taken (confirmed match, created new, updated info), and bottlenecks and overdue verifications.

#### Scenario: Display verification dashboard
- **WHEN** multiple leads are in verification workflow and Sales Manager opens the verification dashboard
- **THEN** the dashboard displays total leads pending verification, leads by verification status, average verification time, overdue verifications (greater than 24 hours), and salespeople with most pending verifications

#### Scenario: Alert for overdue verification
- **WHEN** a lead has been in "Pending Verification" status for 48 hours and salesperson "Jane Smith" was assigned for verification and the system checks for overdue verifications
- **THEN** an alert is sent to "Jane Smith"
- **AND** an escalation notification is sent to Sales Manager
- **AND** the lead is highlighted in verification queue

### Requirement: Log Verification Activities

The system SHALL log all verification activities for audit and performance analysis. Log information includes lead and customer identifiers, salesperson performing verification, verification decision (confirmed, rejected, updated), fields updated (if any), verification start and end timestamps, and total time spent.

#### Scenario: Log successful verification
- **WHEN** salesperson "John Doe" verifies a lead matched to customer ID 12345 and "John Doe" confirms the match and completes verification
- **THEN** a verification log is created with lead ID, customer ID 12345, verified by User ID for "John Doe", decision "confirmed_match", fields updated none, start time, end time, and duration in seconds

#### Scenario: Log new customer creation
- **WHEN** salesperson "Jane Smith" creates new customer from unmatched lead and the new customer record is saved
- **THEN** a verification log is created with lead ID, customer ID (new customer ID), created by User ID for "Jane Smith", decision "new_customer_created", MST enrichment "success" (if applicable), start time, end time, and duration in seconds
