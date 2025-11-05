### **SPRINT 1 – QUẢN LÝ KHÁCH HÀNG, LEAD, CƠ HỘI, SẢN PHẨM, TASK & THẢO LUẬN**

---

#### **1. Quản lý Khách hàng / Merchant / Nhà cung cấp**

**Mục tiêu:** Chuẩn hóa quy trình quản lý khách hàng, tự động phân công Sales, và đồng bộ dữ liệu từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Kiểm tra trùng mã số thuế (MST)** khi tạo hoặc cập nhật khách hàng.

- **Phân công Salesperson tự động**
  - Nếu **khách hàng có MST**: tự động gán Sales theo **rule của GOT IT**.
  - Nếu **khách hàng chưa có MST**: gán cho **Telesale** để xác minh → sau khi xác minh → **Convert** sang Sale chính thức.
  - Cho phép thay đổi Sales hàng loạt đối với khách hàng khi cần. Khi có điều chỉnh nhân sự hoặc tái phân bổ khu vực, admin có thể chọn nhiều khách hàng và gán lại Sales phụ trách trong một lần thao tác. Hệ thống sẽ cập nhật đồng bộ các lead, cơ hội, và ghi log để theo dõi lịch sử thay đổi.

- **Cập nhật thông tin khách hàng theo mã số thuế (MST)**

- **Chuyển trạng thái khách hàng tự động**

- **Quản lý thông tin chi tiết khách hàng:**
  - Điều khoản thanh toán (Terms)
  - Loại thực thể (Entity)
  - Mã khách hàng (Customer Code)
  - Danh sách hợp đồng (Contracts)
  - Báo giá, doanh số mua, chính sách bán hàng
  - Tài khoản xuất đơn (có thể 1 hoặc nhiều)
  - Nhóm công ty (Company Group) – cho phép đối chiếu dữ liệu giữa công ty mẹ và công ty con
  - Địa chỉ giao hàng

- **Chuyển đổi dữ liệu cũ** từ file Excel vào hệ thống CRM.

- **Nhận data khách hàng từ nhiều nguồn (Website / Hotline)** và tạo tự động vào hệ thống CRM qua API.

---

#### **2. Quản lý Lead**

**Mục tiêu:** Chuẩn hóa quy trình nhận, chăm sóc, và phân loại lead từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Thêm trường "Người chăm sóc lead" (Care Owner)**

- **Tự động assign lead theo rule GOT IT**

- **Kiểm tra trùng lead và cảnh báo**

- **Thông báo khi nhận được lead được assign** (qua email, thông báo trong hệ thống).

- **Thay đổi Sales hàng loạt ở lead**.

- **Chuyển đổi dữ liệu cũ** vào hệ thống CRM.

- **Kết nối website → API tạo lead tự động** vào hệ thống CRM.

---

#### **3. Quản lý Cơ hội (Opportunities)**

- Chuyển đổi dữ liệu cũ vào hệ thống.

- Đảm bảo mapping đúng giữa lead và cơ hội khi chuyển giai đoạn (Convert Lead → Opportunity).

---

#### **4. Quản lý Sản phẩm**

**Mục tiêu:** Đồng bộ dữ liệu sản phẩm giữa hệ thống CRM và phần mềm FAST, phục vụ quy trình báo giá và bán hàng.

**Yêu cầu chi tiết & Cách triển khai:**

- Dữ liệu sản phẩm từ **FAST** là dữ liệu chuẩn → chỉ được chỉnh sửa theo **template từ FAST**.

- Phục vụ cho việc **xuất đơn hàng trong SO System**.

- Cho phép **một sản phẩm có nhiều mức giá** theo từng chương trình khuyến mãi / chiến dịch.

- Phân loại sản phẩm: hàng tạo hóa đơn / phiếu thu, hàng có chiết khấu, hàng quà tặng vật lý.

- Custom logic cho **quà vật lý**: kiểm tra tồn kho, so sánh giá bán – giá cost, hỗ trợ bộ phận kiểm soát (controller) duyệt giá.

- **CCS (setup tin nhắn)** liên quan đến sản phẩm.

- Chuyển đổi dữ liệu cũ vào hệ thống.

---

#### **5. Quản lý Task**

- Cho phép **tạo task trong CRM** để giao việc cho các bộ phận liên quan (ví dụ: Kế toán, Hậu cần...).

- Khi tạo task từ **CRM (lead/opportunity)** → có thể gán trực tiếp cho bộ phận xử lý (ví dụ: Kế toán nhận thời gian xuất chứng từ).

- Khi tạo task từ **Sales Order** → cần **customize** để tự động sinh task (ví dụ: khi đơn hàng được xác nhận, hệ thống tự động tạo task "Xuất hóa đơn" cho Kế toán).

---

#### **6. Thảo luận nội bộ**

- Sử dụng **module Thảo luận (Discuss)** của Odoo để các bộ phận có thể **trao đổi trực tiếp trên hệ thống**.

- Mỗi lead, khách hàng, hoặc task đều có thể mở luồng thảo luận riêng (theo mô hình chatter).
