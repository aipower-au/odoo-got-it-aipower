# SPRINT 1 - YÊU CẦU

## Bối cảnh quan trọng

**Tình trạng hiện tại:** Got It hiện đang sử dụng các file Excel để quản lý dữ liệu khách hàng và bán hàng. Một yêu cầu quan trọng là chuyển đổi/import các file Excel này vào Odoo CRM như một phần của quá trình di chuyển dữ liệu.

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

---

## Chi tiết yêu cầu và giải pháp

| Ngày ghi nhận | Loại yêu cầu | Module | Nội dung yêu cầu | Mô tả yêu cầu | Phản hồi và giải pháp của Odoo |
|---------------|--------------|--------|------------------|---------------|--------------------------------|
| 9/19/2025 | | CRM | Nhận lead từ Website | Nhận thông tin Lead từ website của GOT IT | API tạo từ Odoo, website của GOT IT call API |
| 9/19/2025 | | CRM | CRM cho phép lên task và assign cho các bộ phận liên quan | (CRM lên task -> Kế toán nhận thời gian xuất chứng từ) | Create task từ CRM đã có; Create task từ Sales cần customize |
| 9/19/2025 | | CRM | Tự động assign leads theo rule Gotit quy định | Tự động assign leads theo rule Gotit quy định (theo khu vực; giá trị; thứ tự yêu tiên của lead). Phân bổ theo (1) NHÓM NGÀNH HÀNG, (2) KHU VỰC, (3) ĐỐI TƯỢNG KH (4) GIÁ TRỊ ORDER. | Rule tự động customize |
| 9/19/2025 | | CRM | Tự động assign leads theo rule Gotit quy định | Nhận data KH từ nhiều nguồn (Web/Hotline), check trùng MST-> chia theo 2 phần+ Có MST: auto phân user Sale theo rule ->Done + Chưa có MST: assign user (Telesale)-> Sale verify (Tele/ Meeting)->Convert (Sale) | Check trùng MST và phân công salesperson |
| 9/19/2025 | | CRM | Chăm sóc lead | Thêm trường thông tin người chăm sóc lead khi chưa nhận dạng lead này của khách hàng nào và của sales nào. Đến khi nhận dạng ra được thì trả lead về cho Sales phụ trách khách hàng đó. | |
| 9/19/2025 | | CRM | Cập nhật thông tin khách hàng theo mã số thuế | Kết nối đến dịch vụ của third party, lấy thông tin chi tiết của khách hàng theo mã số thuế. | API tới 3rd-party. |
| 9/19/2025 | | CRM | Phân khách hàng cho Sales | Check trùng thông tin liên hệ (Sdt, email), ràng buộc về cùng 1 Sale phụ trách | Check trùng sđt, email và phân công salesperson |
| 9/19/2025 | | CRM | Đồng bộ mail giữa Odoo và Outlook | Điền đầy đủ thông tin trong template ->Action: preview ->gửi mail trực tiếp cho KH trên odoo. Đồng bộ email và lịch sử mail giữa hệ thống -> outlook | Không thực hiện được. |
| 9/19/2025 | | CRM | Tương tác email với khách hàng | Nhu cầu tương tác email giữa GOTIT và Khách hàng. | Bật chức năng portal trên Odoo, khách hàng login lên portal của Odoo để thảo luận với team GOTIT. GOT IT đánh giá có muốn thực hiện theo yêu cầu này không? |
| 19/9/2025 | | CRM | Automation marketing | Gửi email, lịch hẹn, báo giá trên email liên kết với CRM. Gửi email auto cho khách hàng, chức năng automation marketing Ngày 1 gửi email 1 Ngày 3 gửi email 2 Ngày 5 gửi email 3 Thiết lập gửi email auto (dạng email cho 1 action đơn lẻ) theo rule | Đây là một tính năng lớn. GOT IT đánh giá kỹ xem có thực hiện chức năng này không? Nếu thực hiện thì sẽ cần phân tích thêm sâu nữa. |
| 19/9/2025 | | CRM | Mass Mailing | Gửi email với số lượng lớn. Chức năng này cộng hưởng tốt với Giải pháp Automation Marketing, hoặc có thể chạy độc lập không cần Automation Marketing. | Tích hợp Mail Chimp hoặc Get Response. |
