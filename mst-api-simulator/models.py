"""
Pydantic models for MST API responses
"""
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class CompanyStatus(str, Enum):
    """Company status enum"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISSOLVED = "dissolved"


class CompanyResponse(BaseModel):
    """Response model for company lookup"""
    mst: str = Field(..., description="Mã số thuế (Tax ID)", min_length=10, max_length=13)
    company_name: str = Field(..., description="Tên công ty")
    legal_name: str = Field(..., description="Tên pháp lý")
    registration_date: date = Field(..., description="Ngày đăng ký")
    status: CompanyStatus = Field(..., description="Trạng thái")

    class Config:
        json_schema_extra = {
            "example": {
                "mst": "0123456789",
                "company_name": "Công ty TNHH ABC Việt Nam",
                "legal_name": "CÔNG TY TNHH ABC VIỆT NAM",
                "registration_date": "2020-05-15",
                "status": "active"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
