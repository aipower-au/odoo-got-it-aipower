# Spec: Customer Duplicate Detection

## ADDED Requirements

### Requirement: Multi-Identifier Customer Matching

The system SHALL search for existing customers using all available identifiers (MST, phone, email) from validated lead data. The matching logic searches the customer database for exact matches on normalized identifiers, checking MST if present, phone number if present, and email if present, then returning all matching customer records with match confidence.

#### Scenario: Exact match on MST
- **WHEN** an existing customer with MST "0123456789", phone "0901234567", email "old@example.com" is in the database and a new lead arrives with MST "0123456789", phone "0909999999", email "new@example.com" and the system performs duplicate detection
- **THEN** the existing customer is matched with confidence "high"
- **AND** match reason includes "MST exact match"

#### Scenario: Match on multiple identifiers
- **WHEN** an existing customer with MST "0123456789", phone "0901234567", email "customer@example.com" is in the database and a new lead arrives with MST "0123456789", phone "0901234567", email "customer@example.com" and the system performs duplicate detection
- **THEN** the existing customer is matched with confidence "very_high"
- **AND** match reason includes "MST, phone, email exact match"

#### Scenario: No match found
- **WHEN** existing customers with various MST, phone, email combinations are in the database and a new lead arrives with MST "9999999999", phone "0905555555", email "newcustomer@example.com" and the system performs duplicate detection
- **THEN** no existing customer is matched
- **AND** the lead is flagged as "new_customer"

#### Scenario: Partial match on phone only
- **WHEN** an existing customer with phone "0901234567", no MST, email "customer@example.com" is in the database and a new lead arrives with phone "0901234567", MST "0123456789", different email and the system performs duplicate detection
- **THEN** the existing customer is matched with confidence "medium"
- **AND** match reason includes "phone exact match"

### Requirement: Handle Multiple Duplicate Matches

The system SHALL handle scenarios where a lead matches multiple existing customer records. If multiple matches are found, the system selects the customer with the highest confidence score. If confidence is equal, it prefers the customer with an assigned salesperson. If still tied, it prefers the most recently updated customer record. All potential matches are logged for manual review.

#### Scenario: Multiple matches with different confidence levels
- **WHEN** existing customer A with email "shared@example.com" (no other identifiers) and existing customer B with MST "0123456789" and email "shared@example.com" are in the database and a new lead with MST "0123456789" and email "shared@example.com" arrives and the system performs duplicate detection
- **THEN** customer B is selected as the primary match
- **AND** confidence is "very_high"
- **AND** customer A is logged as secondary match

#### Scenario: Multiple matches with equal confidence
- **WHEN** existing customer A with phone "0901234567", assigned to Sales Rep 1, updated 2025-01-01 and existing customer B with phone "0901234567", unassigned, updated 2025-01-15 are in the database and a new lead with phone "0901234567" arrives and the system performs duplicate detection
- **THEN** customer A is selected (has assigned salesperson)
- **AND** customer B is logged as potential duplicate for manual review

### Requirement: Detect Conflicting Customer Information

The system SHALL detect when matched customers have conflicting information compared to incoming lead data. Conflict detection compares company name (if MST matched), contact person name, and address information, then flags significant discrepancies for sales verification.

#### Scenario: Conflicting company name with same MST
- **WHEN** an existing customer with MST "0123456789", company name "ABC Company Ltd" is in the database and a new lead with MST "0123456789", company name "XYZ Corporation" arrives and duplicate detection finds MST match
- **THEN** a conflict is flagged for field "company_name"
- **AND** the lead is routed to sales verification workflow
- **AND** both company names are presented for verification

#### Scenario: No conflicts detected
- **WHEN** an existing customer with MST "0123456789", company name "ABC Company" is in the database and a new lead with MST "0123456789", company name "ABC Company" arrives and duplicate detection finds MST match
- **THEN** no conflicts are flagged
- **AND** customer information is considered consistent

### Requirement: Log Duplicate Detection Results

The system SHALL log all duplicate detection attempts with match outcomes and confidence scores. Log information includes lead identifier, search criteria used (which identifiers checked), matches found (customer IDs), confidence scores, selected primary match (if any), conflicts detected (if any), and processing time.

#### Scenario: Log successful duplicate detection
- **WHEN** a lead with MST "0123456789" matches existing customer ID 12345 and duplicate detection completes
- **THEN** a log entry is created with lead ID, search criteria "MST", match found customer ID 12345, confidence "high", and processing time in milliseconds

#### Scenario: Log no-match scenario
- **WHEN** a lead with MST "9999999999" finds no matches and duplicate detection completes
- **THEN** a log entry is created with lead ID, search criteria "MST, phone, email", matches found 0, result "new_customer", and processing time in milliseconds
