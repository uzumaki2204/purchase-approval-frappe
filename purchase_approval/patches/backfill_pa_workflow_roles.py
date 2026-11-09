"""Register default and already configured Purchase Approval Roles."""

from purchase_approval.workflow_roles import backfill


def execute():
    backfill()
