# Backward-compatibility shim for Frappe hooks.
# Frappe's get_attr() kiểm tra phần đầu của dotted path phải là app đã cài.
# App được cài với tên "purchase_approval_navigation", nên tất cả hook paths
# phải bắt đầu bằng "purchase_approval_navigation.*" thay vì "purchase_approval.*".
# Các module thực tế vẫn chạy từ purchase_approval package thông qua shim files.
import json
from pathlib import Path

# Load catalog từ purchase_approval package thực
_root = Path(__file__).parent.parent / "purchase_approval"
_catalog = json.loads((_root / "ui-translations.json").read_text(encoding="utf-8"))

app_name = "purchase_approval_navigation"
app_title = _catalog["messages"]["nav.purchase_approval"]
app_publisher = "Onichan"
app_description = _catalog["messages"]["app.title"]
app_email = ""
app_license = "Proprietary"
app_logo_url = "/assets/purchase_approval/images/purchase-approval-desk-icon.svg"

add_to_apps_screen = [{
    "name": app_name,
    "title": app_title,
    "logo": app_logo_url,
    "route": "/desk/purchase-approval/trung-t\u00e2m-mua-h\u00e0ng",
    "sequence_id": 40,
    # Dùng shim path để Frappe không báo AppNotInstalledError
    "has_permission": "purchase_approval_navigation.access.can_open",
}]

app_include_js = ["/assets/purchase_approval/js/desk-navigation.js"]
app_include_css = ["/assets/purchase_approval/css/desk-navigation.css"]

# Hook paths trỏ vào shim install.py (đã có _ensure_module_def + forward)
before_install = "purchase_approval_navigation.install.before_install"
after_install = "purchase_approval_navigation.install.after_install"
after_migrate = "purchase_approval_navigation.install.after_migrate"
