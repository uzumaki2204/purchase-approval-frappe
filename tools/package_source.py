"""Build the app-owned Purchase Approval metadata from a read-only Frappe export.

The input is intentionally kept outside Git. It may contain source-site audit
fields and must never be committed directly.
"""

import argparse
import json
from pathlib import Path


SYSTEM_FIELDS = {
    "owner", "creation", "modified", "modified_by", "docstatus",
    "parent", "parentfield", "parenttype", "migration_hash",
}


def clean(value, *, root=False):
    if isinstance(value, list):
        return [clean(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key in SYSTEM_FIELDS or (key == "name" and not root):
            continue
        result[key] = clean(item)
    return result


def merge_fields(doctype, custom_fields, field_order):
    fields = list(doctype.get("fields") or [])
    names = {field.get("fieldname") for field in fields}
    for source in custom_fields:
        if source["dt"] != doctype["name"]:
            continue
        field = clean(source)
        for key in ("name", "dt", "insert_after", "is_system_generated"):
            field.pop(key, None)
        field["doctype"] = "DocField"
        if field["fieldname"] not in names:
            fields.append(field)
            names.add(field["fieldname"])
    if field_order:
        order = {name: index for index, name in enumerate(field_order)}
        fields.sort(key=lambda field: order.get(field.get("fieldname"), len(order)))
    for index, field in enumerate(fields, 1):
        field["idx"] = index
    doctype["fields"] = fields


def build(source, output):
    source_data = json.loads(source.read_text(encoding="utf-8"))
    if len(source_data["doctypes"]) != 16 or len(source_data["server_scripts"]) != 48:
        raise ValueError("Unexpected source metadata count")

    order_by_doctype = {}
    for setter in source_data["property_setters"]:
        if setter.get("property") == "field_order":
            order_by_doctype[setter["doc_type"]] = json.loads(setter["value"])

    doctypes = []
    for raw in source_data["doctypes"]:
        doc = clean(raw, root=True)
        doc["module"] = "Purchase Approval"
        doc["custom"] = 1
        merge_fields(doc, source_data["custom_fields"], order_by_doctype.get(doc["name"]))
        doctypes.append(doc)

    page = clean(source_data["pages"][0], root=True)
    page["module"] = "Purchase Approval"
    page["standard"] = "Yes"

    sidebar = clean(source_data["sidebars"][0], root=True)
    sidebar["app"] = "purchase_approval_navigation"

    server_scripts = [clean(item, root=True) for item in source_data["server_scripts"]]
    for script in server_scripts:
        if script["name"] == "pa_notification_worker":
            script["disabled"] = 1

    payload = {
        "schema_version": 1,
        "doctypes": doctypes,
        "custom_docperms": [
            {**clean(item, root=True), "parent": item["parent"]}
            for item in source_data["custom_docperms"]
        ],
        "roles": [clean(item, root=True) for item in source_data["roles"]],
        "server_scripts": server_scripts,
        "client_scripts": [clean(item, root=True) for item in source_data["client_scripts"]],
        "sidebar": sidebar,
        "print_formats": [clean(item, root=True) for item in source_data["print_formats"]],
        "translations": source_data["translations"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page_path = output.parent.parent / "purchase_approval" / "page" / "purchase_approval" / "purchase_approval.json"
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.source, args.output)
