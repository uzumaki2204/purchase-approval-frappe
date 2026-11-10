"""Restore workflow status choices on sites with older DocField overrides."""

import frappe

from purchase_approval.install import message, metadata


DOCTYPE = "PA Purchase Request"
FIELD = "status"
REQUIRED = {"Pending Workflow Selection", "Pending Stock Check"}


def choices(value):
    return [choice.strip() for choice in (value or "").splitlines() if choice.strip()]


def merged_options(current, expected):
    existing = choices(current)
    if REQUIRED.issubset(existing):
        return current
    return "\n".join(dict.fromkeys([*choices(expected), *existing]))


def execute():
    definition = next(row for row in metadata()["doctypes"] if row["name"] == DOCTYPE)
    expected = next(row["options"] for row in definition["fields"] if row["fieldname"] == FIELD)
    field = frappe.db.get_value(
        "DocField", {"parent": DOCTYPE, "fieldname": FIELD}, ["name", "options"], as_dict=True
    )
    if not field:
        frappe.throw(message("workflow_status_field_missing"))

    updated = merged_options(field.options, expected)
    if updated != field.options:
        frappe.db.set_value("DocField", field.name, "options", updated, update_modified=False)

    for setter in frappe.get_all(
        "Property Setter",
        filters={"doc_type": DOCTYPE, "field_name": FIELD, "property": "options"},
        fields=["name", "value"], limit_page_length=0,
    ):
        updated = merged_options(setter.value, expected)
        if updated != setter.value:
            frappe.db.set_value("Property Setter", setter.name, "value", updated, update_modified=False)

    frappe.clear_cache(doctype=DOCTYPE)
    effective = frappe.get_meta(DOCTYPE).get_field(FIELD)
    if not effective or not REQUIRED.issubset(choices(effective.options)):
        frappe.throw(message("workflow_status_options_missing"))
