"""
Vietnamese Data Sets for Demo Data Generation
Contains realistic Vietnamese business data for Sprint 1 testing
"""

import random

# Vietnamese Company Name Components
COMPANY_TYPES = [
    "Công ty TNHH",
    "Công ty Cổ phần",
    "Công ty Trách nhiệm Hữu hạn",
    "Công ty CP",
    "Doanh nghiệp tư nhân",
]

COMPANY_NAMES = [
    "Thương Mại Phát Triển",
    "Đầu Tư Xây Dựng",
    "Sản Xuất Thực Phẩm",
    "Công Nghệ Số",
    "Vận Tải Logistics",
    "Du Lịch Việt",
    "Nhà Hàng Khách Sạn",
    "Dược Phẩm Sức Khỏe",
    "Điện Tử Viễn Thông",
    "May Mặc Thời Trang",
    "Nông Sản Thực Phẩm",
    "Kỹ Thuật Công Nghiệp",
    "Tư Vấn Quản Lý",
    "Phát Triển Phần Mềm",
    "Marketing Digital",
    "Thiết Kế Nội Thất",
    "Vật Liệu Xây Dựng",
    "Thương Mại Điện Tử",
    "Giáo Dục Đào Tạo",
    "Y Tế Sức Khỏe",
    "Bất Động Sản",
    "Tài Chính Đầu Tư",
    "Xuất Nhập Khẩu",
    "Sản Xuất Cơ Khí",
    "Thực Phẩm Đồ Uống",
    "Công Nghệ Thông Tin",
    "Dịch Vụ Khách Hàng",
    "Kinh Doanh Tổng Hợp",
    "Phát Triển Bền Vững",
    "Năng Lượng Xanh",
]

COMPANY_SUFFIXES = [
    "Việt Nam",
    "Sài Gòn",
    "Hà Nội",
    "Quốc Tế",
    "Á Châu",
    "Thái Bình Dương",
    "Miền Nam",
    "Miền Bắc",
    "Miền Trung",
    "Đông Nam Á",
    "Toàn Cầu",
    "Tân Tiến",
    "Hiện Đại",
    "Phương Nam",
    "Phương Đông",
    "Trung Ương",
    "Đại Phát",
    "Thành Công",
    "Phú Quý",
    "An Khang",
]

# Vietnamese Person Names
FIRST_NAMES = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Mai", "Tô", "Trương",
]

MIDDLE_NAMES_MALE = [
    "Văn", "Đức", "Minh", "Quang", "Hữu", "Công", "Xuân", "Thanh", "Hoàng", "Anh",
    "Tuấn", "Duy", "Bảo", "Khánh", "Phúc", "Tấn", "Huy", "Thành", "Quốc", "Việt",
]

MIDDLE_NAMES_FEMALE = [
    "Thị", "Thu", "Mai", "Lan", "Hồng", "Hương", "Kim", "Ngọc", "Phương", "Thanh",
    "Bích", "Diệu", "Hà", "Linh", "My", "Thúy", "Ánh", "Cẩm", "Tuyết", "Yến",
]

LAST_NAMES_MALE = [
    "Hùng", "Nam", "Khoa", "Long", "Bình", "Phong", "Tùng", "Đạt", "Hải", "Cường",
    "Thắng", "Dũng", "Kiên", "Vương", "Sơn", "Tâm", "Trí", "Hiếu", "Thiện", "An",
    "Quân", "Hoàn", "Toàn", "Phát", "Thịnh", "Khang", "Vinh", "Hưng", "Lâm", "Linh",
]

LAST_NAMES_FEMALE = [
    "Trang", "Hoa", "Chi", "Nhung", "Ly", "Linh", "Hà", "My", "Vy", "Anh",
    "Ngọc", "Thảo", "Hằng", "Dung", "Hạnh", "Loan", "Nga", "Oanh", "Phương", "Quỳnh",
    "Trinh", "Tú", "Vân", "Xuân", "Yến", "Giang", "Huệ", "Khanh", "Nhi", "San",
]

