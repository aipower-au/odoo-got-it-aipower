# Odoo 19 Development Environment

Docker-based Odoo 19 development environment with PostgreSQL, pgAdmin, and Nginx reverse proxy.

## Project Structure

```
.
├── docker-compose.yml      # Docker Compose orchestration
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment template (safe to commit)
├── addons/                # Your custom Odoo modules
├── config/
│   └── odoo.conf         # Odoo configuration file
└── nginx/
    └── nginx.conf        # Nginx reverse proxy configuration
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Start all services:**
   ```bash
   docker compose up -d
   ```

2. **Access the applications:**
   - **Odoo (via Nginx)**: http://localhost
   - **Odoo (direct)**: http://localhost:8069
   - **pgAdmin**: http://localhost:5050
     - Email: `admin@example.com`
     - Password: `admin123`

3. **Initialize Odoo:**
   - Open http://localhost in your browser
   - Create a new database
   - Set master password: `admin` (configured in odoo.conf)
   - Fill in database details and admin account

## Configuration

### Environment Variables

Edit `.env` file to customize:

- **PostgreSQL**: Database credentials and port
- **Odoo**: Application ports (web and chat)
- **pgAdmin**: Admin panel credentials and port
- **Nginx**: HTTP/HTTPS ports

### Odoo Configuration

The `config/odoo.conf` file contains development-friendly settings:
- Debug mode enabled
- Auto-reload on file changes
- Verbose logging
- Single worker mode (good for debugging)

### Custom Addons

Place your custom Odoo modules in the `addons/` directory. They will be automatically available in Odoo.

Example structure:
```
addons/
├── my_custom_module/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   └── security/
```

## Common Commands

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f odoo
docker compose logs -f db
```

### Restart Odoo (to reload code changes)
```bash
docker compose restart odoo
```

### Stop all services
```bash
docker compose down
```

### Stop and remove volumes (clean slate)
```bash
docker compose down -v
```

### Access Odoo container shell
```bash
docker compose exec odoo bash
```

### Access PostgreSQL
```bash
docker compose exec db psql -U odoo -d postgres
```

## Database Management

### Using pgAdmin

1. Access pgAdmin at http://localhost:5050
2. Add new server:
   - **General Tab**:
     - Name: `Odoo Database`
   - **Connection Tab**:
     - Host: `db`
     - Port: `5432`
     - Database: `postgres`
     - Username: `odoo`
     - Password: `odoo123`

### Backup Database
```bash
docker compose exec db pg_dump -U odoo postgres > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker compose exec -T db psql -U odoo postgres
```

## Development Workflow

1. **Create/modify modules** in the `addons/` directory
2. **Update module list** in Odoo (Apps menu → Update Apps List)
3. **Install/upgrade** your module
4. **View logs** for debugging: `docker compose logs -f odoo`

## Troubleshooting

### Odoo won't start
- Check logs: `docker compose logs odoo`
- Verify database is healthy: `docker compose ps`
- Ensure .env variables are correct

### Database connection issues
- Verify PostgreSQL is running: `docker compose ps db`
- Check credentials in `.env` match `config/odoo.conf`

### Port already in use
- Change ports in `.env` file
- Run `docker compose down` and `docker compose up -d`

### Reset everything
```bash
docker compose down -v
docker compose up -d
```

## Production Notes

For production deployment, consider:
- Change all default passwords in `.env`
- Set `workers > 0` in odoo.conf for multi-processing
- Disable `dev_mode` and reduce `log_level`
- Add SSL certificates to Nginx
- Use Docker secrets for sensitive data
- Set up proper backup strategy

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Odoo (Nginx) | http://localhost | Set during initialization |
| Odoo (Direct) | http://localhost:8069 | Set during initialization |
| pgAdmin | http://localhost:5050 | admin@example.com / admin123 |
| PostgreSQL | localhost:5432 | odoo / odoo123 |

## License

This setup configuration is provided as-is for development purposes.
