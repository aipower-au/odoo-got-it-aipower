"""
MST (Tax ID) Lookup API
A simulated third-party API for looking up Vietnamese company information by MST
"""
import re
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse

from models import CompanyResponse, HealthResponse
from database import init_db, get_company_by_mst, save_company, get_stats
from data_generator import generate_company_data


# Initialize FastAPI app
app = FastAPI(
    title="MST Lookup API",
    description="Simulated third-party API for Vietnamese company Tax ID (MST) lookup",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized successfully")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="MST API is running"
    )


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get database statistics"""
    try:
        stats = get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/company/{mst}",
    response_model=CompanyResponse,
    tags=["Company Lookup"],
    summary="Get company information by MST",
    description="Retrieve company information by Vietnamese Tax ID (MST). "
                "If the MST is not in the database, realistic company data will be generated and stored."
)
async def get_company_info(
    mst: str = Path(
        ...,
        description="Mã số thuế (Vietnamese Tax ID)",
        min_length=10,
        max_length=13,
        regex=r'^\d{10,13}$'
    )
):
    """
    Get company information by MST (Tax ID)

    - **mst**: 10-13 digit Vietnamese Tax ID

    Returns company information including:
    - Company name
    - Legal name
    - Registration date
    - Status (active, suspended, dissolved)

    If the MST is not found in the database, realistic data will be automatically
    generated and stored for future requests.
    """

    # Validate MST format
    if not re.match(r'^\d{10,13}$', mst):
        raise HTTPException(
            status_code=400,
            detail="Invalid MST format. MST must be 10-13 digits."
        )

    # Try to get from database first
    company_data = get_company_by_mst(mst)

    if company_data:
        # Found in database - return existing data
        return CompanyResponse(**company_data)

    # Not found in database - generate new data
    try:
        # Generate realistic company data
        generated_data = generate_company_data(mst)

        # Save to database
        save_success = save_company(
            mst=generated_data["mst"],
            company_name=generated_data["company_name"],
            legal_name=generated_data["legal_name"],
            registration_date=generated_data["registration_date"],
            status=generated_data["status"]
        )

        if not save_success:
            # This shouldn't happen, but handle race condition
            # Try to get from database again
            company_data = get_company_by_mst(mst)
            if company_data:
                return CompanyResponse(**company_data)

        return CompanyResponse(**generated_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating company data: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found. Available endpoints: /health, /stats, /api/v1/company/{mst}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
