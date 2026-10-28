# Gửi và duyệt đề nghị trong Outlook

Tại **PA Settings**, PA Super Admin nhập tenant ID, app ID, hộp thư gửi, thumbprint và tải khóa riêng PEM để cấu hình gửi thông báo Purchase Approval qua Microsoft Graph. Cờ Graph nằm trong PA Settings; cờ `pa_outlook_actions_enabled` vẫn nằm trên máy chủ để phát hành nút duyệt trong Outlook. Cả hai mặc định tắt. Gmail Action không còn được tạo trong email. Đường mở hồ sơ và duyệt bằng phiên đăng nhập vẫn có trong email.

## Microsoft 365 cần chuẩn bị

1. Dùng một mailbox Exchange Online cố định làm sender. Tạo ứng dụng Entra ID dành riêng cho gửi mail, cấp quyền ứng dụng `Mail.Send`, quản trị viên cấp consent và giới hạn quyền vào mailbox đó bằng Exchange Application RBAC. Tải chứng thư công khai lên ứng dụng. Khóa riêng PEM được tải qua PA Settings trên kết nối HTTPS và Frappe mã hóa trong `__Auth`; giá trị không được trả về giao diện. Sao lưu `encryption_key` của site cùng dữ liệu để còn giải mã sau khi phục hồi.
2. Tạo ứng dụng Entra ID thứ hai, một tenant, cho callback Outlook. Expose API với `Application ID URI`, đặt `requestedAccessTokenVersion` là 2 và preauthorize Microsoft Actions app `48af08dc-f6d2-435f-b2a7-069abd99c086` cho scope API. Đăng ký provider tại Actionable Email Developer Dashboard với sender, target domain HTTPS và ứng dụng Entra này. Bắt đầu bằng phạm vi Test Users, sau đó Organization.
3. Công khai callback bằng hostname DNS và TLS hợp lệ. Callback là `https://<host>/api/method/purchase_approval.outlook_action.confirm`. Proxy chỉ cho POST đến endpoint; chuyển header `Action-Authorization` sang `X-PA-Outlook-Authorization`, xóa `Authorization` trước khi đến Frappe. Giữ query/body và Host gốc.
4. Cài module app và các dependency từ `pyproject.toml` trong backend và worker. Cài DocType `PA Outlook Approval Token`, các Server Script, Client Script và catalog mới bằng `deploy-outlook.py` sau khi sao lưu.

Ví dụ cấu hình reverse proxy cho callback:

```nginx
location = /api/method/purchase_approval.outlook_action.confirm {
    limit_except POST { deny all; }
    access_log off;
    proxy_set_header X-PA-Outlook-Authorization $http_action_authorization;
    proxy_set_header Authorization "";
    proxy_set_header Host $host;
    proxy_pass http://frappe_backend;
}
```

Graph được cấu hình trong PA Settings; khi chưa có HTTPS hoặc backend/worker chưa cài `msal`, có thể lưu metadata nhưng không thể tải khóa riêng hoặc bật Graph. SMTP tiếp tục hoạt động khi Graph tắt. Site config cho Outlook Action cần các giá trị sau; chỉ bật sau khi provider được Microsoft cho phép và người dùng thử nhìn thấy card:

```json
{
  "pa_outlook_actions_enabled": false,
  "pa_outlook_callback_url": "https://approval.example.com/api/method/purchase_approval.outlook_action.confirm",
  "pa_outlook_registered_sender": "approval@example.com",
  "pa_outlook_originator": "<provider-guid>",
  "pa_outlook_tenant_id": "<tenant-guid>",
  "pa_outlook_app_id_uri": "api://<application-id-uri>"
}
```

`pa_outlook_registered_sender` phải khớp hộp thư Graph đã lưu trong PA Settings. Không ghi token, private key, thông tin Graph HTTP hoặc nội dung PDF vào log. Nếu public HTTPS/đăng ký Microsoft chưa sẵn sàng, giữ `pa_outlook_actions_enabled=false`. Cấu hình Graph cũ trong site config vẫn được đọc để hỗ trợ chuyển tiếp; bỏ các khóa cũ sau khi đã lưu qua PA Settings.

## Phát hành và kiểm tra

- Sao lưu script, catalog, Client Script và app hiện tại. Stage mã và DocType khi cả hai cờ tắt; kiểm tra chức năng duyệt từ Desk và đường callback sai xác thực không duyệt.
- Gửi thử qua Graph tới mailbox Microsoft 365 được chỉ định; xác nhận HTML, PDF, logo, liên kết chi tiết và `PA Notification Outbox` đổi sang `Sent` sau HTTP 202. Graph 202 nghĩa Microsoft nhận yêu cầu gửi, không xác nhận đã phát tới hộp thư.
- Gửi email Actionable Message trực tiếp tới Test Users; xác nhận nút hiển thị trong Outlook và một lần bấm tạo một bản ghi audit đúng người. Kiểm tra token giả/hết hạn/lặp, sai tenant/audience/người duyệt, hồ sơ đổi vòng hoặc bước.
- Sau khi nhóm thử nghiệm đạt, đăng ký phạm vi Organization và bật cờ trên site. Muốn quay lui, tắt cờ, khôi phục script/catalog/app từ bản sao lưu. Bảng token Gmail và Outlook không cần xóa.

Graph `sendMail` với quyền `Mail.Send` hiện chỉ gửi PDF đính kèm dưới 3 MB qua một yêu cầu JSON. PDF lớn hơn giữ outbox ở trạng thái cần xử lý; hỗ trợ upload session sẽ đòi thêm quyền `Mail.ReadWrite` cho mailbox sender. Xem [Graph sendMail](https://learn.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0), [large attachments](https://learn.microsoft.com/en-us/graph/outlook-large-attachments), [Actionable Messages](https://learn.microsoft.com/en-us/outlook/actionable-messages/get-started), [Entra token](https://learn.microsoft.com/en-us/outlook/actionable-messages/enable-entra-token-for-actionable-messages) và [dashboard](https://learn.microsoft.com/en-us/outlook/actionable-messages/email-dev-dashboard).
