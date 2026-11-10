"""Allow the installed workflow guards to accept the newer business APIs."""

import ast
import re

import frappe

from purchase_approval.install import message, metadata


GUARDS = ("pa_instance_guard", "pa_history_guard", "pa_request_validate")
COMMANDS_LINE = re.compile(r"^    COMMANDS = ([^\r\n]*)(\r?\n)", re.MULTILINE)
LEGACY_COMMAND_COUNT = 8


def commands_match(source):
    matches = list(COMMANDS_LINE.finditer(source))
    if len(matches) != 1:
        return None
    try:
        commands = ast.literal_eval(matches[0].group(1))
    except (SyntaxError, ValueError):
        return None
    if not isinstance(commands, list) or not all(isinstance(item, str) for item in commands):
        return None
    return matches[0], commands


def upgraded_script(current, target):
    current_result = commands_match(current)
    target_result = commands_match(target)
    if not current_result or not target_result:
        return None
    current_match, current_commands = current_result
    _, target_commands = target_result
    # The deployed guards contain the original eight API paths. Accept only
    # that known prefix (or an already partially upgraded prefix), leaving
    # unrelated script content untouched and rejecting unknown API paths.
    if len(current_commands) < LEGACY_COMMAND_COUNT or target_commands[: len(current_commands)] != current_commands:
        return None
    if current_commands == target_commands:
        return current
    updated = current[: current_match.start(1)] + repr(target_commands) + current[current_match.end(1) :]
    try:
        compile(updated, "workflow guard", "exec")
    except SyntaxError:
        return None
    return updated


def execute():
    targets = {
        row["name"]: row["script"]
        for row in metadata()["server_scripts"]
        if row["name"] in GUARDS
    }
    pending = []
    conflicts = []
    for name in GUARDS:
        if not frappe.db.exists("Server Script", name):
            continue
        current = frappe.db.get_value("Server Script", name, "script") or ""
        updated = upgraded_script(current, targets[name])
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
