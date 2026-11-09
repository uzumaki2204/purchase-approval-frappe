"""Add the Role creation page to existing Purchase Approval sidebars."""

import frappe

from purchase_approval.install import metadata


ROLE_URL = "/desk/purchase-approval?view=roles"
WORKFLOW_URL = "/desk/purchase-approval?view=workflows"


def execute():
    source = metadata()["sidebar"]
    if not frappe.db.exists("Sidebar", source["name"]):
        return

    sidebar = frappe.get_doc("Sidebar", source["name"])
    if any(row.url == ROLE_URL for row in sidebar.items):
        return

    values = next(row for row in source["items"] if row.get("url") == ROLE_URL)
    new_item = sidebar.append("items", {key: value for key, value in values.items() if key not in ("doctype", "name")})
    sidebar.items.remove(new_item)
    position = next((index + 1 for index, row in enumerate(sidebar.items) if row.url == WORKFLOW_URL), len(sidebar.items))
    sidebar.items.insert(position, new_item)
    for index, row in enumerate(sidebar.items, 1):
        row.idx = index
    sidebar.save(ignore_permissions=True)
    frappe.clear_cache()
