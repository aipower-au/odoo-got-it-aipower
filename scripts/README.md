# Setup Scripts

This directory contains automation scripts for managing the Odoo development environment.

## setup-odoo.sh

Automated setup script that tears down and rebuilds the entire Odoo development environment from scratch.

### What it does:

1. **Tears down existing environment** - Removes all containers and volumes
2. **Starts fresh containers** - Creates new Docker containers
3. **Waits for database** - Ensures PostgreSQL is healthy before proceeding
4. **Initializes Odoo database** - Installs base module without demo data
5. **Restarts Odoo** - Applies clean configuration
6. **Verifies setup** - Checks container status, database tables, and logs

### Usage:

```bash
# Interactive mode (asks for confirmation)
./scripts/setup-odoo.sh

# Skip confirmation (useful for automation/CI)
./scripts/setup-odoo.sh --yes

# Verbose mode (shows all command output)
./scripts/setup-odoo.sh -v

# Both skip confirmation and verbose
./scripts/setup-odoo.sh -y -v
```

### Options:

- `-y, --yes` - Skip confirmation prompt
- `-v, --verbose` - Enable verbose output (shows all Docker command output)
- `-h, --help` - Show help message

### Output:

The script provides:
- Color-coded progress indicators
- Step-by-step status updates
- Verification of database tables and container health
- Error checking in recent logs
- Summary with access URLs and useful commands

### Requirements:

- Docker and Docker Compose installed
- Proper `.env` file configuration
- Execute permission on the script (already set)

### Example Output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Odoo Development Environment Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ This script will:
  1. Tear down existing Docker containers and volumes
  2. Start fresh containers
  3. Initialize Odoo database (gotit_odoo)
  4. Verify the setup

⚠ All existing data will be permanently deleted!

✓ Setup Complete!

ℹ Access URLs:
  • Odoo Web:    http://localhost:8069
  • Odoo (Nginx): http://localhost:80
  • pgAdmin:     http://localhost:5050
  • MST API:     http://localhost:8000
```

### Troubleshooting:

If the script fails:

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Check for port conflicts:**
   ```bash
   docker compose ps
   ```

3. **Run with verbose mode to see detailed output:**
   ```bash
   ./scripts/setup-odoo.sh -y -v
   ```

4. **Manually check logs:**
   ```bash
   docker compose logs db
   docker compose logs odoo
   ```

5. **Verify environment variables:**
   ```bash
   cat .env
   ```
