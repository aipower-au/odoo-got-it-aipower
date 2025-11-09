# Project Context

## Purpose

GotIt CRM is a comprehensive Customer Relationship Management system built on Odoo 18 for the Vietnamese market. The system manages the complete sales lifecycle from lead capture to customer conversion, with specialized features for Vietnamese business requirements.

**Key Goals:**
- Automate customer and lead management with intelligent duplicate detection
- Integrate with Vietnamese Tax ID (MST) lookup services for automatic company data enrichment
- Provide automated sales assignment based on configurable business rules
- Enable seamless data migration from legacy Excel-based systems
- Support multi-channel lead capture (website, hotline, API integrations)
- Streamline product management with integration to FAST accounting system

## Tech Stack

### Core Platform
- **Odoo 18** - Primary CRM and ERP framework
- **Python 3.x** - Backend development language for Odoo custom modules
- **PostgreSQL 15** - Primary database

### Infrastructure & DevOps
- **Docker & Docker Compose** - Containerized development and deployment
- **Nginx** - Reverse proxy and web server
- **pgAdmin** - Database management interface

### APIs & Microservices
- **FastAPI** - MST (Tax ID) lookup API simulator
- **SQLite** - MST API data storage
- **Faker** - Test data generation (Vietnamese locale)

### Development Tools
- **Git** - Version control
- **Bash Scripts** - Automated setup and deployment scripts

## Project Conventions

### Code Style

**Python (Odoo Modules):**
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Class names: PascalCase (e.g., `CustomerManagement`, `LeadAssignment`)
- Function/method names: snake_case (e.g., `check_duplicate_customer`, `assign_salesperson`)
- Constants: UPPER_SNAKE_CASE (e.g., `MST_API_ENDPOINT`)
- Odoo model naming: `model.name.format` (e.g., `crm.lead.custom`, `res.partner.gotit`)

**File Naming:**
- Python modules: snake_case (e.g., `customer_duplicate_check.py`)
- Odoo XML views: descriptive names with module prefix (e.g., `gotit_crm_customer_views.xml`)
- Configuration files: lowercase with hyphens (e.g., `docker-compose.yml`)

**Documentation:**
- All custom Odoo models must have docstrings
- Complex business logic should be commented in Vietnamese when explaining domain-specific rules
- API endpoints must have OpenAPI/Swagger documentation

### Architecture Patterns

**Odoo Module Structure:**
- Place all custom modules in `/addons` directory
- Follow Odoo's standard module structure:
  - `__manifest__.py` - Module metadata and dependencies
  - `models/` - Business logic and data models
  - `views/` - XML view definitions
  - `security/` - Access rights and record rules
  - `data/` - Initial data and demo data
  - `wizards/` - Transient models for user interactions

**Microservices:**
- MST API runs as separate containerized service
- Services communicate via REST APIs
- Use Docker networking for inter-service communication

**Data Flow:**
- External sources (Website, Hotline) → API Gateway → Odoo CRM
- Odoo CRM → MST API → Third-party data enrichment
- Legacy Data (Excel) → Import Scripts → Odoo Database

### Testing Strategy

**Current Status:** Development phase, testing strategy to be formalized

**Planned Approach:**
- Use Odoo's built-in testing framework for custom modules
- Test with both demo data and production-like scenarios
- Validate duplicate detection logic with real MST data
- Test sales assignment rules with various customer profiles
- Use automated setup script (`scripts/setup-odoo.sh`) for clean test environments

### Git Workflow

**Branching Strategy:**
- `main` - Production-ready code
- `feature/*` - Feature development branches (e.g., `feature/implement-sprint-image`)
- Feature branches merge into `main` via pull requests

**Commit Conventions:**
- Use descriptive commit messages
- Prefix with type: `feat:`, `fix:`, `docs:`, `refactor:`
- Examples:
  - `feat: Add automated Odoo environment setup script`
  - `docs: Expand Lead Management section with comprehensive details`
  - `fix: Resolve duplicate customer detection issue`

## Domain Context

### Vietnamese Business Context

**Mã số thuế (MST)** - Vietnamese Tax ID:
- 10-13 digit unique identifier for all Vietnamese companies
- Primary key for identifying and validating business entities
- Used for automatic company data enrichment via third-party APIs
- Company statuses: `active` (operating), `suspended` (temporarily inactive), `dissolved` (closed)

**GotIt Business Rules:**
- Sales assignment based on: Industry Group → Region → Customer Type → Order Value
- Customers without MST assigned to Telesales for verification before conversion
- All duplicate customer records must be assigned to the same salesperson
- Customer lifecycle: Potential → Client (upon account creation) → Lost (inactive)

### CRM Entities

**Customer Types:**
- Merchant - Business customers
- Supplier - Vendors and suppliers
- End Customer - Individual consumers

**Lead Management:**
- **Care Owner** - Interim handler for unidentified leads
- Automatic reassignment to Sales when customer is identified
- Multi-source lead capture: Website forms, hotline, API integrations

**Product Categories:**
- Invoice/Receipt items (hàng tạo hóa đơn/phiếu thu)
- Discounted items (hàng có chiết khấu)
- Physical gifts (hàng quà tặng vật lý) - requires inventory checks and controller approval

### Integration Points

**FAST Accounting System:**
- Master source for product data
- Product data in CRM must follow FAST templates
- Used for Sales Order (SO) system integration

**Multi-channel Lead Sources:**
- Website contact forms
- Hotline calls
- API integrations from marketing platforms
- Legacy Excel imports

## Important Constraints

### Technical Constraints
- Odoo 18 framework limitations and conventions must be respected
- Product data templates must match FAST system structure
- MST API integration must handle rate limiting and timeouts gracefully
- Docker-based deployment required for all environments

### Business Constraints
- **Duplicate Detection:** Mandatory checks on MST, phone, email before saving
- **Sales Integrity:** No customer can be assigned to multiple salespeople
- **Data Migration:** Must preserve all historical data from legacy systems
- **Vietnamese Locale:** All user-facing text must support Vietnamese characters
- **Audit Trail:** All sales assignment changes must be logged for compliance

### Regulatory Constraints
- Must comply with Vietnamese data protection regulations
- MST validation required for all business customers
- Proper handling of company status (active/suspended/dissolved)

## External Dependencies

### Third-Party Services
- **MST Lookup API** (Currently simulated via mst-api-simulator)
  - Production: Will integrate with government or licensed third-party provider
  - Provides: Company name, legal name, registration date, business status
  - Endpoint: `http://mst-api:8000/api/v1/company/{mst}`

### External Systems
- **FAST Accounting System**
  - Purpose: Master product catalog and pricing
  - Integration: Product data sync (implementation pending)

- **Website & Marketing Platforms**
  - Purpose: Lead generation and capture
  - Integration: REST API endpoints for lead creation

### Development Dependencies
- **Odoo Official Docker Image** (`odoo:18`)
- **PostgreSQL Docker Image** (`postgres:15`)
- **Python Packages:** FastAPI, Uvicorn, SQLAlchemy, Pydantic, Faker
- **pgAdmin** for database administration during development
