"""Remove the status badge from the Purchase Request PDF header."""

import re

import frappe


def execute():
    print_format = "PA Purchase Request Invoice"
    if not frappe.db.exists("Print Format", print_format):
        return

    html = frappe.db.get_value("Print Format", print_format, "html") or ""
    css = frappe.db.get_value("Print Format", print_format, "css") or ""
    updated_html = re.sub(
        r"\{% set status_labels = \{.*?\}\s*%\}\s*",
        "",
        html,
        count=1,
        flags=re.S,
    )
    updated_html = re.sub(
        r"\s*<span class=\"pa-invoice-status\">.*?</span>",
        "",
        updated_html,
        count=1,
        flags=re.S,
    )
    updated_css = re.sub(
        r"(?m)^\.pa-invoice-status\s*\{[^}]*\}\s*",
        "",
        css,
        count=1,
    )
    if updated_html == html and updated_css == css:
        return

    frappe.db.set_value(
        "Print Format",
        print_format,
        {"html": updated_html, "css": updated_css},
        update_modified=False,
    )
    frappe.clear_cache(doctype="Print Format")
