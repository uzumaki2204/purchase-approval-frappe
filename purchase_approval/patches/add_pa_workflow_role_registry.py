"""Create the registry used to distinguish Purchase Approval Roles."""

from purchase_approval.install import ensure_doctypes, metadata


def execute():
    definition = next(row for row in metadata()["doctypes"] if row["name"] == "PA Workflow Role")
    ensure_doctypes({"doctypes": [definition]})
