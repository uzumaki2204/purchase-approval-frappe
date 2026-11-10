"""Repair fields needed to start ordered workflows on older installed sites."""

import frappe

from purchase_approval.install import message, metadata


FIELDS = {
    "PA Purchase Request": ("selection_source",),
    "PA Approval Workflow": ("selector_source", "selector_user", "selector_role", "notify_requester"),
    "PA Approval Instance Step": ("step_type", "send_email"),
}
SELECTION_CHOICES = {"Automatic", "Selector"}


def choices(value):
    return [part.strip() for part in (value or "").splitlines() if part.strip()]


def merged_options(current, expected):
    existing = choices(current)
    if SELECTION_CHOICES.issubset(existing):
        return current
    prefix = "\n" if (expected or "").startswith("\n") or (current or "").startswith("\n") else ""
    return prefix + "\n".join(dict.fromkeys([*choices(expected), *existing]))


def execute():
    definitions = {row["name"]: row for row in metadata()["doctypes"]}
    for doctype, names in FIELDS.items():
        definition = {row["fieldname"]: row for row in definitions[doctype]["fields"]}
        doc = frappe.get_doc("DocType", doctype)
        fields = {row.fieldname: row for row in doc.fields}
        changed = False
        for name in names:
            source = definition[name]
            if name not in fields:
                values = {key: value for key, value in source.items() if key not in ("doctype", "name")}
                values["idx"] = max((int(row.idx or 0) for row in doc.fields), default=0) + 1
                fields[name] = doc.append("fields", values)
                changed = True
            elif doctype == "PA Purchase Request" and name == "selection_source":
                updated = merged_options(fields[name].options, source["options"])
                if updated != fields[name].options:
                    fields[name].options = updated
                    changed = True
        if changed:
            doc.save(ignore_permissions=True)

        if doctype == "PA Purchase Request":
            expected = definition["selection_source"]["options"]
            for setter in frappe.get_all(
                "Property Setter",
                filters={"doc_type": doctype, "field_name": "selection_source", "property": "options"},
                fields=["name", "value"], limit_page_length=0,
            ):
                updated = merged_options(setter.value, expected)
                if updated != setter.value:
                    frappe.db.set_value("Property Setter", setter.name, "value", updated, update_modified=False)

        frappe.clear_cache(doctype=doctype)
        effective = frappe.get_meta(doctype)
        invalid = [
            name for name in names
            if not (field := effective.get_field(name)) or field.fieldtype != definition[name]["fieldtype"]
        ]
        selection = effective.get_field("selection_source") if doctype == "PA Purchase Request" else None
        if selection and not SELECTION_CHOICES.issubset(choices(selection.options)):
            invalid.append("selection_source options")
        if invalid:
            frappe.throw(message("workflow_schema_incomplete", doctype=doctype, fields=", ".join(invalid)))

    # The old workflow format selected a purchasing role. Keep that default
    # only where these newly restored selector fields have no saved value.
    for row in frappe.get_all("PA Approval Workflow", fields=["name", "selector_source", "selector_role"], limit_page_length=0):
        values = {}
        if not row.selector_source:
            values["selector_source"] = "Role"
        if (row.selector_source or "Role") == "Role" and not row.selector_role:
            values["selector_role"] = "PA Purchasing"
        if values:
            frappe.db.set_value("PA Approval Workflow", row.name, values, update_modified=False)
