"""Ordered purchase-request workflow runtime.

The instance snapshot is the authority for in-flight requests. Editing a workflow
never changes the actors or order of an existing instance.
"""

import json
from pathlib import Path

import frappe


_catalog = json.loads(Path(__file__).with_name("ui-translations.json").read_text(encoding="utf-8"))["messages"]


REQUEST = "PA Purchase Request"
WORKFLOW = "PA Approval Workflow"
INSTANCE = "PA Approval Instance"
OUTBOX = "PA Notification Outbox"
KINDS = ("Stock Check", "Purchase Handoff", "Quotation", "Quote Approval", "Receiving")
STAGES = {
    "Stock Check": "Pending Stock Check",
    "Purchase Handoff": "Pending Purchasing",
    "Quotation": "Pending Purchasing",
    "Quote Approval": "Pending Approval",
    "Receiving": "Approved",
}


def tr(key):
    translated = frappe.db.get_value("PA Translation", key, "text")
    return translated if translated and translated != key else _catalog.get(key, key)


def fail(key):
    frappe.throw(tr(key))


def roles(user):
    if user == "Administrator":
        return {"PA Super Admin"}
    return {row.role for row in frappe.get_all("Has Role", filters={"parent": user, "parenttype": "User"}, fields=["role"], limit_page_length=0)}


def in_scope(user, request):
    if user == "Administrator" or "PA Super Admin" in roles(user):
        return True
    company = {row.for_value for row in frappe.get_all("User Permission", filters={"user": user, "allow": "Company"}, fields=["for_value"], limit_page_length=0)}
    departments = {row.for_value for row in frappe.get_all("User Permission", filters={"user": user, "allow": "Department"}, fields=["for_value"], limit_page_length=0)}
    if "PA Manager" in roles(user):
        company.add(frappe.db.get_value("User", user, "company"))
        departments.add(frappe.db.get_value("User", user, "deparment"))
    return request.company in company and (not departments or request.department in departments)


def eligible_user(user, request):
    return bool(user and user != "Guest" and frappe.db.get_value("User", user, "enabled") and in_scope(user, request))


def normalize_workflow_users(source, selected, legacy_user, allowed_users):
    if source != "User":
        return []
    if selected is None:
        selected = [legacy_user] if legacy_user else []
    if not isinstance(selected, list) or not selected:
        fail("error.workflow_assignee")
    if any(not isinstance(user, str) or not user.strip() or len(user) > 140 for user in selected):
        fail("error.workflow_assignee")
    users = [user.strip() for user in selected]
    if len(users) != len(set(users)) or any(user not in allowed_users for user in users):
        fail("error.workflow_assignee")
    return users


def assignees(step, request, selected_users=None):
    source = step.approver_source
    if source == "User":
        candidates = selected_users or ([step.approver_user] if step.approver_user else [])
    elif source == "Role":
        candidates = [row.parent for row in frappe.get_all("Has Role", filters={"role": step.approver_role, "parenttype": "User"}, fields=["parent"], limit_page_length=0)]
    elif source == "Department Manager":
        candidates = [row.parent for row in frappe.get_all("Has Role", filters={"role": "PA Manager", "parenttype": "User"}, fields=["parent"], limit_page_length=0) if frappe.db.get_value("User", row.parent, "deparment") == request.department]
    else:
        fail("error.workflow_assignee")
    users = sorted({user for user in candidates if eligible_user(user, request)})
    if step.step_type == "Quote Approval":
        users = [user for user in users if user != request.requester]
    if not users:
        fail("error.no_approver")
    return users


def candidates(request):
    matches = []
    for row in frappe.get_all(WORKFLOW, filters={"company": request.company, "is_active": 1}, fields=["name"], limit_page_length=0):
        workflow = frappe.get_doc(WORKFLOW, row.name)
        if (not workflow.department or workflow.department == request.department) and workflow.currency == request.currency:
            matches.append(workflow)
    if not matches:
        return []
    specificity = max(bool(workflow.department) for workflow in matches)
    return [workflow for workflow in matches if bool(workflow.department) == specificity]


def selector_allowed(user, workflow, request):
    if not eligible_user(user, request):
        return False
    if workflow.selector_source == "User":
        return user == workflow.selector_user
    if workflow.selector_source == "Role":
        return workflow.selector_role in roles(user)
    return False


