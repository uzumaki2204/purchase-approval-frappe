"""Manage level-zero Purchase Approval DocType rights through Frappe permissions."""

import hashlib
import json

import frappe

from purchase_approval import workflow_roles
from purchase_approval.install import PURCHASE_APPROVAL_MODULES
from purchase_approval.workflow_api import actor, checked_text, fail, parse_payload, workflow_admin_scope


RIGHTS = (
    "select", "read", "write", "create", "delete", "submit", "cancel", "amend",
    "print", "email", "report", "import", "export", "share",
)
BASIC_RIGHTS = ("select", "read", "write", "create", "submit", "cancel")


def value(row, field, default=None):
    return row.get(field, default) if isinstance(row, dict) else getattr(row, field, default)


def authorize(data):
    user = actor()
    company = checked_text(data.get("company"), 140, True)
    department = checked_text(data.get("department"), 140) or None
    workflow_admin_scope(user, company, department)
    if user != "Administrator" and "System Manager" not in frappe.get_roles(user):
        fail("error.role_manage_permission")
    frappe.only_for("System Manager")
    role = checked_text(data.get("role_name"), 140, True)
    if role not in workflow_roles.registered_names() or not frappe.db.exists(
        "Role", {"name": role, "disabled": 0}
    ):
        fail("error.role_not_found")
    return role


def available_doctypes():
    rows = frappe.get_all(
        "DocType",
        filters={"module": ["in", PURCHASE_APPROVAL_MODULES], "istable": 0, "name": ["like", "PA %"]},
        fields=["name", "is_submittable", "allow_import", "issingle"],
        order_by="name asc",
        limit_page_length=0,
    )
    return {row.name: row for row in rows if row.name.startswith("PA ")}


def matrix(role, doctypes):
    from frappe.permissions import get_all_perms

    by_doctype = {name: [] for name in doctypes}
    for rule in get_all_perms(role):
        if rule.parent in by_doctype:
            by_doctype[rule.parent].append(rule)

    rows = []
    signature = []
    for name, definition in doctypes.items():
        rules = by_doctype[name]
        base = [rule for rule in rules if not int(value(rule, "permlevel") or 0) and not int(value(rule, "if_owner") or 0)]
        rights = {right: int(bool(value(base[0], right))) if base else 0 for right in RIGHTS}
        rows.append({
            "doctype": name,
            "rights": rights,
            "has_rule": bool(base),
            "locked": len(base) > 1,
            "has_advanced": len(rules) > len(base),
            "is_submittable": bool(definition.is_submittable),
            "allow_import": bool(definition.allow_import),
            "issingle": bool(definition.issingle),
        })
        signature.append({
            "doctype": name,
            "rules": sorted(
                [
                    (value(rule, "name"), int(value(rule, "permlevel") or 0), int(value(rule, "if_owner") or 0),
                     tuple(int(bool(value(rule, right))) for right in RIGHTS))
                    for rule in rules
                ],
                key=lambda item: (item[1], item[2], item[0]),
            ),
        })
    revision = hashlib.sha256(json.dumps(signature, ensure_ascii=False).encode("utf-8")).hexdigest()
    return {"role_name": role, "rows": rows, "revision": revision}


def normalized_changes(changes, rows):
    if not isinstance(changes, list) or len(changes) > len(rows):
        fail("error.role_permissions_invalid")
    current = {row["doctype"]: row for row in rows}
    seen = set()
    result = []
    for change in changes:
        if not isinstance(change, dict) or set(change) != {"doctype", "rights"}:
            fail("error.role_permissions_invalid")
        name = change["doctype"]
        if not isinstance(name, str) or name not in current or name in seen:
            fail("error.role_permissions_invalid")
        seen.add(name)
        row = current[name]
        if row["locked"]:
            fail("error.role_permissions_advanced")
        rights = change["rights"]
        if not isinstance(rights, dict) or set(rights) != set(RIGHTS) or any(
            rights[key] not in (0, 1) or isinstance(rights[key], bool) for key in RIGHTS
        ):
            fail("error.role_permissions_invalid")
        if not any(rights.values()) and row["has_advanced"]:
            fail("error.role_permissions_invalid")
        if any(rights.values()):
            if not any(rights[key] for key in BASIC_RIGHTS):
                fail("error.role_permissions_invalid")
            if (rights["cancel"] and not rights["submit"]) or (
                any(rights[key] for key in ("submit", "cancel", "amend")) and not rights["write"]
            ) or (rights["import"] and not rights["create"]):
                fail("error.role_permissions_invalid")
            if not row["is_submittable"] and any(rights[key] for key in ("submit", "cancel", "amend")):
                fail("error.role_permissions_invalid")
            if not row["allow_import"] and rights["import"]:
                fail("error.role_permissions_invalid")
            if row["issingle"] and any(rights[key] for key in ("report", "import", "export")):
                fail("error.role_permissions_invalid")
        if rights != row["rights"]:
            result.append((name, rights, row["has_rule"]))
    return result


def apply_change(doctype, role, rights, had_rule):
    from frappe.core.doctype.custom_docperm.custom_docperm import update_custom_docperm
    from frappe.core.doctype.doctype.doctype import validate_permissions_for_doctype
    from frappe.core.page.permission_manager.permission_manager import remove
    from frappe.permissions import add_permission, setup_custom_perms

    if not any(rights.values()):
        if had_rule:
            remove(doctype, role, 0, if_owner=0)
        return

    if not had_rule:
        first = next(right for right in BASIC_RIGHTS if rights[right])
        add_permission(doctype, role, 0, ptype=first)
    else:
        setup_custom_perms(doctype)

    name = frappe.db.get_value(
        "Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0}
    )
    if not name:
        fail("error.role_permissions_conflict")
    update_custom_docperm(name, rights)
    validate_permissions_for_doctype(doctype)


@frappe.whitelist(methods=["POST"])
def get_role_permissions(payload=None):
    data = parse_payload(payload or "{}")
    role = authorize(data)
    return matrix(role, available_doctypes())


@frappe.whitelist(methods=["POST"])
def save_role_permissions(payload=None):
    data = parse_payload(payload or "{}")
    role = authorize(data)
    current = matrix(role, available_doctypes())
    if data.get("revision") != current["revision"]:
        fail("error.role_permissions_conflict")
    changes = normalized_changes(data.get("changes"), current["rows"])
    for doctype, rights, had_rule in changes:
        apply_change(doctype, role, rights, had_rule)
    return matrix(role, available_doctypes())
