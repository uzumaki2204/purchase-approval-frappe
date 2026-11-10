"""Python API for workflow administration without rewriting local Server Scripts."""

import json
from types import SimpleNamespace

import frappe

from purchase_approval import workflow_roles, workflow_runtime as runtime


WORKFLOW = "PA Approval Workflow"


def fail(key):
    runtime.fail(key)


def actor():
    user = frappe.session.user
    if not user or user == "Guest":
        fail("error.auth")
    if user != "Administrator" and not frappe.db.get_value("User", user, "enabled"):
        fail("error.inactive")
    return user


def is_super_user(user):
    return user == "Administrator" or "PA Super Admin" in runtime.roles(user)


def require_role(user, role):
    if not is_super_user(user) and role not in runtime.roles(user):
        fail("error.permission")


def checked_text(value, max_length, required=False):
    if value is None:
        value = ""
    if not isinstance(value, str):
        fail("error.required")
    value = value.strip()
    if (required and not value) or len(value) > max_length:
        fail("error.required")
    return value


def workflow_flag(value):
    if value not in (0, 1, "0", "1"):
        fail("error.required")
    return int(value)


def workflow_admin_scope(user, company, department=None):
    require_role(user, "PA Company Admin")
    if not company or not frappe.db.exists("Company", company):
        fail("error.permission")
    if department and frappe.db.get_value("Department", department, "company") != company:
        fail("error.permission")
    if not runtime.in_scope(user, SimpleNamespace(company=company, department=department)):
        fail("error.permission")
    if not department and not is_super_user(user) and frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Department"},
        fields=["name"],
        limit_page_length=0,
    ):
        fail("error.permission")


def workflow_assignee_options(user, company, department):
    workflow_admin_scope(user, company, department)
    target = SimpleNamespace(company=company, department=department)
    users = [
        row
        for row in frappe.get_all(
            "User", filters={"enabled": 1}, fields=["name", "full_name"], limit_page_length=0
        )
        if row.name != "Guest" and runtime.eligible_user(row.name, target)
    ]
    roles = set()
    for row in frappe.get_all(
        "Has Role",
        filters={"parenttype": "User", "parent": ["in", [item.name for item in users]]},
        fields=["role"],
        limit_page_length=0,
    ) if users else []:
        if frappe.db.exists("Role", {"name": row.role, "disabled": 0}):
            roles.add(row.role)
    return users, sorted(roles)


@frappe.whitelist(methods=["POST"])
def workflow_assignees(payload=None):
    """List active, in-scope users through the current workflow assignment rules."""
    data = parse_payload(payload or "{}")
    user = actor()
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    users, roles = workflow_assignee_options(user, company, department)
    query = checked_text(data.get("query"), 100).casefold()
    try:
        page = int(data.get("page") or 0)
    except (TypeError, ValueError):
        fail("error.filters")
    if page < 0 or page > 10000:
        fail("error.filters")
    visible = sorted(
        (row for row in users if not query or query in row.name.casefold() or query in (row.full_name or "").casefold()),
        key=lambda row: ((row.full_name or "").casefold(), row.name),
    )
    return {
        "users": [{"name": row.name, "full_name": row.full_name or row.name} for row in visible[page * 20:(page + 1) * 20]],
        "roles": roles,
        "page": page,
        "has_more": len(visible) > (page + 1) * 20,
    }


@frappe.whitelist(methods=["POST"])
def workflow_role_creation_access(payload=None):
    user = actor()
    data = parse_payload(payload or "{}")
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    return {"can_create_role": bool(frappe.has_permission("Role", "create", user=user))}


@frappe.whitelist(methods=["POST"])
def list_purchase_approval_roles(payload=None):
    user = actor()
    data = parse_payload(payload or "{}")
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    if not frappe.has_permission("Role", "read", user=user):
        fail("error.role_read_permission")

    users, roles = workflow_assignee_options(user, company, department)
    registered = workflow_roles.registered_names()
    roles = [role for role in roles if role in registered]
    if not roles:
        return {"roles": []}

    eligible_users = {row.name for row in users}
    role_users = {role: set() for role in roles}
    for row in frappe.get_all(
        "Has Role",
        filters={"parenttype": "User", "parent": ["in", sorted(eligible_users)]},
        fields=["parent", "role"],
        limit_page_length=0,
    ):
        if row.role in role_users and row.parent in eligible_users:
            role_users[row.role].add(row.parent)
    return {
        "roles": [
            {"name": role, "eligible_user_count": len(role_users[role])}
            for role in roles if role_users[role]
        ]
    }


