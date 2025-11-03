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

Choose one of the following setup options based on your needs:

### Key Difference

The key difference between the two options is the `--without-demo=all` flag:
- **Without demo data (production):** Add `--without-demo=all` to each install command
- **With demo data (testing/training):** Omit `--without-demo=all` from install commands

### Option 1: Clean Setup (No Demo Data) - Production Ready

For production or when you want to start with an empty database:

```bash
# Initialize database with base modules (NO demo data)
docker compose exec odoo odoo -d gotit_odoo -i base --stop-after-init --without-demo=all

# Install CRM and Sales apps (NO demo data)
docker compose exec odoo odoo -d gotit_odoo -i crm,sale --stop-after-init --without-demo=all

# Restart Odoo to apply changes
docker compose restart odoo
```

**Note:** After running these commands, open http://localhost:8069/odoo/apps and click the "Activate" button on the Sales app to complete its installation.

### Option 2: Setup with Demo Data - Testing & Training

For testing, training, or exploring Odoo features with sample data:

```bash
# Initialize database with base modules (WITH demo data)
docker compose exec odoo odoo -d gotit_odoo -i base --stop-after-init

# Install CRM and Sales apps (WITH demo data)
docker compose exec odoo odoo -d gotit_odoo -i crm,sale --stop-after-init

# Restart Odoo to apply changes
docker compose restart odoo
```

**Demo data includes:**
- Sample leads and opportunities in various pipeline stages
- Sample customers and contacts with full details
- Sample products with prices and categories
- Sample quotations and sales orders
- Sales teams with members
- Pre-configured activities and tasks

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
# Install without demo data (production)
docker compose exec odoo odoo -d gotit_odoo -i <your_module_name> --stop-after-init --without-demo=all
docker compose restart odoo

# OR install with demo data (testing)
docker compose exec odoo odoo -d gotit_odoo -i <your_module_name> --stop-after-init
docker compose restart odoo
```

## Clean Start

To reset and start fresh:

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Start services again
docker compose up -d

# Wait for services to be ready, then follow Database Setup steps above
```
