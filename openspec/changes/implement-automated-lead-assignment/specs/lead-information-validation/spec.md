# Spec: Lead Information Validation

## ADDED Requirements

### Requirement: Validate Lead Data Completeness

The system SHALL validate incoming lead data for required customer identification fields before processing. At least ONE of these identifiers must be present and non-empty: MST (Mã số thuế - Tax ID), Phone number (SDT - Số điện thoại), or Email address.

#### Scenario: Complete lead with MST
- **WHEN** a lead arrives from a landing page with MST "0123456789"
- **THEN** the system validates the lead information
- **AND** the lead is marked as "complete"
- **AND** processing continues to duplicate detection

#### Scenario: Complete lead with phone and email only
- **WHEN** a lead arrives with phone "0901234567" and email "customer@example.com" but no MST
- **THEN** the system validates the lead information
- **AND** the lead is marked as "complete"
- **AND** processing continues to duplicate detection

#### Scenario: Incomplete lead missing all identifiers
- **WHEN** a lead arrives without MST, phone, or email
- **THEN** the lead is marked as "incomplete"
- **AND** the lead is assigned to Telesales team for information collection
- **AND** the lead status is set to "Pending Information"

### Requirement: Sanitize and Normalize Customer Data

The system SHALL normalize customer identification data before validation and duplicate detection. Normalization rules: Phone numbers remove spaces, hyphens, parentheses and standardize to Vietnamese format (84XXXXXXXXX or 0XXXXXXXXX); Email addresses convert to lowercase and trim whitespace; MST removes spaces and hyphens, validates length (10-13 digits).

#### Scenario: Normalize Vietnamese phone number
- **WHEN** a lead contains phone number "090 123 4567"
- **THEN** the normalized value is "0901234567"

#### Scenario: Normalize email address
- **WHEN** a lead contains email "Customer@EXAMPLE.COM  "
- **THEN** the normalized value is "customer@example.com"

#### Scenario: Normalize MST with formatting
- **WHEN** a lead contains MST "0123-456-789"
- **THEN** the normalized value is "0123456789"
- **AND** the MST length is validated as 10 digits

### Requirement: Log Validation Results

The system SHALL log all validation attempts with outcomes for audit and troubleshooting. Log information includes: timestamp of validation, lead source (landing page URL/identifier), validation outcome (complete/incomplete), fields present and missing, and assigned team (if routed for information collection).

#### Scenario: Log successful validation
- **WHEN** a lead with MST "0123456789" is validated successfully
- **THEN** a log entry is created with timestamp, lead source identifier, outcome "complete", fields present "MST", and next step "duplicate_detection"

#### Scenario: Log failed validation
- **WHEN** a lead with no identifiers fails validation
- **THEN** a log entry is created with timestamp, lead source identifier, outcome "incomplete", fields missing "MST, phone, email", and assigned to "Telesales"
