# SPRINT 1 - YÊU CẦU

## Bối cảnh quan trọng

**Tình trạng hiện tại:** Got It hiện đang sử dụng các file Excel để quản lý dữ liệu khách hàng và bán hàng. Một yêu cầu quan trọng là chuyển đổi/import các file Excel này vào Odoo CRM như một phần của quá trình di chuyển dữ liệu.

## 1. Quản lý Khách hàng/Merchant/Nhà cung cấp

### 1.1. Kiểm tra trùng lặp và xác thực
- **Check trùng MST (Mã số thuế)**
    + Hệ thống tự động kiểm tra trùng MST khi tạo/cập nhật khách hàng
    + Đảm bảo tính duy nhất của thông tin thuế
- **Check trùng thông tin liên hệ**
    + Kiểm tra trùng Số điện thoại, Email
    + Ràng buộc khách hàng trùng thông tin về cùng 1 Sale phụ trách
    + **Giải pháp:** Check trùng sđt, email và phân công salesperson tự động

### 1.2. Phân công Salesperson
- **Auto phân user Sale theo rule**
    + Nhận data KH từ nhiều nguồn (Web/Hotline), check trùng MST
    + **Có MST:** Auto phân user Sale theo rule → Done
    + **Chưa có MST:** Assign user (Telesale) → Sale verify (Tele/Meeting) → Convert (Sale)
- **Thay đổi sale hàng loạt** ở khách hàng

### 1.3. Cập nhật thông tin khách hàng theo Mã số thuế
- **Kết nối đến dịch vụ third party**
    + Lấy thông tin chi tiết của khách hàng theo mã số thuế
    + **Giải pháp:** API tới 3rd-party để truy xuất dữ liệu công ty

### 1.4. Quản lý trạng thái khách hàng
- **Chuyển trạng thái tự động** từ "Potential" sang "Client"
- **Thời điểm chuyển:** Khi hoàn tất tạo account
- **Các trạng thái:** Client, Lost

### 1.5. Quản lý thông tin chi tiết
- Terms
- Entity
- Mã khách hàng
- Hiển thị list hợp đồng của khách hàng đó
- Báo giá
- Doanh số mua
- Chính sách bán hàng
- Thông tin account xuất đơn (một hoặc nhiều account)
- Company group (nhóm khách hàng, key thông tin group từ phía cty con lẫn cty mẹ mới có thể check được từ 02 đầu)
- Địa chỉ giao hàng

### 1.6. Migration & Data Import
- Chuyển đổi dữ liệu cũ vào hệ thống (từ Excel files)
- Nhận data KH từ nhiều nguồn (Web/Hotline) tạo vào hệ thống

## 2. Quản lý Lead

### 2.1. Nhận Lead từ Website
- **Website gọi API tạo lead vào hệ thống**
    + **Giải pháp:** API tạo từ Odoo, website của GOT IT call API
    + Nhận thông tin Lead từ website của GOT IT
    + Tự động tạo lead trong CRM khi có submission từ web

### 2.2. Chăm sóc Lead
- **Thêm trường thông tin người chăm sóc lead**
    + Áp dụng khi chưa nhận dạng lead này của khách hàng nào và của sales nào
    + Khi nhận dạng ra được thì trả lead về cho Sales phụ trách khách hàng đó

### 2.3. Tự động assign leads theo rule Gotit
- **Phân bổ theo thứ tự ưu tiên:**
    1. **NHÓM NGÀNH HÀNG**
    2. **KHU VỰC**
    3. **ĐỐI TƯỢNG KH**
    4. **GIÁ TRỊ ORDER**
- **Đặc điểm:**
    + Bộ rules này sẽ thay đổi theo từng thời điểm khác nhau
    + **Giải pháp:** Rule tự động customize theo yêu cầu Gotit
