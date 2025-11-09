# Design: Automated Lead Assignment Architecture

## Overview

This document captures the architectural decisions and design patterns for implementing the automated lead assignment system in Odoo CRM.

## Architecture Decisions

### AD-1: Service-Oriented Architecture within Odoo Framework

**Decision:** Implement business logic as service classes separate from Odoo models.

**Rationale:**
- **Separation of Concerns:** Keep models focused on data structure, move complex logic to services
- **Testability:** Service classes are easier to unit test in isolation
- **Reusability:** Services can be called from multiple contexts (UI, API, scheduled jobs)
- **Maintainability:** Easier to locate and modify specific business logic

**Implementation:**
- `crm.lead.normalizer` - Data normalization service
- `crm.customer.matcher` - Duplicate detection service
- `crm.assignment.engine` - Assignment rule evaluation service

**Trade-offs:**
- Slightly more complex module structure
- Need to instantiate services (minimal overhead in Odoo)
- Worth it for long-term maintainability

### AD-2: Confidence-Based Duplicate Detection

**Decision:** Use multi-factor matching with confidence scores rather than binary match/no-match.

**Confidence Levels:**
- **Very High (95%+):** Multiple identifiers match (MST + phone + email, or MST + phone)
- **High (85-95%):** MST exact match only
- **Medium (70-85%):** Phone or email exact match only
- **Low (<70%):** Partial matches or fuzzy matches (not used in Sprint 1)

**Rationale:**
- **Flexibility:** Handles varying data quality (some leads missing MST, etc.)
- **Accuracy:** Multiple identifiers provide higher confidence than single match
- **Sales Verification:** Medium confidence triggers manual review, preventing false positives
- **Auditable:** Clear reasoning for why matches were made or missed

**Implementation:**
```python
def calculate_confidence(self, lead, customer, match_fields):
    score = 0
    if 'mst' in match_fields: score += 60  # MST is strongest identifier
    if 'phone' in match_fields: score += 25
    if 'email' in match_fields: score += 15
    # Bonus for multiple matches
    if len(match_fields) >= 2: score += 10
    return min(score, 100)
```

**Trade-offs:**
- More complex than simple boolean matching
- Requires tuning confidence thresholds based on real-world data
- Worth it for better accuracy and fewer false positives

### AD-3: Rule Engine for Assignment Logic

**Decision:** Implement configurable assignment rules stored in database rather than hard-coded logic.

**Rule Structure:**
- Sequential evaluation (priority-based)
- Condition matching (industry, region, customer type, order value)
- Multiple assignment methods (direct assign, round-robin, queue)
- Active/inactive rules for testing

**Rationale:**
- **Configurability:** Business users can modify rules without code changes
- **Flexibility:** Different assignment strategies for different scenarios
- **Testing:** Easy to enable/disable rules for A/B testing
- **Audit Trail:** Rule changes are tracked in database

**Implementation:**
```python
class CrmAssignmentRule(models.Model):
    _name = 'crm.assignment.rule'
    _order = 'sequence'

    def evaluate_lead(self, lead):
        # Returns True if rule conditions match lead attributes

    def assign_lead(self, lead):
        # Executes assignment based on rule configuration
```

**Trade-offs:**
- More database queries to fetch and evaluate rules
- Need UI for rule management
- Worth it for business flexibility and maintainability

### AD-4: Atomic Operations with Database Locking

**Decision:** Use database transactions and row-level locking to prevent assignment conflicts.

**Locking Strategy:**
- Lock customer record during duplicate detection + assignment
- Use Odoo's `WITH FOR UPDATE` through ORM
- Keep lock duration minimal (only during assignment operation)

**Rationale:**
- **Data Integrity:** Prevent race conditions with concurrent lead submissions
- **Consistency:** Ensure one customer → one salesperson invariant
- **Reliability:** Handle high-volume lead intake without conflicts