def is_modern(request):
    if not request.current_instance or not frappe.db.exists(INSTANCE, request.current_instance):
        return False
    raw = frappe.db.get_value(INSTANCE, request.current_instance, "workflow_snapshot")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return False
    return isinstance(raw, dict) and raw.get("workflow_schema") == 2


def snapshot(instance):
    raw = instance.workflow_snapshot
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return {}
    return raw if isinstance(raw, dict) else {}


def active_step(instance):
    return next((step for step in instance.steps if step.step_order == instance.current_sequence), None)


def assigned(instance, user):
    return any(row.user == user and row.step_order == instance.current_sequence and row.status == "Pending" for row in instance.assignees)


def save(doc):
    doc.flags.pa_internal = True
    doc.save(ignore_permissions=True)


def enqueue(request, instance, step=None):
    if step is None:
        if not snapshot(instance).get("notify_requester"):
            return
        targets = [(0, request.requester, "notification.requester_subject", "notification.requester_body")]
    elif step.send_email:
        targets = [(step.step_order, row.user, "notification.step_subject", "notification.step_body") for row in instance.assignees if row.step_order == step.step_order and row.status == "Pending"]
    else:
        return
    for order, recipient, subject_key, body_key in targets:
        key = f"{instance.name}:{order}:{recipient}"
        existing = frappe.db.get_value(OUTBOX, {"notification_key": key}, ["name", "status"], as_dict=True)
        if existing:
            if existing.status == "Cancelled":
                frappe.db.set_value(OUTBOX, existing.name, "status", "Pending", update_modified=False)
            continue
        body = tr(body_key).replace("{step}", step.step_name) if step else tr(body_key)
        frappe.get_doc({"doctype": OUTBOX, "request": request.name, "instance": instance.name, "step_order": order, "recipient": recipient, "notification_key": key, "subject": f"{tr(subject_key)} {request.name}", "body": body, "status": "Pending"}).insert(ignore_permissions=True)


def advance(request, instance):
    """Move to the next pending workflow action."""
    while True:
        pending = sorted((step for step in instance.steps if step.status == "Pending"), key=lambda step: step.step_order)
        if not pending:
            instance.current_sequence = 0
            instance.status = "Approved"
            instance.completed_at = frappe.utils.now()
            request.status = "Closed"
            break
        step = pending[0]
        instance.current_sequence = step.step_order
        request.status = STAGES[step.step_type]
        break
    save(instance)
    save(request)
    if instance.status == "Pending":
        enqueue(request, instance, step)


def begin(request, workflow, source):
    frappe.db.sql("select name from `tabPA Approval Workflow` where name=%s for update", workflow.name)
    workflow.reload()
    if workflow.name not in {row.name for row in candidates(request)}:
        fail("error.workflow")
    snapshot = workflow.as_dict()
    snapshot["workflow_schema"] = 2
    instance = frappe.get_doc({"doctype": INSTANCE, "request": request.name, "company": request.company, "department": request.department, "workflow": workflow.name, "workflow_name": workflow.workflow_name, "workflow_version": workflow.modified, "workflow_snapshot": snapshot, "revision": request.revision, "status": "Pending", "steps": [], "assignees": []})
    selected_by_order = {}
    for assigned in getattr(workflow, "assignees", []):
        selected_by_order.setdefault(assigned.step_order, []).append(assigned.user)
    for definition in sorted(workflow.steps, key=lambda row: row.step_order):
        kind = definition.step_type
        instance.append("steps", {"step_order": definition.step_order, "step_name": definition.step_name, "step_type": kind, "approval_method": definition.approval_method or "Any", "send_email": definition.send_email, "status": "Pending"})
        for user in assignees(definition, request, selected_by_order.get(definition.step_order)):
            instance.append("assignees", {"step_order": definition.step_order, "user": user, "status": "Pending"})
    instance.flags.pa_internal = True
    instance.insert(ignore_permissions=True)
    request.selected_workflow = workflow.name
    request.selection_source = source
    request.current_instance = instance.name
    advance(request, instance)
    enqueue(request, instance)
    return instance