# Vietnamese Regions and Cities
REGIONS = {
    "Hồ Chí Minh": {
        "districts": ["Quận 1", "Quận 2", "Quận 3", "Quận 7", "Bình Thạnh", "Tân Bình", "Phú Nhuận", "Thủ Đức"],
        "streets": ["Nguyễn Huệ", "Lê Lợi", "Trần Hưng Đạo", "Điện Biên Phủ", "Cách Mạng Tháng 8", "Võ Văn Tần", "Nguyễn Thị Minh Khai", "Hai Bà Trưng"]
    },
    "Hà Nội": {
        "districts": ["Ba Đình", "Hoàn Kiếm", "Hai Bà Trưng", "Đống Đa", "Cầu Giấy", "Thanh Xuân", "Tây Hồ", "Long Biên"],
        "streets": ["Trần Duy Hưng", "Láng Hạ", "Giảng Võ", "Kim Mã", "Nguyễn Chí Thanh", "Trần Phú", "Lý Thường Kiệt", "Hoàng Quốc Việt"]
    },
    "Đà Nẵng": {
        "districts": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn", "Liên Chiểu"],
        "streets": ["Trần Phú", "Nguyễn Văn Linh", "Lê Duẩn", "Điện Biên Phủ", "Hoàng Diệu", "Hùng Vương"]
    },
    "Nha Trang": {
        "districts": ["Trung tâm", "Vĩnh Hải", "Vĩnh Nguyên", "Phước Hải"],
        "streets": ["Trần Phú", "Lê Thánh Tôn", "Thích Quảng Đức", "Nguyễn Thiện Thuật", "Hoàng Hoa Thám"]
    },
    "Vũng Tàu": {
        "districts": ["Phường 1", "Phường 2", "Phường 3", "Thắng Tam"],
        "streets": ["Trương Công Định", "Thùy Vân", "Hạ Long", "Phan Chu Trinh", "Lê Lợi"]
    },
    "Hải Phòng": {
        "districts": ["Hồng Bàng", "Ngô Quyền", "Lê Chân", "Hải An", "Kiến An"],
        "streets": ["Điện Biên Phủ", "Lạch Tray", "Trần Nguyên Hãn", "Hoàng Văn Thụ", "Lê Thánh Tông"]
    },
    "Cần Thơ": {
        "districts": ["Ninh Kiều", "Bình Thuỷ", "Cái Răng", "Ô Môn", "Thốt Nốt"],
        "streets": ["Nguyễn An Ninh", "Mậu Thân", "Ngô Quyền", "Trần Phú", "Phan Đình Phùng"]
    },
    "Huế": {
        "districts": ["Thuận Hòa", "Thuận Lộc", "Phú Hội", "Phú Nhuận", "Vỹ Dạ"],
        "streets": ["Lê Lợi", "Hùng Vương", "Trần Hưng Đạo", "Chi Lăng", "Điện Biên Phủ"]
    },
    "Biên Hòa": {
        "districts": ["Trung tâm", "Tân Hòa", "Tân Biên", "Hòa Bình"],
        "streets": ["Phạm Văn Thuận", "Cách Mạng Tháng 8", "Võ Thị Sáu", "Trần Quốc Toản", "Lý Thái Tổ"]
    },
}

