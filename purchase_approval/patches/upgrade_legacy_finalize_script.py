"""Upgrade the untouched v2.0.7 quotation script without replacing site edits."""

import hashlib
import json
from pathlib import Path

import frappe

from purchase_approval.install import metadata


SCRIPT = "pa_finalize_purchase_request"
LEGACY_SHA256 = json.loads(
    Path(__file__).with_name("v207_script_hashes.json").read_text(encoding="utf-8")
)["server_scripts"][SCRIPT]


def replacement(current, target):
    if not current or current == target:
        return None
    if hashlib.sha256(current.encode("utf-8")).hexdigest() != LEGACY_SHA256:
        return None
    return target


def execute():
    if not frappe.db.exists("Server Script", SCRIPT):
        return
    current = frappe.db.get_value("Server Script", SCRIPT, "script") or ""
    target = next(row["script"] for row in metadata()["server_scripts"] if row["name"] == SCRIPT)
    updated = replacement(current, target)
    if updated is None:
        return
    frappe.db.set_value("Server Script", SCRIPT, "script", updated, update_modified=False)
    frappe.clear_cache()