@frappe.whitelist(methods=["POST"])
def register_existing_workflow_role(payload=None):
    user = actor()
    data = parse_payload(payload or "{}")
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    if not frappe.has_permission("Role", "read", user=user):
        fail("error.role_read_permission")
    role_name = checked_text(data.get("role_name"), 140, True)
    if not frappe.db.exists("Role", role_name):
        fail("error.role_not_found")
    if frappe.db.get_value("Role", role_name, "disabled"):
        fail("error.role_disabled")
    workflow_roles.register(role_name)
    return {"role_name": role_name}


@frappe.whitelist(methods=["POST"])
def create_workflow_role(payload=None):
    user = actor()
    data = parse_payload(payload or "{}")
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    if not frappe.has_permission("Role", "create", user=user):
        fail("error.role_create_permission")
    role_name = data.get("role_name")
    if not isinstance(role_name, str):
        fail("error.role_name")
    role_name = role_name.strip()
    if not role_name or len(role_name) > 140 or any(ord(char) < 32 or ord(char) == 127 for char in role_name):
        fail("error.role_name")
    if frappe.db.exists("Role", role_name):
        fail("error.role_exists")
    role = frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1, "disabled": 0, "is_custom": 1})
    try:
        role.insert()
    except frappe.DuplicateEntryError:
        fail("error.role_exists")
    workflow_roles.register(role.name)
    return {"role_name": role.name}


def workflow_admin_doc(user, name, lock=False):
    name = checked_text(name, 140, True)
    row = frappe.db.get_value(WORKFLOW, name, ["company", "department"], as_dict=True)
    if not row:
        fail("error.not_found")
    workflow_admin_scope(user, row.company, row.department)
    if lock:
        frappe.db.sql(f"select name from `tab{WORKFLOW}` where name=%s for update", (name,))
    doc = frappe.get_doc(WORKFLOW, name)
    workflow_admin_scope(user, doc.company, doc.department)
    return doc


def document_values(doc):
    return json.loads(json.dumps(doc.as_dict(), default=str))


def workflow_admin_result(doc):
    users = {}
    for assigned in doc.assignees:
        users[assigned.user] = frappe.db.get_value("User", assigned.user, "full_name") or assigned.user
    if doc.selector_source == "User" and doc.selector_user:
        users[doc.selector_user] = frappe.db.get_value("User", doc.selector_user, "full_name") or doc.selector_user
    return {
        "workflow": document_values(doc),
        "labels": {
            "company": frappe.db.get_value("Company", doc.company, "company_name") or doc.company,
            "department": frappe.db.get_value("Department", doc.department, "department_name") if doc.department else None,
            "users": users,
        },
    }


def workflow_step_signature(rows, assignments=None):
    result = []
    fields = ("step_name", "step_type", "approval_method", "approver_source", "approver_role", "send_email")
    users_by_order = {}
    for assigned in assignments or []:
        users_by_order.setdefault(assigned.step_order, []).append(assigned.user)
    for step in rows:
        selected = step.get("approver_users") or users_by_order.get(step.get("step_order"), [])
        users = [row if isinstance(row, str) else row.get("user") for row in selected if row]
        if not users and step.get("approver_user"):
            users = [step.get("approver_user")]
        values = {field: step.get(field) or "" for field in fields}
        values["approver_user"] = step.get("approver_user") or (users[0] if users else "")
        values["approver_users"] = users
        result.append(values)
    return result


def parse_payload(payload):
    try:
        data = json.loads(payload) if isinstance(payload, str) else payload
    except (TypeError, ValueError):
        fail("error.required")
    if not isinstance(data, dict):
        fail("error.required")
    return data


def register_referenced_roles(selector_source, selector_role, steps):
    names = {step["approver_role"] for step in steps if step["approver_source"] == "Role"}
    if selector_source == "Role":
        names.add(selector_role)
    for name in sorted(names):
        if name:
            workflow_roles.register(name)


