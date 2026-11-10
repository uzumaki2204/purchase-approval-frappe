"""Upgrade installed approval and receiving actions to the ordered workflow."""

import json
from pathlib import Path

import frappe

from purchase_approval.install import message, metadata
from purchase_approval.patches.activate_step_notifications import function_span
from purchase_approval.patches.multi_user_workflow import merge_managed_script, script_lines


FUNCTIONS = {
    "pa_approval_action": "approval_action",
    "pa_receive_purchase_request": "receive_request",
}
BASELINES = Path(__file__).with_name("approval_receive_baselines.json")


def upgraded_script(name, current, target, baselines):
    function = FUNCTIONS[name]
    current_span = function_span(current, function)
    target_span = function_span(target, function)
    if current_span is None or target_span is None:
        return None
    current_block = current[slice(*current_span)]
    target_block = target[slice(*target_span)]
    if script_lines(current_block) == script_lines(target_block):
        return current
    version = "modern" if "action='is_modern'" in current_block else "legacy"
    merged = merge_managed_script(baselines[name][version], target_block, current_block)
    if merged is None:
        return None
    updated = current[: current_span[0]] + merged + current[current_span[1] :]
    try:
        compile(updated, name, "exec")
    except SyntaxError:
        return None
    return updated


def execute():
    baselines = json.loads(BASELINES.read_text(encoding="utf-8"))
    targets = {
        row["name"]: row["script"]
        for row in metadata()["server_scripts"]
        if row["name"] in FUNCTIONS
    }
    pending = []
    conflicts = []
    for name in FUNCTIONS:
        if not frappe.db.exists("Server Script", name):
            continue
        current = frappe.db.get_value("Server Script", name, "script") or ""
        updated = upgraded_script(name, current, targets[name], baselines)
        if updated is None:
            conflicts.append(f"Server Script {name}")
        elif script_lines(updated) != script_lines(current):
            pending.append((name, updated))
    if conflicts:
        frappe.throw(message("workflow_script_conflict", script=", ".join(conflicts)))
    for name, updated in pending:
        frappe.db.set_value("Server Script", name, "script", updated, update_modified=False)
    if pending:
        frappe.clear_cache()
