### **SPRINT 1 – QUẢN LÝ KHÁCH HÀNG, LEAD, CƠ HỘI, SẢN PHẨM, TASK & THẢO LUẬN**

---

#### **1. Quản lý Khách hàng / Merchant / Nhà cung cấp**

**Mục tiêu:** Chuẩn hóa quy trình quản lý khách hàng, tự động phân công Sales, và đồng bộ dữ liệu từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Kiểm tra trùng mã số thuế (MST)** khi tạo hoặc cập nhật khách hàng.
  ➤ *Cần module custom để kiểm tra trùng MST, SĐT, email và cảnh báo hợp nhất dữ liệu.*

- **Phân công Salesperson tự động**
  ➤ *Cần module custom để định nghĩa rule auto-assign theo Khu vực, Ngành hàng, Đối tượng KH, Giá trị Order.*
  - Nếu **khách hàng có MST**: tự động gán Sales theo **rule của GOT IT**.
  - Nếu **khách hàng chưa có MST**: gán cho **Telesale** để xác minh → sau khi xác minh → **Convert** sang Sale chính thức.
  - Cho phép thay đổi Sales hàng loạt đối với khách hàng khi cần. Khi có điều chỉnh nhân sự hoặc tái phân bổ khu vực, admin có thể chọn nhiều khách hàng và gán lại Sales phụ trách trong một lần thao tác. Hệ thống sẽ cập nhật đồng bộ các lead, cơ hội, và ghi log để theo dõi lịch sử thay đổi.
  ➤ *Cần wizard custom để cập nhật hàng loạt và ghi log tự động.*

- **Cập nhật thông tin khách hàng theo mã số thuế (MST)**
  ➤ *Cần module tích hợp API third-party để tự động tra cứu và cập nhật thông tin doanh nghiệp theo MST.*

- **Chuyển trạng thái khách hàng tự động**
  ➤ *Cần automation rule (server action) để đổi trạng thái từ "Potential" sang "Client" khi tạo xong account.*

- **Quản lý thông tin chi tiết khách hàng:**
  ➤ *Cấu hình và mapping field chuẩn trong Odoo CRM.*
  - Điều khoản thanh toán (Terms)
  - Loại thực thể (Entity)
  - Mã khách hàng (Customer Code)
  - Danh sách hợp đồng (Contracts)
  - Báo giá, doanh số mua, chính sách bán hàng
  - Tài khoản xuất đơn (có thể 1 hoặc nhiều)
  - Nhóm công ty (Company Group) – cho phép đối chiếu dữ liệu giữa công ty mẹ và công ty con
  - Địa chỉ giao hàng

- **Chuyển đổi dữ liệu cũ** từ file Excel vào hệ thống CRM.
  ➤ *Cần import script / data migration tool.*

- **Nhận data khách hàng từ nhiều nguồn (Website / Hotline)** và tạo tự động vào hệ thống CRM qua API.
  ➤ *Cần module API endpoint để nhận dữ liệu từ website/hotline và tự động tạo record.*

---

#### **2. Quản lý Lead**

**Mục tiêu:** Chuẩn hóa quy trình nhận, chăm sóc, và phân loại lead từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Thêm trường "Người chăm sóc lead" (Care Owner)**
  ➤ *Cần thêm field custom và automation để tự động trả lead về Sales phụ trách khi nhận dạng được khách hàng.*

- **Tự động assign lead theo rule GOT IT**
  ➤ *Cần module custom quản lý rule động (phân bổ theo ngành, khu vực, loại KH, giá trị đơn hàng) và tự gán Sales khi lead mới được tạo.*

- **Kiểm tra trùng lead và cảnh báo**
  ➤ *Cần logic kiểm tra trùng MST, email, SĐT trong model crm.lead khi tạo mới.*

- **Thông báo khi nhận được lead được assign** (qua email, thông báo trong hệ thống).
  ➤ *Cần automation gửi notification.*

- **Thay đổi Sales hàng loạt ở lead**.
  ➤ *Cần wizard custom tương tự như phần khách hàng.*

- **Chuyển đổi dữ liệu cũ** vào hệ thống CRM.
  ➤ *Cần import script / migration tool.*

- **Kết nối website → API tạo lead tự động** vào hệ thống CRM.
  ➤ *Cần custom API endpoint (POST /api/leads) để nhận và ghi lead mới.*

---

#### **3. Quản lý Cơ hội (Opportunities)**

- Chuyển đổi dữ liệu cũ vào hệ thống.
  ➤ *Cần migration script mapping từ hệ thống cũ sang crm.lead.*

- Đảm bảo mapping đúng giữa lead và cơ hội khi chuyển giai đoạn (Convert Lead → Opportunity).
  ➤ *Kiểm tra và điều chỉnh automation rule khi chuyển trạng thái.*

---

#### **4. Quản lý Sản phẩm**

**Mục tiêu:** Đồng bộ dữ liệu sản phẩm giữa hệ thống CRM và phần mềm FAST, phục vụ quy trình báo giá và bán hàng.

**Yêu cầu chi tiết & Cách triển khai:**

- Dữ liệu sản phẩm từ **FAST** là dữ liệu chuẩn → chỉ được chỉnh sửa theo **template từ FAST**.
  ➤ *Cần module sync dữ liệu với FAST hoặc import template tự động.*

- Phục vụ cho việc **xuất đơn hàng trong SO System**.
  ➤ *Mapping model crm.product với sale.order line.*

- Cho phép **một sản phẩm có nhiều mức giá** theo từng chương trình khuyến mãi / chiến dịch.
  ➤ *Cần custom bảng giá hoặc module pricing rule.*

- Phân loại sản phẩm: hàng tạo hóa đơn / phiếu thu, hàng có chiết khấu, hàng quà tặng vật lý.
  ➤ *Thêm field custom và logic xử lý khi tạo hóa đơn.*

- Custom logic cho **quà vật lý**: kiểm tra tồn kho, so sánh giá bán – giá cost, hỗ trợ bộ phận kiểm soát (controller) duyệt giá.
  ➤ *Cần module bổ sung logic kiểm tra kho và phê duyệt giá.*

- **CCS (setup tin nhắn)** liên quan đến sản phẩm.
  ➤ *Cần config module message template.*

- Chuyển đổi dữ liệu cũ vào hệ thống.
  ➤ *Cần import script.*

---

#### **5. Quản lý Task**

- Cho phép **tạo task trong CRM** để giao việc cho các bộ phận liên quan (ví dụ: Kế toán, Hậu cần...).
  ➤ *Sử dụng module Project; thêm automation tạo task từ CRM.*

- Khi tạo task từ **CRM (lead/opportunity)** → có thể gán trực tiếp cho bộ phận xử lý (ví dụ: Kế toán nhận thời gian xuất chứng từ).
  ➤ *Có sẵn trong Odoo, chỉ cần cấu hình project và user nhóm.*

- Khi tạo task từ **Sales Order** → cần **customize** để tự động sinh task (ví dụ: khi đơn hàng được xác nhận, hệ thống tự động tạo task "Xuất hóa đơn" cho Kế toán).
  ➤ *Cần module custom kết nối sale.order → project.task.*

---

#### **6. Thảo luận nội bộ**

- Sử dụng **module Thảo luận (Discuss)** của Odoo để các bộ phận có thể **trao đổi trực tiếp trên hệ thống**.
  ➤ *Chỉ cần cấu hình quyền truy cập và enable chatter trên lead, customer, task.*

- Mỗi lead, khách hàng, hoặc task đều có thể mở luồng thảo luận riêng (theo mô hình chatter).