@frappe.whitelist(methods=["POST"])
def save_approval_workflow(payload=None):
    """Save a workflow through Python so local Server Script edits remain intact."""
    user = actor()
    require_role(user, "PA Company Admin")
    data = parse_payload(payload or "{}")
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    users, roles = workflow_assignee_options(user, company, department)
    user_names = [row.name for row in users]

    if data.get("currency", "VND") != "VND":
        fail("error.required")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps or len(steps) > 30:
        fail("error.workflow_steps")

    normalized = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            fail("error.workflow_steps")
        kind = step.get("step_type")
        source = step.get("approver_source")
        assigned_users = runtime.normalize_workflow_users(
            source,
            step.get("approver_users"),
            step.get("approver_user"),
            user_names,
        )
        assigned_user = assigned_users[0] if assigned_users else ""
        assigned_role = checked_text(step.get("approver_role"), 140) if source == "Role" else ""
        if (source == "Role" and assigned_role not in roles) or source not in (
            "User", "Role", "Department Manager"
        ):
            fail("error.workflow_assignee")
        method = "Any" if kind == "Quotation" else (step.get("approval_method") or "Any")
        if method not in ("Any", "All"):
            fail("error.workflow_steps")
        normalized.append(
            {
                "step_order": index + 1,
                "step_name": checked_text(step.get("step_name"), 140, True),
                "step_type": kind,
                "approval_method": method,
                "approver_source": source,
                "approver_user": assigned_user,
                "approver_users": assigned_users,
                "approver_role": assigned_role,
                "send_email": workflow_flag(step.get("send_email", 0)),
            }
        )
    runtime.validate_steps(normalized)

    selector_source = data.get("selector_source") or "Role"
    selector_user = checked_text(data.get("selector_user"), 140) if selector_source == "User" else ""
    selector_role = checked_text(data.get("selector_role"), 140) if selector_source == "Role" else ""
    if (selector_source == "User" and selector_user not in user_names) or (
        selector_source == "Role" and selector_role not in roles
    ) or selector_source not in ("User", "Role"):
        fail("error.workflow_assignee")

    values = {
        "workflow_name": checked_text(data.get("workflow_name"), 140, True),
        "company": company,
        "department": department,
        "currency": "VND",
        "is_active": workflow_flag(data.get("is_active", 1)),
        "note": checked_text(data.get("note"), 2000),
        "selector_source": selector_source,
        "selector_user": selector_user,
        "selector_role": selector_role,
        "notify_requester": workflow_flag(data.get("notify_requester", 0)),
    }
    saved_steps = [{key: value for key, value in step.items() if key != "approver_users"} for step in normalized]
    saved_assignees = [
        {"step_order": step["step_order"], "user": name}
        for step in normalized
        for name in step["approver_users"]
    ]

    if data.get("name"):
        doc = workflow_admin_doc(user, data["name"], lock=True)
        if not data.get("expected_modified") or str(doc.modified) != str(data["expected_modified"]):
            fail("error.conflict")
        for key, value in values.items():
            doc.set(key, value)
        doc.set("steps", saved_steps)
        doc.set("assignees", saved_assignees)
        doc.save(ignore_permissions=True)
    else:
        key = checked_text(data.get("idempotency_key"), 32, True).lower()
        if len(key) != 32 or any(char not in "0123456789abcdef" for char in key):
            fail("error.idempotency")
        name = "PAWF-" + key
        frappe.db.sql("select name from `tabCompany` where name=%s for update", (company,))
        if frappe.db.exists(WORKFLOW, name):
            existing = workflow_admin_doc(user, name, lock=True)
            same_steps = workflow_step_signature(existing.steps, existing.assignees)
            requested_steps = workflow_step_signature(normalized)
            if (
                existing.owner != user
                or any((existing.get(field) or "") != (values[field] or "") for field in values)
                or same_steps != requested_steps
            ):
                fail("error.idempotency")
            register_referenced_roles(selector_source, selector_role, normalized)
            return workflow_admin_result(existing)
        doc = frappe.get_doc({"doctype": WORKFLOW, **values, "steps": saved_steps, "assignees": saved_assignees})
        doc.insert(ignore_permissions=True, set_name=name)

    register_referenced_roles(selector_source, selector_role, normalized)
    return workflow_admin_result(doc)


@frappe.whitelist(methods=["POST"])
def delete_approval_workflow(payload=None):
    """Delete an unused workflow while preserving request and instance history."""
    data = parse_payload(payload or "{}")
    doc = workflow_admin_doc(actor(), data.get("name"), lock=True)
    if not data.get("expected_modified") or str(doc.modified) != str(data["expected_modified"]):
        fail("error.workflow_delete_conflict")
    if frappe.db.exists("PA Purchase Request", {"selected_workflow": doc.name}) or frappe.db.exists(
        "PA Approval Instance", {"workflow": doc.name}
    ):
        fail("error.workflow_in_use")
    frappe.delete_doc(WORKFLOW, doc.name, ignore_permissions=True)
    return {"name": doc.name}