def start_submitted(request):
    matches = candidates(request)
    if not matches:
        fail("error.no_workflow")
    if len(matches) == 1:
        begin(request, matches[0], "Automatic")
        return
    selected = next((row for row in matches if row.name == request.selected_workflow), None)
    if selected and selector_allowed(request.requester, selected, request):
        begin(request, selected, "Selector")
        return
    request.selected_workflow = None
    request.selection_source = None
    request.status = "Pending Workflow Selection"
    save(request)


def select(request, workflow_name, user):
    if request.status != "Pending Workflow Selection" or request.current_instance:
        fail("error.status")
    workflow = next((row for row in candidates(request) if row.name == workflow_name), None)
    if not workflow:
        fail("error.workflow")
    if not selector_allowed(user, workflow, request):
        fail("error.permission")
    begin(request, workflow, "Selector")


def finish_step(request, instance, user, comment=""):
    step = active_step(instance)
    if not step or not assigned(instance, user) or not eligible_user(user, request):
        fail("error.permission")
    previous_receipt = None
    if step.step_type == "Receiving":
        previous_receipt = frappe.db.get_value(
            REQUEST,
            request.name,
            ["received_by", "received_at"],
            as_dict=True,
        )
    acted_at = frappe.utils.now()
    row = next(row for row in instance.assignees if row.step_order == step.step_order and row.user == user and row.status == "Pending")
    row.status = "Approved"
    row.acted_at = acted_at
    row.comment = comment
    step_rows = [row for row in instance.assignees if row.step_order == step.step_order]
    complete = step.approval_method != "All" or all(row.status == "Approved" for row in step_rows)
    if complete:
        step.status = "Approved"
        step.completed_at = acted_at
        for row in step_rows:
            if row.status == "Pending":
                row.status = "Skipped"
    for outbox in frappe.get_all(OUTBOX, filters={"instance": instance.name, "step_order": step.step_order, "status": "Pending"}, fields=["name", "recipient"], limit_page_length=0):
        if complete or outbox.recipient == user:
            frappe.db.set_value(OUTBOX, outbox.name, "status", "Cancelled", update_modified=False)
    if not complete:
        save(instance)
        if previous_receipt:
            request.received_by = previous_receipt.get("received_by")
            request.received_at = previous_receipt.get("received_at")
        save(request)
        return False
    advance(request, instance)
    return True


def notification_active(request, instance, outbox):
    if request.current_instance != instance.name:
        return False
    if outbox.step_order == 0:
        return outbox.recipient == request.requester
    handoff = next((step for step in instance.steps if step.step_order == outbox.step_order and step.step_type == "Purchase Handoff"), None)
    if handoff:
        if handoff.status == "Approved":
            # Preserve notifications queued by the previous automatic handoff
            # behavior for requests already in flight during an upgrade.
            return bool(handoff.send_email and request.status not in ("Cancelled", "Rejected", "Returned") and any(row.user == outbox.recipient and row.step_order == outbox.step_order for row in instance.assignees))
        return bool(handoff.send_email and instance.status == "Pending" and handoff.status == "Pending" and instance.current_sequence == handoff.step_order and assigned(instance, outbox.recipient) and eligible_user(outbox.recipient, request))
    step = active_step(instance)
    return bool(instance.status == "Pending" and step and step.step_order == outbox.step_order and step.send_email and assigned(instance, outbox.recipient) and eligible_user(outbox.recipient, request))


def generic_email(request, outbox):
    escape = frappe.utils.escape_html
    url = frappe.utils.get_url("/desk/purchase-approval?view=detail&request=" + request.name)
    return ("<html><body><p>" + escape(outbox.body) + "</p><p><strong>" + escape(request.name) + "</strong></p><p><a href=\"" + escape(url) + "\">" + escape(tr("notification.view_button")) + "</a></p></body></html>")


def actions(request, user):
    if request.status == "Pending Workflow Selection":
        return ["select_workflow"] if any(selector_allowed(user, row, request) for row in candidates(request)) else []
    if not is_modern(request):
        return None
    instance = frappe.get_doc(INSTANCE, request.current_instance)
    step = active_step(instance)
    if not step or not assigned(instance, user) or not eligible_user(user, request):
        return []
    return {"Stock Check": ["stock_check"], "Purchase Handoff": ["confirm_handoff"], "Quotation": ["finalize"], "Quote Approval": ["approve", "return", "reject"], "Receiving": ["receive"]}.get(step.step_type, [])


