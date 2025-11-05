# MST (Tax ID) Lookup API Simulator

A simulated third-party API for looking up Vietnamese company information by MST (Mã số thuế - Tax ID).

## Overview

This FastAPI-based service simulates a real-world MST lookup API that would be provided by Vietnamese government or third-party business data providers. It's designed for development and testing of the Odoo CRM custom module.

## Features

- **Dynamic Data Generation**: Automatically generates realistic Vietnamese company data on first request
- **Persistent Storage**: Uses SQLite to store generated data for consistent responses
- **Vietnamese Company Names**: Generates authentic-looking Vietnamese company names using Faker
- **RESTful API**: Clean REST endpoints with OpenAPI documentation
- **Docker Support**: Easy deployment via Docker container
- **Health Checks**: Built-in health check endpoint for monitoring

## API Endpoints

### Get Company Information

```
GET /api/v1/company/{mst}
```

Retrieve company information by MST (Tax ID).

**Parameters:**
- `mst` (path): 10-13 digit Vietnamese Tax ID

**Response:**
```json
{
  "mst": "0123456789",
  "company_name": "Công ty TNHH ABC Việt Nam",
  "legal_name": "CÔNG TY TNHH ABC VIỆT NAM",
  "registration_date": "2020-05-15",
  "status": "active"
}
```

**Company Status Values:**
- `active`: Company is operating normally (80% of generated data)
- `suspended`: Company is temporarily suspended (15% of generated data)
- `dissolved`: Company has been dissolved (5% of generated data)

### Health Check

```
GET /health
```

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "MST API is running"
}
```

### Statistics

```
GET /stats
```

Returns database statistics.

**Response:**
```json
{
  "total_companies": 150,
  "by_status": {
    "active": 120,
    "suspended": 25,
    "dissolved": 5
  }
}
```

## Running with Docker

### Build the Image

```bash
cd mst-api-simulator
docker build -t mst-api:latest .
```

### Run the Container

```bash
docker run -d \
  --name mst-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  mst-api:latest
```

### With Docker Compose

The service is integrated into the main `docker-compose.yml`:

```bash
# Start the MST API service
docker-compose up -d mst-api

# View logs
docker-compose logs -f mst-api

# Stop the service
docker-compose down mst-api
```

## Running Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Example Usage

### Using curl

```bash
# Lookup a company by MST
curl http://localhost:8000/api/v1/company/0123456789

# Check health
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/stats
```

### Using Python requests

```python
import requests

# Lookup company
response = requests.get("http://localhost:8000/api/v1/company/0123456789")
company_data = response.json()
print(company_data)
```

### Using httpie

```bash
http localhost:8000/api/v1/company/0123456789
```

## Interactive API Documentation

Once the server is running, access the auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Data Generation

### How it Works

1. First request for an MST → Generate realistic Vietnamese company data
2. Store in SQLite database (`/app/data/mst_database.db`)
3. Subsequent requests → Retrieve from database

### Generated Data

The API generates realistic Vietnamese company data including:

- **Company Names**: Using Faker with Vietnamese locale
- **Company Types**: TNHH, Cổ phần, TNHH MTV, Doanh nghiệp Tư nhân
- **Business Sectors**: Thương mại, Dịch vụ, Công nghệ, Xây dựng, etc.
- **Registration Dates**: Random dates between 1990-2024
- **Status**: Weighted distribution (80% active, 15% suspended, 5% dissolved)

### Deterministic Generation

For testing purposes, the same MST will always generate the same company data (seeded by the MST number).

## Configuration

### Environment Variables

- `PORT`: API port (default: 8000)
- Database file is stored in `/app/data/mst_database.db`

### Volume Mounts

To persist data across container restarts, mount a volume:

```bash
-v /path/to/host/data:/app/data
```

## Integration with Odoo

This API is designed to be called from the Odoo CRM custom module:

```python
# In Odoo module
import requests

def lookup_company_by_mst(mst):
    response = requests.get(f"http://mst-api:8000/api/v1/company/{mst}")
    if response.status_code == 200:
        return response.json()
    return None
```

## Development

### Project Structure

```
mst-api-simulator/
├── app.py              # FastAPI application
├── models.py           # Pydantic models
├── database.py         # SQLite operations
├── data_generator.py   # Data generation logic
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .dockerignore      # Docker ignore patterns
└── README.md          # This file
```

### Adding New Fields

To add new company fields:

1. Update `models.py` - add field to `CompanyResponse`
2. Update `database.py` - add column to table schema
3. Update `data_generator.py` - add generation logic
4. Restart the service

## License

This is a development tool for the Got It Odoo CRM project.
