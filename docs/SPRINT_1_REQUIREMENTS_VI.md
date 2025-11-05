### **SPRINT 1 – QUẢN LÝ KHÁCH HÀNG, LEAD, CƠ HỘI, SẢN PHẨM, TASK & THẢO LUẬN**

---

#### **1. Quản lý Khách hàng / Merchant / Nhà cung cấp**

**Mục tiêu:** Chuẩn hóa quy trình quản lý khách hàng, tự động phân công Sales, và đồng bộ dữ liệu từ nhiều nguồn.

**Yêu cầu chi tiết & Cách triển khai:**

- **Quản lý trùng lặp khách hàng và phân công Sale:**

  **Business Context:**
  Đảm bảo dữ liệu khách hàng sạch, tránh nhiều Sale cùng làm việc với một khách hàng, và duy trì lịch sử giao dịch đầy đủ.

  **User Stories:**

  **Story 1: Phát hiện trùng lặp khi tạo/cập nhật khách hàng**
  - **Vai trò**: Sales/Admin
  - **Mục đích**: Khi tạo hoặc cập nhật khách hàng, tôi muốn hệ thống cảnh báo ngay nếu thông tin trùng với khách hàng đã tồn tại, để tôi có thể xử lý trước khi lưu dữ liệu.

  **Workflow:**
  1. User nhập thông tin khách hàng (MST, SĐT, hoặc Email)
  2. Hệ thống kiểm tra real-time khi user blur khỏi trường nhập
  3. **NẾU** phát hiện trùng lặp:
     - Hiển thị cảnh báo với thông tin khách hàng trùng lặp
     - Hiển thị tên Sale đang phụ trách (nếu có)
     - **NẾU** Sale khác nhau: Chặn lưu, yêu cầu xử lý trước
     - **NẾU** cùng Sale hoặc chưa có Sale: Đưa ra tùy chọn: (a) Hợp nhất, (b) Tiếp tục tạo mới, (c) Hủy bỏ
  4. **NẾU** không trùng lặp: Cho phép lưu bình thường

  **Story 2: Quét và phát hiện trùng lặp trong dữ liệu hiện có**
  - **Vai trò**: Admin
  - **Mục đích**: Tôi muốn quét toàn bộ database để tìm các bản ghi khách hàng trùng lặp đã tồn tại, để có thể dọn dẹp dữ liệu hàng loạt.

  **Workflow:**
  1. Admin mở công cụ "Quét trùng lặp"
  2. Admin chọn tiêu chí quét: MST / SĐT / Email / Tất cả
  3. Hệ thống quét database và tạo báo cáo
  4. Báo cáo hiển thị:
     - Các nhóm bản ghi trùng lặp
     - Số lượng trùng lặp trong mỗi nhóm
     - Thông tin Sale phụ trách mỗi bản ghi
     - Số lượng giao dịch của mỗi bản ghi
  5. Admin xem chi tiết và quyết định hành động (xem Story 3)

  **Story 3: Hợp nhất các bản ghi trùng lặp**
  - **Vai trò**: Admin/Sales Manager
  - **Mục đích**: Khi phát hiện trùng lặp, tôi muốn hợp nhất các bản ghi thành một, giữ lại đầy đủ lịch sử, và xác định Sale phụ trách hợp lý.

  **Workflow:**
  1. User chọn các bản ghi cần hợp nhất (từ danh sách trùng lặp)
  2. Hệ thống hiển thị wizard hợp nhất:
     - So sánh thông tin của các bản ghi
     - Cho phép chọn thông tin nào giữ lại (master record)
     - Hiển thị tổng số giao dịch, leads, opportunities sẽ được chuyển
  3. **Xác định Sale phụ trách** (tự động đề xuất):
     - **Ưu tiên 1**: Sale có nhiều giao dịch nhất với khách hàng này
     - **Ưu tiên 2**: Sale được gán gần đây nhất
     - **Ưu tiên 3**: Admin/Manager quyết định thủ công
  4. User xác nhận hợp nhất
  5. Hệ thống thực hiện:
     - Chuyển tất cả leads, opportunities, orders, invoices sang bản ghi master
     - Cập nhật Sale phụ trách
     - Lưu log lịch sử hợp nhất
     - Đánh dấu các bản ghi cũ là "Merged" (không xóa hoàn toàn)

  **Acceptance Criteria:**
  - ✓ **Cho Story 1**: Khi nhập MST/SĐT/Email trùng, hệ thống cảnh báo trong vòng 1 giây
  - ✓ **Cho Story 1**: Nếu trùng lặp thuộc Sale khác, hệ thống chặn không cho lưu
  - ✓ **Cho Story 2**: Công cụ quét có thể xử lý database > 100,000 khách hàng trong < 5 phút
  - ✓ **Cho Story 2**: Báo cáo hiển thị đầy đủ thông tin để ra quyết định
  - ✓ **Cho Story 3**: Sau hợp nhất, không mất bất kỳ giao dịch hoặc thông tin nào
  - ✓ **Cho Story 3**: Có thể rollback (undo merge) trong vòng 24 giờ

  **Business Rules:**
  - **Tiêu chí trùng lặp**: MST HOẶC SĐT HOẶC Email giống nhau
  - **Ràng buộc Sale**: Các bản ghi trùng lặp phải cùng 1 Sale (nếu đã có Sale)
  - **Ưu tiên hợp nhất**: Master record = bản ghi có nhiều giao dịch nhất
  - **Bảo toàn dữ liệu**: Không xóa cứng, chỉ đánh dấu "Merged"

  **Edge Cases:**
  - **Trường hợp 1**: MST giống nhau nhưng SĐT/Email khác → Vẫn coi là trùng (MST là unique identifier)
  - **Trường hợp 2**: 3+ bản ghi trùng lặp → Hỗ trợ merge nhiều bản ghi cùng lúc
  - **Trường hợp 3**: Trùng một phần thông tin (fuzzy match) → Đưa vào báo cáo "Có thể trùng" để review thủ công

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

