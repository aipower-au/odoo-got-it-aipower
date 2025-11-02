# SPRINT 1 - YÊU CẦU

## 1. Quản lý Khách hàng/Merchant/Nhà cung cấp

- Check trùng MST
- Phân công salesperson
    + Auto phân user Sale theo rule. Chưa có MST: assign user (Telesale)-> Sale verify (Tele/ Meeting)->Convert  (Sale)
    + Check trùng thông tin liên hệ (Sdt, email), MST, ràng buộc về cùng 1 Sale phụ trách
    + Thay đổi sale hàng loạt ở khách hàng
- Cập nhật thông tin khách hàng theo mã số thuế.
    + Kết nối đến dịch vụ của third party, lấy thông tin chi tiết của khách hàng theo mã số thuế.
- Khách hàng (trạng thái: client, lost): Chuyển trạng thái tự động từ "Potential" sang "Client". Thời điểm chuyển trạng thái: khi hoàn tất tạo account
- Quản lý thông tin:
    + Terms
    + Entity
    + Mã khách hàng
    + Hiển thị list hợp đồng của khách hàng đó
    + Báo giá
    + Doanh số mua
    + Chính sách bán hàng
    + Thông tin account xuất đơn (một hoặc nhiều account)
    + company group(nhóm khách hàng, key thông tin group từ phía cty con lẫn cty mẹ mới có thể check được từ 02 đầu.)
    + Địa chỉ giao hàng
- Chuyển đổi dữ liệu cũ vào hệ thống
- Nhận data KH từ nhiều nguồn (Web/Hotline) tạo vào hệ thống

## 2. Quản lý Lead

- Thêm trường thông tin người chăm sóc lead khi chưa nhận dạng lead này của khách hàng nào và của sales nào. Đến khi nhận dạng ra được thì trả lead về cho Sales phụ trách khách hàng đó.
- Tự động assign leads theo rule Gotit quy định (theo khu vực; giá trị; thứ tự yêu tiên của lead). Phân bổ theo (1) NHÓM NGÀNH HÀNG, (2) KHU VỰC, (3) ĐỐI TƯỢNG KH  (4) GIÁ TRỊ ORDER.
    + Bộ rules này sẽ thay đổi theo từng thời điểm khác nhau.
- Có hệ thống alert lead trùng nhau hoặc trùng data so với thông tin khách hàng sẵn có của Dayone
- Thông báo khi nhận được assign Lead
- Thay đổi sale hàng loạt ở lead
- Chuyển đổi dữ liệu cũ vào hệ thống
- các websie gọi API tạo lead vào hệ thống

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

## 5. Quản lý task

- Tạo task trên CRM: assign cho các bộ phận liên quan

## 6. Thảo luận

- Sử dụng module thảo luận của odoo để giao tiếp vs nhau trực tiếp trên hệ thống.
