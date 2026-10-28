"""Install read-only source metadata as independently owned Purchase Approval docs."""

import json
from pathlib import Path

import frappe


ROOT = Path(__file__).parent
METADATA = ROOT / "metadata" / "purchase_approval.json"
MESSAGES = ROOT / "install-messages.json"
EXTERNAL_DOCTYPES = ("Company", "Department", "Product", "User", "Role")


def message(key, **values):
    catalog = json.loads(MESSAGES.read_text(encoding="utf-8"))
    language = (getattr(frappe.local, "lang", None) or "vi").split("-")[0]
    template = catalog.get(language, catalog["vi"])[key]
    return template.format(**values)


def metadata():
    payload = json.loads(METADATA.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        frappe.throw(message("metadata_version"))
    return payload


def ensure_roles(payload):
    for values in payload["roles"]:
        if not frappe.db.exists("Role", values["name"]):
            frappe.get_doc(values).insert(ignore_permissions=True)


def before_install():
    for doctype in EXTERNAL_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            frappe.throw(message("missing_doctype", doctype=doctype))
    if not frappe.conf.get("server_script_enabled"):
        frappe.throw(message("missing_server_scripts"))
    ensure_roles(metadata())


def ensure_doctypes(payload):
    # First create every name without Link fields. This lets Frappe validate
    # cross-references when the complete field definitions are applied.
    for values in payload["doctypes"]:
        name = values["name"]
        if frappe.db.exists("DocType", name):
            if frappe.db.get_value("DocType", name, "module") != "Purchase Approval":
                frappe.throw(message("doctype_exists", doctype=name))
            continue
        frappe.get_doc({
            "doctype": "DocType",
            "name": name,
            "module": "Purchase Approval",
            "custom": 1,
            "istable": values.get("istable", 0),
            "issingle": values.get("issingle", 0),
            "fields": [],
            "permissions": [],
        }).insert(ignore_permissions=True)

    for values in payload["doctypes"]:
        name = values["name"]
        doc = frappe.get_doc("DocType", name)
        # Existing definitions belong to administrators. Only fill an empty
        # skeleton created in this run, making future migrations non-destructive.
        if doc.fields:
            continue
        doc.update({key: value for key, value in values.items() if key not in ("doctype", "name")})
        doc.save(ignore_permissions=True)


def ensure_named_docs(doctype, values):
    for item in values:
        if not frappe.db.exists(doctype, item["name"]):
            frappe.get_doc(item).insert(ignore_permissions=True)


def ensure_permissions(payload):
    for item in payload["custom_docperms"]:
        exists = frappe.db.exists("Custom DocPerm", {
            "parent": item["parent"],
            "role": item["role"],
            "permlevel": item.get("permlevel", 0),
        })
        if not exists:
            frappe.get_doc(item).insert(ignore_permissions=True)


def ensure_translations(payload):
    existing = {
        (row.message_key, row.language)
        for row in frappe.get_all(
            "PA Translation", fields=["message_key", "language"], limit_page_length=10000
        )
    }
    for item in payload["translations"]:
        key = (item["message_key"], item["language"])
        if key in existing:
            continue
        frappe.get_doc({"doctype": "PA Translation", **item}).insert(ignore_permissions=True)
        existing.add(key)


def ensure_metadata():
    payload = metadata()
    ensure_roles(payload)
    ensure_doctypes(payload)
    ensure_permissions(payload)
    ensure_named_docs("Print Format", payload["print_formats"])
    ensure_named_docs("Client Script", payload["client_scripts"])
    ensure_named_docs("Server Script", payload["server_scripts"])
    sidebar = payload["sidebar"]
    ensure_named_docs("Sidebar", [sidebar])
    ensure_translations(payload)
    frappe.clear_cache()


def after_install():
    ensure_metadata()
    frappe.db.set_single_value("PA Settings", "email_enabled", 0)
    frappe.db.set_single_value("PA Settings", "graph_mail_enabled", 0)


def after_migrate():
    ensure_metadata()
