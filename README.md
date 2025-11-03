# GotIt CRM - Odoo 18 Development Environment

Docker-based Odoo 18 CRM development environment with PostgreSQL, pgAdmin, and Nginx.

## Quick Start

```bash
# Start all services
docker compose up -d

# Wait for services to be ready (30-60 seconds)
# Access Odoo at http://localhost:8069
```

## Database Setup

The database is pre-configured as `gotit_odoo`. On first run, initialize it:

```bash
# Initialize database with base modules
docker compose exec odoo odoo -d gotit_odoo -i base --stop-after-init --without-demo=all

# Install CRM and Sales apps
docker compose exec odoo odoo -d gotit_odoo -i crm,sale --stop-after-init --without-demo=all

# Restart Odoo to apply changes
docker compose restart odoo
```

## Install Custom Modules (Optional)

```bash
# Install all GotIt custom modules
docker compose exec odoo odoo -d gotit_odoo -i gotit_crm_base,gotit_crm_lead_assignment,gotit_crm_customer_mgmt,gotit_crm_tax_id_api,gotit_crm_product_ext,gotit_crm_api --stop-after-init --without-demo=all

# Restart Odoo
docker compose restart odoo
```

## Access Points

- **Odoo**: http://localhost:8069
- **Odoo (via Nginx)**: http://localhost:80
- **pgAdmin**: http://localhost:5050 (admin@localhost.com / GGOTNvHYymogQS3YyIZaYkWiwYmiDflK)
- **PostgreSQL**: localhost:5432 (odoo / vzpylmzXnlcOtDverIJAspZBpiOjl3lG)

## Default Login

- **Email**: admin
- **Password**: admin (set during first login)

## Development Commands

```bash
# View logs
docker compose logs -f odoo

# Update a module after code changes
docker compose exec odoo odoo -d gotit_odoo -u <module_name> --stop-after-init
docker compose restart odoo

# Run tests for a module
docker compose exec odoo odoo -d gotit_odoo -i <module_name> --test-enable --stop-after-init --log-level=test

# Access Odoo shell
docker compose exec odoo odoo shell -d gotit_odoo

# Access PostgreSQL
docker compose exec db psql -U odoo -d gotit_odoo

# Stop all services
docker compose down

# Clean slate (WARNING: deletes all data!)
docker compose down -v
```

## Custom Modules

Located in `addons/` directory:

- **gotit_crm_base**: Shared audit logging and base configuration
- **gotit_crm_lead_assignment**: Automated lead assignment with configurable rules
- **gotit_crm_customer_mgmt**: Duplicate detection and extended customer fields
- **gotit_crm_tax_id_api**: Tax ID enrichment via VNPT/Viettel API
- **gotit_crm_product_ext**: Product multiple pricing and physical gifts
- **gotit_crm_api**: External API for lead creation (website/hotline integration)

## Configuration Files

- **docker-compose.yml**: Docker services configuration
- **config/odoo.conf**: Odoo server configuration
- **.env**: Environment variables (database name, passwords, ports)

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

## Troubleshooting

```bash
# Check container status
docker compose ps

# View recent logs
docker compose logs odoo --tail 100

# Restart specific service
docker compose restart odoo

# Check database exists
docker compose exec db psql -U odoo -d postgres -c "\l"

# Rebuild containers
docker compose down
docker compose up -d --build
```

## Documentation

- **Implementation Plan**: `specs/001-gotit-crm-customization/plan.md`
- **Data Model**: `specs/001-gotit-crm-customization/data-model.md`
- **Quickstart Guide**: `specs/001-gotit-crm-customization/quickstart.md`

---

**Database**: `gotit_odoo`
**Odoo Version**: 18.0
**Branch**: `playground`