def capabilities(user):
    result = {"stock_check": False, "selection": False, "approvals": False, "purchasing": False, "receiving": False}
    instance_names = {row.parent for row in frappe.get_all("PA Approval Assignee", filters={"user": user, "status": "Pending"}, fields=["parent"], limit_page_length=0)}
    for name in instance_names:
        instance = frappe.get_doc(INSTANCE, name)
        if instance.status != "Pending":
            continue
        step = active_step(instance)
        if not step or not any(row.user == user and row.status == "Pending" and row.step_order == step.step_order for row in instance.assignees):
            continue
        request = frappe.get_doc(REQUEST, instance.request)
        if not eligible_user(user, request):
            continue
        key = {"Stock Check": "stock_check", "Purchase Handoff": "purchasing", "Quotation": "purchasing", "Quote Approval": "approvals", "Receiving": "receiving"}.get(step.step_type)
        if key:
            result[key] = True
    for row in frappe.get_all(REQUEST, filters={"status": "Pending Workflow Selection"}, fields=["name", "company", "department", "currency"], limit_page_length=0):
        if any(selector_allowed(user, workflow, row) for workflow in candidates(row)):
            result["selection"] = True
            break
    return result


def validate_steps(steps):
    if not steps or len(steps) > 30:
        fail("error.workflow_steps")
    def value(step, key):
        return step.get(key)
    kinds = [value(step, "step_type") for step in steps]
    if any(kind not in KINDS for kind in kinds):
        fail("error.workflow_steps")
    for one in ("Stock Check", "Purchase Handoff", "Quotation", "Receiving"):
        if kinds.count(one) > 1:
            fail("error.workflow_steps")
    if "Receiving" in kinds and kinds[-1] != "Receiving":
        fail("error.workflow_steps")
    for step in steps:
        if value(step, "approver_source") not in ("User", "Role", "Department Manager"):
            fail("error.workflow_assignee")
        method = value(step, "approval_method") or "Any"
        if method not in ("Any", "All"):
            fail("error.workflow_steps")
        if value(step, "step_type") == "Quotation" and method != "Any":
            fail("error.workflow_steps")


@frappe.whitelist(methods=["POST"])
def bridge(action, **kwargs):
    """Expose only named operations to an already running PA Server Script."""
    if not frappe.flags.get("in_safe_exec"):
        fail("error.permission")
    operations = {
        "start_submitted": lambda: start_submitted(kwargs["request"]),
        "is_modern": lambda: is_modern(kwargs["request"]),
        "active_step": lambda: active_step(kwargs["instance"]),
        "assigned": lambda: assigned(kwargs["instance"], kwargs["user"]),
        "finish_step": lambda: finish_step(kwargs["request"], kwargs["instance"], kwargs["user"], kwargs.get("comment", "")),
        "eligible_user": lambda: eligible_user(kwargs["user"], kwargs["request"]),
        "advance": lambda: advance(kwargs["request"], kwargs["instance"]),
        "actions": lambda: actions(kwargs["request"], kwargs["user"]),
        "validate_steps": lambda: validate_steps(kwargs["steps"]),
        "normalize_workflow_users": lambda: normalize_workflow_users(kwargs["source"], kwargs.get("selected"), kwargs.get("legacy_user"), kwargs["allowed_users"]),
        "capabilities": lambda: capabilities(kwargs["user"]),
        "enqueue": lambda: enqueue(kwargs["request"], kwargs["instance"], kwargs.get("step")),
        "selector_allowed": lambda: selector_allowed(kwargs["user"], kwargs["workflow"], kwargs["request"]),
        "select": lambda: select(kwargs["request"], kwargs["workflow_name"], kwargs["user"]),
        "notification_active": lambda: notification_active(kwargs["request"], kwargs["instance"], kwargs["outbox"]),
        "generic_email": lambda: generic_email(kwargs["request"], kwargs["outbox"]),
    }
    if action not in operations:
        fail("error.permission")
    return operations[action]()