# Industries (Vietnamese context)
INDUSTRIES = {
    "F&B": {
        "name": "Thực phẩm & Đồ uống",
        "products": ["Thực phẩm chế biến", "Đồ uống", "Nguyên liệu", "Thiết bị bếp"]
    },
    "Construction": {
        "name": "Xây dựng",
        "products": ["Vật liệu xây dựng", "Thiết bị công trình", "Dịch vụ thi công", "Thiết kế kiến trúc"]
    },
    "Logistics": {
        "name": "Logistics & Vận tải",
        "products": ["Dịch vụ vận chuyển", "Kho bãi", "Phần mềm quản lý", "Thiết bị logistics"]
    },
    "Hospitality": {
        "name": "Khách sạn & Du lịch",
        "products": ["Phần mềm quản lý khách sạn", "Thiết bị khách sạn", "Dịch vụ booking", "Marketing du lịch"]
    },
    "Technology": {
        "name": "Công nghệ thông tin",
        "products": ["Phần mềm doanh nghiệp", "Dịch vụ cloud", "Bảo mật", "Phát triển app"]
    },
    "Retail": {
        "name": "Bán lẻ",
        "products": ["Hệ thống POS", "Phần mềm quản lý bán hàng", "E-commerce", "Marketing"]
    },
    "Healthcare": {
        "name": "Y tế & Sức khỏe",
        "products": ["Thiết bị y tế", "Phần mềm quản lý bệnh viện", "Dược phẩm", "Dịch vụ chăm sóc"]
    },
    "Finance": {
        "name": "Tài chính & Ngân hàng",
        "products": ["Phần mềm kế toán", "Tư vấn tài chính", "Dịch vụ thanh toán", "Quản lý rủi ro"]
    },
    "Education": {
        "name": "Giáo dục & Đào tạo",
        "products": ["Nền tảng e-learning", "Phần mềm quản lý trường học", "Nội dung đào tạo", "Thiết bị giảng dạy"]
    },
    "Manufacturing": {
        "name": "Sản xuất",
        "products": ["Thiết bị sản xuất", "Phần mềm ERP", "Tự động hóa", "Quản lý chất lượng"]
    },
}

# Customer Types
CUSTOMER_TYPES = {
    "Enterprise": {"name": "Doanh nghiệp lớn", "min_employees": 200, "order_range": (100, 500)},
    "SME": {"name": "Doanh nghiệp vừa và nhỏ", "min_employees": 10, "order_range": (10, 100)},
    "Startup": {"name": "Công ty khởi nghiệp", "min_employees": 5, "order_range": (5, 50)},
}

# Order Value Ranges (in million VND)
ORDER_VALUE_RANGES = [
    {"label": "< 10M", "min": 1, "max": 10},
    {"label": "10M - 50M", "min": 10, "max": 50},
    {"label": "50M - 100M", "min": 50, "max": 100},
    {"label": "100M - 500M", "min": 100, "max": 500},
    {"label": "> 500M", "min": 500, "max": 2000},
]

# Payment Terms (Vietnamese business context)
PAYMENT_TERMS = {
    "cod": "Thanh toán khi giao hàng (COD)",
    "net7": "Thanh toán trong 7 ngày",
    "net15": "Thanh toán trong 15 ngày",
    "net30": "Thanh toán trong 30 ngày",
    "net45": "Thanh toán trong 45 ngày",
    "net60": "Thanh toán trong 60 ngày",
    "custom": "Điều khoản tùy chỉnh",
}

# Entity Types
ENTITY_TYPES = {
    "company": "Công ty",
    "individual": "Cá nhân",
    "government": "Cơ quan nhà nước",
    "ngo": "Tổ chức phi chính phủ",
}

# Sales Policies
SALES_POLICIES = {
    "standard": "Tiêu chuẩn",
    "vip": "VIP",
    "strategic": "Đối tác chiến lược",
    "government": "Khách hàng chính phủ",
}

# Lead Sources
LEAD_SOURCES = [
    "Website",
    "Hotline",
    "Email Marketing",
    "Referral",
    "Event/Hội thảo",
    "Social Media",
    "Partner",
    "Direct Contact",
    "Trade Show",
    "Cold Call",
]

# CRM Stages
CRM_STAGES = [
    {"name": "New", "sequence": 1},
    {"name": "Qualified", "sequence": 2},
    {"name": "Proposition", "sequence": 3},
    {"name": "Negotiation", "sequence": 4},
    {"name": "Won", "sequence": 5, "is_won": True},
    {"name": "Lost", "sequence": 6, "fold": True},
]

# Activity Types
ACTIVITY_TYPES = [
    "Gọi điện",
    "Gửi email",
    "Họp meeting",
    "Demo sản phẩm",
    "Gửi báo giá",
    "Follow-up",
    "Ký hợp đồng",
    "Tư vấn",
]

