#!/bin/bash
#
# Odoo Development Environment Setup Script
# This script tears down and rebuilds the Odoo development environment from scratch
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_NAME="${POSTGRES_DB:-gotit_odoo}"

# Default options
SKIP_CONFIRMATION=false
VERBOSE=false

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Automated Odoo development environment setup script.
This script will tear down and rebuild the entire Odoo environment.

OPTIONS:
    -y, --yes       Skip confirmation prompt
    -v, --verbose   Enable verbose output
    -h, --help      Show this help message

EXAMPLES:
    $0                  # Interactive mode
    $0 --yes            # Skip confirmation
    $0 -y -v            # Skip confirmation with verbose output

EOF
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            SKIP_CONFIRMATION=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Change to project directory
cd "$PROJECT_DIR"

# Show banner
clear
print_header "Odoo Development Environment Setup"
echo ""
print_info "This script will:"
echo "  1. Tear down existing Docker containers and volumes"
echo "  2. Start fresh containers"
echo "  3. Initialize Odoo database ($DB_NAME)"
echo "  4. Verify the setup"
echo ""
print_warning "All existing data will be permanently deleted!"
echo ""

# Confirmation prompt
if [ "$SKIP_CONFIRMATION" = false ]; then
    read -p "Do you want to continue? (yes/no) " -n 3 -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_error "Setup cancelled by user"
        exit 1
    fi
    echo ""
fi

# Step 1: Tear down existing environment
print_header "Step 1: Tearing Down Existing Environment"
print_step "Stopping and removing containers and volumes..."
if [ "$VERBOSE" = true ]; then
    docker compose down -v
else
    docker compose down -v > /dev/null 2>&1
fi
print_success "Environment cleaned"
echo ""

# Step 2: Start fresh containers
print_header "Step 2: Starting Fresh Containers"
print_step "Starting Docker containers..."
if [ "$VERBOSE" = true ]; then
    docker compose up -d
else
    docker compose up -d > /dev/null 2>&1
fi
print_success "Containers started"
echo ""

# Step 3: Wait for database to be healthy
print_header "Step 3: Waiting for Database"
print_step "Checking database health..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    DB_STATUS=$(docker compose ps db --format json | grep -o '"Health":"[^"]*"' | cut -d'"' -f4)
    if [ "$DB_STATUS" = "healthy" ]; then
        print_success "Database is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Database failed to become healthy within timeout"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""

# Step 4: Initialize Odoo database
print_header "Step 4: Initializing Odoo Database"
print_step "Installing base module (this may take a few minutes)..."
if [ "$VERBOSE" = true ]; then
    docker compose exec odoo odoo -d "$DB_NAME" -i base --stop-after-init --without-demo=all
else
    docker compose exec odoo odoo -d "$DB_NAME" -i base --stop-after-init --without-demo=all > /dev/null 2>&1
fi
print_success "Database initialized with base module"
echo ""

# Step 5: Restart Odoo
print_header "Step 5: Restarting Odoo"
print_step "Restarting Odoo container..."
if [ "$VERBOSE" = true ]; then
    docker compose restart odoo
else
    docker compose restart odoo > /dev/null 2>&1
fi
print_success "Odoo restarted"
echo ""

# Wait for Odoo to be ready
print_step "Waiting for Odoo to be ready..."
sleep 5
echo ""

# Step 6: Verification
print_header "Step 6: Verification"

# Check container status
print_step "Checking container status..."
CONTAINERS_UP=$(docker compose ps --format json | grep -c '"State":"running"' || true)
print_info "Running containers: $CONTAINERS_UP/5"

# Check database tables
print_step "Verifying database tables..."
TABLE_COUNT=$(docker compose exec -T db psql -U odoo -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
if [ "$TABLE_COUNT" -gt 100 ]; then
    print_success "Database has $TABLE_COUNT tables"
else
    print_warning "Database has only $TABLE_COUNT tables (expected > 100)"
fi

# Check for errors in logs
print_step "Checking for errors in logs..."
DB_ERRORS=$(docker compose logs db --tail 50 2>/dev/null | grep -c "FATAL\|ERROR" || true)
ODOO_ERRORS=$(docker compose logs odoo --tail 50 2>/dev/null | grep -c "ERROR" || true)

if [ "$DB_ERRORS" -eq 0 ] && [ "$ODOO_ERRORS" -eq 0 ]; then
    print_success "No errors found in recent logs"
else
    print_warning "Found $DB_ERRORS database errors and $ODOO_ERRORS Odoo errors"
    if [ "$VERBOSE" = true ]; then
        echo ""
        print_info "Recent database logs:"
        docker compose logs db --tail 10
        echo ""
        print_info "Recent Odoo logs:"
        docker compose logs odoo --tail 10
    fi
fi
echo ""

# Final summary
print_header "Setup Complete!"
echo ""
print_success "Odoo development environment is ready!"
echo ""
print_info "Access URLs:"
echo "  • Odoo Web:    http://localhost:8069"
echo "  • Odoo (Nginx): http://localhost:80"
echo "  • pgAdmin:     http://localhost:5050"
echo "  • MST API:     http://localhost:8000"
echo ""
print_info "Database: $DB_NAME"
print_info "Tables created: $TABLE_COUNT"
echo ""
print_info "Useful commands:"
echo "  • View logs:        docker compose logs -f"
echo "  • Stop containers:  docker compose stop"
echo "  • Start containers: docker compose start"
echo "  • Container status: docker compose ps"
echo ""
print_header "Happy coding!"
echo ""
