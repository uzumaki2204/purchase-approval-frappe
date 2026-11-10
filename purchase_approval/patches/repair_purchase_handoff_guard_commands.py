"""Upgrade guards already migrated before the purchase handoff API existed."""

from purchase_approval.patches.repair_workflow_guard_commands import execute as upgrade_guards


def execute():
    upgrade_guards()