# Products (Vietnamese context)
PRODUCT_CATEGORIES = {
    "Software": {
        "name": "Phần mềm",
        "products": [
            "Phần mềm CRM",
            "Phần mềm ERP",
            "Phần mềm kế toán",
            "Phần mềm bán hàng",
            "Phần mềm quản lý kho",
            "Phần mềm HRM",
            "Phần mềm quản lý dự án",
            "Phần mềm marketing",
        ]
    },
    "Service": {
        "name": "Dịch vụ",
        "products": [
            "Tư vấn triển khai",
            "Đào tạo sử dụng",
            "Bảo trì hệ thống",
            "Tích hợp hệ thống",
            "Tùy chỉnh phần mềm",
            "Hỗ trợ kỹ thuật",
            "Tư vấn chiến lược",
            "Kiểm thử chất lượng",
        ]
    },
    "Hardware": {
        "name": "Phần cứng",
        "products": [
            "Máy chủ server",
            "Máy trạm workstation",
            "Thiết bị mạng",
            "Máy in mã vạch",
            "Máy quét",
            "Thiết bị lưu trữ",
            "Máy tính bảng",
            "Thiết bị POS",
        ]
    },
    "Gift": {
        "name": "Quà tặng",
        "products": [
            "USB quà tặng",
            "Sổ tay cao cấp",
            "Bình giữ nhiệt",
            "Túi vải canvas",
            "Móc khóa",
            "Pin sạc dự phòng",
            "Balo laptop",
            "Ô dù",
        ]
    },
}


def generate_company_name():
    """Generate a realistic Vietnamese company name"""
    company_type = random.choice(COMPANY_TYPES)
    company_name = random.choice(COMPANY_NAMES)
    suffix = random.choice(COMPANY_SUFFIXES)

    return f"{company_type} {company_name} {suffix}"


def generate_person_name(gender="random"):
    """Generate a realistic Vietnamese person name"""
    if gender == "random":
        gender = random.choice(["male", "female"])

    first_name = random.choice(FIRST_NAMES)

    if gender == "male":
        middle_name = random.choice(MIDDLE_NAMES_MALE)
        last_name = random.choice(LAST_NAMES_MALE)
    else:
        middle_name = random.choice(MIDDLE_NAMES_FEMALE)
        last_name = random.choice(LAST_NAMES_FEMALE)

    return f"{first_name} {middle_name} {last_name}"


def generate_tax_id():
    """Generate a 10-digit Vietnamese Tax ID (MST)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


def generate_phone():
    """Generate a Vietnamese phone number"""
    prefixes = ['090', '091', '093', '094', '097', '098', '086', '088', '089']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"+84{prefix[1:]}{number}"


def generate_email(name, company_name):
    """Generate a business email"""
    name_parts = name.lower().split()
    email_name = f"{name_parts[-1]}.{name_parts[0]}"

    # Create domain from company name
    company_parts = company_name.lower().split()
    # Find the main business name (skip company type words)
    skip_words = ['công', 'ty', 'tnhh', 'cp', 'cổ', 'phần', 'trách', 'nhiệm', 'hữu', 'hạn']
    domain_parts = [p for p in company_parts if p not in skip_words][:2]
    domain = ''.join(domain_parts)

    return f"{email_name}@{domain}.vn"


def generate_address(region):
    """Generate a Vietnamese address"""
    region_data = REGIONS.get(region, list(REGIONS.values())[0])
    district = random.choice(region_data["districts"])
    street = random.choice(region_data["streets"])
    number = random.randint(1, 500)

    return {
        "street": f"{number} {street}",
        "street2": district,
        "city": region,
        "country": "Vietnam",
        "zip": f"{random.randint(70000, 99999)}",
    }


def get_random_region():
    """Get a random Vietnamese region"""
    return random.choice(list(REGIONS.keys()))


def get_random_industry():
    """Get a random industry"""
    return random.choice(list(INDUSTRIES.keys()))
