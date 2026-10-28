# Shim module for "Purchase Approval" module under purchase_approval_navigation app.
# Frappe sync.py gọi frappe.get_module("purchase_approval_navigation.purchase_approval")
# để tìm thư mục chứa DocType JSON. File này đảm bảo __file__ hợp lệ (không None).
# DocType thực sự được cài từ metadata/purchase_approval.json trong install.py.
