"""Enable Excel/CSV imports for independent Purchase Approval DocTypes."""

import frappe

from purchase_approval.install import metadata


def execute():
    for values in metadata()["doctypes"]:
        if values.get("istable") or values.get("issingle"):
            continue

        doctype = values["name"]
        frappe.db.set_value("DocType", doctype, "allow_import", 1, update_modified=False)

        for permission_type in ("DocPerm", "Custom DocPerm"):
            rows = frappe.get_all(
                permission_type,
                filters={"parent": doctype, "role": "PA Super Admin", "permlevel": 0},
                pluck="name",
            )
            for name in rows:
                frappe.db.set_value(
                    permission_type,
                    name,
                    {"create": 1, "write": 1, "import": 1},
                    update_modified=False,
                )

        frappe.clear_cache(doctype=doctype)
