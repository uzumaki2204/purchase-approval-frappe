"""Upgrade the installed functions needed to enter and use the first PA steps."""

import json
from pathlib import Path

import frappe

from purchase_approval.install import message, metadata
from purchase_approval.patches.multi_user_workflow import merge_managed_script, script_lines


BASELINES = Path(__file__).with_name("notification_delivery_baselines.json")
SCRIPTS = {
    "pa_submit_purchase_request": ("submit_request", "request_actions"),
    "pa_notification_worker": ("notification_worker",),
    "pa_get_context": ("read_capabilities", "get_context"),
    "pa_get_purchase_request": ("can_read", "request_actions"),
    "pa_list_purchase_requests": ("can_read",),
    "pa_get_purchase_request_pdf": ("can_read",),
}
MODERN_MARKERS = {
    "submit_request": "action='start_submitted'",
    "notification_worker": "action='notification_active'",
    "read_capabilities": "action='capabilities'",
    "get_context": "action='capabilities'",
    "can_read": "'PA Approval Assignee'",
    "request_actions": "action='actions'",
}


def function_span(source, name):
    lines = source.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith(f"    def {name}(")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("    def ")),
        len(lines),
    )
    return sum(map(len, lines[:start])), sum(map(len, lines[:end]))


def upgraded_script(name, current, target, baselines):
    updated = current
    for function in SCRIPTS[name]:
        current_span = function_span(updated, function)
        target_span = function_span(target, function)
        if current_span is None or target_span is None:
            return None
        current_block = updated[slice(*current_span)]
        target_block = target[slice(*target_span)]
        if script_lines(current_block) == script_lines(target_block):
            continue
        baseline = baselines[name][function][
            "modern" if MODERN_MARKERS[function] in current_block else "legacy"
        ]
        merged = merge_managed_script(baseline, target_block, current_block)
        if merged is None:
            return None
        updated = updated[: current_span[0]] + merged + updated[current_span[1] :]
    try:
        compile(updated, name, "exec")
    except SyntaxError:
        return None
    return updated


def execute():
    baselines = json.loads(BASELINES.read_text(encoding="utf-8"))
    targets = {row["name"]: row["script"] for row in metadata()["server_scripts"] if row["name"] in SCRIPTS}
    pending = []
    conflicts = []
    for name in SCRIPTS:
        if not frappe.db.exists("Server Script", name):
            continue
        current = frappe.db.get_value("Server Script", name, "script") or ""
        updated = upgraded_script(name, current, targets[name], baselines)
        if updated is None:
            conflicts.append(f"Server Script {name}")
        elif updated != current:
            pending.append((name, updated))
    if conflicts:
        frappe.throw(message("workflow_script_conflict", script=", ".join(conflicts)))
    for name, updated in pending:
        frappe.db.set_value("Server Script", name, "script", updated, update_modified=False)
    if pending:
        frappe.clear_cache()