- **Quy trình phân công:**
    + Nhận data từ nhiều nguồn (Web/Hotline)
    + Check trùng MST
    + Có MST: Auto phân user Sale theo rule
    + Chưa có MST: Assign user (Telesale) → Sale verify (Tele/Meeting) → Convert (Sale)

### 2.4. Hệ thống cảnh báo và thông báo
- **Alert lead trùng nhau** hoặc trùng data so với thông tin khách hàng sẵn có của Dayone
- **Thông báo khi nhận được assign Lead**

### 2.5. Quản lý hàng loạt
- **Thay đổi sale hàng loạt** ở lead

### 2.6. Migration & Data Import
- Chuyển đổi dữ liệu cũ vào hệ thống

## 3. Quản lý cơ hội

- Chuyển đổi dữ liệu cũ vào hệ thống

## 4. Quản lý sản phẩm

- Thông tin sản phẩm trên Fast là thông tin chung: sửa theo template lưu ở FAST
- Phù hợp cho phần xuất đơn hàng của SO System.
- Giảm giá sản phẩm, 1 sản phẩm có nhiều giá bán tùy theo từng chương trình khác nhau
- Phân loại sản phẩm: tạo hóa đơn/phiếu thu; thông tin bổ sung cho sản phẩm, chiết khấu
- Custom quà vật lý: check tồn kho, đối chiếu chênh lệch giá bán và giá cost, hỗ trợ controller trong chuyện duyệt giá xuất code
- CCS (set up tin nhắn)
- Chuyển đổi dữ liệu cũ vào hệ thống

## 5. Quản lý Task

### 5.1. Tạo task và phân công
- **CRM cho phép lên task và assign cho các bộ phận liên quan**
    + Ví dụ: CRM lên task → Kế toán nhận thời gian xuất chứng từ
    + **Giải pháp:**
        * Create task từ CRM: Sử dụng chức năng có sẵn
        * Create task từ Sales: Cần customize

## 6. Thảo luận

### 6.1. Giao tiếp nội bộ
- **Sử dụng module thảo luận của Odoo**
    + Giao tiếp trực tiếp trên hệ thống
    + Theo dõi lịch sử trao đổi

## 7. Email & Marketing

### 7.1. Đồng bộ Email với Outlook
- **Yêu cầu:**
    + Điền đầy đủ thông tin trong template → Action: preview → Gửi mail trực tiếp cho KH trên Odoo
    + Đồng bộ email và lịch sử mail giữa hệ thống ↔ Outlook
- **Trạng thái:** ⚠️ **Không thực hiện được**

### 7.2. Tương tác Email với Khách hàng
- **Nhu cầu:** Tương tác email giữa GOTIT và Khách hàng
- **Giải pháp đề xuất:**
    + Bật chức năng **Portal** trên Odoo
    + Khách hàng login lên portal của Odoo để thảo luận với team GOTIT
- **Cần quyết định:** GOT IT đánh giá có muốn thực hiện theo yêu cầu này không?

### 7.3. Automation Marketing
- **Chức năng:**
    + Gửi email, lịch hẹn, báo giá trên email liên kết với CRM
    + Gửi email auto cho khách hàng theo lịch trình:
        * Ngày 1: Gửi email 1
        * Ngày 3: Gửi email 2
        * Ngày 5: Gửi email 3
    + Thiết lập gửi email auto (dạng email cho 1 action đơn lẻ) theo rule
- **Đánh giá:** ⚠️ **Đây là một tính năng lớn**
    + GOT IT cần đánh giá kỹ xem có thực hiện chức năng này không
    + Nếu thực hiện thì sẽ cần phân tích thêm sâu nữa

### 7.4. Mass Mailing
- **Chức năng:** Gửi email với số lượng lớn
- **Đặc điểm:**
    + Cộng hưởng tốt với Giải pháp Automation Marketing
    + Có thể chạy độc lập không cần Automation Marketing
- **Giải pháp:** Tích hợp **Mail Chimp** hoặc **Get Response**
