"""Fix the Company DocType reference in the installed request Print Format."""

import frappe


def execute():
    print_format = "PA Purchase Request Invoice"
    if not frappe.db.exists("Print Format", print_format):
        return

    html = frappe.db.get_value("Print Format", print_format, "html") or ""
    if "KTG Company" not in html:
        return

    frappe.db.set_value(
        "Print Format",
        print_format,
        "html",
        html.replace("KTG Company", "Company"),
        update_modified=False,
    )
    frappe.clear_cache(doctype="Print Format")