- **Người chăm sóc lead (Care Owner):**
  - Thêm trường thông tin "Người chăm sóc lead" để quản lý lead khi chưa nhận dạng được lead này thuộc về khách hàng nào hoặc thuộc về Sales nào.
  - **Quy trình xử lý**: Care Owner chăm sóc lead → Khi nhận dạng được khách hàng → Hệ thống tự động trả lead về cho Sales phụ trách khách hàng đó.
  - Mục đích: Đảm bảo không có lead nào bị bỏ sót trong quá trình chờ nhận dạng.

- **Tự động phân công lead theo rule GOT IT:**
  - Hệ thống tự động phân bổ lead cho Sales dựa trên bộ rules có thể cấu hình, theo thứ tự ưu tiên:
    1. **Nhóm ngành hàng** (Industry Group)
    2. **Khu vực** (Region)
    3. **Đối tượng khách hàng** (Customer Type)
    4. **Giá trị order** (Order Value)
  - Bộ rules này có thể thay đổi theo từng thời điểm khác nhau tùy thuộc vào chiến lược kinh doanh và cơ cấu tổ chức.
  - Hệ thống cần hỗ trợ quản trị viên dễ dàng cập nhật và điều chỉnh rules phân bổ mà không cần can thiệp kỹ thuật.

- **Phát hiện lead trùng lặp:**
  - Hệ thống cảnh báo khi phát hiện lead trùng lặp với nhau hoặc trùng với thông tin khách hàng đã có sẵn trong database (DayOne).
  - Kiểm tra dựa trên: MST, số điện thoại, email.
  - Tích hợp với hệ thống phát hiện trùng lặp khách hàng để đảm bảo tính nhất quán.

- **Thông báo khi được phân công lead:**
  - Sales nhận được thông báo ngay lập tức khi có lead mới được assign cho mình.
  - Các kênh thông báo: Email và thông báo trong hệ thống (in-app notification).
  - Thông báo bao gồm thông tin tóm tắt về lead để Sales có thể nhanh chóng đánh giá và xử lý.

- **Thay đổi Sales hàng loạt cho lead:**
  - Cho phép quản lý gán lại hàng loạt lead cho Sales khác khi có thay đổi về phân công công việc hoặc tái cấu trúc team.
  - Ghi log đầy đủ lịch sử thay đổi để theo dõi và audit.

- **Chuyển đổi dữ liệu cũ vào hệ thống:**
  - Import dữ liệu lead từ hệ thống cũ (Excel, database cũ) vào CRM mới.
  - Đảm bảo mapping đúng các trường thông tin và lịch sử tương tác.

- **Tích hợp API từ website:**
  - Cung cấp API endpoint cho phép các website gọi và tạo lead tự động vào hệ thống CRM.
  - API hỗ trợ nhận thông tin lead từ form đăng ký, landing page, và các nguồn digital marketing khác.

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
