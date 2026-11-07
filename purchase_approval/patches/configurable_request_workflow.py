"""Install ordered business steps while preserving every in-flight snapshot."""

import hashlib
import json
from pathlib import Path

import frappe

from purchase_approval.install import message, metadata


HASHES = json.loads(Path(__file__).with_name("v207_script_hashes.json").read_text(encoding="utf-8"))
FIELD_DOCTYPES = (
    "PA Purchase Request",
    "PA Approval Workflow",
    "PA Approval Workflow Step",
    "PA Approval Instance Step",
)
UPDATED_TRANSLATIONS = {
    "common.auto_workflow", "error.no_workflow", "error.ambiguous", "workflow.conditions",
    "field.step_name", "field.steps", "field.approver_source", "field.approver_user",
    "field.approver_role", "common.approval_steps", "common.workflow_preview",
    "action.finalize", "status.Closed", "error.no_approver", "error.range",
}


def digest(source):
    return hashlib.sha256((source or "").encode("utf-8")).hexdigest()


def script_updates(payload):
    pending = []
    conflicts = []
    for key, doctype in (("server_scripts", "Server Script"), ("client_scripts", "Client Script")):
        targets = {row["name"]: row["script"] for row in payload[key]}
        for name, old_hash in HASHES[key].items():
            if not frappe.db.exists(doctype, name):
                continue
            current = frappe.db.get_value(doctype, name, "script") or ""
            target = targets.get(name)
            if target is None or digest(current) == digest(target):
                continue
            if digest(current) != old_hash:
                conflicts.append(f"{doctype} {name}")
            else:
                pending.append((doctype, name, target))
    if conflicts:
        frappe.throw(message("workflow_script_conflict", script=", ".join(conflicts)))
    return pending


def update_fields(payload):
    definitions = {row["name"]: row for row in payload["doctypes"]}
    for doctype in FIELD_DOCTYPES:
        doc = frappe.get_doc("DocType", doctype)
        fields = {row.fieldname: row for row in doc.fields}
        changed = False
        for source in definitions[doctype]["fields"]:
            name = source["fieldname"]
            if name not in fields:
                values = {key: value for key, value in source.items() if key not in ("doctype", "name")}
                values["idx"] = max((int(field.idx or 0) for field in doc.fields), default=0) + 1
                fields[name] = doc.append("fields", values)
                changed = True
            elif doctype == "PA Purchase Request" and name in ("status", "selection_source") and fields[name].options != source["options"]:
                fields[name].options = source["options"]
                changed = True
        if changed:
            doc.save(ignore_permissions=True)


def upgrade_workflows(payload):
    labels = {row["message_key"]: row["text"] for row in payload["translations"] if row["language"] == "vi"}
    for row in frappe.get_all("PA Approval Workflow", fields=["name"], limit_page_length=0):
        workflow = frappe.get_doc("PA Approval Workflow", row.name)
        if any(step.step_type for step in workflow.steps):
            continue
        approvals = [
            {
                "step_name": step.step_name,
                "step_type": "Quote Approval",
                "approval_method": step.approval_method,
                "approver_source": step.approver_source,
                "approver_user": step.approver_user,
                "approver_role": step.approver_role,
                "send_email": 1,
            }
            for step in sorted(workflow.steps, key=lambda step: step.step_order)
        ]
        chain = [
            {"step_name": labels["step.Stock Check"], "step_type": "Stock Check", "approval_method": "Any", "approver_source": "Role", "approver_role": "PA Stock Checker", "send_email": 0},
            {"step_name": labels["step.Purchase Handoff"], "step_type": "Purchase Handoff", "approval_method": "Any", "approver_source": "Role", "approver_role": "PA Purchasing", "send_email": 0},
            {"step_name": labels["step.Quotation"], "step_type": "Quotation", "approval_method": "Any", "approver_source": "Role", "approver_role": "PA Purchasing", "send_email": 0},
            *approvals,
            {"step_name": labels["step.Receiving"], "step_type": "Receiving", "approval_method": "Any", "approver_source": "Role", "approver_role": "PA Receiver", "send_email": 0},
        ]
        workflow.selector_source = "Role"
        workflow.selector_role = "PA Purchasing"
        workflow.notify_requester = 0
        workflow.set("steps", [])
        for index, step in enumerate(chain, 1):
            workflow.append("steps", {"step_order": index, **step})
        workflow.save(ignore_permissions=True)


def update_translations(payload):
    for source in payload["translations"]:
        name = frappe.db.exists("PA Translation", {"message_key": source["message_key"], "language": source["language"]})
        if not name:
            frappe.get_doc({"doctype": "PA Translation", **source}).insert(ignore_permissions=True)
        elif source["message_key"] in UPDATED_TRANSLATIONS:
            frappe.db.set_value("PA Translation", name, "text", source["text"], update_modified=False)


def update_sidebar(payload):
    source = payload["sidebar"]
    if not frappe.db.exists("Sidebar", source["name"]):
        return
    sidebar = frappe.get_doc("Sidebar", source["name"])
    changed = False
    anchor = next((i for i, row in enumerate(sidebar.items) if row.url == "/desk/purchase-approval?view=edit"), len(sidebar.items) - 1)
    for view in ("selection", "stock_check"):
        url = "/desk/purchase-approval?view=" + view
        if any(row.url == url for row in sidebar.items):
            continue
        values = next(row for row in source["items"] if row.get("url") == url)
        item = sidebar.append("items", {key: value for key, value in values.items() if key not in ("doctype", "name")})
        sidebar.items.remove(item)
        anchor += 1
        sidebar.items.insert(anchor, item)
        changed = True
    if changed:
        for index, item in enumerate(sidebar.items, 1):
            item.idx = index
        sidebar.save(ignore_permissions=True)


def execute():
    payload = metadata()
    pending = script_updates(payload)
    update_fields(payload)
    role = next(row for row in payload["roles"] if row["name"] == "PA Stock Checker")
    if not frappe.db.exists("Role", role["name"]):
        frappe.get_doc(role).insert(ignore_permissions=True)
    for doctype, name, source in pending:
        frappe.db.set_value(doctype, name, "script", source, update_modified=False)
    update_translations(payload)
    upgrade_workflows(payload)
    update_sidebar(payload)
    frappe.clear_cache()
