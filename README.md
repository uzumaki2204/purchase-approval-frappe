# Purchase Approval for Frappe 16

Ứng dụng độc lập cho trang **Purchase Approval**. Mã nguồn được phát hành tại repo riêng tư `uzumaki2204/purchase-approval-frappe`, nhánh `version-16`.

## Điều kiện cài đặt

- Frappe `16.53.0` trở lên trong nhánh 16.
- `factory_management` `0.1.29` trở lên trong nhánh 0.1; site phải có DocType `Company`, `Department`, `Product`.
- Site bật Server Scripts bằng `server_script_enabled = 1`.
- Python 3.14 trên bench Pilot hiện tại.

## Cài qua Pilot

1. Cấp quyền đọc repo riêng tư cho máy Pilot bằng GitHub account đã kết nối hoặc deploy key chỉ đọc.
2. Trong Pilot, chọn bench và site đích, nhập repo `uzumaki2204/purchase-approval-frappe` nhánh `version-16`, rồi cài app `purchase_approval_navigation`.
3. Chạy build assets và migrate nếu Pilot chưa tự thực hiện; sau đó tải lại worker và web.
4. Gán một Role `PA` phù hợp cho người dùng và thiết lập quy trình duyệt, người duyệt, nhà cung cấp và email trên site đích.

App tạo metadata mặc định gồm 16 DocType, Page, Sidebar, 7 Role, 48 Server Script, 3 Client Script, Print Format và bản dịch tiếng Việt. Bản cài không chứa đề nghị mua hàng, lịch sử, người dùng, hai quy trình duyệt của site nguồn hoặc thông tin xác thực email/Graph. Scheduler gửi thông báo được để tắt; quản trị viên bật sau khi cấu hình email.

Metadata được ghi trong `purchase_approval_navigation/metadata/purchase_approval.json`. Hook cài đặt chỉ thêm các bản ghi còn thiếu; migrate lần sau không ghi đè cấu hình đã chỉnh trên site. Page JavaScript/CSS, biểu tượng và bản dịch được phân phát từ app, không cần tệp trong `/files` của site nguồn.

## Phát hành

Mã chuẩn nằm trong `integrations/frappe/purchase-approval-navigation` của repo FactoryManagement. Khi phát hành, xuất đúng thư mục này sang repo app, kiểm tra commit và gắn tag. `tools/package_source.py` chuyển bản export metadata đọc từ site nguồn thành JSON đã bỏ thông tin audit và dữ liệu nghiệp vụ; không commit bản export thô.
