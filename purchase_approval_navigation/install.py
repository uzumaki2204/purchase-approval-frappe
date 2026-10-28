"""Shim install hooks for purchase_approval_navigation backward compatibility.

Đảm bảo Module Def 'Purchase Approval' tồn tại trước khi after_install của
purchase_approval chạy. Frappe tạo Module Def từ modules.txt nhưng chỉ sau khi
bench migrate, không phải trong quá trình install. Vì vậy ta tạo thủ công ở đây.
"""
import frappe


def _ensure_module_def():
    """Tạo Module Def 'Purchase Approval' nếu chưa có."""
    if not frappe.db.exists("Module Def", "Purchase Approval"):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": "Purchase Approval",
            "app_name": "purchase_approval_navigation",
        }).insert(ignore_permissions=True)


def before_install():
    _ensure_module_def()
    from purchase_approval.install import before_install as _before_install
    _before_install()


def after_install():
    _ensure_module_def()
    from purchase_approval.install import after_install as _after_install
    _after_install()


def after_migrate():
    _ensure_module_def()
    from purchase_approval.install import after_migrate as _after_migrate
    _after_migrate()