**Implementation:**
```python
def assign_lead_safely(self, lead_id):
    with self.env.cr.savepoint():
        # Lock the lead record
        lead = self.env['crm.lead'].browse(lead_id).with_context(for_update=True)
        # Detect duplicates
        matched_customer = self._detect_duplicates(lead)
        if matched_customer:
            # Lock customer record
            matched_customer = matched_customer.with_context(for_update=True)
            # Assign to existing owner
            self._assign_to_owner(lead, matched_customer)
        else:
            # Apply assignment rules
            self._apply_rules(lead)
```

**Trade-offs:**
- Potential for lock contention under very high load
- Slightly slower processing due to locking overhead
- Worth it to guarantee data consistency

### AD-5: Event-Driven Workflow with Odoo Activities

**Decision:** Use Odoo's activity system for notifications and workflow tracking rather than custom notification model.

**Activity Types:**
- "Lead Assignment" - for new assignments to salespeople
- "Manual Assignment Required" - for manager intervention
- "Customer Verification Needed" - for duplicate verification
- "Ownership Dispute" - for escalations

**Rationale:**
- **Native Integration:** Leverages Odoo's built-in notification system
- **User Familiar:** Sales team already uses activities
- **Actionable:** Activities have due dates, priorities, and can trigger actions
- **Minimal Code:** No need to build custom notification infrastructure

**Implementation:**
- Create activities on assignment completion
- Use activity types to categorize different workflow states
- Leverage activity scheduling for reminders and escalations

**Trade-offs:**
- Dependent on Odoo's activity system (less flexibility)
- Limited customization of notification format
- Worth it for rapid development and user familiarity

### AD-6: Comprehensive Audit Logging

**Decision:** Implement dedicated audit log model rather than relying solely on Odoo's built-in tracking.

**Logged Information:**
- All validation attempts and outcomes
- Duplicate detection searches and match confidence
- Assignment operations and methods used
- Verification decisions and field updates
- Performance metrics (processing time)

**Rationale:**
- **Compliance:** Audit trail for sales assignment decisions
- **Debugging:** Detailed logs help troubleshoot matching issues
- **Analytics:** Performance data for optimization
- **Transparency:** Clear record of why each decision was made

**Implementation:**
```python
class CrmLeadAuditLog(models.Model):
    _name = 'crm.lead.audit.log'

    lead_id = fields.Many2one('crm.lead')
    operation_type = fields.Selection([...])
    operation_result = fields.Text()
    processing_time_ms = fields.Integer()
    details = fields.Json()  # Flexible structured data
```

**Trade-offs:**
- Additional database writes on every operation
- Storage overhead for logs
- Worth it for audit requirements and debugging capabilities

### AD-7: Normalization Pipeline for Data Quality

**Decision:** Implement normalization layer that standardizes all identifier data before matching.

**Normalization Rules:**
- **Phone:** Remove formatting, standardize to Vietnamese format (84XXXXXXXXX or 0XXXXXXXXX)
- **Email:** Lowercase, trim whitespace
- **MST:** Remove formatting, validate 10-13 digit format

**Rationale:**
- **Match Accuracy:** Prevents missing duplicates due to formatting differences
- **Data Quality:** Ensures consistent storage format
- **Validation:** Catches invalid data early in workflow

**Implementation:**
- Computed fields on `crm.lead` model: `normalized_phone`, `normalized_email`, `normalized_mst`
- Separate normalizer service for testability
- Apply normalization on create/write operations
- Index normalized fields for fast searching

**Trade-offs:**
- Additional processing on lead creation
- Storage overhead for normalized fields
- Worth it for significant improvement in duplicate detection accuracy

## Data Flow Diagram

