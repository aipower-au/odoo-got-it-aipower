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

# Install CRM and Sales apps (wait 30s for full installation)
timeout 30s docker compose exec odoo odoo -d gotit_odoo -i crm,sale --without-demo=all || true

# Restart Odoo to apply changes
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

## Adding Custom Modules

Place your custom Odoo modules in the `addons/` directory. They will be automatically available to Odoo.

```bash
# After adding a module to addons/, install it
docker compose exec odoo odoo -d gotit_odoo -i <your_module_name> --stop-after-init --without-demo=all
docker compose restart odoo
```
