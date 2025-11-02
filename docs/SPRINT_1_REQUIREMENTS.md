# SPRINT 1 - YÊU CẦU CHI TIẾT

## Tổng quan
Tài liệu này mô tả các yêu cầu chi tiết cho Sprint 1 của dự án Odoo CRM cho Dayone JSC (Got It).

---

## 1. Quản lý Khách hàng/Merchant/Nhà cung cấp

### 1.1. Kiểm tra trùng Mã số thuế (MST)
- Hệ thống tự động kiểm tra trùng lặp MST khi tạo/cập nhật khách hàng
- Cảnh báo khi phát hiện MST đã tồn tại trong hệ thống
- Ngăn chặn việc tạo khách hàng trùng MST

### 1.2. Phân công Salesperson
#### 1.2.1. Tự động phân công theo quy tắc
- **Quy trình phân công:**
  - Chưa có MST → Assign user (Telesale)
  - Sale verify (Tele/Meeting)
  - Convert (Sale)

#### 1.2.2. Kiểm tra trùng lặp thông tin
- Kiểm tra trùng thông tin liên hệ:
  - Số điện thoại
  - Email
  - Mã số thuế
- Ràng buộc: Đảm bảo cùng 1 Sale phụ trách các thông tin trùng lặp

#### 1.2.3. Thay đổi Sale hàng loạt
- Chức năng thay đổi người phụ trách hàng loạt cho nhiều khách hàng
- Hỗ trợ bulk update để tối ưu thời gian

### 1.3. Cập nhật thông tin theo Mã số thuế
- **Tích hợp Third Party Service:**
  - Kết nối đến dịch vụ của bên thứ ba
  - Tự động lấy thông tin chi tiết khách hàng theo MST
  - Cập nhật thông tin công ty, địa chỉ, đại diện pháp luật

### 1.4. Quản lý trạng thái Khách hàng
- **Các trạng thái:**
  - Potential (Tiềm năng)
  - Client (Khách hàng)
  - Lost (Mất khách)

- **Chuyển đổi tự động:**
  - Từ "Potential" → "Client"
  - Thời điểm: Khi hoàn tất tạo account

### 1.5. Quản lý thông tin chi tiết

#### 1.5.1. Thông tin cơ bản
- **Terms:** Điều khoản thanh toán, điều kiện giao dịch
- **Entity:** Pháp nhân, loại hình doanh nghiệp
- **Mã khách hàng:** Mã định danh duy nhất trong hệ thống

#### 1.5.2. Thông tin giao dịch
- **Danh sách hợp đồng:**
  - Hiển thị tất cả hợp đồng của khách hàng
  - Trạng thái, giá trị, thời hạn hợp đồng

- **Báo giá:**
  - Lịch sử báo giá
  - Trạng thái báo giá (Draft, Sent, Confirmed)

- **Doanh số mua:**
  - Tổng doanh số theo thời gian
  - Phân tích xu hướng mua hàng

#### 1.5.3. Chính sách và Account
- **Chính sách bán hàng:**
  - Giá ưu đãi
  - Điều khoản đặc biệt
  - Hạn mức công nợ

- **Thông tin account xuất đơn:**
  - Hỗ trợ một hoặc nhiều account
  - Quản lý thông tin xuất hóa đơn

#### 1.5.4. Quản lý nhóm
- **Company Group (Nhóm khách hàng):**
  - Key thông tin group từ phía công ty con
  - Key thông tin group từ phía công ty mẹ
  - Có thể check được từ 2 đầu (công ty con ↔ công ty mẹ)

#### 1.5.5. Địa chỉ
- **Địa chỉ giao hàng:**
  - Hỗ trợ nhiều địa chỉ giao hàng
  - Địa chỉ mặc định
  - Thông tin người nhận, số điện thoại liên hệ

### 1.6. Migration dữ liệu
- Chuyển đổi dữ liệu cũ vào hệ thống
- Đảm bảo tính toàn vẹn dữ liệu
- Mapping dữ liệu từ hệ thống cũ sang Odoo

### 1.7. Tích hợp đa nguồn
- **Nhận data khách hàng từ:**
  - Website
  - Hotline
  - Các nguồn khác
- Tự động tạo khách hàng trong hệ thống

---

## 2. Quản lý Lead

### 2.1. Quản lý người chăm sóc Lead
- **Thêm trường:** Người chăm sóc lead
- **Quy trình:**
  - Khi chưa nhận dạng lead → Assign người chăm sóc tạm thời
  - Khi nhận dạng được khách hàng → Trả lead về cho Sales phụ trách

### 2.2. Tự động phân bổ Lead theo quy tắc

#### 2.2.1. Các tiêu chí phân bổ
1. **Nhóm ngành hàng**
2. **Khu vực địa lý**
3. **Đối tượng khách hàng**
4. **Giá trị đơn hàng (Order)**

#### 2.2.2. Đặc điểm hệ thống
- Bộ rules có thể thay đổi theo từng thời điểm
- Hỗ trợ cấu hình linh hoạt
- Phân bổ tự động theo thứ tự ưu tiên

### 2.3. Hệ thống cảnh báo trùng lặp
- **Alert lead trùng nhau:**
  - So sánh giữa các lead
  - So sánh với data khách hàng có sẵn của Dayone
