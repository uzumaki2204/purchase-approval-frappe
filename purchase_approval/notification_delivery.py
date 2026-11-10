"""Dispatch Purchase Approval outbox rows through the managed mail worker."""

import frappe


WORKER = "pa_notification_worker"


def dispatch_pending(outbox_names=None):
    """Run the existing PDF, SMTP and Graph delivery logic in a background job."""
    if not frappe.db.get_single_value("PA Settings", "email_enabled"):
        return
    script = frappe.get_doc("Server Script", WORKER)
    if script.script_type != "Scheduler Event":
        return
    # The scheduled Server Script runs as Administrator; queued jobs should
    # have the same print and mail permissions regardless of the submitter.
    frappe.set_user("Administrator")
    previous = getattr(frappe.local, "form_dict", None)
    if outbox_names is not None:
        frappe.local.form_dict = frappe._dict(pa_notification_only=outbox_names)
    try:
        script.execute_scheduled_method()
    finally:
        if outbox_names is not None:
            frappe.local.form_dict = previous if previous is not None else frappe._dict()


def retry_pending():
    """Cover fresh installs where the optional Server Script scheduler is off."""
    if frappe.db.get_value("Server Script", WORKER, "disabled"):
        dispatch_pending()
