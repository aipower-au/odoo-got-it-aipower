#!/bin/bash
# Sprint 1 - Complete Reset and Import Script
# This script automates the entire process of cleaning and importing test data

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}SPRINT 1 - COMPLETE RESET AND IMPORT${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# Function to print step header
print_step() {
    echo ""
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================================================${NC}"
    echo ""
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check if scripts exist
cd "$SCRIPT_DIR"

if [ ! -f "config.py" ]; then
    print_error "config.py not found!"
    exit 1
fi

# Parse command line arguments
SKIP_DELETE=false
SKIP_GENERATE=false
SKIP_VERIFY=false
AUTO_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-delete)
            SKIP_DELETE=true
            shift
            ;;
        --skip-generate)
            SKIP_GENERATE=true
            shift
            ;;
        --skip-verify)
            SKIP_VERIFY=true
            shift
            ;;
        -y|--yes)
            AUTO_CONFIRM=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-delete      Skip data deletion step"
            echo "  --skip-generate    Skip CSV generation step"
            echo "  --skip-verify      Skip data verification step"
            echo "  -y, --yes          Auto-confirm (no prompts)"
            echo "  -h, --help         Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Confirmation prompt
if [ "$AUTO_CONFIRM" = false ]; then
    print_warning "This script will:"
    echo "  1. Delete all existing CRM data (leads, teams, customers)"
    echo "  2. Generate fresh test data CSV files"
    echo "  3. Import staff, teams, and customers"
    echo "  4. Verify the imported data"
    echo ""
    read -p "Do you want to continue? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        print_warning "Operation cancelled by user"
        exit 0
    fi
fi

# Step 1: Generate CSV files
if [ "$SKIP_GENERATE" = false ]; then
    print_step "STEP 1: GENERATING TEST DATA CSV FILES"

    cd "$PROJECT_DIR/test_data"

    if [ -f "generate_all_test_data.py" ]; then
        python3 generate_all_test_data.py
        print_success "Test data CSV files generated"
    else
        print_error "generate_all_test_data.py not found!"
        exit 1
    fi

    cd "$SCRIPT_DIR"
else
    print_warning "Skipping CSV generation (--skip-generate)"
fi

# Step 2: Delete existing data
if [ "$SKIP_DELETE" = false ]; then
    print_step "STEP 2: DELETING EXISTING CRM DATA"

    if [ "$AUTO_CONFIRM" = true ]; then
        python3 delete_crm_data.py --no-confirm
    else
        python3 delete_crm_data.py
    fi

    print_success "Existing data deleted"
else
    print_warning "Skipping data deletion (--skip-delete)"
fi

# Step 3: Import all data
print_step "STEP 3: IMPORTING SPRINT 1 DATA"

python3 import_all_sprint1.py

print_success "Data import completed"

# Step 4: Verify data
if [ "$SKIP_VERIFY" = false ]; then
    print_step "STEP 4: VERIFYING IMPORTED DATA"

    python3 verify_data.py

    print_success "Data verification completed"
else
    print_warning "Skipping data verification (--skip-verify)"
fi

# Final message
echo ""
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${GREEN}✓ SPRINT 1 SETUP COMPLETED SUCCESSFULLY!${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Access Odoo at: http://localhost:8069"
echo "  2. Login with your admin credentials"
echo "  3. Navigate to CRM module to see imported data"
echo ""
echo -e "${YELLOW}Imported data:${NC}"
echo "  • Staff users (with default password: gotit2025)"
echo "  • Sales teams with members"
echo "  • Customer companies with salespeople assigned"
echo ""

exit 0
