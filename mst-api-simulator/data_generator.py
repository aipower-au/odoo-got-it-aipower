"""
Generate realistic Vietnamese company data using Faker
"""
import random
from datetime import date, timedelta
from faker import Faker

from models import CompanyStatus


# Initialize Faker with Vietnamese locale
fake = Faker('vi_VN')


# Common Vietnamese company types
COMPANY_TYPES = [
    "Công ty TNHH",  # Limited Liability Company
    "Công ty Cổ phần",  # Joint Stock Company
    "Công ty TNHH MTV",  # Single Member Limited Liability Company
    "Doanh nghiệp Tư nhân",  # Private Enterprise
]


# Common business sectors in Vietnamese
BUSINESS_SECTORS = [
    "Thương mại",
    "Dịch vụ",
    "Công nghệ",
    "Xây dựng",
    "Sản xuất",
    "Du lịch",
    "Giáo dục",
    "Y tế",
    "Nông nghiệp",
    "Vận tải",
]


def generate_company_name() -> str:
    """Generate a realistic Vietnamese company name"""
    company_type = random.choice(COMPANY_TYPES)
    sector = random.choice(BUSINESS_SECTORS)

    # Mix of real-sounding Vietnamese business names
    name_patterns = [
        f"{fake.first_name()} {fake.last_name()}",  # Personal name
        f"{sector} {fake.city().split()[0]}",  # Sector + City
        f"{fake.word().title()} {sector}",  # Random word + Sector
        f"Tập đoàn {fake.last_name()}",  # Group + Name
    ]

    base_name = random.choice(name_patterns)
    full_name = f"{company_type} {base_name}"

    return full_name


def generate_legal_name(company_name: str) -> str:
    """Generate legal name (uppercase version)"""
    return company_name.upper()


def generate_registration_date() -> date:
    """Generate a random registration date between 1990 and 2024"""
    start_date = date(1990, 1, 1)
    end_date = date(2024, 12, 31)

    # Calculate days between dates
    days_between = (end_date - start_date).days

    # Generate random number of days
    random_days = random.randint(0, days_between)

    # Create random date
    registration_date = start_date + timedelta(days=random_days)

    return registration_date


def generate_company_status() -> CompanyStatus:
    """
    Generate company status with weighted distribution:
    - Active: 80%
    - Suspended: 15%
    - Dissolved: 5%
    """
    rand = random.random()

    if rand < 0.80:
        return CompanyStatus.ACTIVE
    elif rand < 0.95:
        return CompanyStatus.SUSPENDED
    else:
        return CompanyStatus.DISSOLVED


def generate_company_data(mst: str) -> dict:
    """
    Generate complete company data for a given MST

    Args:
        mst: Mã số thuế (Tax ID)

    Returns:
        Dictionary with generated company information
    """
    # Set seed based on MST for consistent generation for same MST
    # (useful for testing)
    Faker.seed(int(mst[:10]))
    random.seed(int(mst[:10]))

    company_name = generate_company_name()
    legal_name = generate_legal_name(company_name)
    registration_date = generate_registration_date()
    status = generate_company_status()

    return {
        "mst": mst,
        "company_name": company_name,
        "legal_name": legal_name,
        "registration_date": registration_date,
        "status": status
    }
