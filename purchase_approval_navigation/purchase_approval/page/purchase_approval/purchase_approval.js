/* Generated from the backed-up live Web Page and the UTF-8 catalog. */
(() => {
let lastDialogTrigger = null;
function restoreFocusBeforeDialogHide(dialog) {
  const active = document.activeElement;
  const previous = active instanceof HTMLElement && active !== document.body ? active : lastDialogTrigger;
  dialog.$wrapper.on('hide.bs.modal', () => {
    const focused = document.activeElement;
    if (!dialog.$wrapper[0].contains(focused)) return;
    focused.blur();
    if (previous instanceof HTMLElement && previous.isConnected && !dialog.$wrapper[0].contains(previous)) {
      previous.focus({preventScroll: true});
    }
  });
  dialog.$wrapper.on('hidden.bs.modal', () => {
    requestAnimationFrame(() => {
      if (previous instanceof HTMLElement && previous.isConnected && document.activeElement === document.body) {
        previous.focus({preventScroll: true});
      }
    });
  });
}
const embeddedCatalog = {"schema_version":1,"default_language":"vi","context":"purchase-approval","messages":{"vi":{"app.title":"Phê duyệt đề nghị mua hàng","unit.PCS":"Cái","unit.SET":"Bộ","unit.KG":"Kilôgam","unit.M":"Mét","unit.L":"Lít","nav.requests":"Đề nghị mua hàng","nav.workflows":"Quy trình phê duyệt","nav.create":"Tạo đề nghị","nav.dashboard":"Tổng quan","action.save":"Lưu nháp","action.submit":"Gửi đề nghị","action.finalize":"Chốt giá và gửi duyệt","action.approve":"Phê duyệt","action.quick_approve":"Phê duyệt nhanh đề nghị {name}","action.quick_receive":"Nhận hàng nhanh đề nghị {name}","action.view_request":"Xem chi tiết đề nghị {name}","action.return":"Trả sửa","action.reject":"Từ chối","action.receive":"Xác nhận nhận hàng","action.cancel":"Hủy đề nghị","action.reassign":"Thay người duyệt","action.add_line":"Thêm dòng","action.remove_line":"Xóa dòng","action.refresh":"Tải lại","action.open":"Mở đề nghị","action.pricing":"Nhập giá mua","action.previous":"Trang trước","action.next":"Trang sau","action.print_request":"In / lưu PDF","history.Create":"Tạo đề nghị","history.Save":"Lưu đề nghị","history.Submit":"Gửi đề nghị","history.Finalize":"Chốt giá","history.Approve":"Phê duyệt","history.Return":"Trả sửa","history.Reject":"Từ chối","history.Receive":"Nhận hàng","history.Cancel":"Hủy đề nghị","history.Reassign":"Thay người duyệt","common.loading":"Đang tải…","common.saved":"Đã lưu đề nghị.","common.done":"Đã hoàn tất thao tác.","common.empty":"Chưa có đề nghị trong phạm vi được cấp quyền.","common.unavailable":"Không có dữ liệu","common.auto_workflow":"Tự chọn theo giá cuối cùng","common.required":"Bắt buộc","common.filters":"Lọc đề nghị","common.all_statuses":"Tất cả trạng thái","common.workflow_preview":"Các bước phê duyệt","common.history":"Lịch sử xử lý","common.price_history":"Lịch sử báo giá","common.price_history_empty":"Chưa có lần chốt giá nào.","common.price_history_snapshot_missing":"Không có dữ liệu dòng hàng cho lần chốt này.","common.price":"Giá mua trước VAT","common.price_lines":"Giá mua theo dòng hàng","common.approval_steps":"Tuyến duyệt đã chụp","common.from":"Từ","common.to_exclusive":"đến dưới","common.onward":"trở lên","field.name":"Số đề nghị","field.company":"Công ty","field.department":"Phòng ban","field.requester":"Người đề nghị","field.requester_name":"Tên người đề nghị","field.request_date":"Ngày đề nghị","field.required_date":"Ngày cần hàng","field.purchase_type":"Loại mua","field.priority":"Mức độ ưu tiên","field.currency":"Tiền tệ","field.purpose":"Mục đích đề nghị","field.project":"Dự án","field.note":"Ghi chú","field.items":"Dòng hàng","field.product":"Sản phẩm tham khảo","field.item_code":"Mã hàng","field.item_name":"Tên hàng","field.description":"Mô tả","field.uom":"Đơn vị tính","field.quantity":"Số lượng","field.estimated_unit_price":"Đơn giá ước tính","field.has_estimated_price":"Có giá ước tính","field.estimated_vat_percent":"VAT ước tính (%)","field.estimated_amount":"Thành tiền ước tính","field.estimated_tax":"Tiền thuế ước tính","field.estimated_subtotal":"Tổng trước thuế ước tính","field.estimated_gross_total":"Tổng sau thuế ước tính","field.estimated_gross_amount":"Thành tiền sau thuế ước tính","field.delivery_date":"Ngày cần giao","field.final_unit_price_net":"Đơn giá mua trước VAT","field.final_unit_price_gross":"Đơn giá mua sau VAT","field.vat_percent":"VAT (%)","field.final_subtotal":"Tổng trước thuế","field.final_tax":"Tiền thuế","field.final_amount":"Thành tiền sau thuế","field.final_total":"Tổng sau thuế","field.estimated_total":"Tổng ước tính","field.supplier":"Nhà cung cấp","field.selected_workflow":"Quy trình được chọn","field.selection_source":"Nguồn chọn quy trình","field.status":"Trạng thái","field.revision":"Vòng duyệt","field.current_instance":"Phiên duyệt hiện tại","field.submitted_at":"Gửi lúc","field.priced_at":"Định giá lúc","field.priced_by":"Người định giá","field.received_at":"Nhận hàng lúc","field.received_by":"Người nhận","field.workflow_name":"Tên quy trình","field.amount_from":"Giá trị từ","field.amount_to":"Giá trị đến (không bao gồm)","field.has_amount_to":"Có giới hạn trên","field.is_active":"Đang hoạt động","field.steps":"Các bước duyệt","field.step_order":"Thứ tự bước","field.step_name":"Tên bước duyệt","field.approval_method":"Cách phê duyệt","field.approver_source":"Nguồn người duyệt","field.approver_user":"Người duyệt","field.approver_role":"Vai trò người duyệt","field.request":"Đề nghị","field.workflow":"Quy trình","field.workflow_version":"Phiên bản cấu hình","field.workflow_snapshot":"Cấu hình đã chụp","field.current_sequence":"Cấp đang chờ","field.completed_at":"Hoàn tất lúc","field.assignees":"Người được phân công","field.user":"Người dùng","field.acted_at":"Xử lý lúc","field.comment":"Ý kiến / lý do","field.instance":"Phiên duyệt","field.action":"Thao tác","field.actor":"Người thực hiện","field.actor_name":"Tên người thực hiện","field.old_values":"Giá trị trước","field.new_values":"Giá trị sau","field.message_key":"Khóa ngôn ngữ","field.language":"Ngôn ngữ","field.text":"Nội dung","field.unit_code":"Mã đơn vị tính","field.unit_name":"Tên đơn vị tính","field.supplier_code":"Mã nhà cung cấp","field.supplier_name":"Tên nhà cung cấp","field.companies":"Công ty được phục vụ","field.manager_user":"Trưởng phòng","field.allow_self_approval":"Cho phép tự duyệt đề nghị","field.email_enabled":"Gửi email thông báo cấp đang chờ","field.outgoing_email_account":"Tài khoản gửi email","field.mail_configuration_section":"Cấu hình gửi email","mail.default_sender_name":"Hệ thống phê duyệt","mail.sender_name":"Tên người gửi","mail.sender_email":"Địa chỉ gửi","mail.smtp_server":"Máy chủ SMTP","mail.smtp_port":"Cổng SMTP","mail.security":"Bảo mật kết nối","mail.security.STARTTLS":"STARTTLS","mail.security.SSL":"SSL/TLS","mail.security.NONE":"Không mã hóa","mail.use_authentication":"Đăng nhập máy chủ SMTP","mail.login_id":"Tên đăng nhập SMTP","mail.password":"Mật khẩu SMTP hoặc mật khẩu ứng dụng","mail.password_existing":"Để trống để giữ mật khẩu đã lưu.","mail.password_new":"Nhập mật khẩu để xác thực với máy chủ SMTP.","mail.default_note":"Tài khoản này sẽ được dùng làm địa chỉ gửi mặc định của site. Frappe kiểm tra kết nối khi có mật khẩu SMTP.","mail.loading":"Đang tải cấu hình email…","mail.save":"Lưu cấu hình email","mail.saving":"Đang lưu cấu hình…","mail.saved":"Đã lưu cấu hình gửi email.","field.recipient":"Người nhận","field.subject":"Tiêu đề","field.body":"Nội dung thông báo","field.sent_at":"Gửi lúc","field.attempts":"Số lần gửi","field.last_error":"Lỗi gửi gần nhất","field.idempotency_key":"Khóa chống tạo trùng","field.notification_key":"Khóa thông báo","status.Draft":"Nháp","status.Pending Purchasing":"Chờ mua hàng định giá","status.Pending Approval":"Chờ phê duyệt","status.Approved":"Đã duyệt","status.Closed":"Đã nhận hàng","status.Returned":"Trả sửa","status.Rejected":"Từ chối","status.Cancelled":"Đã hủy","status.Pending":"Đang chờ","status.Skipped":"Bỏ qua","status.Superseded":"Đã thay thế","type.Goods":"Hàng hóa","type.Service":"Dịch vụ","type.Asset":"Tài sản","priority.Low":"Thấp","priority.Normal":"Bình thường","priority.High":"Ưu tiên","priority.Urgent":"Khẩn cấp","source.Requester":"Người đề nghị","source.Purchasing":"Người mua hàng","source.User":"Người dùng","source.Role":"Vai trò","source.Department Manager":"Trưởng phòng (PA Manager)","mode.Any":"Một người duyệt","mode.All":"Tất cả người duyệt","error.auth":"Cần đăng nhập để thực hiện thao tác.","error.permission":"Không có quyền trong công ty hoặc phòng ban này.","error.not_found":"Không tìm thấy đề nghị trong phạm vi được cấp quyền.","error.inactive":"Công ty, phòng ban hoặc tài khoản đã ngừng hoạt động.","error.department":"Phòng ban không thuộc công ty đã chọn.","error.required":"Vui lòng nhập đủ các trường bắt buộc.","error.lines":"Đề nghị cần từ 1 đến 100 dòng hàng hợp lệ.","error.line":"Kiểm tra tên hàng, đơn vị tính, số lượng, đơn giá và VAT.","error.status":"Thao tác không phù hợp với trạng thái hiện tại.","error.conflict":"Đề nghị đã thay đổi. Vui lòng tải lại trước khi thao tác.","error.workflow":"Quy trình đã chọn không còn phù hợp.","error.no_workflow":"Chưa có quy trình phù hợp với tổng giá mua sau thuế.","error.ambiguous":"Có nhiều quy trình cùng độ ưu tiên phù hợp.","error.no_approver":"Có cấp duyệt không có người duyệt hợp lệ.","error.self":"Không được tự phê duyệt đề nghị của mình.","error.comment":"Vui lòng nhập lý do cho thao tác này.","error.supplier":"Nhà cung cấp không hoạt động hoặc không phục vụ công ty này.","error.server":"Không thể hoàn tất yêu cầu. Vui lòng thử lại sau.","error.command_only":"Thay đổi trạng thái phải qua API nghiệp vụ Purchase Approval.","error.range":"Khoảng tiền hoặc thứ tự bước duyệt không hợp lệ.","error.immutable":"Tuyến duyệt và lịch sử chỉ được cập nhật bởi API nghiệp vụ.","error.method":"Thao tác thay đổi dữ liệu yêu cầu phương thức POST.","error.email":"Không thể gửi thông báo phê duyệt; hệ thống sẽ thử lại.","error.mail_load":"Không tải được cấu hình gửi email.","error.mail_required":"Vui lòng nhập đủ thông tin người gửi và máy chủ SMTP.","error.mail_email":"Địa chỉ gửi không hợp lệ.","error.mail_transport":"Cổng hoặc chế độ bảo mật SMTP không hợp lệ.","error.mail_password":"Vui lòng nhập mật khẩu SMTP hợp lệ.","error.mail_account_missing":"Tài khoản gửi email đã cấu hình không còn tồn tại.","error.mail_account_ambiguous":"Có nhiều tài khoản gửi mặc định; vui lòng kiểm tra cấu hình Email Account.","error.mail_name_in_use":"Tên người gửi đã được một Email Account khác sử dụng.","error.mail_save":"Không lưu được cấu hình email. Vui lòng kiểm tra thông tin Microsoft Graph.","error.graph_auth":"Không xác thực được dịch vụ gửi Microsoft Graph.","error.graph_configuration":"Chưa cấu hình đầy đủ dịch vụ gửi Microsoft Graph.","error.graph_attachment_large":"Tệp PDF vượt giới hạn đính kèm của luồng gửi hiện tại.","error.graph_send":"Microsoft Graph chưa nhận email; hệ thống sẽ thử lại.","error.mail_managed":"Cấu hình gửi email đang được quản lý trong PA Settings.","error.missing_translation":"Thiếu nội dung ngôn ngữ.","error.package_pending":"Quy trình đang chờ kích hoạt Server Script.","error.scope_required":"Tài khoản cần User Permission cho công ty trước khi sử dụng.","notification.subject":"Đề nghị mua hàng cần phê duyệt","notification.body":"Có đề nghị mua hàng đang chờ bạn xử lý. Mở liên kết để xem nội dung và phê duyệt.","notification.gmail_body":"Có đề nghị mua hàng đang chờ bạn xử lý. Bấm Phê duyệt trong Gmail để duyệt ngay hoặc mở hồ sơ để xem đầy đủ.","notification.outlook_body":"Có đề nghị mua hàng đang chờ bạn xử lý. Bấm Phê duyệt trong Outlook để duyệt ngay hoặc mở hồ sơ để xem đầy đủ.","notification.approve_button":"Phê duyệt đề nghị","notification.view_button":"Xem đầy đủ đề nghị","notification.attachment_note":"Phiếu đề nghị đầy đủ được đính kèm dưới dạng PDF.","notification.confirm_note":"Nút phê duyệt mở trang xác nhận; chỉ người được phân công ở bước hiện tại mới có thể duyệt.","notification.gmail_confirm_note":"Bấm Phê duyệt trong Gmail để duyệt ngay. Chỉ người được phân công ở bước hiện tại mới có thể duyệt.","notification.outlook_confirm_note":"Bấm Phê duyệt trong Outlook để duyệt ngay. Chỉ người được phân công ở bước hiện tại mới có thể duyệt.","outlook.approved":"Đã phê duyệt đề nghị.","outlook.already_processed":"Đề nghị đã được xử lý từ email này.","outlook.unauthorized":"Không xác thực được thao tác phê duyệt từ Outlook.","outlook.invalid":"Nút phê duyệt Outlook không hợp lệ.","outlook.expired":"Nút phê duyệt trong email đã hết hạn. Vui lòng mở đề nghị trong hệ thống.","outlook.stale":"Đề nghị đã thay đổi. Vui lòng mở đề nghị trong hệ thống.","outlook.unavailable":"Chức năng phê duyệt trong Outlook chưa sẵn sàng.","mail.graph_provider":"Microsoft Graph","mail.graph_sender":"Hộp thư gửi","mail.graph_ready":"Đã cấu hình gửi qua Microsoft Graph.","mail.graph_pending":"Chưa cấu hình đầy đủ Microsoft Graph.","mail.graph_disabled":"Microsoft Graph chưa được bật; thông báo vẫn gửi qua tài khoản hiện tại.","mail.outlook_action_ready":"Nút duyệt Outlook đã được bật.","mail.outlook_action_disabled":"Nút duyệt Outlook chưa được bật.","diagnostic.outlook_precondition":"Cần sao lưu và giữ Outlook Action ở trạng thái tắt trước khi cập nhật.","diagnostic.outlook_schema_conflict":"DocType token Outlook trên site không khớp nguồn triển khai.","diagnostic.outlook_app_missing":"Ứng dụng Outlook Action chưa được cài trên Frappe.","diagnostic.outlook_script_missing":"Thiếu Server Script cần cập nhật cho Outlook Action.","diagnostic.outlook_catalog_missing":"Thiếu bản dịch Outlook Action trong gói triển khai.","diagnostic.outlook_arguments":"Tham số lệnh triển khai Outlook Action không hợp lệ.","gmail.approved":"Đã phê duyệt đề nghị.","gmail.already_processed":"Đề nghị đã được xử lý từ email này.","gmail.unauthorized":"Không xác thực được thao tác phê duyệt từ Gmail.","gmail.invalid":"Liên kết phê duyệt không hợp lệ.","gmail.expired":"Nút phê duyệt trong email đã hết hạn. Vui lòng mở đề nghị trong hệ thống.","gmail.stale":"Đề nghị đã thay đổi. Vui lòng mở đề nghị trong hệ thống.","gmail.unavailable":"Chức năng phê duyệt trong Gmail chưa sẵn sàng.","diagnostic.gmail_script_missing":"Thiếu Server Script cần sao lưu trước khi cập nhật Gmail Action.","diagnostic.gmail_precondition":"Cần có bản sao lưu và giữ Gmail Action ở trạng thái tắt trước khi cập nhật.","diagnostic.gmail_app_missing":"Ứng dụng Gmail Action chưa được cài trên Frappe.","diagnostic.gmail_schema_conflict":"DocType token trên site không khớp nguồn triển khai.","diagnostic.gmail_catalog_missing":"Thiếu bản dịch Gmail Action trong gói triển khai.","diagnostic.gmail_arguments":"Tham số lệnh triển khai Gmail Action không hợp lệ.","field.token_hash":"Mã xác thực đã băm","field.outbox":"Thông báo gửi đi","field.expected_revision":"Vòng duyệt tại lúc gửi","field.expected_modified":"Thời điểm sửa tại lúc gửi","field.expires_at":"Hết hạn lúc","field.consumed_at":"Đã sử dụng lúc","notification.approval_unavailable":"Đề nghị này không còn chờ bạn phê duyệt ở bước hiện tại.","legacy.description":"Luồng cũ được giữ để tham chiếu; đề nghị mới sử dụng module Purchase Approval.","test.failed":"Kiểm thử chưa đạt.","test.passed":"Kiểm thử đạt.","deploy.ready":"Package đã sẵn sàng kích hoạt.","deploy.pending":"Package đã cài ở trạng thái chưa công khai; cần kiểm thử và cấu hình tuyến duyệt trước khi chuyển đổi.","diagnostic.api":"Lỗi API","diagnostic.credentials":"Cần cấu hình PA_SITE, PA_API_KEY và PA_API_SECRET trong môi trường chạy.","diagnostic.scope":"Chưa có cấu hình phạm vi quyền hoặc người duyệt hoạt động.","diagnostic.existing":"Phát hiện đối tượng trùng tên ngoài package được quản lý.","diagnostic.conflict":"Đối tượng trên site đã thay đổi; không ghi đè.","diagnostic.disabled":"Server Script chưa được bật trên site.","diagnostic.activation":"Cần kết quả kiểm thử trên môi trường test trước khi công khai trang.","diagnostic.secret":"Phát hiện chuỗi thông tin xác thực trong nguồn export.","nav.purchasing":"Chờ báo giá","nav.approvals":"Chờ duyệt","nav.receiving":"Chờ nhận hàng","nav.received":"Lịch sử nhận hàng","nav.work":"Công việc","nav.procurement":"Mua hàng","nav.administration":"Quản trị","nav.desk":"Frappe Desk","nav.logout":"Đăng xuất","nav.menu":"Mở menu","nav.account":"Tài khoản","app.brand":"KIM THÀNH","app.short_name":"Purchase Approval","app.internal":"Hệ thống nội bộ","view.edit":"Tạo đề nghị","view.edit_existing":"Sửa đề nghị","view.detail":"Chi tiết đề nghị","view.pricing":"Báo giá đề nghị","metric.mine":"Đề nghị của tôi","metric.returned_mine":"Đề nghị trả sửa","metric.approvals":"Chờ tôi duyệt","metric.approved_by_me":"Tôi đã duyệt","metric.rejected_by_me":"Tôi đã từ chối","metric.purchasing":"Chờ báo giá","metric.receiving":"Chờ nhận hàng","metric.received":"Tôi đã nhận","dashboard.recent":"Đề nghị gần đây","dashboard.activity":"Hoạt động gần nhất","dashboard.company_totals":"Giá trị theo công ty","dashboard.view_all":"Xem tất cả","common.search":"Tìm mã đề nghị, mục đích, người đề nghị","common.filter":"Lọc","common.reset":"Đặt lại","common.all_companies":"Tất cả công ty","common.all_departments":"Tất cả phòng ban","common.mine":"Chỉ đề nghị của tôi","common.to":"Đến ngày","common.page":"Trang {page}/{pages} · {total} đề nghị","common.back":"Quay lại","common.close":"Đóng","common.confirm":"Xác nhận","common.cancel":"Bỏ qua","common.more":"Xem chi tiết","common.clear":"Bỏ chọn","common.no_activity":"Chưa có hoạt động trong phạm vi đã chọn.","common.no_data":"Chưa có dữ liệu.","common.unsaved":"Có thay đổi chưa lưu. Onichan muốn rời trang?","common.sort":"Sắp xếp","common.direction":"Chiều sắp xếp","common.asc":"Tăng dần","common.desc":"Giảm dần","common.all":"Tất cả","common.header":"Thông tin đề nghị","common.workflow":"Quy trình phê duyệt","common.total":"Tổng giá trị","common.subtotal":"Giá trị trước VAT","common.tax":"Tiền VAT","common.estimated_total":"Tổng dự kiến","common.request_document":"ĐỀ NGHỊ MUA HÀNG","common.new_line":"Dòng hàng","common.product_placeholder":"Nhập tên hoặc mã hàng để tìm dòng hàng đã có","common.suggestions_empty":"Không có dòng hàng phù hợp.","common.suggestions_loading":"Đang tìm dòng hàng…","common.suggestions_error":"Không thể tải gợi ý dòng hàng.","common.workflow_empty":"Chưa có quy trình phù hợp. Quản trị viên có thể cấu hình tại mục Quy trình phê duyệt trên dashboard.","common.workflow_loading":"Đang tải quy trình…","common.preview":"Giá trị xem trước","common.changed":"Đề nghị đã thay đổi. Tải lại để kiểm tra dữ liệu mới.","common.auth_required":"Đăng nhập để sử dụng Purchase Approval.","common.company_logo":"Logo Kim Thành","common.line_number":"STT","confirm.submit":"Gửi đề nghị này sang bộ phận mua hàng?","confirm.receive":"Xác nhận đã nhận hàng cho đề nghị này?","confirm.cancel":"Hủy đề nghị này?","confirm.approve":"Phê duyệt đề nghị này?","confirm.quick_approve":"Phê duyệt đề nghị {name}?","approval.quick_done":"Đã phê duyệt đề nghị {name}.","confirm.quick_receive":"Xác nhận đã nhận hàng cho đề nghị {name}?","receiving.quick_done":"Đã xác nhận nhận hàng đề nghị {name}.","confirm.return":"Trả đề nghị để người đề nghị chỉnh sửa?","confirm.reject":"Từ chối đề nghị này?","error.filters":"Bộ lọc, khoảng ngày hoặc thứ tự sắp xếp không hợp lệ.","error.decimal":"Nhập số thập phân hợp lệ, không dùng dấu phân cách hàng nghìn.","error.preview_write":"Preview không thực hiện thay đổi dữ liệu.","diagnostic.ui_backup":"Cần lưu backup trước khi triển khai giao diện.","diagnostic.ui_verified":"Giao diện và API đọc đã được đối chiếu.","preview.company":"Công ty Kim Thành","preview.department":"Phòng mua hàng","preview.person":"Nguyễn Văn An","preview.supplier":"Nhà cung cấp mẫu","preview.purpose":"Bổ sung vật tư phục vụ sản xuất","preview.item":"Vật tư sản xuất","preview.step":"Trưởng bộ phận","preview.note":"Dữ liệu minh họa, không phải đề nghị thật.","common.select":"Chọn","field.modified":"Cập nhật gần nhất","role.PA Requester":"Người đề nghị","role.PA Manager":"Quản lý","role.PA Purchasing":"Mua hàng","role.PA Approver":"Người phê duyệt","role.PA Receiver":"Người nhận hàng","role.PA Company Admin":"Quản trị công ty","role.PA Super Admin":"Quản trị hệ thống","view.workflow_edit":"Sửa quy trình phê duyệt","workflow.create":"Tạo quy trình","workflow.edit":"Chỉnh sửa","workflow.save":"Lưu quy trình","workflow.saved":"Đã lưu quy trình phê duyệt.","workflow.search":"Tìm mã hoặc tên quy trình","workflow.filters":"Lọc quy trình","workflow.conditions":"Điều kiện áp dụng","workflow.active":"Đang hoạt động","workflow.inactive":"Ngừng hoạt động","workflow.all_types":"Tất cả loại mua hàng","workflow.all_departments":"Tất cả phòng ban","workflow.empty":"Chưa có quy trình trong phạm vi đã chọn.","workflow.page":"Trang {page}/{pages} · {total} quy trình","workflow.range":"Từ {from} đến dưới {to}","workflow.range_open":"Từ {from}, không giới hạn trên","workflow.step_number":"Bước {number}","workflow.add_step":"Thêm bước duyệt","workflow.remove_step":"Xóa bước","workflow.up":"Chuyển lên","workflow.down":"Chuyển xuống","workflow.user_search":"Tìm tên hoặc tài khoản người duyệt","workflow.more_users":"Tải thêm người duyệt","workflow.no_user":"Chưa chọn người duyệt","workflow.no_users":"Không có người duyệt phù hợp với phạm vi và từ khóa.","workflow.no_roles":"Chưa có vai trò với người duyệt hợp lệ trong phạm vi này.","workflow.role_with_code":"{label} ({code})","workflow.select_scope":"Chọn công ty và phạm vi phòng ban trước khi tìm người duyệt.","workflow.manager_hint":"Người duyệt có vai trò PA Manager và cùng Company với đề nghị. Phòng ban trong User Details để trống áp dụng cho tất cả phòng ban của Company; có giá trị thì chỉ áp dụng cho phòng ban đó.","error.workflow_assignee":"Chọn người duyệt hoặc vai trò có người duyệt đang hoạt động và được cấp quyền trong phạm vi đã chọn.","error.idempotency":"Mã lưu quy trình đã được dùng cho nội dung khác hoặc không hợp lệ. Tải lại trang để tạo mã mới.","nav.view":"Màn hình","workspace.title":"Trung tâm mua hàng","shell.name":"Purchase Approval","error.catalog_load":"Chưa tải được bản dịch mới. Đang dùng bản dịch đã triển khai.","error.migration_source":"Mã live đã thay đổi. Cần đọc và sao lưu lại trước khi triển khai.","migration.stage_done":"Đã tạo trang Desk để kiểm tra.","migration.cutover_done":"Đã chuyển các đường dẫn tương thích sang trang Desk.","migration.rollback_done":"Đã khôi phục cấu hình giao diện trước triển khai.","nav.purchase_request":"Purchase Request","nav.purchase_approval":"Purchase Approval","diagnostic.navigation_changed":"Menu đã thay đổi; tải lại trang trước khi cập nhật.","diagnostic.legacy_workflow_in_use":"Mục quy trình cũ đang được sử dụng.","diagnostic.navigation_deployed":"Đã cập nhật menu Purchase Approval.","diagnostic.navigation_restored":"Đã khôi phục menu Purchase Approval.","nav.catalog":"Danh mục","nav.companies":"Công ty","nav.departments":"Phòng ban","nav.units":"Đơn vị tính","nav.suppliers":"Nhà cung cấp","nav.settings":"Thiết lập","nav.translations":"Bản dịch","nav.history":"Nhật ký phê duyệt","nav.outbox":"Thông báo chờ gửi","nav.instances":"Lượt phê duyệt","nav.master_requests":"Hồ sơ đề nghị","nav.workflow_records":"Hồ sơ quy trình","org.create_company":"Thêm công ty","org.create_department":"Thêm phòng ban","org.edit_company":"Sửa công ty","org.edit_department":"Sửa phòng ban","org.save":"Lưu thay đổi","org.saved":"Đã lưu thông tin.","org.deactivate":"Ngừng hoạt động","org.deactivated":"Đã ngừng hoạt động.","org.confirm_deactivate":"Ngừng hoạt động mục này? Đề nghị và lịch sử liên quan vẫn được giữ.","org.active":"Đang hoạt động","org.inactive":"Ngừng hoạt động","org.empty_companies":"Không có công ty phù hợp.","org.empty_departments":"Không có phòng ban phù hợp.","org.filter_company":"Lọc theo công ty","org.filter_status":"Trạng thái","org.all_statuses":"Tất cả trạng thái","org.loading":"Đang tải danh mục…","org.code_hint":"Đổi mã sẽ cập nhật các liên kết hồ sơ và quyền phân quyền.","field.company_code":"Mã công ty","field.company_name":"Tên công ty","field.short_name":"Tên viết tắt","field.tax_code":"Mã số thuế","field.phone":"Điện thoại","field.email":"Email","field.address":"Địa chỉ","field.department_code":"Mã phòng ban","field.department_name":"Tên phòng ban","field.active":"Trạng thái","error.org_code_locked":"Hãy đổi mã trong màn hình quản trị danh mục.","error.org_duplicate":"Mã đã tồn tại. Vui lòng chọn mã khác.","error.org_department_linked":"Phòng ban đã được đề nghị hoặc quy trình tham chiếu nên không thể chuyển công ty.","error.org_company_inactive":"Không thể dùng công ty đã ngừng hoạt động cho phòng ban đang hoạt động.","error.org_soft_delete":"Hãy dùng Ngừng hoạt động để giữ đề nghị và lịch sử.","org.filters":"Lọc danh mục","error.org_not_found":"Không tìm thấy công ty hoặc phòng ban trong phạm vi quản lý.","error.org_conflict":"Thông tin đã thay đổi. Vui lòng tải lại trước khi lưu.","org.create_action":"Tạo mới","outlook.header_error":"Approval failed. Open the request in the system.","field.graph_mail_enabled":"Gửi qua Microsoft Graph","field.graph_tenant_id":"Tenant ID Microsoft 365","field.graph_client_id":"App ID gửi email","field.graph_sender_mailbox":"Hộp thư gửi Graph","field.graph_certificate_thumbprint":"Thumbprint chứng thư","field.graph_private_key":"Khóa riêng chứng thư","error.graph_ids":"Tenant ID hoặc App ID không đúng định dạng.","error.graph_thumbprint":"Thumbprint chứng thư không hợp lệ.","error.graph_private_key":"Tệp khóa PEM không hợp lệ hoặc vượt quá 64 KB.","error.graph_https":"Chỉ tải khóa riêng chứng thư qua kết nối HTTPS.","error.graph_activation":"Chưa thể bật Graph: cần HTTPS, khóa chứng thư và thư viện MSAL trên máy chủ.","error.graph_managed":"Hãy thay đổi cấu hình Graph trong biểu mẫu gửi email.","mail.graph_tenant_id":"Tenant ID","mail.graph_client_id":"App ID gửi email","mail.graph_thumbprint":"Thumbprint chứng thư","mail.graph_private_key":"Tải tệp khóa riêng PEM","mail.graph_certificate_saved":"Đã lưu khóa riêng. Chọn tệp mới để thay thế.","mail.graph_certificate_missing":"Chưa lưu khóa riêng.","mail.graph_enable":"Bật gửi thông báo PA qua Microsoft Graph","mail.graph_https_notice":"Cần mở Frappe bằng HTTPS để tải khóa chứng thư và bật Graph.","mail.graph_dependency_notice":"Máy chủ chưa cài thư viện MSAL; có thể lưu thông tin nhưng chưa bật Graph.","mail.graph_channel_active":"Hộp thư Graph đang dùng","mail.graph_smtp_sender":"Hộp thư SMTP hiện tại","common.additional_items":"Dòng hàng bổ sung"}}};
let catalogPromise;
function normalizeLegacyPageUrl(){
  if(location.pathname!=='/desk/purchase-approval/purchase-approval')return;
  frappe.router.current_shell=null;
  history.replaceState(history.state,'','/desk/purchase-approval'+location.search+location.hash);
}
function loadCatalog(){
  return catalogPromise ||= fetch('/assets/purchase_approval_navigation/ui-translations.json',{credentials:'same-origin',cache:'no-cache'}).then(response=>{if(!response.ok)throw new Error(String(response.status));return response.json();}).then(value=>value.schema_version===1&&value.messages?.vi?{...embeddedCatalog,messages:{vi:{...embeddedCatalog.messages.vi,...value.messages.vi}}}:embeddedCatalog).catch(()=>embeddedCatalog);
}
function keepDeskLinksInTab(){
  window.PADeskNavigation?.sync();
}
frappe.pages['purchase-approval'].on_page_load = function(wrapper){
  normalizeLegacyPageUrl();
  keepDeskLinksInTab();
  const page=frappe.ui.make_app_page({parent:wrapper,title:embeddedCatalog.messages.vi['app.title'],single_column:true});
  const root=document.createElement('div');root.id='pa-root';root.className='pa-desk';root.setAttribute('aria-busy','true');
  const content=document.createElement('main');content.id='pa-content';content.tabIndex=-1;root.append(content);page.main.append(root);
  wrapper._paReady=loadCatalog().then(catalog=>{wrapper._paApp=createApp(page,root,catalog);return wrapper._paApp.start();});
};
frappe.pages['purchase-approval'].on_page_show = function(wrapper){
  normalizeLegacyPageUrl();
  keepDeskLinksInTab();
  wrapper._paReady?.then(()=>{wrapper._paApp?.show();});
};
function createApp(page,root,catalog){

const controlHosts=new WeakMap();
let controlId=0;
function deskNode(tag,attrs={}){
  if(['input','select','textarea'].includes(tag)){
    const host=document.createElement('div');
    const control=frappe.ui.form.make_control({parent:host,df:{fieldtype:tag==='select'?'Select':tag==='textarea'?'Small Text':attrs.type==='checkbox'?'Check':'Data',fieldname:'pa_control_'+(++controlId),label:'',options:[]},render_input:true});
    const input=control.$input[0];control.tooltip?.remove();controlHosts.set(input,control);
    if(tag==='select')input.addEventListener('change',()=>{control.df.options=[...input.options].map(option=>({value:option.value,label:option.textContent}));},true);
    return input;
  }
  const node=document.createElement(tag);
  if(tag==='button')node.className='btn btn-default btn-sm';
  return node;
}
function deskClasses(tag,value){
  const classes=value.split(/\s+/).filter(Boolean);
  if(['input','select','textarea'].includes(tag))classes.push('form-control','input-with-feedback');
  if(tag==='button'||classes.includes('pa-button'))classes.push('btn','btn-sm',classes.includes('pa-primary')?'btn-primary':'btn-default');
  if(['input','select','textarea'].includes(tag))classes.push('form-control');
  if(tag==='table')classes.push('table');
  return [...new Set(classes)].join(' ');
}
function deskField(label,input,full){
  const control=controlHosts.get(input);
  if(!control){const host=document.createElement('div');host.className='frappe-control pa-field'+(full?' pa-span-all':'');const caption=document.createElement('label');caption.className='control-label';caption.textContent=label;host.append(caption,input);return host;}
  control.df.label=label;control.df.reqd=input.required?1:0;control.set_label();control.set_mandatory(input.value);
  const wrapper=control.$wrapper[0];wrapper.classList.add('pa-field');if(full)wrapper.classList.add('pa-span-all');
  control.input_area.appendChild(input);const id='pa-desk-field-'+(++controlId);input.id=id;$(control.label_area).attr('for',id);return wrapper;
}
function deskIcon(key){
  const names={grid:'grid',file:'file',check:'check',compare:'bar-chart',bag:'shopping-bag',box:'package',wallet:'credit-card',users:'users',flow:'git-branch',clock:'clock',settings:'settings',plus:'plus',arrow:'arrow-right',search:'search',menu:'menu','chevron-down':'chevron-down',logout:'log-out',eye:'eye',edit:'edit',trash:'trash',restore:'rotate-ccw',x:'x'};
  const holder=document.createElement('span');holder.innerHTML=frappe.utils.icon(names[key]||'circle','sm');const icon=holder.firstElementChild||holder;icon.classList.add('pa-icon');icon.setAttribute('aria-hidden','true');return icon;
}
function deskHeading(page,mount){
  page._paActionObserver?.disconnect();
  const heading=mount.querySelector('.pa-heading');if(!heading)return;
  page.set_title(heading.querySelector('h1').textContent);
  const actions=[...heading.querySelectorAll('a,button')];
  const submit=[...mount.querySelectorAll('button[type="submit"].pa-primary')].find(el=>!el.closest('.pa-filters'));
  const primary=submit||actions.find(el=>el.classList.contains('pa-primary')||(el.tagName==='A'&&new URL(el.href).searchParams.get('view')==='edit'));
  if(primary){page.set_primary_action(primary.textContent,()=>primary.click());if(submit){submit.parentElement.classList.add('pa-submit-source');if(submit.parentElement.querySelector('.pa-danger'))submit.parentElement.classList.add('pa-has-danger');}const observer=new MutationObserver(()=>page.btn_primary?.prop('disabled',primary.disabled));observer.observe(primary,{attributes:true,attributeFilter:['disabled']});page._paActionObserver=observer;}
  for(const action of actions){if(action===primary)continue;const fn=()=>action.click();if(!page._paSecondary&&action===actions[0]){page.set_secondary_action(action.textContent,fn);page._paSecondary=true;}else page.add_inner_button(action.textContent,fn);}
  page._paSecondary=false;heading.hidden=true;
}
/* Catalog is injected from translations/pa-i18n.vi.json by the exporter. */
const PA = (() => {
  let context;
  const t = key => {const translated = __(key, null, catalog.context); return translated !== key ? translated : catalog.messages.vi[key] || catalog.messages.vi['common.unavailable'] || '';};
  const node = (tag, text, attrs = {}) => {
    const el = deskNode(tag,attrs);
    if(text!==undefined&&text!==null){el.textContent=String(text);if(tag==='textarea')el.value=String(text);}
    for (const [key, value] of Object.entries(attrs)) {
      if (key === 'class') el.className = deskClasses(tag, value);
      else if(key==='value'&&['input','textarea'].includes(tag)){el.value=value;el.setAttribute(key,value);}else el.setAttribute(key, value);
    }
    if(tag==='input'&&el.type==='checkbox'){el.classList.remove('form-control');el.classList.add('input-with-feedback');}return el;
  };
  const call = async (action, payload = {}) => {
    for(let attempt=0;attempt<3;attempt++) {
      try {
        const response = await frappe.call({
          method: `pa_${action}`,
          // Website RPC defaults to '/' instead of the Desk API route.
          url: `/api/method/pa_${action}`,
          type: 'POST',
          args: {payload: JSON.stringify(payload)},
          // Callers own localized error display. Desk honors silent; Website
          // needs an empty jQuery target and no automatic status-code popups.
          silent: true,
          error_msg: [],
          statusCode: {},
        });
        if (response.exc) throw new Error(t('error.server'));
        return response.message;
      } catch (error) {
        const raw=String(error.responseText||error.message||'')+String(error.responseJSON?._server_messages||error._server_messages||'')+String(error.responseJSON?.exception||error.exception||'');
        const catalog=context?.messages||catalog.messages.vi||{};
        const matched=Object.entries(catalog).find(([key,value])=>key.startsWith('error.')&&raw.includes(value));
        if(action==='create_purchase_request'&&matched?.[0]==='error.conflict'&&attempt<2){await new Promise(resolve=>setTimeout(resolve,150*(attempt+1)));continue;}
        throw new Error(matched?.[1]||t('error.server'), {cause: error});
      }
    }
  };
  const boot = async () => context ||= await call('get_context');
  const money = n => new Intl.NumberFormat('vi-VN', {minimumFractionDigits: 0, maximumFractionDigits: 2}).format(n || 0);
  const option = (value, label) => ({value,label:node('span',label).innerHTML});
  const expected = r => ({name: r.name, expected_modified: r.modified, expected_revision: r.revision || 0});
  const idempotencyKey = () => {
    // randomUUID requires a secure context; the current LAN site uses HTTP.
    if(window.crypto?.randomUUID)return window.crypto.randomUUID();
    if(!window.crypto?.getRandomValues)throw new Error(t('error.server'));
    return Array.from(window.crypto.getRandomValues(new Uint8Array(16)),n=>n.toString(16).padStart(2,'0')).join('');
  };
  const input = (type, value = '', label) => node('input', null, {type, value: value ?? '', ...(label ? {'aria-label': t(label)} : {})});
  const select = (rows, label, empty = true) => {
    const el = node('select', null, {'aria-label': t(label)});
    if (empty) el.append(node('option', t('common.unavailable'), {value: ''}));
    for (const [value, title] of rows) el.append(node('option', title, {value}));
    return el;
  };
  const table = (labels, rows) => {
    const wrap = node('div', null, {class: 'pa-table-wrap'});
    const el = node('table', null, {class: 'pa-table'});
    const head = node('tr');
    for (const key of labels) head.append(node('th', t(key), {scope: 'col'}));
    const thead = node('thead'); thead.append(head); el.append(thead);
    const tbody = node('tbody');
    for (const values of rows) {
      const tr = node('tr');
      values.forEach((value, index) => {
        const td = node('td', null, {'data-label': t(labels[index])});
        if (value instanceof Node) td.append(value); else td.textContent = value ?? '';
        tr.append(td);
      });
      tbody.append(tr);
    }
    el.append(tbody); wrap.append(el); return wrap;
  };
  const button = (key, fn, primary = false) => {
    const el = node('button', t(key), {type: 'button', class: `pa-button${primary ? ' pa-primary' : ''}`});
    el.addEventListener('click', async () => {
      lastDialogTrigger = el;
      el.disabled = true;
      try { await fn(); } catch (e) { frappe.msgprint(e.message || t('error.server')); }
      finally { el.disabled = false; if (el.isConnected && document.activeElement === document.body) el.focus({preventScroll: true}); }
    });
    return el;
  };
  const modal = (title, content, onSave) => {
    const dialog=new frappe.ui.Dialog({title:t(title),size:'large',fields:[{fieldtype:'HTML',fieldname:'body',label:'',hide_label:1}],primary_action_label:t(title),primary_action:async()=>{dialog.get_primary_btn().prop('disabled',true);try{await onSave();dialog.hide();}catch(error){frappe.msgprint(frappe.utils.escape_html(error.message||t('error.server')));}finally{dialog.get_primary_btn().prop('disabled',false);}}});
    dialog.$wrapper.addClass('pa-desk-dialog');dialog.fields_dict.body.$wrapper.find('.control-label').hide();dialog.fields_dict.body.$wrapper.find('.tooltip-content').remove();dialog.fields_dict.body.$wrapper.append(content);dialog.set_secondary_action_label(t('action.cancel'));dialog.set_secondary_action(()=>dialog.hide());
    const element=dialog.$wrapper[0];element.close=()=>dialog.hide();dialog.onhide=()=>element.dispatchEvent(new Event('close'));restoreFocusBeforeDialogHide(dialog);dialog.show();return element;
  };
  const comment = async (title, command, detail, extra = {}) => {
    const el = node('textarea', null, {'aria-label': t('field.comment'), rows: 4, maxlength: 2000});
    return new Promise(resolve => {
      const dialog = modal(title, el, async () => {
        if (['action.return', 'action.reject', 'action.cancel'].includes(title) && !el.value.trim()) throw new Error(t('error.comment'));
        const result = await call(command, {...expected(detail.request), ...extra, comment: el.value.trim()});
        resolve(result);
      });
      dialog.addEventListener('close', () => resolve(null));
    });
  };
  const pricing = async detail => {
    const ctx = await boot(); const request = detail.request;
    const body = node('div');
    const supplier = select(ctx.suppliers.filter(s=>s.companies.includes(request.company)).map(s=>[s.name,s.supplier_name]), 'field.supplier');
    body.append(node('label', t('field.supplier')), supplier);
    const controls = request.items.map(line => ({name: line.name, net: input('number', line.final_unit_price_net || '', 'field.final_unit_price_net'), vat: input('number', line.vat_percent || 0, 'field.vat_percent')}));
    for (const c of controls) {c.net.min='0';c.net.step='0.01';c.vat.min='0';c.vat.max='100';c.vat.step='0.0001';}
    body.append(table(['field.item_name','field.quantity','field.final_unit_price_net','field.vat_percent'], request.items.map((line,i)=>[line.item_name, money(line.quantity),controls[i].net,controls[i].vat])));
    const options = await call('workflow_options', {company:request.company,department:request.department,purchase_type:request.purchase_type});
    const workflow = select([['',t('common.auto_workflow')], ...options.map(w=>[w.name, `${w.workflow_name} (${money(w.amount_from)} ${w.has_amount_to ? '– < '+money(w.amount_to) : '+'})`])], 'field.selected_workflow', false);
    workflow.value = request.selected_workflow || '';
    body.append(node('label',t('field.selected_workflow')),workflow);
    return new Promise(resolve => {
      const dialog = modal('action.finalize',body, async () => {
        if (!supplier.value || controls.some(c=>c.net.value==='')) throw new Error(t('error.required'));
        const result = await call('finalize_purchase_request',{...expected(request),supplier:supplier.value, selected_workflow:workflow.value,prices:controls.map(c=>({name:c.name,unit_price:c.net.value,vat_percent:c.vat.value}))});
        resolve(result);
      }); dialog.addEventListener('close',()=>resolve(null));
    });
  };
  const reassign = async detail => {
    const current = detail.instances.find(i=>i.name===detail.request.current_instance);
    const rows = current.assignees.filter(a=>a.status==='Pending' && a.step_order===current.current_sequence);
    const content = node('div'); const from = select(rows.map(a=>[a.user,a.user]),'field.user',false);
    const to = input('email','','field.user'); const reason = node('textarea',null,{'aria-label':t('field.comment'),maxlength:2000});
    content.append(from,to,reason);
    return new Promise(resolve => {
      const dialog=modal('action.reassign',content, async()=>{
        if (!to.value || !reason.value.trim()) throw new Error(t('error.comment'));
        resolve(await call('reassign_approver',{...expected(detail.request),from_user:from.value,to_user:to.value,comment:reason.value.trim()}));
      });dialog.addEventListener('close',()=>resolve(null));
    });
  };
  const act = async (action, detail) => {
    if (action==='finalize') return pricing(detail);
    if (action==='reassign') return reassign(detail);
    if (['approve','return','reject'].includes(action)) return comment(`action.${action}`,'approval_action',detail,{action:{approve:'Approve',return:'Return',reject:'Reject'}[action]});
    if (['receive','cancel'].includes(action)) return comment(`action.${action}`,`${action}_purchase_request`,detail);
    if (action==='submit') return call('submit_purchase_request',expected(detail.request));
    return null;
  };
  const lineEditor = (mount, initial = []) => {
    const lines = structuredClone(initial);
    const render = () => {
      mount.replaceChildren(); const ctx=context;
      const rows = lines.map((line,index) => {
        const name=input('text',line.item_name,'field.item_name');name.maxLength=250;name.required=true;name.addEventListener('input',()=>line.item_name=name.value);
        const unit=select(ctx.units.map(u=>[u.name,u.unit_name]),'field.uom');unit.value=line.uom||'';unit.addEventListener('change',()=>line.uom=unit.value);
        const qty=input('number',line.quantity ?? 1,'field.quantity');qty.min='0.0001';qty.step='0.0001';qty.addEventListener('input',()=>line.quantity=qty.value);
        const price=input('number',line.has_estimated_price ? line.estimated_unit_price : '', 'field.estimated_unit_price');price.min='0';price.step='0.01';price.addEventListener('input',()=>{line.estimated_unit_price=price.value;line.has_estimated_price=price.value!==''?1:0;});
        const note=input('text',line.note,'field.note');note.addEventListener('input',()=>line.note=note.value);
        return [name,unit,qty,price,note,button('action.remove_line',()=>{lines.splice(index,1);render();})];
      });
      mount.append(table(['field.item_name','field.uom','field.quantity','field.estimated_unit_price','field.note','field.action'],rows),button('action.add_line',()=>{
        if(lines.length>=100)throw new Error(t('error.lines'));
        lines.push({item_name:'',uom:'',quantity:'1',has_estimated_price:0,estimated_vat_percent:0});render();
      }));
    }; if(!lines.length)lines.push({item_name:'',uom:'',quantity:'1',has_estimated_price:0,estimated_vat_percent:0}); render();
    return {values:()=>structuredClone(lines)};
  };
  return {t,node,call,boot,money,option,expected,idempotencyKey,input,select,table,button,modal,act,lineEditor};
})();

/* Pure routing/decimal helpers shared by the app, preview and tests. */
const PAShell = (() => {
  const views = ['dashboard','requests','edit','detail','purchasing','pricing','approvals','receiving','received','workflows','workflow-edit','organizations','organization-edit'];
  const filters = ['company','department','status','from','to','query','sort','direction','queue','page','active','kind'];
  const route = search => {
    const params = new URLSearchParams(search);
    const view = params.getAll('view').at(-1) || params.get('pa_compat') || (params.get('request') ? 'detail' : 'dashboard');
    return {view: views.includes(view) ? view : 'dashboard', request: params.get('request') || '', workflow: params.get('workflow') || '', organization: params.get('organization') || '', filters: Object.fromEntries(filters.filter(key=>params.has(key)).map(key=>[key,params.get(key)]))};
  };
  const url = (view, request='', values={}) => {
    const params = new URLSearchParams({view});
    if(request)params.set(view==='workflow-edit'?'workflow':view==='organization-edit'?'organization':'request',request);
    for(const key of filters)if(values[key]!==undefined&&values[key]!==null&&String(values[key])!=='')params.set(key,String(values[key]));
    return '/desk/purchase-approval?'+params.toString();
  };
  const scaled = (value, precision=2) => {
    const raw=String(value??'').trim();
    if(!/^\d+(?:\.\d*)?$/.test(raw)||raw.length>30)throw new Error(PA.t('error.decimal'));
    const [whole, decimal='']=raw.split('.');
    let n=BigInt(whole)*10n**BigInt(precision)+BigInt((decimal+'0'.repeat(precision)).slice(0,precision)||'0');
    if(Number(decimal[precision]||0)>=5)n++;
    return n;
  };
  const amountParts = (value, invariant=false) => {
    const raw=String(value??'').trim();
    if(!raw)return null;
    const negative=raw.startsWith('-');
    if(!/^-?[0-9.,]+$/.test(raw))return null;
    let body=raw.replace(/-/g,'');
    if(invariant&&(body.includes(',')||body.split('.').length>2)||!invariant&&body.split(',').length>2)return null;
    const separator=invariant?(body.includes('.')?'.':''):(body.includes(',')?',':'');
    let integer=body,fraction='';
    if(separator){const index=body.lastIndexOf(separator);integer=body.slice(0,index);fraction=body.slice(index+1).replace(/[.,]/g,'');}
    integer=integer.replace(/[.,]/g,'').replace(/^0+(?=\d)/,'')||'0';
    return {negative,integer,fraction,hadSeparator:Boolean(separator)};
  };
  const canonicalAmount = (value, invariant=false) => {
    const parts=amountParts(value,invariant);
    if(!parts)return '';
    const fraction=parts.fraction.replace(/0+$/,'');
    return `${parts.negative&&(parts.integer!=='0'||fraction)?'-':''}${parts.integer}${fraction?'.'+fraction:''}`;
  };
  const formatAmount = value => {
    const parts=amountParts(value,true);
    if(!parts)return '';
    const whole=parts.integer.replace(/\B(?=(\d{3})+(?!\d))/g,'.');
    return `${parts.negative&&parts.integer!=='0'?'-':''}${whole}${parts.fraction?','+parts.fraction:''}`;
  };
  const formatAmountInput = value => {
    const parts=amountParts(value,false);
    if(!parts)return String(value??'');
    const whole=parts.integer.replace(/\B(?=(\d{3})+(?!\d))/g,'.');
    return `${parts.negative&&parts.integer!=='0'?'-':''}${whole}${parts.fraction||parts.hadSeparator?','+parts.fraction:''}`;
  };
  const round = (n,d) => (n+d/2n)/d;
  const price = (quantity, unitPrice, vat) => {
    const qty=scaled(quantity,4),unit=scaled(unitPrice),rate=scaled(vat,4);
    const grossUnit=round(unit*(1000000n+rate),1000000n);
    const net=round(qty*unit,10000n),total=round(qty*grossUnit,10000n);
    return {net:Number(net)/100,tax:Number(total-net)/100,total:Number(total)/100};
  };
  const text = (key,values={}) => PA.t(key).replace(/\{(\w+)\}/g,(_,name)=>String(values[name]??''));
  const date = value => value ? String(value).slice(0,10).split('-').reverse().join('/') : PA.t('common.unavailable');
  const time = value => value ? date(value)+' '+String(value).slice(11,16) : PA.t('common.unavailable');
  const quantity = value => new Intl.NumberFormat('vi-VN',{maximumFractionDigits:4}).format(value||0);
  const queue = view => ({purchasing:'purchasing',approvals:'approvals',receiving:'receiving',received:'received'}[view]||'all');
  return {views,route,url,scaled,canonicalAmount,formatAmount,formatAmountInput,price,text,date,time,quantity,queue};
})();

/* Workflow administration in the website shell; no Desk/global styles. */
const PAWorkflows = (() => {
  const {t,node:n,call,money}=PA,S=PAShell;
  const typeLabel=value=>value?t('type.'+value):t('workflow.all_types');
  const roleLabel=value=>{const label=t('role.'+value);return label===t('common.unavailable')?value:S.text('workflow.role_with_code',{label,code:value});};
  const stateBadge=active=>n('span',t(active?'workflow.active':'workflow.inactive'),{class:'pa-badge','data-state':active?'Approved':'Skipped'});
  const range=w=>S.text(w.has_amount_to?'workflow.range':'workflow.range_open',{from:money(w.amount_from),to:money(w.amount_to)})+' '+w.currency;
  async function list(mount,H){
    const {ctx,state,field,input,select,panel,heading,link,btn,empty,go}=H,f=state.filters;
    mount.append(heading('nav.workflows',[link('workflow.create','workflow-edit','',{company:f.company,department:f.department},'pa-button pa-primary')]));
    const form=n('form',null,{class:'pa-filters'}),query=input('search',f.query||'',{maxlength:100}),company=select(ctx.companies.map(c=>[c.name,c.company_name]),f.company,'common.all_companies'),department=select(ctx.departments.filter(d=>d.company===company.value).map(d=>[d.name,d.department_name]),f.department,'common.all_departments'),active=select([['1',t('workflow.active')],['0',t('workflow.inactive')]],f.active,'common.all');
    form.append(field('workflow.search',query),field('field.company',company),field('field.department',department),field('field.is_active',active));
    company.onchange=()=>department.replaceChildren(...select(ctx.departments.filter(d=>d.company===company.value).map(d=>[d.name,d.department_name]),'','common.all_departments').children);
    const actions=n('div',null,{class:'pa-actions'}),apply=n('button',t('common.filter'),{type:'submit',class:'pa-button pa-primary'});actions.append(apply,btn('common.reset',()=>go('workflows')));form.append(actions);
    form.onsubmit=e=>{e.preventDefault();void go('workflows','',{query:query.value.trim(),company:company.value,department:department.value,active:active.value});};mount.append(panel('workflow.filters',form));
    const result=await call('list_approval_workflows',Object.fromEntries(['query','company','department','active','page'].filter(k=>f[k]!==undefined).map(k=>[k,f[k]]))),body=n('div',null,{class:'pa-workflow-cards'});
    for(const entry of result.data){const w=entry.workflow,labels=entry.labels||{},card=n('article',null,{class:'pa-panel pa-workflow-card'}),head=n('div',null,{class:'pa-panel-head'}),title=n('div');title.append(n('h2',w.workflow_name),n('div',[labels.company||w.company,labels.department||t('workflow.all_departments'),typeLabel(w.purchase_type),range(w)].join(' · '),{class:'pa-workflow-condition'}));const actions=n('div',null,{class:'pa-actions'});actions.append(stateBadge(w.is_active),link('workflow.edit','workflow-edit',w.name));head.append(title,actions);card.append(head);const route=n('ol',null,{class:'pa-workflow-preview'});for(const step of [...w.steps].sort((a,b)=>a.step_order-b.step_order)){const row=n('li'),person=step.approver_source==='User'?(labels.users?.[step.approver_user]||step.approver_user):step.approver_source==='Role'?roleLabel(step.approver_role):t('source.Department Manager');row.append(n('strong',step.step_order+'. '+step.step_name),n('span',person+' · '+t('mode.'+step.approval_method)));route.append(row);}card.append(route);body.append(card);}
    if(!result.data.length)body.append(empty('workflow.empty'));mount.append(body);
    const pages=n('div',null,{class:'pa-pagination'}),paginationActions=n('div',null,{class:'pa-actions'});pages.append(n('span',S.text('workflow.page',{page:result.page+1,pages:Math.max(1,result.total_pages),total:result.total})));if(result.page>0)paginationActions.append(btn('action.previous',()=>go('workflows','',{...f,page:result.page-1})));if(result.has_more)paginationActions.append(btn('action.next',()=>go('workflows','',{...f,page:result.page+1})));pages.append(paginationActions);mount.append(pages);
  }
  async function edit(mount,H){
    const {ctx,state,field,input,select,panel,heading,link,btn,go,toast,markDirty,markSaved,isCurrent}=H;
    const result=state.workflow?await call('get_approval_workflow',{name:state.workflow}):null,w=result?.workflow||{},labels=result?.labels?.users||{};
    mount.append(heading(result?'view.workflow_edit':'workflow.create',[link('common.back','workflows','',state.filters)]));
    const form=n('form',null,{class:'pa-workflow-form'}),error=n('div',null,{class:'pa-inline-error',role:'alert'});error.hidden=true;form.append(error);
    const grid=n('div',null,{class:'pa-panel-body pa-form-grid'}),controls={};
    controls.workflow_name=input('text',w.workflow_name||'',{required:'required',maxlength:140,name:'workflow_name'});
    controls.company=select(ctx.companies.map(c=>[c.name,c.company_name]),w.company||state.filters.company||(ctx.companies.length===1?ctx.companies[0].name:''),'common.select');controls.company.required=true;controls.company.name='company';
    controls.department=select(ctx.departments.filter(d=>d.company===controls.company.value).map(d=>[d.name,d.department_name]),w.department||state.filters.department,'workflow.all_departments');controls.department.name='department';
    controls.purchase_type=select(['Goods','Service','Asset'].map(v=>[v,t('type.'+v)]),w.purchase_type,'workflow.all_types');
    controls.amount_from=input('text',w.amount_from??'0',{required:'required',inputmode:'decimal','data-money-input':'true',name:'amount_from'});controls.amount_to=input('text',w.amount_to??'0',{inputmode:'decimal','data-money-input':'true',name:'amount_to'});
    for(const key of ['workflow_name','company','department','purchase_type','amount_from','amount_to'])grid.append(field('field.'+key,controls[key]));
    for(const key of ['has_amount_to','is_active']){controls[key]=input('checkbox');controls[key].checked=Boolean(w[key]??(key==='is_active'));controls[key].name=key;const label=n('label',null,{class:'pa-checkbox'});label.append(controls[key],n('span',t('field.'+key)));grid.append(label);}
    controls.amount_to.disabled=!controls.has_amount_to.checked;controls.has_amount_to.onchange=()=>{controls.amount_to.disabled=!controls.has_amount_to.checked;controls.amount_to.required=controls.has_amount_to.checked;};controls.has_amount_to.onchange();
    controls.note=n('textarea',w.note||'',{maxlength:2000});grid.append(field('field.note',controls.note,true));form.append(panel('workflow.conditions',grid));
    const scope=()=>({company:controls.company.value,department:controls.department.value}),steps=structuredClone(w.steps||[{step_name:'',approval_method:'Any',approver_source:'User',approver_user:'',approver_role:''}]);
    const stepBody=n('div',null,{class:'pa-panel-body'}),notice=n('p',null,{class:'pa-inline-error',role:'status'}),stepMount=n('div',null,{class:'pa-step-builder'});notice.hidden=true;stepBody.append(notice,stepMount);let options={users:[],roles:[]},scopeVersion=0,loading=false;
    const showError=err=>{notice.textContent=err.message||t('error.server');notice.hidden=false;};
    function userPicker(step){
      const box=n('div',null,{class:'pa-assignee-picker',role:'group','aria-label':t('field.approver_user')}),picked=n('div',step.approver_user?(labels[step.approver_user]||step.approver_user):t('workflow.no_user'),{class:'pa-assignee-selected'}),search=input('search','',{placeholder:t('workflow.user_search'),maxlength:100,'aria-label':t('workflow.user_search')}),status=n('div',null,{role:'status',class:'pa-sub'}),results=n('div',null,{class:'pa-assignee-results'}),more=btn('workflow.more_users',()=>load(page+1)),clear=btn('common.clear',()=>{step.approver_user='';picked.textContent=t('workflow.no_user');markDirty();});let timer,generation=0,page=0;
      more.hidden=true;const capturedScope=scopeVersion;
      async function load(next=0){
        const ticket=++generation;more.hidden=true;status.textContent=t('common.loading');
        if(!scope().company||loading){status.textContent=t('workflow.select_scope');results.replaceChildren();return;}
        try{const response=await call('workflow_assignees',{...scope(),query:search.value.trim(),page:next});if(ticket!==generation||capturedScope!==scopeVersion||!isCurrent())return;page=response.page;if(!next)results.replaceChildren();for(const user of response.users){const choice=btn('common.select',()=>{step.approver_user=user.name;labels[user.name]=user.full_name;picked.textContent=user.full_name;results.replaceChildren();more.hidden=true;status.textContent='';markDirty();});choice.textContent=user.full_name+' · '+user.name;choice.classList.add('pa-assignee-choice');results.append(choice);}more.hidden=!response.has_more;status.textContent=response.users.length?'':t('workflow.no_users');}catch(e){if(ticket===generation&&capturedScope===scopeVersion&&isCurrent())status.textContent=e.message||t('error.server');}
      }
      search.oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>void load(),250);};search.onfocus=()=>void load();box.append(picked,search,status,results,more,clear);return box;
    }
    function draw(){
      stepMount.replaceChildren();steps.forEach((step,index)=>{
        const row=n('fieldset',null,{class:'pa-step-card'}),legend=n('legend',S.text('workflow.step_number',{number:index+1})),fields=n('div',null,{class:'pa-form-grid'}),name=input('text',step.step_name,{required:'required',maxlength:140,'data-step-field':'step_name'}),method=select(['Any','All'].map(v=>[v,t('mode.'+v)]),step.approval_method),source=select(['User','Role','Department Manager'].map(v=>[v,t('source.'+v)]),step.approver_source);
        name.oninput=()=>step.step_name=name.value;method.onchange=()=>step.approval_method=method.value;source.onchange=()=>{step.approver_source=source.value;step.approver_user='';step.approver_role='';markDirty();draw();};fields.append(field('field.step_name',name),field('field.approval_method',method),field('field.approver_source',source));
        if(step.approver_source==='User')fields.append(field('field.approver_user',userPicker(step),true));
        else if(step.approver_source==='Role'){const role=select([...options.roles].sort((a,b)=>Number(!a.startsWith('PA '))-Number(!b.startsWith('PA '))||a.localeCompare(b)).map(v=>[v,roleLabel(v)]),step.approver_role,'common.select');role.required=true;role.disabled=loading;role.onchange=()=>step.approver_role=role.value;fields.append(field('field.approver_role',role));if(!options.roles.length&&!loading)fields.append(n('p',t('workflow.no_roles'),{class:'pa-sub pa-span-all'}));}
        else fields.append(n('p',t('workflow.manager_hint'),{class:'pa-sub pa-span-all'}));
        const actions=n('div',null,{class:'pa-actions'}),up=btn('workflow.up',()=>{[steps[index-1],steps[index]]=[steps[index],steps[index-1]];markDirty();draw();}),down=btn('workflow.down',()=>{[steps[index+1],steps[index]]=[steps[index],steps[index+1]];markDirty();draw();}),remove=btn('workflow.remove_step',()=>{steps.splice(index,1);markDirty();draw();});up.disabled=index===0;down.disabled=index===steps.length-1;remove.disabled=steps.length===1;actions.append(up,down,remove);row.append(legend,fields,actions);stepMount.append(row);
      });
    }
    stepBody.append(btn('workflow.add_step',()=>{if(steps.length>=30)throw new Error(t('error.range'));steps.push({step_name:'',approval_method:'Any',approver_source:'User',approver_user:'',approver_role:''});markDirty();draw();}));form.append(panel('field.steps',stepBody));
    const save=n('button',t('workflow.save'),{type:'submit',class:'pa-button pa-primary'}),actions=n('div',null,{class:'pa-actions'});actions.append(save,link('common.cancel','workflows','',state.filters));form.append(actions);let busy=false;const key=PA.idempotencyKey().replaceAll('-','');
    async function refresh(clear=false){
      const ticket=++scopeVersion;loading=true;notice.hidden=true;save.disabled=true;
      if(clear)for(const step of steps){step.approver_user='';step.approver_role='';}
      options={users:[],roles:[]};draw();
      try{if(!scope().company)throw new Error(t('workflow.select_scope'));options=await call('workflow_assignees',scope());if(ticket!==scopeVersion||!isCurrent())return;}catch(e){if(ticket===scopeVersion&&isCurrent())showError(e);}finally{if(ticket===scopeVersion&&isCurrent()){loading=false;save.disabled=false;draw();}}
    }
    controls.company.onchange=()=>{controls.department.replaceChildren(...select(ctx.departments.filter(d=>d.company===controls.company.value).map(d=>[d.name,d.department_name]),'','workflow.all_departments').children);void refresh(true);};controls.department.onchange=()=>void refresh(true);
    form.addEventListener('input',markDirty);form.addEventListener('change',markDirty);
    form.onsubmit=async e=>{e.preventDefault();if(busy||loading||!form.reportValidity())return;busy=true;save.disabled=true;error.hidden=true;try{const amountFrom=S.canonicalAmount(controls.amount_from.value),amountTo=S.canonicalAmount(controls.amount_to.value);S.scaled(amountFrom);if(controls.has_amount_to.checked)S.scaled(amountTo);if(steps.some(s=>s.approver_source==='User'&&!s.approver_user))throw new Error(t('error.workflow_assignee'));const payload={...Object.fromEntries(['workflow_name','company','department','purchase_type','note'].map(k=>[k,controls[k].value])),amount_from:amountFrom,amount_to:amountTo,currency:'VND',has_amount_to:controls.has_amount_to.checked?1:0,is_active:controls.is_active.checked?1:0,steps:steps.map((s,i)=>({...s,step_order:i+1})),...(result?{name:w.name,expected_modified:w.modified}:{idempotency_key:key})};const saved=await call('save_approval_workflow',payload);if(!isCurrent())return;markSaved();toast(t('workflow.saved'));await go('workflows','',{company:saved.workflow.company});}catch(err){if(isCurrent()){error.textContent=err.message||t('error.server');error.hidden=false;error.scrollIntoView({block:'nearest'});}}finally{busy=false;save.disabled=false;}};
    mount.append(form);await refresh();
  }
  return {list,edit};
})();

/* Company and department administration in the Purchase Approval page. */
const PAOrganizations = (() => {
  const {t,node:n,call}=PA,S=PAShell;
  const kindOf=state=>state.filters.kind==='department'?'department':'company';
  const status=active=>n('span',t(active?'org.active':'org.inactive'),{class:'pa-badge','data-state':active?'Approved':'Skipped'});
  async function list(mount,H){
    const {state,heading,link,select,field,panel,empty,go}=H,kind=kindOf(state),data=await call('list_organizations',{}),isCompany=kind==='company';
    const headingActions=[];
    if(isCompany?data.can_create_company:data.companies.some(c=>c.active))headingActions.push(link(isCompany?'org.create_company':'org.create_department','organization-edit','',{kind},'pa-button pa-primary'));
    mount.append(heading(isCompany?'nav.companies':'nav.departments',headingActions));
    const tabs=n('nav',null,{class:'pa-org-tabs','aria-label':t('nav.catalog')});
    for(const [value,key] of [['company','nav.companies'],['department','nav.departments']]){
      const a=link(key,'organizations','',{kind:value},'pa-button'+(kind===value?' pa-primary':''));
      if(kind===value)a.setAttribute('aria-current','page');
      tabs.append(a);
    }
    mount.append(tabs);
    const filters=n('form',null,{class:'pa-filters'}),company=select(data.companies.map(c=>[c.name,c.company_name]),state.filters.company,'common.all_companies'),active=select([['1',t('org.active')],['0',t('org.inactive')]],state.filters.active,'org.all_statuses');
    if(!isCompany)filters.append(field('org.filter_company',company));
    const actions=n('div',null,{class:'pa-actions'}),apply=n('button',t('common.filter'),{type:'submit',class:'pa-button pa-primary'});actions.append(apply);filters.append(field('org.filter_status',active),actions);
    filters.onsubmit=e=>{e.preventDefault();void go('organizations','',{kind,company:isCompany?'':company.value,active:active.value});};
    mount.append(panel('org.filters',filters));
    const rows=(isCompany?data.companies:data.departments).filter(row=>(isCompany||!company.value||row.company===company.value)&&(!active.value||Number(row.active)===Number(active.value)));
    const table=n('div',null,{class:'pa-table-wrap'}),grid=n('table',null,{class:'pa-table pa-table-responsive'}),head=n('tr');
    const keys=isCompany?['field.company_code','field.company_name','field.short_name','field.active','field.action']:['field.department_code','field.department_name','field.company','field.active','field.action'];
    for(const key of keys)head.append(n('th',t(key),{scope:'col'}));const thead=n('thead');thead.append(head);grid.append(thead);
    const body=n('tbody');
    for(const row of rows){
      const tr=n('tr'),values=isCompany?[row.company_code,row.company_name,row.short_name,status(row.active),link('workflow.edit','organization-edit',row.name,{kind})]:[row.department_code,row.department_name,data.companies.find(c=>c.name===row.company)?.company_name||row.company,status(row.active),link('workflow.edit','organization-edit',row.name,{kind})];
      values.forEach((value,i)=>{const td=n('td',null,{'data-label':t(keys[i])});if(value instanceof Node)td.append(value);else td.textContent=value||t('common.unavailable');tr.append(td);});body.append(tr);
    }
    grid.append(body);table.append(grid);
    const result=n('section',null,{class:'pa-panel'});result.append(rows.length?table:empty(isCompany?'org.empty_companies':'org.empty_departments'));mount.append(result);
  }
  async function edit(mount,H){
    const {state,field,input,select,panel,heading,link,go,toast,markDirty,markSaved,isCurrent}=H,kind=kindOf(state),isCompany=kind==='company';
    const data=await call('list_organizations',{}),record=state.organization?await call('get_organization',{kind,name:state.organization}):null;
    if(!record&&isCompany&&!data.can_create_company)throw new Error(t('error.permission'));
    mount.append(heading(record?(isCompany?'org.edit_company':'org.edit_department'):(isCompany?'org.create_company':'org.create_department'),[link('common.back','organizations','',{kind})]));
    const form=n('form'),error=n('div',null,{class:'pa-inline-error',role:'alert'});error.hidden=true;form.append(error);
    const grid=n('div',null,{class:'pa-panel-body pa-form-grid'}),controls={},code=isCompany?'company_code':'department_code',name=isCompany?'company_name':'department_name';
    controls[code]=input('text',record?.[code]||'',{required:'required',maxlength:50});
    grid.append(field('field.'+code,controls[code]));
    if(record)grid.append(n('p',t('org.code_hint'),{class:'pa-sub'}));
    controls[name]=input('text',record?.[name]||'',{required:'required',maxlength:140});grid.append(field('field.'+name,controls[name]));
    if(isCompany){
      for(const [key,type,max] of [['short_name','text',140],['tax_code','text',140],['phone','tel',50],['email','email',140]]){
        controls[key]=input(type,record?.[key]||'',{maxlength:max});grid.append(field('field.'+key,controls[key]));
      }
      controls.address=n('textarea',record?.address||'',{maxlength:2000});grid.append(field('field.address',controls.address,true));
    }else{
      const companies=data.companies.filter(c=>c.active||c.name===record?.company);
      controls.company=select(companies.map(c=>[c.name,c.company_name]),record?.company||state.filters.company||(companies.length===1?companies[0].name:''),'common.select');controls.company.required=true;grid.append(field('field.company',controls.company));
    }
    if(record){controls.active=select([['1',t('org.active')],['0',t('org.inactive')]],String(Number(record.active)));grid.append(field('field.active',controls.active));}
    const section=n('section',null,{class:'pa-panel'});section.append(grid);form.append(section);
    const actions=n('div',null,{class:'pa-actions'}),save=n('button',t(record?'org.save':'org.create_action'),{type:'submit',class:'pa-button pa-primary'});actions.append(save);
    if(record&&record.active){const deactivate=n('button',t('org.deactivate'),{type:'button',class:'pa-button pa-danger'});deactivate.onclick=async()=>{if(!await new Promise(resolve=>{const dialog=frappe.confirm(t('org.confirm_deactivate'),()=>resolve(true),()=>resolve(false),t('common.confirm'),t('common.cancel'));dialog.set_title(t('common.confirm'));}))return;deactivate.disabled=true;try{await call('deactivate_organization',{kind,name:record.name,expected_modified:record.modified});await H.refreshContext?.();markSaved();toast(t('org.deactivated'));await go('organizations','',{kind});}catch(e){error.textContent=e.message||t('error.server');error.hidden=false;}finally{deactivate.disabled=false;}};actions.append(deactivate);}
    actions.append(link('common.cancel','organizations','',{kind}));form.append(actions);
    form.addEventListener('input',markDirty);form.addEventListener('change',markDirty);
    form.onsubmit=async e=>{e.preventDefault();if(save.disabled||!form.reportValidity())return;save.disabled=true;error.hidden=true;try{const payload={kind,...Object.fromEntries(Object.entries(controls).map(([key,el])=>[key,el.value])),...(record?{name:record.name,expected_modified:record.modified}:{})};await call('save_organization',payload);await H.refreshContext?.();if(!isCurrent())return;markSaved();toast(t('org.saved'));await go('organizations','',{kind});}catch(err){if(isCurrent()){error.textContent=err.message||t('error.server');error.hidden=false;error.scrollIntoView({block:'nearest'});}}finally{save.disabled=false;}};
    mount.append(form);
  }
  return {list,edit};
})();


/* Purchase Approval Desk app. All dynamic content uses DOM text nodes. */
const PAApp = (() => {
  const {t,node:n,call,money,expected,idempotencyKey}=PA;
  const S=PAShell,$=selector=>selector==='#pa-root'?root:root.querySelector(selector);
  const titles={dashboard:'nav.dashboard',requests:'nav.requests',edit:'view.edit',detail:'view.detail',purchasing:'nav.purchasing',pricing:'view.pricing',approvals:'nav.approvals',receiving:'nav.receiving',received:'nav.received',workflows:'nav.workflows','workflow-edit':'view.workflow_edit',organizations:'nav.catalog','organization-edit':'nav.catalog'};
  let ctx,state,dirty=false,epoch=0,lastUrl,counts={},writing=false,started=false,active=false,renderedSearch=null,showPromise=null,activePdfUrl='';
  const icon=key=>deskIcon(key);
  const toast=(message,error=false)=>frappe.show_alert({message:frappe.utils.escape_html(message),indicator:error?'red':'green'},6);
  const btn=(key,handler,primary=false,iconKey)=>{const el=n('button',null,{type:'button',class:'pa-button'+(primary?' pa-primary':'')});if(iconKey)el.append(icon(iconKey));el.append(n('span',t(key)));el.addEventListener('click',async()=>{if(el.disabled)return;lastDialogTrigger=el;el.disabled=true;try{await handler();}catch(e){toast(e.message||t('error.server'),true);}finally{el.disabled=false;if(el.isConnected&&document.activeElement===document.body)el.focus({preventScroll:true});}});return el;};
  const iconBtn=(key,handler,iconKey)=>{const el=btn(key,handler,false,iconKey);el.classList.add('pa-table-icon');el.title=t(key);el.setAttribute('aria-label',t(key));el.querySelector('span')?.remove();return el;};
  const link=(key,view,request='',filters={},className='pa-button')=>n('a',t(key),{href:S.url(view,request,filters),class:className,'data-pa-route':'1'});
  const badge=(value,priority=false)=>n('span',t((priority?'priority.':'status.')+value),{class:'pa-badge'+(priority?' pa-priority':''),[priority?'data-priority':'data-state']:value});
  const textValue=value=>value===null||value===undefined||value===''?t('common.unavailable'):String(value);
  const input=(type,value='',attrs={})=>{
    const el=n('input',null,{type,value:value??'',...attrs});
    if(attrs['data-money-input']!==undefined){
      el.type='text';el.inputMode='decimal';el.autocomplete='off';el.value=value===''?'':S.formatAmount(value);
      el.addEventListener('input',()=>{
        const raw=el.value,caret=el.selectionStart??raw.length,formatted=S.formatAmountInput(raw),prefix=raw.slice(0,caret),decimalAt=Math.max(prefix.lastIndexOf(','),prefix.lastIndexOf('.'));
        el.value=formatted;
        if(decimalAt>=0&&prefix.includes(',')){const fractionDigits=prefix.slice(decimalAt+1).replace(/\D/g,'').length,comma=formatted.indexOf(','),position=comma<0?formatted.length:Math.min(comma+1+fractionDigits,formatted.length);el.setSelectionRange(position,position);}
        else {const digitCount=prefix.replace(/\D/g,'').length;let seen=0,position=0;for(;position<formatted.length;position++){if(/\d/.test(formatted[position]))seen++;if(seen>=digitCount&&digitCount>0){position++;break;}}el.setSelectionRange(position,position);}
      });
      el.addEventListener('blur',()=>{if(el.value.trim())el.value=S.formatAmount(S.canonicalAmount(el.value));});
    }
    return el;
  };
  const field=(key,control,full=false)=>deskField(t(key),control,full);
  const select=(rows,value='',emptyKey)=>{const el=n('select');if(emptyKey)el.append(n('option',t(emptyKey),{value:''}));for(const [v,label]of rows)el.append(n('option',label,{value:v}));el.value=value??'';return el;};
  const panel=(key,body,headAction)=>{const el=n('section',null,{class:'pa-panel'}),head=n('div',null,{class:'pa-panel-head'});if(key===titles[state?.view]&&!headAction){el.append(body);return el;}head.append(n('h2',t(key)));if(headAction)head.append(headAction);el.append(head,body);return el;};
  const empty=(key='common.empty')=>n('div',t(key),{class:'pa-empty'});
  const heading=(key,actions=[])=>{const el=n('header',null,{class:'pa-heading'}),bar=n('div',null,{class:'pa-actions'});bar.append(...actions);el.append(n('h1',t(key)),bar);return el;};
  const table=(keys,rows,{responsive=true,classes='',numeric=[]}={})=>{
    const wrap=n('div',null,{class:'pa-table-wrap'}),el=n('table',null,{class:'pa-table'+(responsive?' pa-table-responsive':'')+' '+classes}),head=n('tr');
    keys.forEach((key,index)=>head.append(n('th',t(key),{scope:'col',class:numeric.includes(index)?'pa-number':''})));const thead=n('thead');thead.append(head);el.append(thead);const tbody=n('tbody');
    for(const values of rows){const tr=n('tr');values.forEach((value,index)=>{const td=n('td',null,{'data-label':t(keys[index]),class:numeric.includes(index)?'pa-number':''});if(value instanceof Node)td.append(value);else td.textContent=textValue(value);tr.append(td);});tbody.append(tr);}el.append(tbody);wrap.append(el);return wrap;
  };
  const renderPriceHistory=entries=>{
    const wrap=n('div',null,{class:'pa-price-history'});
    if(!Array.isArray(entries)||!entries.length){wrap.append(empty('common.price_history_empty'));return wrap;}
    const displayNumber=value=>value===null||value===undefined||value===''?t('common.unavailable'):money(value);
    entries.forEach((entry,index)=>{
      const details=n('details',null,{class:'pa-price-history-entry'});details.open=index===0;
      const revision=entry.revision===null||entry.revision===undefined?t('common.unavailable'):String(entry.revision),summary=n('summary');
      summary.append(n('strong',t('field.revision')+' '+revision),n('span',t('field.priced_at')+': '+S.time(entry.finalized_at)),n('span',t('field.priced_by')+': '+(entry.actor_name||t('common.unavailable'))));details.append(summary);
      const meta=n('div',null,{class:'pa-price-history-meta'});meta.append(n('span',t('field.supplier')+': '+(entry.supplier||t('common.unavailable'))));details.append(meta);
      const items=Array.isArray(entry.items)?entry.items.filter(line=>line&&typeof line==='object'):[];
      if(items.length){
        const rows=items.map((line,lineIndex)=>{const item=n('div');item.append(n('strong',line.item_name||t('common.unavailable')));if(line.item_code)item.append(n('div',line.item_code,{class:'pa-sub'}));if(line.description)item.append(n('div',line.description,{class:'pa-sub'}));const vat=line.vat_percent===null||line.vat_percent===undefined||line.vat_percent===''?t('common.unavailable'):money(line.vat_percent)+'%';return[lineIndex+1,item,line.uom||t('common.unavailable'),displayNumber(line.quantity),displayNumber(line.final_unit_price_net),vat,displayNumber(line.final_tax),displayNumber(line.final_amount)];});
        details.append(table(['common.line_number','field.item_name','field.uom','field.quantity','field.final_unit_price_net','field.vat_percent','field.final_tax','field.final_amount'],rows,{numeric:[3,4,5,6,7],classes:'pa-price-history-table'}));
      }else details.append(empty('common.price_history_snapshot_missing'));
      wrap.append(details);
    });
    return wrap;
  };
  const companyName=name=>ctx.companies.find(c=>c.name===name)?.company_name||name;
  const departmentName=name=>ctx.departments.find(d=>d.name===name)?.department_name||name;
  const allowedView=view=>!({approvals:'approvals',purchasing:'purchasing',pricing:'purchasing',receiving:'receiving',received:'receiving',edit:'create',workflows:'administration','workflow-edit':'administration',organizations:'administration','organization-edit':'administration'}[view])||ctx.capabilities[{approvals:'approvals',purchasing:'purchasing',pricing:'purchasing',receiving:'receiving',received:'receiving',edit:'create',workflows:'administration','workflow-edit':'administration',organizations:'administration','organization-edit':'administration'}[view]];
  function navigation(){
    const views=['dashboard','requests','approvals','purchasing','receiving','received','workflows','organizations'].filter(allowedView);
    if(!page.fields_dict.pa_view)page.add_field({fieldname:'pa_view',fieldtype:'Select',label:t('nav.view'),options:views.map(value=>({value,label:t(titles[value])})),change:()=>{const next=page.fields_dict.pa_view.get_value();if(next&&next!==state?.view&&views.includes(next))void go(next);}});
    const control=page.fields_dict.pa_view;control.tooltip?.remove();control.$wrapper.addClass('pa-view-control');control.$input.attr('aria-label',t('nav.view'));control.df.options=views.map(value=>({value,label:t(titles[value])}));control.set_options();
    const current=({'edit':'requests','detail':'requests','pricing':'purchasing','workflow-edit':'workflows','organization-edit':'organizations'})[state.view]||state.view;
    control.$input.val(current);
  }
  function confirm(key,{comment=false,required=false,values={}}={}){
    return new Promise(resolve=>{
      let result=null;const dialog=new frappe.ui.Dialog({title:t('common.confirm'),fields:[{fieldtype:'HTML',fieldname:'body',label:'',hide_label:1},...(comment?[{fieldtype:'Small Text',fieldname:'comment',label:t('field.comment'),reqd:required}]:[])],primary_action_label:t('common.confirm'),primary_action:()=>{const values=dialog.get_values();if(!values)return;const reason=values.comment?.trim()||'';if(required&&!reason){frappe.msgprint(t('error.comment'));return;}result={comment:reason};dialog.hide();},onhide:()=>resolve(result)});
      dialog.$wrapper.addClass('pa-desk-dialog');dialog.fields_dict.body.$wrapper.find('.control-label').hide();dialog.fields_dict.body.$wrapper.find('.tooltip-content').remove();dialog.fields_dict.body.$wrapper.append(n('p',S.text(key,values)));dialog.set_secondary_action_label(t('common.cancel'));dialog.set_secondary_action(()=>dialog.hide());restoreFocusBeforeDialogHide(dialog);dialog.show();
    });
  }
  async function canLeave(){return !dirty||Boolean(await confirm('common.unsaved'));}
  async function go(view,request='',filters={},replace=false){if(!await canLeave())return;dirty=false;const target=new URL(S.url(view,request,filters),location.origin);frappe.route_options=Object.fromEntries(target.searchParams);if(replace)frappe.route_flags.replace_route=true;await frappe.set_route('purchase-approval');await show(true);}
  function filtersBar(current,{dashboard=false}={}){
    const form=n('form',null,{class:'pa-filters'}),controls={};
    const add=(key,type,rows,emptyKey)=>{const value=current[key]||'';const control=rows?select(rows,value,emptyKey):input(type,value,{name:key});control.name=key;controls[key]=control;const wrap=field(['query','from','to','sort','direction'].includes(key)?'common.'+(key==='query'?'search':key):'field.'+key,control);if(key==='query')wrap.classList.add('pa-search');form.append(wrap);};
    if(!dashboard)add('query','search');add('company',null,ctx.companies.map(c=>[c.name,c.company_name]),'common.all_companies');add('department',null,ctx.departments.filter(d=>!current.company||d.company===current.company).map(d=>[d.name,d.department_name]),'common.all_departments');
    add('status',null,['Draft','Pending Purchasing','Pending Approval','Approved','Closed','Returned','Rejected','Cancelled'].map(v=>[v,t('status.'+v)]),'common.all_statuses');add('from','date');add('to','date');
    controls.company.addEventListener('change',()=>controls.department.replaceChildren(...select(ctx.departments.filter(d=>!controls.company.value||d.company===controls.company.value).map(d=>[d.name,d.department_name]),'','common.all_departments').children));
    let mine;if(!dashboard){add('sort',null,['modified','request_date','name','amount'].map(v=>[v,t('field.'+(v==='amount'?'final_total':v))]));controls.sort.value=current.sort||'modified';add('direction',null,[['desc',t('common.desc')],['asc',t('common.asc')]]);controls.direction.value=current.direction||'desc';if(state.view==='requests'){const label=n('label',null,{class:'pa-checkbox'});mine=input('checkbox');mine.checked=current.queue==='mine';label.append(mine,n('span',t('common.mine')));form.append(label);}}
    const actions=n('div',null,{class:'pa-actions'}),submit=n('button',t('common.filter'),{type:'submit',class:'pa-button pa-primary'});actions.append(submit,btn('common.reset',()=>go(state.view,'',{})));form.append(actions);
    form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const values=Object.fromEntries(Object.entries(controls).map(([key,el])=>[key,el.value]));if(mine?.checked)values.queue='mine';else if(current.queue&&current.queue!=='mine')values.queue=current.queue;void go(state.view,'',values);});return form;
  }
  async function quickApprove(row){
    if(writing)return;
    writing=true;
    try{
      if(!await confirm('confirm.quick_approve',{values:{name:row.name}}))return;
      await call('approval_action',{...expected(row),action:'Approve'});
      toast(S.text('approval.quick_done',{name:row.name}));
      await render();
    }finally{writing=false;}
  }
  async function quickReceive(row){
    if(writing)return;
    writing=true;
    try{
      if(!await confirm('confirm.quick_receive',{values:{name:row.name}}))return;
      await call('receive_purchase_request',expected(row));
      toast(S.text('receiving.quick_done',{name:row.name}));
      await render();
    }finally{writing=false;}
  }
  function requestTable(rows){
    if(!rows.length)return empty(ctx.companies.length?'common.empty':'error.scope_required');
    return table(['field.name','field.purpose','field.company','field.department','field.priority','field.final_total','field.status','field.action'],rows.map(row=>{
      const code=link('common.more','detail',row.name,{},'pa-code');code.textContent=row.name;const first=n('div');first.append(code,n('div',S.date(row.request_date),{class:'pa-sub'}));const purpose=n('div');purpose.append(n('div',row.purpose,{class:'pa-table-title'}),n('div',row.requester_name,{class:'pa-sub'}));
      const actions=n('div',null,{class:'pa-row-actions'}),view=link('action.view_request','detail',row.name,{},'pa-button pa-table-icon');view.replaceChildren(icon('eye'));view.title=S.text('action.view_request',{name:row.name});view.setAttribute('aria-label',view.title);actions.append(view);
      if(state.view==='approvals'&&ctx.capabilities.approvals&&row.status==='Pending Approval'){
        const approve=btn('action.quick_approve',()=>quickApprove(row),false,'check');approve.classList.add('pa-table-icon','pa-quick-approve');approve.lastElementChild.remove();approve.title=S.text('action.quick_approve',{name:row.name});approve.setAttribute('aria-label',approve.title);actions.append(approve);
      }
      if(state.view==='receiving'&&ctx.capabilities.receiving&&row.status==='Approved'){
        const receive=iconBtn('action.quick_receive',()=>quickReceive(row),'box');receive.classList.add('pa-quick-receive');receive.title=S.text('action.quick_receive',{name:row.name});receive.setAttribute('aria-label',receive.title);actions.append(receive);
      }
      return[first,purpose,n('span',companyName(row.company),{class:'pa-company-chip'}),departmentName(row.department),badge(row.priority||'Normal',true),money(row.amount??(row.priced_at?row.final_total:row.estimated_total))+' '+(row.currency||'VND'),badge(row.status),actions];
    }),{numeric:[5]});
  }
  async function dashboard(mount){
    mount.append(heading('nav.dashboard',ctx.capabilities.create?[link('nav.create','edit')]:[]),panel('common.filters',filtersBar(state.filters,{dashboard:true})));
    const result=await call('get_dashboard',state.filters);counts=result.metrics;navigation();
    const kpis=n('div',null,{class:'pa-kpis'});
    for(const [metric,value]of Object.entries(result.metrics)){if(metric==='returned_mine')continue;const view={approvals:'approvals',purchasing:'purchasing',receiving:'receiving',received:'received'}[metric]||'requests';const values={...state.filters,...(['mine','approved_by_me','rejected_by_me'].includes(metric)?{queue:metric}:{})};const a=link('metric.'+metric,view,'',values,'pa-kpi');a.replaceChildren();a.dataset.metric=metric;const head=n('div',null,{class:'pa-kpi-head'}),glyph=n('span',null,{class:'pa-kpi-icon'});glyph.append(icon(metric==='mine'?'file':metric==='purchasing'?'bag':metric.includes('receiv')?'box':'check'));head.append(n('span',t('metric.'+metric)),glyph);a.append(head,n('div',String(value).padStart(2,'0'),{class:'pa-kpi-value'}));kpis.append(a);}mount.append(kpis);
    const columns=n('div',null,{class:'pa-dashboard-columns'}),main=n('div'),side=n('aside');main.append(panel('dashboard.recent',requestTable(result.recent),link('dashboard.view_all','requests','',state.filters,'pa-code')));
    const chart=n('div',null,{class:'pa-panel-body'}),max=Math.max(1,...result.company_totals.map(r=>r.amount));for(const row of result.company_totals){const line=n('div',null,{class:'pa-chart-row'});line.append(n('span',row.company_name,{class:'pa-company-chip'}),n('progress',null,{value:row.amount,max,'aria-label':row.company_name}),n('strong',money(row.amount)+' VND',{class:'pa-number'}));chart.append(line);}if(!result.company_totals.length)chart.append(empty('common.no_data'));main.append(panel('dashboard.company_totals',chart));
    const activity=n('div',null,{class:'pa-panel-body'});for(const h of result.activity){const row=n('div',null,{class:'pa-activity'}),body=n('div',null,{class:'pa-activity-body'});body.append(link('common.more','detail',h.request,{},'pa-code'),n('p',h.actor_name+' · '+t('history.'+h.action)),n('small',S.time(h.creation)));row.append(icon('clock'),body);activity.append(row);}if(!result.activity.length)activity.append(empty('common.no_activity'));side.append(panel('dashboard.activity',activity));columns.append(main,side);mount.append(columns);
  }
  async function list(mount){
    mount.append(heading(titles[state.view],ctx.capabilities.create&&state.view==='requests'?[link('nav.create','edit')]:[]));const values={...state.filters,queue:state.view==='requests'?(state.filters.queue||'all'):S.queue(state.view)};mount.append(panel('common.filters',filtersBar(values)));
    const result=await call('list_purchase_requests',values),body=n('div');body.append(requestTable(result.data));const pager=n('nav',null,{class:'pa-pagination','aria-label':S.text('common.page',{page:result.page+1,pages:Math.max(1,result.total_pages),total:result.total})}),actions=n('div',null,{class:'pa-actions'});pager.append(n('span',S.text('common.page',{page:result.page+1,pages:Math.max(1,result.total_pages),total:result.total})),actions);if(result.page>0)actions.append(link('action.previous',state.view,'',{...values,page:result.page-1}));if(result.has_more)actions.append(link('action.next',state.view,'',{...values,page:result.page+1}));body.append(pager);mount.append(panel(titles[state.view],body));
  }
  function routePreview(rows,value,mount){
    mount.replaceChildren();const row=rows.find(w=>w.name===value);if(!row)return;
    mount.append(n('h3',t('common.workflow_preview')));for(const step of row.steps){const el=n('div',null,{class:'pa-workflow-step'});el.append(n('strong',step.step_order+'. '+step.step_name),n('p',t('mode.'+step.approval_method)+' · '+t('source.'+step.approver_source)));mount.append(el);}
  }
  function workflowPicker(form,readScope,selected='',readTotal=()=>undefined,requireSelection=false){
    const selectEl=select([],selected,'common.auto_workflow'),wrap=field('common.workflow',selectEl,true),status=n('small',null,{role:'status','aria-live':'polite'}),preview=n('div',null,{class:'pa-workflow-preview'});wrap.append(status,preview);let rows=[],generation=0;
    async function refresh(){const current=++generation,scope=readScope();if(!scope.company||!scope.department){rows=[];selectEl.replaceChildren(n('option',t('common.auto_workflow'),{value:''}));routePreview(rows,'',preview);status.textContent='';return;}status.textContent=t('common.workflow_loading');try{const result=await call('workflow_options',{...scope,total:readTotal()});if(current!==generation)return;rows=result;const value=selectEl.value||selected;selectEl.replaceChildren(...select(rows.map(w=>[w.name,w.workflow_name]),'','common.auto_workflow').children);selectEl.value=rows.some(w=>w.name===value)?value:'';status.textContent=rows.length?'':t('common.workflow_empty');routePreview(rows,selectEl.value,preview);}catch(e){if(current===generation)status.textContent=e.message||t('error.server');}}
    selectEl.required=requireSelection;selectEl.addEventListener('change',()=>routePreview(rows,selectEl.value,preview));return {wrap,value:()=>selectEl.value,refresh};
  }
  function lineEditor(mount,initial,readScope){
    const lines=structuredClone(initial.length?initial:[{item_name:'',uom:'',quantity:'1',has_estimated_price:0,estimated_vat_percent:'0'}]);let alive=true;let generation=0,activeSuggestion=null,suggestionObserver=null;
    function closeSuggestions(){
      if(!activeSuggestion)return;
      const {name,options}=activeSuggestion;activeSuggestion=null;options.hidden=true;options.remove();name.setAttribute('aria-expanded','false');
      window.removeEventListener('resize',positionSuggestions);
      document.removeEventListener('scroll',positionSuggestions,true);
      document.removeEventListener('pointerdown',dismissSuggestions,true);
      document.removeEventListener('focusin',dismissSuggestions,true);
      suggestionObserver?.disconnect();suggestionObserver=null;
    }
    function positionSuggestions(){
      if(!activeSuggestion)return;
      const {name,options}=activeSuggestion,rect=name.getBoundingClientRect(),clip=name.closest('.pa-table-wrap')?.getBoundingClientRect();
      if(!name.isConnected||rect.bottom<=0||rect.top>=innerHeight||(clip&&(rect.right<=clip.left||rect.left>=clip.right||rect.bottom<=clip.top||rect.top>=clip.bottom))){closeSuggestions();return;}
      const width=Math.min(Math.max(rect.width,260),innerWidth-16),below=innerHeight-rect.bottom-8,above=rect.top-8,openAbove=below<160&&above>below;
      options.style.width=width+'px';options.style.left=Math.max(8,Math.min(rect.left,innerWidth-width-8))+'px';
      options.style.maxHeight=Math.min(220,Math.max(80,(openAbove?above:below)-4))+'px';
      options.style.top=openAbove?'auto':Math.round(rect.bottom+4)+'px';
      options.style.bottom=openAbove?Math.round(innerHeight-rect.top+4)+'px':'auto';
    }
    function dismissSuggestions(event){
      if(activeSuggestion&&!activeSuggestion.name.contains(event.target)&&!activeSuggestion.options.contains(event.target))closeSuggestions();
    }
    function showSuggestions(name,options){
      closeSuggestions();activeSuggestion={name,options};document.body.append(options);options.hidden=false;name.setAttribute('aria-expanded','true');
      window.addEventListener('resize',positionSuggestions);
      document.addEventListener('scroll',positionSuggestions,true);
      document.addEventListener('pointerdown',dismissSuggestions,true);
      document.addEventListener('focusin',dismissSuggestions,true);
      suggestionObserver=new MutationObserver(()=>{if(!name.isConnected)closeSuggestions();});suggestionObserver.observe(root,{childList:true,subtree:true});
      positionSuggestions();
    }
    function render(){generation++;closeSuggestions();mount.replaceChildren();const estimates=[];const rows=lines.map((line,index)=>{
      const valueInput=(key,type='text',extra={})=>{const el=input(type,line[key]??'',{class:'pa-line-input','aria-label':t('field.'+key),...extra});el.addEventListener('input',()=>{line[key]=extra['data-money-input']?S.canonicalAmount(el.value):el.value;dirty=true;});return el;};
      const code=valueInput('item_code','text',{maxlength:140});code.addEventListener('input',()=>line.product='');const name=valueInput('item_name','text',{class:'pa-line-input pa-wide',required:'required',maxlength:250,placeholder:t('common.product_placeholder'),'aria-autocomplete':'list','aria-expanded':'false'});const suggestion=n('div',null,{class:'pa-suggestion'}),options=n('ul',null,{class:'pa-suggestions pa-suggestion-portal',role:'listbox',id:'pa-suggestions-'+index}),status=n('div',null,{class:'pa-suggestion-status',role:'status','aria-live':'polite'});options.hidden=true;name.setAttribute('aria-controls',options.id);suggestion.append(name,status);let timer,queryVersion=0;
      name.addEventListener('input',()=>{line.product='';clearTimeout(timer);const version=++queryVersion,renderVersion=generation;closeSuggestions();status.textContent='';if(name.value.trim().length<2)return;timer=setTimeout(async()=>{const scope=readScope();if(!scope.company||!scope.department)return;status.textContent=t('common.suggestions_loading');try{const matches=await call('item_suggestions',{...scope,query:name.value.trim()});if(!alive||version!==queryVersion||renderVersion!==generation||!name.isConnected)return;options.replaceChildren();for(const match of matches){const li=n('li',null,{role:'option'}),label=match.product_code?match.product_code+' \u00b7 '+match.product_name:match.product_name,choose=n('button',label,{type:'button'});choose.addEventListener('click',()=>{queryVersion++;line.product=match.name||'';line.item_code=match.product_code||'';line.item_name=match.product_name;name.value=line.item_name;code.value=line.item_code;if(match.source==='history'){line.description=match.description||'';description.value=line.description;if(match.uom&&[...unit.options].some(option=>option.value===match.uom)){line.uom=match.uom;unit.value=match.uom;}}closeSuggestions();status.textContent='';dirty=true;name.focus();});li.append(choose);options.append(li);}if(matches.length)showSuggestions(name,options);else closeSuggestions();status.textContent=matches.length?'':t('common.suggestions_empty');}catch(e){if(alive&&version===queryVersion)status.textContent=t('common.suggestions_error');}},250);});
      name.addEventListener('keydown',e=>{if(e.key==='ArrowDown'&&!options.hidden){e.preventDefault();options.querySelector('button')?.focus();}if(e.key==='Escape')closeSuggestions();});options.addEventListener('keydown',e=>{const buttons=[...options.querySelectorAll('button')],at=buttons.indexOf(document.activeElement);if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();buttons[(at+(e.key==='ArrowDown'?1:-1)+buttons.length)%buttons.length]?.focus();}if(e.key==='Escape'){closeSuggestions();name.focus();}});
      const unit=select(ctx.units.map(u=>[u.name,u.unit_name]),line.uom,'common.select');unit.classList.add('pa-line-input');unit.required=true;unit.setAttribute('aria-label',t('field.uom'));unit.addEventListener('change',()=>{line.uom=unit.value;dirty=true;});const qty=valueInput('quantity','number',{min:'0.0001',step:'0.0001',required:'required'});const price=valueInput('estimated_unit_price','text',{inputmode:'decimal','data-money-input':'true'});price.value=line.has_estimated_price?S.formatAmount(line.estimated_unit_price):'';price.addEventListener('input',()=>{line.estimated_unit_price=S.canonicalAmount(price.value);line.has_estimated_price=price.value.trim()!==''?1:0;});const vat=valueInput('estimated_vat_percent','text',{inputmode:'decimal'});const tax=n('span',t('common.unavailable')),gross=n('span',t('common.unavailable'));estimates.push({line,tax,gross});for(const control of [qty,price,vat])control.addEventListener('input',updateEstimates);
      const description=valueInput('description','text',{maxlength:2000});return [code,suggestion,description,qty,unit,price,vat,tax,gross,valueInput('delivery_date','date'),valueInput('note','text',{maxlength:2000}),iconBtn('action.remove_line',()=>{lines.splice(index,1);dirty=true;render();},'trash')];
    });mount.append(table(['field.item_code','field.item_name','field.description','field.quantity','field.uom','field.estimated_unit_price','field.estimated_vat_percent','field.estimated_tax','field.estimated_gross_amount','field.delivery_date','field.note','field.action'],rows,{classes:'pa-line-table',numeric:[3,5,6,7,8]}));const total=n('strong','0 VND');const totalPanel=n('div',null,{class:'pa-total'});totalPanel.append(n('span',t('field.estimated_total')),total);mount.append(totalPanel);function updateEstimates(){let totalCents=0;for(const {line,tax,gross}of estimates){try{if(!line.has_estimated_price)throw new Error();const amount=S.price(line.quantity,line.estimated_unit_price,line.estimated_vat_percent||'0');tax.textContent=money(amount.tax);gross.textContent=money(amount.total);totalCents+=Math.round(amount.total*100);}catch{tax.textContent=t('common.unavailable');gross.textContent=t('common.unavailable');}}total.textContent=money(totalCents/100)+' VND';}updateEstimates();const bar=n('div',null,{class:'pa-panel-body'});bar.append(btn('action.add_line',()=>{if(lines.length>=100)throw new Error(t('error.lines'));lines.push({item_name:'',uom:'',quantity:'1',has_estimated_price:0,estimated_vat_percent:'0'});dirty=true;render();},false,'plus'));mount.append(bar);}
    render();return {values:()=>{if(!lines.length)throw new Error(t('error.lines'));for(const l of lines){S.scaled(l.quantity,4);if(l.has_estimated_price)S.scaled(l.estimated_unit_price);S.scaled(l.estimated_vat_percent||'0',4);}return structuredClone(lines);},clearProducts:()=>{generation++;closeSuggestions();for(const line of lines)line.product='';mount.querySelectorAll('[aria-expanded]').forEach(el=>el.setAttribute('aria-expanded','false'));mount.querySelectorAll('.pa-suggestion-status').forEach(el=>el.textContent='');},dispose:()=>{alive=false;generation++;closeSuggestions();}};
  }
  async function edit(mount){
    const result=state.request?await call('get_purchase_request',{name:state.request}):null;if(result&&!result.actions.includes('save'))throw new Error(t('error.permission'));const r=result?.request||{};
    mount.append(heading(result?'view.edit_existing':'view.edit',[link('common.back',result?'detail':'requests',r.name||'')]));const form=n('form'),error=n('div',null,{class:'pa-inline-error',role:'alert'});error.hidden=true;form.append(error);const grid=n('div',null,{class:'pa-panel-body pa-form-grid'}),controls={};
    controls.company=select(ctx.companies.map(c=>[c.name,c.company_name]),r.company||(ctx.companies.length===1?ctx.companies[0].name:''),'common.select');controls.department=select(ctx.departments.filter(d=>d.company===controls.company.value).map(d=>[d.name,d.department_name]),r.department,'common.select');controls.priority=select(['Low','Normal','High','Urgent'].map(v=>[v,t('priority.'+v)]),r.priority||'Normal');controls.request_date=input('date',r.request_date||ctx.today||new Date().toISOString().slice(0,10));controls.required_date=input('date',r.required_date||'');controls.purchase_type=select(['Goods','Service','Asset'].map(v=>[v,t('type.'+v)]),r.purchase_type||'Goods');
    for(const key of ['company','department','priority','request_date','required_date','purchase_type']){controls[key].required=true;grid.append(field('field.'+key,controls[key]));}if(result){controls.company.disabled=true;controls.department.disabled=true;}
    const scope=()=>({company:controls.company.value,department:controls.department.value,purchase_type:controls.purchase_type.value});const picker=workflowPicker(form,scope,r.selected_workflow);grid.append(picker.wrap);
    for(const key of ['project','purpose','note']){const el=key==='note'?n('textarea',r[key]||''):input('text',r[key]||'');el.maxLength={project:140,purpose:500,note:4000}[key];if(key==='purpose')el.required=true;controls[key]=el;grid.append(field('field.'+key,el,true));}
    form.append(panel('common.header',grid));const lines=n('div');const editor=lineEditor(lines,r.items||[],scope);form.append(panel('field.items',lines));
    controls.company.addEventListener('change',()=>{controls.department.replaceChildren(...select(ctx.departments.filter(d=>d.company===controls.company.value).map(d=>[d.name,d.department_name]),'','common.select').children);editor.clearProducts();void picker.refresh();});controls.department.addEventListener('change',()=>{editor.clearProducts();void picker.refresh();});controls.purchase_type.addEventListener('change',()=>void picker.refresh());form.addEventListener('input',()=>dirty=true);form.addEventListener('change',()=>dirty=true);
    const actions=n('div',null,{class:'pa-actions'}),save=n('button',t('action.save'),{type:'submit',class:'pa-button pa-primary'});actions.append(save);form.append(actions);const key=idempotencyKey();let busy=false;
    form.addEventListener('submit',async e=>{e.preventDefault();if(busy||!form.reportValidity())return;busy=true;save.disabled=true;error.hidden=true;try{const payload={...Object.fromEntries(Object.entries(controls).map(([name,el])=>[name,el.value])),currency:'VND',selected_workflow:picker.value(),items:editor.values(),...(result?expected(r):{idempotency_key:key})};const saved=await call(result?'save_purchase_request':'create_purchase_request',payload);dirty=false;editor.dispose();toast(t('common.saved'));await go('detail',saved.request.name);}catch(err){error.textContent=err.message||t('error.server');error.hidden=false;error.scrollIntoView({block:'nearest'});}finally{busy=false;save.disabled=false;}});
    mount.append(form);await picker.refresh();
  }
  async function command(action,result,comment=''){
    if(writing)return;
    if(!result.actions.includes(action))throw new Error(t('error.permission'));
    if(['return','reject'].includes(action)&&!comment.trim())throw new Error(t('error.comment'));
    writing=true;
    try{
    const confirmation=await confirm('confirm.'+action,{comment:['receive','cancel'].includes(action),required:action==='cancel'});if(!confirmation)return;
    const payload={...expected(result.request),comment:comment||confirmation.comment};let next;
    if(['approve','return','reject'].includes(action)){if(action!=='approve'&&!comment.trim())throw new Error(t('error.comment'));next=await call('approval_action',{...payload,action:{approve:'Approve',return:'Return',reject:'Reject'}[action]});}
    else next=await call(action+'_purchase_request',payload);
    dirty=false;toast(t('common.done'));await go('detail',next.request.name,{},true);
    }finally{writing=false;}
  }
  async function detail(mount){
    if(!state.request)throw new Error(t('error.not_found'));const result=await call('get_purchase_request',{name:state.request}),r=result.request,labels=result.labels||{};const download=btn('action.print_request',()=>{if(!activePdfUrl)return;const anchor=document.createElement('a');anchor.href=activePdfUrl;anchor.download=r.name+'.pdf';document.body.append(anchor);anchor.click();anchor.remove();});download.disabled=true;const actions=[link('common.back','requests'),download];
    if(result.actions.includes('save'))actions.push(link('view.edit_existing','edit',r.name));if(result.actions.includes('submit'))actions.push(btn('action.submit',()=>command('submit',result),true));if(result.actions.includes('finalize'))actions.push(link('action.pricing','pricing',r.name));if(result.actions.includes('receive'))actions.push(btn('action.receive',()=>command('receive',result),true));if(result.actions.includes('cancel'))actions.push(btn('action.cancel',()=>command('cancel',result)));if(result.actions.includes('reassign'))actions.push(btn('action.reassign',async()=>{const next=await PA.act('reassign',result);if(next){toast(t('common.done'));await go('detail',r.name,{},true);}}));
    const head=heading('view.detail',actions);head.querySelector('h1').textContent=r.name;mount.append(head);
    if(result.actions.includes('approve')){const body=n('div',null,{class:'pa-panel-body'}),reason=n('textarea',null,{maxlength:2000});body.append(field('field.comment',reason));const bar=n('div',null,{class:'pa-actions'});for(const action of ['approve','return','reject'])if(result.actions.includes(action)){const button=btn('action.'+action,()=>command(action,result,reason.value),action==='approve');if(action==='reject')button.classList.add('pa-danger');bar.append(button);}body.append(bar);const decision=panel('nav.approvals',body);decision.classList.add('pa-decision');mount.append(decision);}
    const columns=n('div',null,{class:'pa-doc-body'}),main=n('div',null,{class:'pa-doc-main'}),paper=n('article',null,{class:'pa-doc-paper'}),pdfViewer=n('section',null,{class:'pa-pdf-viewer'}),pdfStatus=n('div',t('common.loading'),{class:'pa-pdf-loading',role:'status'}),pdfFrame=n('iframe',null,{class:'pa-pdf-frame',title:t('common.request_document')});pdfFrame.hidden=true;pdfViewer.append(pdfStatus,pdfFrame);const docHead=n('div',null,{class:'pa-doc-head'}),code=n('div',null,{class:'pa-doc-meta'});code.append(n('div',r.name,{class:'pa-doc-name'}),n('div',S.date(r.request_date),{class:'pa-sub'}),badge(r.status));if(labels.company_logo){const logo=n('img',null,{class:'pa-doc-company-logo',src:new URL(labels.company_logo,window.location.origin).href,alt:t('common.company_logo')});logo.addEventListener('error',()=>logo.remove(),{once:true});docHead.append(logo);}docHead.append(n('h2',t('common.request_document')),code);paper.append(docHead);const info=n('dl',null,{class:'pa-doc-info'});
    for(const [key,value,full]of [['field.company',labels.company||companyName(r.company)],['field.department',labels.department||departmentName(r.department)],['field.requester',r.requester_name],['field.required_date',S.date(r.required_date)],['field.purchase_type',t('type.'+r.purchase_type)],['field.priority',t('priority.'+(r.priority||'Normal'))],['field.project',r.project],['field.supplier',labels.supplier||r.supplier],['field.purpose',r.purpose,true],['field.note',r.note,true]]){const cell=n('div',null,{class:full?'pa-span-all':''});if(key==='field.priority')cell.classList.add('pa-doc-priority');cell.append(n('dt',t(key)),n('dd',textValue(value)));info.append(cell);}paper.append(info);
    const priced=Boolean(r.priced_at),lineFields=priced?['common.line_number','field.item_name','field.uom','field.quantity','field.final_unit_price_net','field.vat_percent','field.final_tax','field.final_amount']:['common.line_number','field.item_name','field.uom','field.quantity','field.estimated_unit_price','field.estimated_vat_percent','field.estimated_gross_amount'];
    const lineRows=r.items.map((line,index)=>{const item=n('div');item.append(n('strong',line.item_name),n('div',[line.item_code,line.description,line.note,line.delivery_date?S.date(line.delivery_date):''].filter(Boolean).join(' · '),{class:'pa-sub'}));if(priced)return[index+1,item,line.uom,S.quantity(line.quantity),money(line.final_unit_price_net),S.quantity(line.vat_percent)+'%',money(line.final_tax),money(line.final_amount)];const estimated=Number(line.has_estimated_price)===1;return[index+1,item,line.uom,S.quantity(line.quantity),estimated?money(line.estimated_unit_price):t('common.unavailable'),S.quantity(line.estimated_vat_percent)+'%',estimated?money(line.estimated_amount):t('common.unavailable')];});
    const invoiceTable=table(lineFields,lineRows,{responsive:false,numeric:priced?[3,4,5,6,7]:[3,4,5,6]});invoiceTable.querySelector('.pa-table')?.classList.add('pa-invoice-table',priced?'pa-invoice-priced':'pa-invoice-estimate');paper.append(invoiceTable);
    const summary=n('div',null,{class:'pa-doc-summary'}),summaryRow=(key,value,grand=false)=>{const row=n('div',null,{class:'pa-doc-summary-row'+(grand?' pa-grand-total':'')});row.append(n('span',t(key)),n('strong',value));return row;};
    if(priced)summary.append(summaryRow('field.final_subtotal',money(r.final_subtotal)+' '+r.currency),summaryRow('field.final_tax',money(r.final_tax)+' '+r.currency));
    summary.append(summaryRow(priced?'field.final_total':'field.estimated_total',money(priced?r.final_total:r.estimated_total)+' '+r.currency,true));paper.append(summary);paper.hidden=true;main.append(pdfViewer,paper);
    const pdfEpoch=epoch;void(async()=>{try{const response=await fetch('/api/method/pa_get_purchase_request_pdf',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8','X-Frappe-CSRF-Token':frappe.csrf_token||''},body:new URLSearchParams({payload:JSON.stringify({name:r.name})})});if(!response.ok||!(response.headers.get('content-type')||'').toLowerCase().includes('application/pdf'))throw new Error(t('error.server'));const blob=await response.blob();if(pdfEpoch!==epoch)return;activePdfUrl=URL.createObjectURL(blob);pdfFrame.src=activePdfUrl;pdfFrame.hidden=false;pdfStatus.hidden=true;download.disabled=false;}catch(e){if(pdfEpoch!==epoch)return;pdfStatus.textContent=t('error.server');pdfStatus.classList.add('pa-pdf-error');}})();
    main.append(panel('common.price_history',renderPriceHistory(result.price_history)));
    main.append(panel('common.history',result.history.length?table(['field.acted_at','field.action','field.actor_name','field.comment'],result.history.map(h=>[S.time(h.creation),t('history.'+h.action),h.actor_name,h.comment])):empty('common.no_activity')));
    const routeBody=n('div',null,{class:'pa-panel-body'});for(const instance of result.instances){routeBody.append(n('h3',t('field.revision')+' '+instance.revision));for(const step of instance.steps){const row=n('div',null,{class:'pa-workflow-step','data-state':step.status});row.append(n('strong',step.step_order+'. '+step.step_name),badge(step.status),n('p',t('mode.'+step.approval_method)));for(const assigned of instance.assignees.filter(a=>a.step_order===step.step_order)){const person=n('p');person.append(n('span',labels.users?.[assigned.user]||assigned.user),n('span',' · '+t('status.'+assigned.status)));row.append(person);}routeBody.append(row);}}if(!result.instances.length)routeBody.append(empty('common.no_data'));const route=panel('common.approval_steps',routeBody);route.classList.add('pa-route-panel');columns.append(main,route);mount.append(columns);
    return result.actions.includes('approve') ? r : null;
  }
  function additionalPriceEditor(mount,scope,originalCount,onChange){
    const lines=[],body=mount.querySelector('tbody'),bar=n('div',null,{class:'pa-line-add-bar'});let generation=0,alive=true;
    mount.after(bar);
    function render(){
      generation++;body.querySelectorAll('.pa-added-item').forEach(row=>row.remove());
      lines.forEach((line,index)=>{
        const row=n('tr',null,{class:'pa-added-item'});
        const value=(key,type='text',attributes={})=>{const el=input(type,line[key]??'',{...attributes,'aria-label':t(key==='unit_price'?'field.final_unit_price_net':'field.'+key)});el.addEventListener('input',()=>{line[key]=attributes['data-money-input']?S.canonicalAmount(el.value):el.value;dirty=true;onChange();});return el;};
        const code=value('item_code','text',{maxlength:140});code.addEventListener('input',()=>{line.product='';line.product_label='';});
        const name=value('item_name','text',{required:'required',maxlength:250,placeholder:t('common.product_placeholder'),'aria-autocomplete':'list','aria-expanded':'false'}),suggestion=n('div',null,{class:'pa-suggestion'}),options=n('ul',null,{class:'pa-suggestions',role:'listbox'}),status=n('div',null,{class:'pa-suggestion-status',role:'status','aria-live':'polite'});options.hidden=true;suggestion.append(name,options,status);let timer,queryVersion=0;
        name.addEventListener('input',()=>{line.product='';line.product_label='';clearTimeout(timer);const version=++queryVersion,renderVersion=generation;options.hidden=true;name.setAttribute('aria-expanded','false');status.textContent='';if(name.value.trim().length<2)return;timer=setTimeout(async()=>{try{const matches=await call('item_suggestions',{...scope(),query:name.value.trim()});if(!alive||version!==queryVersion||renderVersion!==generation||!name.isConnected)return;options.replaceChildren();for(const match of matches){const option=n('li',null,{role:'option'}),choose=n('button',match.product_code?match.product_code+' · '+match.product_name:match.product_name,{type:'button'});choose.addEventListener('click',()=>{queryVersion++;line.product=match.name||'';line.product_label=match.name?(match.product_code?match.product_code+' · '+match.product_name:match.product_name):'';line.item_code=match.product_code||'';line.item_name=match.product_name;code.value=line.item_code;name.value=line.item_name;if(match.source==='history'){line.description=match.description||'';description.value=line.description;if(match.uom&&[...unit.options].some(item=>item.value===match.uom)){line.uom=match.uom;unit.value=line.uom;}}options.hidden=true;name.setAttribute('aria-expanded','false');status.textContent='';dirty=true;name.focus();});option.append(choose);options.append(option);}options.hidden=!matches.length;name.setAttribute('aria-expanded',String(Boolean(matches.length)));status.textContent=matches.length?'':t('common.suggestions_empty');}catch(e){if(alive&&version===queryVersion)status.textContent=t('common.suggestions_error');}},250);});
        name.addEventListener('keydown',e=>{if(e.key==='Escape'){options.hidden=true;name.setAttribute('aria-expanded','false');}if(e.key==='ArrowDown'&&!options.hidden){e.preventDefault();options.querySelector('button')?.focus();}});
        const description=value('description','text',{maxlength:2000}),unit=select(ctx.units.map(u=>[u.name,u.unit_name]),line.uom,'common.select');unit.required=true;unit.setAttribute('aria-label',t('field.uom'));unit.addEventListener('change',()=>{line.uom=unit.value;dirty=true;onChange();});
        const qty=value('quantity','number',{required:'required',min:'0.0001',step:'0.0001'}),net=value('unit_price','text',{required:'required',inputmode:'decimal','data-money-input':'true'}),vat=value('vat_percent','text',{required:'required',inputmode:'decimal'}),tax=n('span',t('common.unavailable')),amount=n('span',t('common.unavailable'));
        line.controls={qty,net,vat,tax,amount};
        const cells=[['field.item_code',code],['field.item_name',suggestion],['field.description',description],['field.uom',unit],['field.quantity',qty],['field.delivery_date',value('delivery_date','date')],['field.note',value('note','text',{maxlength:2000})],['field.estimated_unit_price',t('common.unavailable')],['field.estimated_vat_percent',t('common.unavailable')],['field.final_unit_price_net',net],['field.vat_percent',vat],['field.final_tax',tax],['field.final_amount',amount]];
        for(const [key,element] of cells){const cell=n('td',null,{'data-label':t(key)});if(element instanceof Node)cell.append(element);else cell.textContent=element;row.append(cell);}
        const action=n('td',null,{'data-label':t('action.remove_line')});action.append(btn('action.remove_line',()=>{lines.splice(index,1);dirty=true;render();onChange();},false,'trash'));row.append(action);body.append(row);
      });
      const add=btn('action.add_line',()=>{lines.push({product:'',item_code:'',item_name:'',description:'',uom:'',quantity:'1',delivery_date:'',note:'',unit_price:'',vat_percent:'0'});dirty=true;render();onChange();},false,'plus');add.disabled=originalCount()+lines.length>=100;bar.replaceChildren(add);
    }
    render();return {entries:()=>lines,values:()=>lines.map(line=>({product:line.product,item_code:line.item_code,item_name:line.item_name,description:line.description,uom:line.uom,quantity:line.quantity,delivery_date:line.delivery_date,note:line.note,unit_price:S.canonicalAmount(line.controls.net.value),vat_percent:line.controls.vat.value})),refresh:render,dispose:()=>{alive=false;generation++;}};
  }
  async function pricing(mount){
    if(!state.request)throw new Error(t('error.not_found'));const result=await call('get_purchase_request',{name:state.request});if(!result.actions.includes('finalize'))throw new Error(t('error.permission'));const r=result.request;mount.append(heading('view.pricing',[link('common.back','detail',r.name)]));const form=n('form'),error=n('div',null,{class:'pa-inline-error',role:'alert'});error.hidden=true;form.append(error);
    const info=n('div',null,{class:'pa-panel-body'});info.append(n('strong',r.name),n('p',r.purpose),badge(r.status));form.append(panel('common.header',info));const supplier=select(ctx.suppliers.filter(s=>s.companies.includes(r.company)).map(s=>[s.name,s.supplier_name]),r.supplier,'common.select');supplier.required=true;const supplierBody=n('div',null,{class:'pa-panel-body'});supplierBody.append(field('field.supplier',supplier));form.append(panel('field.supplier',supplierBody));
    const total=n('strong'),controls=r.items.map(line=>({name:line.name,quantity:line.quantity,net:input('text',r.priced_at?line.final_unit_price_net:(line.has_estimated_price?line.estimated_unit_price:''),{class:'pa-line-input',required:'required',inputmode:'decimal','data-money-input':'true','aria-label':t('field.final_unit_price_net')}),vat:input('text',r.priced_at?(line.vat_percent??'0'):(line.estimated_vat_percent??'0'),{class:'pa-line-input',required:'required',inputmode:'decimal','aria-label':t('field.vat_percent')}),tax:n('span',t('common.unavailable')),amount:n('span',t('common.unavailable'))}));
    const removedItems=[],priceFields=['field.item_code','field.item_name','field.description','field.uom','field.quantity','field.delivery_date','field.note','field.estimated_unit_price','field.estimated_vat_percent','field.final_unit_price_net','field.vat_percent','field.final_tax','field.final_amount','action.remove_line'];
    const priceTable=table(priceFields,r.items.map((line,index)=>{const c=controls[index],blank=()=>n('span');const remove=btn('action.remove_line',()=>{const position=controls.findIndex(control=>control.name===line.name);if(position<0)return;controls.splice(position,1);removedItems.push(line.name);remove.closest('tr')?.remove();dirty=true;added.refresh();update();},false,'trash');return[line.item_code||blank(),line.item_name,line.description||blank(),line.uom,S.quantity(line.quantity),line.delivery_date?S.date(line.delivery_date):blank(),line.note||blank(),line.has_estimated_price?money(line.estimated_unit_price):t('common.unavailable'),S.quantity(line.estimated_vat_percent)+'%',c.net,c.vat,c.tax,c.amount,remove];}),{responsive:false,classes:'pa-price-table',numeric:[4,7,8,9,10,11,12]});
    const lines=n('div');lines.append(priceTable);const added=additionalPriceEditor(priceTable,()=>({company:r.company,department:r.department,purchase_type:r.purchase_type}),()=>controls.length,()=>update());const totalBar=n('div',null,{class:'pa-total'});totalBar.append(n('span',t('common.preview')),total);lines.append(totalBar);form.append(panel('field.items',lines));
    form.append(panel('common.price_history',renderPriceHistory(result.price_history)));
    let previewTotal;const picker=workflowPicker(form,()=>({company:r.company,department:r.department,purchase_type:r.purchase_type}),r.selected_workflow,()=>previewTotal,Boolean(r.selected_workflow));const workflowBody=n('div',null,{class:'pa-panel-body'});workflowBody.append(picker.wrap);form.append(panel('common.workflow',workflowBody));let refreshTimer;
    function update(){let sum=0,valid=controls.length+added.entries().length>0;for(const c of [...controls,...added.entries().map(line=>({quantity:line.controls.qty.value,net:line.controls.net,vat:line.controls.vat,tax:line.controls.tax,amount:line.controls.amount}))]){try{if(!String(c.net.value).trim()||!String(c.vat.value).trim())throw new Error(t('error.line'));const amount=S.price(c.quantity,S.canonicalAmount(c.net.value),c.vat.value);if(Number(c.vat.value)>100)throw new Error(t('error.line'));c.tax.textContent=money(amount.tax);c.amount.textContent=money(amount.total);sum+=amount.total;}catch(e){valid=false;c.tax.textContent=t('common.unavailable');c.amount.textContent=t('common.unavailable');}}previewTotal=valid?Math.round(sum*100)/100:undefined;total.textContent=valid?money(previewTotal)+' '+r.currency:t('common.unavailable');clearTimeout(refreshTimer);refreshTimer=setTimeout(()=>void picker.refresh(),300);}
    for(const c of controls)for(const el of [c.net,c.vat])el.addEventListener('input',update);form.addEventListener('input',()=>dirty=true);form.addEventListener('change',()=>dirty=true);const actions=n('div',null,{class:'pa-actions'}),save=n('button',t('action.finalize'),{type:'submit',class:'pa-button pa-primary'});actions.append(save);form.append(actions);let busy=false;
    form.addEventListener('submit',async e=>{e.preventDefault();if(busy||!form.reportValidity())return;busy=true;save.disabled=true;error.hidden=true;try{for(const c of controls){S.scaled(S.canonicalAmount(c.net.value));S.scaled(c.vat.value,4);}const next=await call('finalize_purchase_request',{...expected(r),supplier:supplier.value,selected_workflow:picker.value(),prices:controls.map(c=>({name:c.name,unit_price:S.canonicalAmount(c.net.value),vat_percent:c.vat.value})),removed_items:removedItems,additional_items:added.values()});dirty=false;added.dispose();clearTimeout(refreshTimer);toast(t('common.done'));await go('detail',next.request.name);}catch(e){error.textContent=e.message||t('error.server');error.hidden=false;error.scrollIntoView({block:'nearest'});}finally{busy=false;save.disabled=false;}});mount.append(form);update();await picker.refresh();
  }
  async function render(){
    const current=++epoch;state=S.route(location.search);if(activePdfUrl){URL.revokeObjectURL(activePdfUrl);activePdfUrl='';}navigation();page.set_title(t(titles[state.view]));page.clear_primary_action();page.clear_secondary_action();page.clear_custom_actions();page.clear_menu();let approvalIntentRow=null;const mount=n('div');$('#pa-content').replaceChildren(n('p',t('common.loading'),{role:'status'}));$('#pa-root').setAttribute('aria-busy','true');
    try{if(!allowedView(state.view))throw new Error(t('error.permission'));if(['workflows','workflow-edit'].includes(state.view))await PAWorkflows[state.view==='workflows'?'list':'edit'](mount,{ctx,state,field,input,select,panel,heading,link,btn,empty,go,toast,markDirty:()=>dirty=true,markSaved:()=>dirty=false,isCurrent:()=>current===epoch});else if(['organizations','organization-edit'].includes(state.view))await PAOrganizations[state.view==='organizations'?'list':'edit'](mount,{ctx,state,field,input,select,panel,heading,link,btn,empty,go,toast,markDirty:()=>dirty=true,markSaved:()=>dirty=false,isCurrent:()=>current===epoch,refreshContext:async()=>{ctx=await call('get_context');}});else if(state.view==='dashboard')await dashboard(mount);else if(state.view==='edit')await edit(mount);else if(state.view==='detail')approvalIntentRow=await detail(mount);else if(state.view==='pricing')await pricing(mount);else await list(mount);if(current!==epoch)return;$('#pa-content').replaceChildren(mount);deskHeading(page,mount);if(!ctx.companies.length&&!['organizations','organization-edit'].includes(state.view))mount.prepend(n('div',t('error.scope_required'),{class:'pa-inline-error'}));document.title=t(titles[state.view])+' · '+t('app.short_name');$('#pa-content').focus({preventScroll:true});if(state.view==='detail'&&new URLSearchParams(location.search).get('intent')==='approve'){const url=new URL(location.href);url.searchParams.delete('intent');history.replaceState(history.state,'',url.pathname+url.search+url.hash);renderedSearch=location.search;lastUrl=location.pathname+location.search;if(approvalIntentRow)void quickApprove(approvalIntentRow).catch(error=>frappe.msgprint(error.message||t('error.server')));else frappe.show_alert({message:t('notification.approval_unavailable'),indicator:'orange'});}}catch(e){if(current===epoch){const error=n('div',e.message||t('error.server'),{class:'pa-inline-error',role:'alert'});$('#pa-content').replaceChildren(error,btn('action.refresh',()=>render()),link('common.back','dashboard'));}}finally{if(current===epoch)$('#pa-root').setAttribute('aria-busy','false');}
  }
  async function show(force=false){
    if(!started)return;
    active=true;const search=location.search;
    if(!force&&renderedSearch===search)return showPromise;
    renderedSearch=search;lastUrl=location.pathname+location.search;
    showPromise=render();await showPromise;
  }
  async function leave(){
    if(!await canLeave()){frappe.route_flags.replace_route=true;frappe.route_options=Object.fromEntries(new URL(lastUrl,location.origin).searchParams);await frappe.set_route('purchase-approval');return false;}
    active=false;dirty=false;epoch++;return true;
  }
  async function start(){
    if(started)return show();
    try{ctx=await PA.boot();}catch(e){$('#pa-content').replaceChildren(n('div',e.message||t('error.server'),{class:'pa-inline-error',role:'alert'}),btn('action.refresh',start));root.setAttribute('aria-busy','false');return;}
    window.PADeskNavigation?.setContext(ctx);
    started=true;
    root.addEventListener('click',e=>{const a=e.target.closest('a[data-pa-route]');if(!a||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button>0)return;e.preventDefault();e.stopPropagation();const next=S.route(new URL(a.href,location.href).search);void go(next.view,next.workflow||next.organization||next.request,next.filters);});
    document.addEventListener('click',async e=>{if(!active||!dirty||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button>0)return;const a=e.target.closest('a[href]');if(!a||root.contains(a))return;const target=new URL(a.href,location.href);if(target.origin!==location.origin||!/^\/(app|desk)(\/|$)/.test(target.pathname))return;e.preventDefault();e.stopImmediatePropagation();if(await canLeave()){dirty=false;await frappe.set_route(target.pathname+target.search);}},true);
    window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
    frappe.router.on('change',()=>{if(frappe.get_route()[0]==='purchase-approval')void show();else if(active)void leave();});
    await show(true);
  }
  return {start,show,leave};
})();
return PAApp;

}
})();

