"""Add multi-user workflow assignees and preserve existing approval snapshots."""

import hashlib

import frappe

from purchase_approval.install import message, metadata


CHILD_DOCTYPE = "PA Approval Workflow Assignee"
PARENT_DOCTYPE = "PA Approval Workflow"
OWNED_MODULES = ("Purchase Approval", "Purchase Approval (Custom)")
OLD_SERVER_SCRIPT_SHA256 = {
    "pa_get_approval_workflow": "fd4013feced51bc523780a4dd91f4788487a62c1df20cb02ed5be96c43ff6af4",
    "pa_save_approval_workflow": "309a34f5a2fe472090e75423fcb369cc2663e320eaa3211482fb50a261c85d3d",
    "pa_receive_purchase_request": "b70f72d073eb750d9e9bb70ca87042b906e02de37e3a085b12d801304f877de8",
}
UPDATED_TRANSLATIONS = {
    "action.confirm_handoff",
    "confirm.confirm_handoff",
    "history.Purchase Handoff",
    "field.approver_users",
    "workflow.remove_assignee",
}


def digest(source):
    return hashlib.sha256((source or "").encode("utf-8")).hexdigest()


def ensure_child_doctype(payload):
    definition = next(row for row in payload["doctypes"] if row["name"] == CHILD_DOCTYPE)
    if frappe.db.exists("DocType", CHILD_DOCTYPE):
        module = frappe.db.get_value("DocType", CHILD_DOCTYPE, "module")
        if module not in OWNED_MODULES:
            frappe.throw(message("doctype_exists", doctype=CHILD_DOCTYPE))
        doc = frappe.get_doc("DocType", CHILD_DOCTYPE)
    else:
        doc = frappe.get_doc(
            {
                "doctype": "DocType",
                "name": CHILD_DOCTYPE,
                "module": "Purchase Approval",
                "custom": 1,
                "istable": 1,
                "issingle": 0,
                "fields": [],
                "permissions": [],
            }
        )
        doc.insert(ignore_permissions=True)

    changed = False
    fields = {row.fieldname: row for row in doc.fields}
    if not fields:
        doc.update({key: value for key, value in definition.items() if key not in ("doctype", "name")})
        changed = True
    else:
        for source in definition["fields"]:
            if source["fieldname"] in fields:
                continue
            values = {key: value for key, value in source.items() if key not in ("doctype", "name")}
            values["idx"] = max((int(row.idx or 0) for row in doc.fields), default=0) + 1
            doc.append("fields", values)
            changed = True
    if changed:
        doc.save(ignore_permissions=True)


def ensure_parent_field(payload):
    definition = next(row for row in payload["doctypes"] if row["name"] == PARENT_DOCTYPE)
    doc = frappe.get_doc("DocType", PARENT_DOCTYPE)
    existing = {row.fieldname for row in doc.fields}
    source = next(row for row in definition["fields"] if row["fieldname"] == "assignees")
    if "assignees" in existing:
        return
    values = {key: value for key, value in source.items() if key not in ("doctype", "name")}
    values["idx"] = max((int(row.idx or 0) for row in doc.fields), default=0) + 1
    doc.append("fields", values)
    doc.save(ignore_permissions=True)


def backfill_workflows():
    for row in frappe.get_all("PA Approval Workflow", fields=["name"], limit_page_length=0):
        workflow = frappe.get_doc("PA Approval Workflow", row.name)
        changed = False
        for step in workflow.steps:
            if step.step_type == "Quotation" and step.approval_method != "Any":
                step.approval_method = "Any"
                changed = True
            elif step.step_type != "Quote Approval" and step.approval_method != "Any":
                step.approval_method = "Any"
                changed = True
            elif step.step_type == "Quote Approval" and step.approval_method not in ("Any", "All"):
                step.approval_method = "Any"
                changed = True
            if step.approver_source == "User" and step.approver_user:
                current = {assigned.user for assigned in workflow.assignees if assigned.step_order == step.step_order}
                if step.approver_user not in current:
                    workflow.append("assignees", {"step_order": step.step_order, "user": step.approver_user})
                    changed = True
        if changed:
            workflow.save(ignore_permissions=True)


def update_server_scripts(payload):
    targets = {row["name"]: row["script"] for row in payload["server_scripts"]}
    pending = []
    conflicts = []
    for name, old_hash in OLD_SERVER_SCRIPT_SHA256.items():
        if not frappe.db.exists("Server Script", name):
            continue
        current = frappe.db.get_value("Server Script", name, "script") or ""
        target = targets[name]
        current_hash = digest(current)
        if current_hash == digest(target):
            continue
        if current_hash != old_hash:
            conflicts.append(f"Server Script {name}")
        else:
            pending.append((name, target))
    if conflicts:
        frappe.throw(message("workflow_script_conflict", script=", ".join(conflicts)))
    for name, source in pending:
        frappe.db.set_value("Server Script", name, "script", source, update_modified=False)


def update_translations(payload):
    for source in payload["translations"]:
        if source["message_key"] not in UPDATED_TRANSLATIONS:
            continue
        filters = {"message_key": source["message_key"], "language": source["language"]}
        name = frappe.db.exists("PA Translation", filters)
        if not name:
            frappe.get_doc({"doctype": "PA Translation", **source}).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("PA Translation", name, "text", source["text"], update_modified=False)


def execute():
    payload = metadata()
    update_server_scripts(payload)
    ensure_child_doctype(payload)
    ensure_parent_field(payload)
    backfill_workflows()
    update_translations(payload)
    frappe.clear_cache()
