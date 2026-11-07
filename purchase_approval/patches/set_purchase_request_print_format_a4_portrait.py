"""Set the Purchase Request PDF Print Format to A4 portrait."""

import frappe


def execute():
    print_format = "PA Purchase Request Invoice"
    if not frappe.db.exists("Print Format", print_format):
        return

    css = frappe.db.get_value("Print Format", print_format, "css") or ""
    updated_css = css.replace("size: A4 landscape;", "size: A4 portrait;", 1)
    if updated_css == css:
        return

    frappe.db.set_value(
        "Print Format",
        print_format,
        "css",
        updated_css,
        update_modified=False,
    )
    frappe.clear_cache(doctype="Print Format")
