"""Checks for workflow ordering, automatic handoff and assignment boundaries."""

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


fake_frappe = types.ModuleType("frappe")
fake_frappe.db = types.SimpleNamespace(get_value=lambda *_args, **_kwargs: None)
fake_frappe.utils = types.SimpleNamespace(now=lambda: "2026-11-07 10:00:00")
fake_frappe.throw = lambda text: (_ for _ in ()).throw(ValueError(text))
fake_frappe.whitelist = lambda **_kwargs: lambda fn: fn
fake_frappe.flags = types.SimpleNamespace(get=lambda _key: False)
sys.modules.setdefault("frappe", fake_frappe)
path = Path(__file__).resolve().parents[1] / "purchase_approval" / "workflow_runtime.py"
spec = importlib.util.spec_from_file_location("pa_workflow_runtime_test", path)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
sys.path.insert(0, str(path.parents[1]))
from purchase_approval.patches import configurable_request_workflow as migration


def step(order, kind, status="Pending", email=0):
    return types.SimpleNamespace(
        step_order=order, step_type=kind, status=status, send_email=email,
        approval_method="Any", completed_at=None,
    )


class WorkflowRuntimeTests(unittest.TestCase):
    def test_bridge_rejects_direct_http_calls(self):
        with self.assertRaises(ValueError):
            runtime.bridge("capabilities", user="other")
        with patch.object(runtime.frappe.flags, "get", return_value=True), patch.object(
            runtime, "validate_steps", return_value=None
        ) as validate:
            runtime.bridge("validate_steps", steps=[{"step_type": "Stock Check"}], payload="ignored")
        validate.assert_called_once()

    def test_migration_accepts_only_installer_size_variant(self):
        payload = json.loads((path.parent / "metadata" / "purchase_approval.json").read_text(encoding="utf-8"))
        source = next(row["script"] for row in payload["server_scripts"] if row["name"] == "pa_scope_query_size")
        adapted = source.replace("'Size'", "'ProductSize'").replace("`tabSize`", "`tabProductSize`")
        with patch.object(migration.frappe.db, "exists", side_effect=lambda _doctype, name: name == "pa_scope_query_size", create=True), patch.object(
            migration.frappe.db, "get_value", return_value=adapted, create=True
        ), patch.object(migration, "message", return_value="conflict"):
            self.assertEqual(migration.script_updates(payload), [])
        with patch.object(migration.frappe.db, "exists", side_effect=lambda _doctype, name: name == "pa_scope_query_size", create=True), patch.object(
            migration.frappe.db, "get_value", return_value="custom script", create=True
        ), patch.object(migration, "message", return_value="conflict"):
            with self.assertRaises(ValueError):
                migration.script_updates(payload)

    def test_rejects_invalid_step_orders(self):
        valid = [{"step_type": "Quotation", "approver_source": "Role", "approval_method": "Any"},
                 {"step_type": "Quote Approval", "approver_source": "User", "approval_method": "All"},
                 {"step_type": "Receiving", "approver_source": "Role", "approval_method": "Any"}]
        runtime.validate_steps(valid)
        runtime.validate_steps([valid[1]])  # Approval can use estimated prices without quotation.
        for invalid in (
            [],
            [valid[1], valid[0]],
            [valid[2], valid[1]],
            [valid[0], valid[2], valid[1]],
            [valid[0], valid[0]],
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                runtime.validate_steps(invalid)

    def test_handoff_advances_without_user_confirmation(self):
        request = types.SimpleNamespace(status="Pending Stock Check")
        handoff = step(2, "Purchase Handoff", email=1)
        quotation = step(3, "Quotation")
        instance = types.SimpleNamespace(steps=[step(1, "Stock Check", "Approved"), handoff, quotation],
                                         assignees=[], current_sequence=1, status="Pending", completed_at=None)
        saved = []
        notices = []
        with patch.object(runtime, "save", side_effect=lambda doc: saved.append(doc)), patch.object(
            runtime, "enqueue", side_effect=lambda *_args: notices.append(True)
        ):
            runtime.advance(request, instance)
        self.assertEqual(handoff.status, "Approved")
        self.assertEqual(instance.current_sequence, 3)
        self.assertEqual(request.status, "Pending Purchasing")
        self.assertEqual(len(saved), 2)
        self.assertEqual(len(notices), 2)

    def test_closes_when_no_steps_remain(self):
        request = types.SimpleNamespace(status="Pending Approval")
        instance = types.SimpleNamespace(steps=[step(1, "Quote Approval", "Approved")],
                                         current_sequence=1, status="Pending", completed_at=None)
        with patch.object(runtime, "save"), patch.object(runtime, "enqueue") as enqueue:
            runtime.advance(request, instance)
        self.assertEqual(request.status, "Closed")
        self.assertEqual(instance.status, "Approved")
        self.assertEqual(instance.current_sequence, 0)
        enqueue.assert_not_called()

    def test_only_assigned_user_gets_current_action(self):
        request = types.SimpleNamespace(status="Pending Stock Check", current_instance="PAI-1")
        instance = types.SimpleNamespace(steps=[step(1, "Stock Check")], current_sequence=1,
                                         assignees=[types.SimpleNamespace(user="checker", step_order=1, status="Pending")])
        with patch.object(runtime, "is_modern", return_value=True), patch.object(
            runtime.frappe, "get_doc", return_value=instance, create=True
        ), patch.object(runtime, "eligible_user", return_value=True):
            self.assertEqual(runtime.actions(request, "checker"), ["stock_check"])
            self.assertEqual(runtime.actions(request, "other"), [])

    def test_step_email_toggle_and_idempotency_key(self):
        request = types.SimpleNamespace(name="PA-1", requester="creator")
        instance = types.SimpleNamespace(name="PAI-1", assignees=[types.SimpleNamespace(step_order=1, user="checker", status="Pending")])
        current = step(1, "Stock Check")
        current.step_name = "Kiểm tra kho"
        created = []
        with patch.object(runtime.frappe.db, "exists", return_value=False, create=True), patch.object(
            runtime.frappe, "get_doc", side_effect=lambda doc: types.SimpleNamespace(insert=lambda **_kwargs: created.append(doc)), create=True
        ), patch.object(runtime, "tr", side_effect=lambda key: "Bước {step}" if key == "notification.step_body" else key):
            runtime.enqueue(request, instance, current)
            current.send_email = 1
            runtime.enqueue(request, instance, current)
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0]["notification_key"], "PAI-1:1:checker")
        self.assertEqual(created[0]["body"], "Bước Kiểm tra kho")

    def test_handoff_email_remains_valid_after_auto_advance(self):
        request = types.SimpleNamespace(status="Pending Purchasing", current_instance="PAI-1")
        handoff = step(2, "Purchase Handoff", "Approved", 1)
        instance = types.SimpleNamespace(name="PAI-1", steps=[handoff, step(3, "Quotation")], current_sequence=3,
                                         assignees=[types.SimpleNamespace(step_order=2, user="buyer", status="Pending")])
        outbox = types.SimpleNamespace(step_order=2, recipient="buyer")
        self.assertTrue(runtime.notification_active(request, instance, outbox))
        request.status = "Cancelled"
        self.assertFalse(runtime.notification_active(request, instance, outbox))

    def test_migration_keeps_existing_approval_sequence(self):
        original = [types.SimpleNamespace(step_type=None, step_order=index, step_name=name,
                                          approval_method=method, approver_source="User",
                                          approver_user=user, approver_role=None)
                    for index, name, method, user in ((1, "Manager", "Any", "manager"), (2, "Director", "All", "director"))]

        class Workflow:
            def __init__(self):
                self.steps = original
                self.saved = False

            def set(self, key, value):
                setattr(self, key, value)

            def append(self, key, value):
                getattr(self, key).append(types.SimpleNamespace(**value))

            def save(self, **_kwargs):
                self.saved = True

        workflow = Workflow()
        payload = {"translations": [{"message_key": "step." + kind, "language": "vi", "text": kind}
                                    for kind in runtime.KINDS]}
        with patch.object(migration.frappe, "get_all", return_value=[types.SimpleNamespace(name="WF-1")], create=True) as get_all, patch.object(
            migration.frappe, "get_doc", return_value=workflow, create=True
        ):
            migration.upgrade_workflows(payload)
        self.assertTrue(workflow.saved)
        self.assertEqual([step.step_type for step in workflow.steps],
                         ["Stock Check", "Purchase Handoff", "Quotation", "Quote Approval", "Quote Approval", "Receiving"])
        self.assertEqual([(step.step_name, step.approval_method, step.approver_user, step.send_email)
                          for step in workflow.steps[3:5]],
                         [("Manager", "Any", "manager", 1), ("Director", "All", "director", 1)])
        self.assertEqual(workflow.selector_role, "PA Purchasing")
        self.assertEqual(get_all.call_args.args[0], "PA Approval Workflow")


if __name__ == "__main__":
    unittest.main()
