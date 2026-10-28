"""Adopt an existing Purchase Approval site without uninstalling its DocTypes."""

import frappe

from purchase_approval.install import message, metadata


OLD_APP = "purchase_approval_navigation"
NEW_APP = "purchase_approval"
MODULE = "Purchase Approval"
OLD_PATCH = f"{OLD_APP}.patches.enable_independent_doctype_import"
NEW_PATCH = f"{NEW_APP}.patches.enable_independent_doctype_import"
CALLBACK_SETTINGS = ("pa_outlook_callback_url", "pa_gmail_callback_url")
SCRIPT_FIELDS = (
    ("Server Script", "script"),
    ("Client Script", "script"),
    ("Print Format", "html"),
    ("Print Format", "css"),
    ("Print Format", "js"),
    ("Page", "script"),
    ("Page", "style"),
)


def _replace_saved_references():
    changed = 0
    for doctype, field in SCRIPT_FIELDS:
        if not frappe.get_meta(doctype).has_field(field):
            continue
        for row in frappe.get_all(
            doctype, fields=["name", field], limit_page_length=10000
        ):
            value = row.get(field)
            if isinstance(value, str) and OLD_APP in value:
                frappe.db.set_value(
                    doctype,
                    row.name,
                    field,
                    value.replace(OLD_APP, NEW_APP),
                    update_modified=False,
                )
                changed += 1
    return changed


def execute():
    """Run once on an existing site after the new package is in apps.txt."""
    from frappe.installer import add_to_installed_apps, remove_from_installed_apps, update_site_config

    installed = frappe.get_installed_apps()
    if OLD_APP in installed and NEW_APP in installed:
        frappe.throw(message("slug_both_installed"))
    if OLD_APP not in installed and NEW_APP not in installed:
        frappe.throw(message("slug_old_missing"))
    if NEW_APP not in frappe.get_all_apps():
        frappe.throw(message("slug_new_missing"))

    owner = frappe.db.get_value("Module Def", MODULE, "app_name")
    if owner not in (OLD_APP, NEW_APP):
        frappe.throw(message("slug_wrong_module_owner", owner=owner or ""))
    for values in metadata()["doctypes"]:
        if not frappe.db.exists("DocType", values["name"]):
            frappe.throw(message("slug_missing_doctype", doctype=values["name"]))

    changed = _replace_saved_references()
    for sidebar in frappe.get_all("Sidebar", filters={"app": OLD_APP}, pluck="name"):
        frappe.db.set_value("Sidebar", sidebar, "app", NEW_APP, update_modified=False)

    if frappe.db.exists("Patch Log", {"patch": OLD_PATCH, "skipped": 0}) and not frappe.db.exists(
        "Patch Log", {"patch": NEW_PATCH, "skipped": 0}
    ):
        frappe.get_doc({"doctype": "Patch Log", "patch": NEW_PATCH}).insert(
            ignore_permissions=True
        )

    if owner == OLD_APP:
        frappe.db.set_value("Module Def", MODULE, "app_name", NEW_APP, update_modified=False)
    frappe.db.commit()

    for key in CALLBACK_SETTINGS:
        url = frappe.conf.get(key)
        if isinstance(url, str) and OLD_APP in url:
            update_site_config(key, url.replace(OLD_APP, NEW_APP))

    if OLD_APP in installed:
        remove_from_installed_apps(OLD_APP)
        add_to_installed_apps(NEW_APP)

    frappe.clear_cache()
    frappe.client_cache.erase_persistent_caches()
    print(message("slug_migrated", site=frappe.local.site, references=changed))
