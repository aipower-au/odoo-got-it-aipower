### **SPRINT 1 – QUẢN LÝ KHÁCH HÀNG, LEAD, CƠ HỘI, SẢN PHẨM, TASK & THẢO LUẬN**

---

#### **1. Quản lý Khách hàng / Merchant / Nhà cung cấp**

**Mục tiêu:** Chuẩn hóa quy trình quản lý khách hàng, tự động phân công Sales, và đồng bộ dữ liệu từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Quản lý trùng lặp khách hàng và phân công Sale:**
  - **Tiêu chí phát hiện trùng lặp:**
    - Hệ thống kiểm tra trùng lặp dựa trên ba trường thông tin: **Mã số thuế (MST)**, **Số điện thoại**, và **Email**.
    - Phát hiện trùng lặp xảy ra khi: (1) tạo mới hoặc cập nhật khách hàng, (2) sử dụng công cụ quét dữ liệu hiện có trong database.
  - **Cơ chế phát hiện và cảnh báo:**
    - **Validation real-time**: Cảnh báo ngay lập tức khi người dùng nhập thông tin trùng với khách hàng đã tồn tại.
    - **Công cụ quét dữ liệu**: Cho phép quét toàn bộ database để phát hiện các bản ghi trùng lặp trong dữ liệu hiện có.
    - Hiển thị thông tin bản ghi trùng lặp để người dùng đối chiếu và xác nhận.
  - **Quy tắc phân công Sale:**
    - Tất cả các bản ghi khách hàng trùng lặp phải được gán cho **cùng một Salesperson** để tránh xung đột khi nhiều Sale cùng làm việc với một khách hàng.
    - Nếu phát hiện bản ghi trùng lặp thuộc về các Sale khác nhau, hệ thống cảnh báo và yêu cầu xử lý trước khi cho phép tạo/cập nhật.
  - **Quy trình giải quyết trùng lặp:**
    - **Chức năng hợp nhất (Merge)**: Cho phép hợp nhất các bản ghi trùng lặp thành một bản ghi duy nhất, đồng thời bảo toàn toàn bộ lịch sử giao dịch và thông tin quan trọng.
    - **Xác định Sale phụ trách**: Hệ thống hỗ trợ xác định Sale nào sẽ phụ trách khách hàng sau hợp nhất dựa trên: Sale có nhiều giao dịch nhất, Sale được gán gần đây nhất, hoặc quyết định của quản lý.

- **Phân công Salesperson tự động**
  - Nếu **khách hàng có MST**: tự động gán Sales theo **rule của GOT IT**.
  - Nếu **khách hàng chưa có MST**: gán cho **Telesale** để xác minh → sau khi xác minh → **Convert** sang Sale chính thức.
  - Cho phép thay đổi Sales hàng loạt đối với khách hàng khi cần. Khi có điều chỉnh nhân sự hoặc tái phân bổ khu vực, admin có thể chọn nhiều khách hàng và gán lại Sales phụ trách trong một lần thao tác. Hệ thống sẽ cập nhật đồng bộ các lead, cơ hội, và ghi log để theo dõi lịch sử thay đổi.

- **Cập nhật thông tin khách hàng theo mã số thuế (MST):**
  - Kết nối đến dịch vụ của third party để tự động lấy thông tin chi tiết của khách hàng dựa trên mã số thuế.
  - Hệ thống tự động điền các thông tin như: tên doanh nghiệp, địa chỉ đăng ký, người đại diện pháp luật, ngành nghề kinh doanh, và các thông tin công khai khác.

- **Chuyển trạng thái khách hàng tự động:**
  - Hệ thống quản lý ba trạng thái chính của khách hàng: **Potential** (tiềm năng), **Client** (khách hàng chính thức), và **Lost** (khách hàng mất).
  - **Chuyển từ Potential → Client**: Tự động chuyển trạng thái khi hoàn tất tạo account trong hệ thống.
  - **Trạng thái Lost**: Áp dụng cho khách hàng không còn hoạt động hoặc không còn quan tâm đến sản phẩm/dịch vụ. Hệ thống cần hỗ trợ đánh dấu và theo dõi lý do chuyển sang trạng thái này.

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
