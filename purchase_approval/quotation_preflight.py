"""Read-only quotation checks for requests that still use the legacy approval snapshot."""

import frappe

from purchase_approval import workflow_runtime as runtime
from purchase_approval.workflow_api import actor, checked_text, is_super_user, parse_payload


def legacy_scope(user, request):
    """Match the scope check in the installed purchase-request Server Script."""
    if not request.company or not frappe.db.exists("Company", request.company):
        return False
    if request.department and frappe.db.get_value("Department", request.department, "company") != request.company:
        return False
    if is_super_user(user):
        return True
    if "PA Manager" in runtime.roles(user):
        company = frappe.db.get_value("User", user, "company")
        department = frappe.db.get_value("User", user, "deparment")
        companies = [company] if company else []
        departments = [department] if department else []
    else:
        companies = [row.for_value for row in frappe.get_all(
            "User Permission", filters={"user": user, "allow": "Company"}, fields=["for_value"]
        )]
        departments = [row.for_value for row in frappe.get_all(
            "User Permission", filters={"user": user, "allow": "Department"}, fields=["for_value"]
        )]
    return request.company in companies and (
        not request.department or not departments or request.department in departments
    )


def legacy_approver(user, request):
    return bool(
        user and user != "Guest" and frappe.db.get_value("User", user, "enabled")
        and legacy_scope(user, request)
        and (is_super_user(user) or runtime.roles(user).intersection({"PA Approver", "PA Manager", "PA Company Admin"}))
    )


def step_candidates(step, request):
    source = getattr(step, "approver_source", None)
    if source == "User":
        return [getattr(step, "approver_user", None)]
    if source == "Role":
        role = getattr(step, "approver_role", None)
        return [row.parent for row in frappe.get_all(
            "Has Role", filters={"role": role, "parenttype": "User"}, fields=["parent"]
        )] if role else []
    if source == "Department Manager":
        return [row.parent for row in frappe.get_all(
            "Has Role", filters={"role": "PA Manager", "parenttype": "User"}, fields=["parent"]
        ) if frappe.db.get_value("User", row.parent, "deparment") == request.department]
    return []


def missing_approval_steps(workflow, request):
    missing = []
    approval_steps = [step for step in sorted(workflow.steps, key=lambda row: row.step_order)
                      if getattr(step, "step_type", None) in (None, "", "Quote Approval")]
    for step in approval_steps:
        users = {user for user in step_candidates(step, request) if legacy_approver(user, request)}
        users.discard(request.requester)
        if users:
            continue
        source = getattr(step, "approver_source", None)
        missing.append({
            "step_order": step.step_order,
            "step_name": step.step_name,
            "source": source,
            "target": (
                getattr(step, "approver_user", None) if source == "User" else
                getattr(step, "approver_role", None) if source == "Role" else
                "PA Manager" if source == "Department Manager" else None
            ),
        })
    return approval_steps, missing


@frappe.whitelist(methods=["POST"])
def check_quotation_approval(payload=None):
    """Check approvers without changing prices, a workflow, or an approval instance."""
    data = parse_payload(payload or "{}")
    user = actor()
    name = checked_text(data.get("name"), 140, True)
    if not frappe.db.exists("PA Purchase Request", name):
        runtime.fail("error.not_found")
    request = frappe.get_doc("PA Purchase Request", name)
    if not legacy_scope(user, request):
        runtime.fail("error.not_found")
    try:
        revision = int(data.get("expected_revision", -1))
    except (TypeError, ValueError):
        runtime.fail("error.conflict")
    if str(data.get("expected_modified") or "") != str(request.modified) or revision != int(request.revision or 0):
        runtime.fail("error.conflict")
    if request.status != "Pending Purchasing":
        runtime.fail("error.status")
    if runtime.is_modern(request):
        if "finalize" not in runtime.actions(request, user):
            runtime.fail("error.permission")
        return {"ready": True, "missing": [], "no_approval_step": False}
    if not is_super_user(user) and "PA Purchasing" not in runtime.roles(user):
        runtime.fail("error.permission")

    selected = checked_text(data.get("selected_workflow"), 140) if "selected_workflow" in data else request.selected_workflow
    candidates = runtime.candidates(request)
    if not candidates:
        runtime.fail("error.no_workflow")
    if selected:
        workflow = next((row for row in candidates if row.name == selected), None)
        if not workflow:
            runtime.fail("error.workflow")
    elif len(candidates) == 1:
        workflow = candidates[0]
    else:
        runtime.fail("error.ambiguous")
    approval_steps, missing = missing_approval_steps(workflow, request)
    return {"ready": bool(approval_steps and not missing), "missing": missing,
            "no_approval_step": not bool(approval_steps)}