```
[Landing Page] → [Odoo CRM API]
                       ↓
                 [Lead Created]
                       ↓
              [Validation Service]
              /                 \
         Complete           Incomplete
            ↓                    ↓
    [Normalization]     [Assign to Telesales]
            ↓
    [Duplicate Detection]
       /            \
  Match Found    No Match
      ↓              ↓
[Has Owner?]   [Assignment Rules]
   /      \           ↓
 Yes      No     [Auto Assign]
  ↓        ↓          ↓
[Auto    [Manual  [Notification]
Assign]  Assign]      ↓
  ↓        ↓      [COMPLETE]
[Notification]
  ↓
[COMPLETE]
```

## Technology Choices

### Odoo ORM vs. Raw SQL
**Decision:** Use Odoo ORM for all database operations except performance-critical duplicate detection queries.

**Rationale:**
- ORM provides security, access control, and audit trail
- Raw SQL only where proven performance bottleneck
- Maintain Odoo conventions for long-term maintainability

### JSON Fields for Flexible Logging
**Decision:** Use JSON fields in audit log for flexible structured data storage.

**Rationale:**
- PostgreSQL native JSON support
- Schema flexibility for different log types
- Query capabilities with PostgreSQL JSON operators

### Database Indexing Strategy
**Decision:** Create composite indexes on `(mst, phone, email)` for customer and lead tables.

**Rationale:**
- Optimize most common query pattern (search by multiple identifiers)
- Balance index overhead vs. query performance
- Monitor index usage in production and adjust

## Performance Considerations

### Expected Load
- Peak: 100 leads/hour (2 leads/minute)
- Average: 20 leads/hour
- Customer database: 10,000-100,000 records

### Performance Targets
- Lead validation: <100ms
- Duplicate detection: <500ms
- Total lead processing: <2 seconds (90th percentile)

### Scaling Strategies
1. **Database Optimization:** Proper indexing, query optimization
2. **Asynchronous Processing:** Move non-urgent operations to background jobs
3. **Caching:** Cache assignment rules (rarely change)
4. **Batch Processing:** Group notifications to reduce overhead

## Security Considerations

### Access Control
- Sales: Can view own assigned leads and customers
- Sales Managers: Can view all leads, manage assignments, resolve disputes
- Telesales: Can view and edit incomplete leads only
- System Admin: Full access for configuration and troubleshooting

### Data Protection
- Audit logs are read-only after creation
- Customer PII (phone, email, MST) protected by Odoo security
- Assignment changes require proper user permissions
- Escalations require manager role

## Future Enhancements (Out of Scope for Sprint 1)

1. **Machine Learning for Match Confidence:** Train model to improve duplicate detection accuracy
2. **Lead Scoring:** Prioritize high-value leads for faster response
3. **Geographic Assignment:** GPS-based territory assignment for field sales
4. **Multi-Product Assignment:** Different salespeople for different product lines
5. **API Integration:** Webhooks for real-time assignment notifications
6. **Advanced Analytics:** Predictive assignment based on conversion rates
7. **Fuzzy Matching:** Handle typos and variations in company names

## Open Questions for Implementation

1. **MST API Integration:** Should duplicate detection wait for MST enrichment or proceed without it?
   - **Recommendation:** Proceed with duplicate detection, enrich asynchronously

2. **Assignment Rule Priority:** Should later rules be able to override earlier matches?
   - **Recommendation:** No, first match wins (more predictable)

3. **Round-Robin State:** Where to store round-robin counter (global vs. per-team)?
   - **Recommendation:** Per-team state in `crm.team` model with `last_assigned_user_id` field

4. **Verification Timeout:** How long before overdue verification escalation?
   - **Recommendation:** 24 hours reminder, 48 hours escalation (configurable)

## Success Metrics

Post-implementation, track these metrics to validate design decisions:

- **Duplicate Detection Accuracy:** >95% precision and recall
- **False Positive Rate:** <5% (leads incorrectly matched)
- **Average Processing Time:** <2 seconds per lead
- **Assignment Distribution:** Even distribution across sales team (for round-robin)
- **Verification Time:** Average time from assignment to verification completion
- **User Satisfaction:** Sales team feedback on assignment quality
