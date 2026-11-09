"""Track which Frappe Roles belong to Purchase Approval."""

import frappe

from purchase_approval.install import metadata


REGISTRY = "PA Workflow Role"


def registered_names():
    return {
        row.role
        for row in frappe.get_all(REGISTRY, fields=["role"], limit_page_length=0)
        if row.role
    }


def register(role_name):
    if not role_name or frappe.db.exists(REGISTRY, role_name):
        return
    try:
        frappe.get_doc({"doctype": REGISTRY, "role": role_name}).insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        if not frappe.db.exists(REGISTRY, role_name):
            raise


def backfill():
    names = {item["name"] for item in metadata()["roles"]}
    if frappe.db.exists("DocType", "PA Approval Workflow"):
        names.update(
            row.selector_role
            for row in frappe.get_all(
                "PA Approval Workflow", fields=["selector_role"], limit_page_length=0
            )
            if row.selector_role
        )
    if frappe.db.exists("DocType", "PA Approval Workflow Step"):
        names.update(
            row.approver_role
            for row in frappe.get_all(
                "PA Approval Workflow Step",
                filters={"parenttype": "PA Approval Workflow"},
                fields=["approver_role"],
                limit_page_length=0,
            )
            if row.approver_role
        )
    names.update(
        row.name
        for row in frappe.get_all(
            "Role", filters={"name": ["like", "PA %"]}, fields=["name"], limit_page_length=0
        )
    )
    for name in sorted(names):
        if frappe.db.exists("Role", name):
            register(name)
