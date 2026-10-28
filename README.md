# Purchase Approval for Frappe 16

Ứng dụng độc lập cho trang **Purchase Approval**. Mã nguồn được phát hành tại repo riêng tư `uzumaki2204/purchase-approval-frappe`, nhánh `version-16`.

## Điều kiện cài đặt

- Frappe `16.53.0` trở lên trong nhánh 16.
- `factory_management` `0.1.29` trở lên trong nhánh 0.1; site phải có DocType `Company`, `Department`, `Product`.
- Site bật Server Scripts bằng `server_script_enabled = 1`.
- Python 3.14 trên bench Pilot hiện tại.

## Cài qua Pilot

1. Cấp quyền đọc repo riêng tư cho máy Pilot bằng GitHub account đã kết nối hoặc deploy key chỉ đọc.
2. Trong Pilot, chọn bench và site đích, nhập repo `uzumaki2204/purchase-approval-frappe` nhánh `version-16`, rồi cài app `purchase_approval`.
3. Chạy build assets và migrate nếu Pilot chưa tự thực hiện; sau đó tải lại worker và web.
4. Gán một Role `PA` phù hợp cho người dùng và thiết lập quy trình duyệt, người duyệt, nhà cung cấp và email trên site đích.

App tạo metadata mặc định gồm 16 DocType, Page, Sidebar, 7 Role, 48 Server Script, 3 Client Script, Print Format và bản dịch tiếng Việt. Bản cài không chứa đề nghị mua hàng, lịch sử, người dùng, hai quy trình duyệt của site nguồn hoặc thông tin xác thực email/Graph. Scheduler gửi thông báo được để tắt; quản trị viên bật sau khi cấu hình email.

Metadata được ghi trong `purchase_approval/metadata/purchase_approval.json`. Hook cài đặt chỉ thêm các bản ghi còn thiếu; migrate lần sau không ghi đè cấu hình đã chỉnh trên site. Page JavaScript/CSS, biểu tượng và bản dịch được phân phát từ app, không cần tệp trong `/files` của site nguồn.

## Chuyển site đã cài tên app cũ

Với site đã cài `purchase_approval_navigation`, hãy sao lưu database và public/private files trước khi chuyển. Đưa mã `purchase_approval` vào bench và thêm app mới vào `sites/apps.txt`, nhưng chưa chạy `install-app`. Khi site đang ở maintenance, chạy `bench --site <ten-site> execute purchase_approval.migrate_slug.execute`, tiếp theo là `bench --site <ten-site> migrate` và build assets. Lệnh chuyển cập nhật đăng ký app, Module Def, Sidebar, đường dẫn callback đã cấu hình và các tham chiếu trong Server/Client Script đã lưu; không xóa các DocType hoặc dữ liệu. Xác nhận app mới và dữ liệu trước khi bỏ package cũ khỏi bench.

URL callback mới là `/api/method/purchase_approval.outlook_action.confirm` và `/api/method/purchase_approval.gmail_action.confirm`. Cập nhật địa chỉ này ở proxy hoặc hệ thống bên ngoài trước khi bật các hành động email. Các API Server Script `pa_*` giữ nguyên tên.

Từ bản 1.1.1, cả 10 DocType Purchase Approval độc lập đều hỗ trợ Data Import bằng Excel (`.xlsx`) hoặc CSV. Role `PA Super Admin` có quyền Import, Create và Write cho các DocType này; Administrator cũng có thể import. Năm bảng con được import qua file của DocType cha. `PA Settings` là DocType Single nên chỉnh trực tiếp trong form. Khi nâng cấp site đã cài, chạy `bench --site <ten-site> migrate` để áp dụng patch một lần. Với token, lịch sử và đơn mua hàng, file import phải có đủ liên kết và dữ liệu hợp lệ; thao tác import có thể tạo bản ghi ngoài quy trình phê duyệt thông thường.

## Phát hành

Mã chuẩn nằm trong `integrations/frappe/purchase-approval` của repo FactoryManagement. Khi phát hành, xuất đúng thư mục này sang repo app, kiểm tra commit và gắn tag. `tools/package_source.py` chuyển bản export metadata đọc từ site nguồn thành JSON đã bỏ thông tin audit và dữ liệu nghiệp vụ; không commit bản export thô.
