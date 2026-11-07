"""Fix the Department DocType reference in the request Print Format."""

import frappe


def execute():
    print_format = "PA Purchase Request Invoice"
    if not frappe.db.exists("Print Format", print_format):
        return

    html = frappe.db.get_value("Print Format", print_format, "html") or ""
    if "KTG Department" not in html:
        return

    frappe.db.set_value(
        "Print Format",
        print_format,
        "html",
        html.replace("KTG Department", "Department"),
        update_modified=False,
    )
    frappe.clear_cache(doctype="Print Format")