- **Thông tin kiểm tra:**
  - Số điện thoại
  - Email
  - Tên công ty
  - Mã số thuế

### 2.4. Thông báo
- Thông báo khi nhận được assign Lead
- Gửi qua email và notification trong hệ thống

### 2.5. Quản lý hàng loạt
- Thay đổi Sale phụ trách hàng loạt ở lead
- Bulk update để tối ưu hiệu suất

### 2.6. Migration và Tích hợp
- **Migration:** Chuyển đổi dữ liệu lead cũ vào hệ thống
- **API Integration:** Các website gọi API tạo lead vào hệ thống

---

## 3. Quản lý Cơ hội (Opportunity)

### 3.1. Migration dữ liệu
- Chuyển đổi dữ liệu cơ hội cũ vào hệ thống
- Mapping stages, probability, expected revenue
- Bảo toàn lịch sử hoạt động

---

## 4. Quản lý Sản phẩm

### 4.1. Thông tin sản phẩm trên FAST
- **Đặc điểm:**
  - Thông tin sản phẩm trên FAST là thông tin chung
  - Sửa theo template lưu ở FAST
  - Đồng bộ thông tin giữa Odoo và FAST

### 4.2. Tích hợp SO System
- Phù hợp cho phần xuất đơn hàng của SO System
- Đồng bộ thông tin sản phẩm, giá, tồn kho

### 4.3. Quản lý giá bán
- **Giảm giá sản phẩm:**
  - 1 sản phẩm có nhiều giá bán
  - Giá bán tùy theo từng chương trình khác nhau
  - Hỗ trợ pricelist theo:
    - Khách hàng
    - Thời gian
    - Số lượng
    - Chương trình khuyến mãi

### 4.4. Phân loại sản phẩm
- **Tạo hóa đơn/phiếu thu:**
  - Phân loại sản phẩm theo mục đích sử dụng
  - Tạo chứng từ kế toán tương ứng

- **Thông tin bổ sung:**
  - Mô tả chi tiết
  - Specifications
  - Images, documents

- **Chiết khấu:**
  - Chiết khấu theo sản phẩm
  - Chiết khấu theo chương trình

### 4.5. Quản lý Quà vật lý (Custom)
- **Kiểm tra tồn kho:**
  - Check tồn kho trước khi xuất
  - Cảnh báo khi hết hàng

- **Đối chiếu giá:**
  - Chênh lệch giá bán và giá cost
  - Báo cáo margin

- **Quy trình duyệt:**
  - Hỗ trợ Controller duyệt giá xuất code
  - Workflow approval

### 4.6. CCS (Customer Communication Service)
- Set up tin nhắn tự động
- Template messages
- Gửi thông báo đến khách hàng

### 4.7. Migration dữ liệu
- Chuyển đổi dữ liệu sản phẩm cũ vào hệ thống
- Import danh mục sản phẩm
- Đồng bộ giá bán

---

## 5. Quản lý Task

### 5.1. Tạo task trên CRM
- **Chức năng:**
  - Tạo task từ CRM
  - Assign cho các bộ phận liên quan:
    - Sales
    - Marketing
    - Customer Service
    - Logistics
    - Accounting

### 5.2. Theo dõi task
- Trạng thái task
- Deadline
- Priority
- Progress tracking

---

## 6. Thảo luận (Discuss)

### 6.1. Module Discuss của Odoo
- Sử dụng module thảo luận của Odoo
- Giao tiếp trực tiếp trên hệ thống

### 6.2. Tính năng
- **Chat:**
  - 1-1 chat
  - Group chat
  - Channel theo dự án/bộ phận

- **Thông báo:**
  - Mention users (@username)
  - Real-time notifications
  - Email integration

- **File sharing:**
  - Chia sẻ files, images
  - Xem trước files
  - Version control

---

## Timeline và Ưu tiên

### High Priority
1. Quản lý Khách hàng - MST check & auto assignment
2. Quản lý Lead - Auto assignment rules
3. Quản lý Sản phẩm - Giá bán và pricelist

### Medium Priority
4. Migration dữ liệu cũ
5. API integration cho lead creation
6. Task management

### Low Priority
7. CCS setup
8. Advanced reporting

---

## Ghi chú kỹ thuật

### Yêu cầu kỹ thuật
- Odoo version: 18
- Database: PostgreSQL 15
- Currency: VND
- Localization: Vietnam
- Language: Vietnamese

### Integration Points
- FAST system (Product information)
- SO System (Sales Order)
- Third-party MST service
- Website API
- Hotline system

### Performance Requirements
- Bulk operations phải xử lý được > 1000 records
- API response time < 2 seconds
- Real-time notifications
- Auto-save để tránh mất dữ liệu

---

## Phụ lục

### Danh sách Module Odoo cần sử dụng
- CRM
- Sales
- Contacts
- Product
- Inventory (cho quà vật lý)
- Discuss
- Calendar

### Custom Modules cần phát triển
- `gotit_crm_extension` - CRM customizations
- `gotit_mst_integration` - MST service integration
- `gotit_lead_assignment` - Auto lead assignment
- `gotit_product_management` - Product & pricing
- `gotit_sales_policy` - Sales policies

---

**Ngày tạo:** 2025-11-02
**Phiên bản:** 1.0
**Công ty:** Dayone JSC (Got It)
**Dự án:** Odoo CRM Implementation
