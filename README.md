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

App tạo metadata mặc định gồm 17 DocType, Page, Sidebar, 8 Role, 51 Server Script, 3 Client Script, Print Format và bản dịch tiếng Việt. Bản cài không chứa đề nghị mua hàng, lịch sử, người dùng, hai quy trình duyệt của site nguồn hoặc thông tin xác thực email/Graph. Scheduler gửi thông báo được để tắt; quản trị viên bật sau khi cấu hình email.

Từ v2.0.8, mỗi quy trình có thể cấu hình thứ tự các bước kiểm tra kho, bàn giao đề nghị mua, báo giá, duyệt báo giá và nhận hàng. Người xử lý được gán bằng User hoặc Role; mỗi bước có cờ email riêng. Người tạo vẫn lập và gửi phiếu. Nếu chỉ một quy trình phù hợp, hệ thống chọn tự động; nếu nhiều quy trình phù hợp, phiếu chờ người được cấu hình chọn. Sau khi nâng cấp, các quy trình cũ có chuỗi bước mặc định và các bước duyệt đang chạy giữ nguyên snapshot. Quản trị viên cần gán thành viên cho Role `PA Stock Checker` trước khi gửi phiếu mới theo quy trình đã chuyển đổi.

Từ v2.0.10, mỗi bước có thể gán nhiều User và chọn `Any` hoặc `All`; Báo giá luôn do một người hoàn tất. Bàn giao đề nghị mua cần người được giao xác nhận. Các phiên duyệt đang chạy giữ nguyên người xử lý đã chụp trước đó.

Từ v2.0.11, patch cập nhật Server Script hòa trộn thay đổi không trùng với phần nâng cấp. Nếu site và app cùng sửa một đoạn mã, migrate dừng để tránh ghi đè tùy chỉnh đó.

Từ v2.0.12, trang quản trị lưu quy trình qua Python API để không cần ghi đè `pa_save_approval_workflow` trên site. Server Script nhận hàng cục bộ cũng được giữ nguyên; runtime không lưu người nhận cuối cho đến khi đủ người trong bước `All`. Patch chỉ hòa trộn cập nhật nhãn người xử lý vào `pa_get_approval_workflow`.

Từ v2.0.13, patch nâng cấp tự bổ sung các trường còn thiếu của bước quy trình trước khi chuyển người xử lý cũ; nếu bước cũ chưa có loại, chế độ `Any/All` đang lưu được giữ nguyên.

Từ v2.0.14, bản dịch backend được lưu một dòng tiếng Việt theo mỗi `message_key`, đúng với khóa chính của `PA Translation`; bản dịch tiếng Anh tiếp tục được phân phát từ catalog giao diện.

Từ v2.0.15, người có quyền tạo Role trong Frappe có thể tạo Role ngay tại trang sửa quy trình. Role mới được chọn sau khi gán cho User đang hoạt động và đủ phạm vi công ty/phòng ban. Bước duyệt chung dùng hành vi duyệt hiện có và có thể đứng trước hoặc sau Báo giá; Nhận hàng vẫn ở cuối. Các phiếu đang xử lý giữ nguyên snapshot.

Từ v2.0.16, mục **Vai trò xử lý** trong nhóm Quản trị mở trang tạo Role riêng. Chọn công ty/phòng ban để kiểm tra quyền quản trị, nhập tên Role rồi tạo. Sau đó gán Role cho User trong Frappe; chỉ Role có User đang hoạt động và đủ phạm vi mới xuất hiện trong quy trình. Patch migrate thêm mục menu trên site đã cài.

v2.0.9 cho phép patch nâng cấp nhận đúng Server Script `pa_scope_query_size` mà bộ cài đã tự chuyển từ `Size` sang `ProductSize`; các chỉnh sửa tùy biến khác vẫn được bảo vệ.

Metadata được ghi trong `purchase_approval/metadata/purchase_approval.json`. Hook cài đặt chỉ thêm các bản ghi còn thiếu; migrate lần sau không ghi đè cấu hình đã chỉnh trên site. Page JavaScript/CSS, biểu tượng và bản dịch được phân phát từ app, không cần tệp trong `/files` của site nguồn.

## Chuyển site đã cài tên app cũ

Với site đã cài `purchase_approval_navigation`, hãy sao lưu database và public/private files trước khi chuyển. Đưa mã `purchase_approval` vào bench và thêm app mới vào `sites/apps.txt`, nhưng chưa chạy `install-app`. Khi site đang ở maintenance, chạy `bench --site <ten-site> execute purchase_approval.migrate_slug.execute`, tiếp theo là `bench --site <ten-site> migrate` và build assets. Lệnh chuyển cập nhật đăng ký app, Module Def, Sidebar, đường dẫn callback đã cấu hình và các tham chiếu trong Server/Client Script đã lưu; không xóa các DocType hoặc dữ liệu. Xác nhận app mới và dữ liệu trước khi bỏ package cũ khỏi bench.

URL callback mới là `/api/method/purchase_approval.outlook_action.confirm` và `/api/method/purchase_approval.gmail_action.confirm`. Cập nhật địa chỉ này ở proxy hoặc hệ thống bên ngoài trước khi bật các hành động email. Các API Server Script `pa_*` giữ nguyên tên.

Từ bản 1.1.1, cả 10 DocType Purchase Approval độc lập đều hỗ trợ Data Import bằng Excel (`.xlsx`) hoặc CSV. Role `PA Super Admin` có quyền Import, Create và Write cho các DocType này; Administrator cũng có thể import. Năm bảng con được import qua file của DocType cha. `PA Settings` là DocType Single nên chỉnh trực tiếp trong form. Khi nâng cấp site đã cài, chạy `bench --site <ten-site> migrate` để áp dụng patch một lần. Với token, lịch sử và đơn mua hàng, file import phải có đủ liên kết và dữ liệu hợp lệ; thao tác import có thể tạo bản ghi ngoài quy trình phê duyệt thông thường.

## Phát hành

Mã chuẩn nằm trong `integrations/frappe/purchase-approval` của repo FactoryManagement. Khi phát hành, xuất đúng thư mục này sang repo app, kiểm tra commit và gắn tag. `tools/package_source.py` chuyển bản export metadata đọc từ site nguồn thành JSON đã bỏ thông tin audit và dữ liệu nghiệp vụ; không commit bản export thô.
