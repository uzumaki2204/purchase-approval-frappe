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
from purchase_approval.patches import multi_user_workflow as multi_user_migration


def step(order, kind, status="Pending", email=0, method="Any"):
    return types.SimpleNamespace(
        step_order=order, step_type=kind, status=status, send_email=email,
        approval_method=method, completed_at=None,
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

    def test_advance_waits_for_manual_handoff(self):
        request = types.SimpleNamespace(status="Pending Stock Check")
        handoff = step(2, "Purchase Handoff", email=1)
        quotation = step(3, "Quotation")
        instance = types.SimpleNamespace(steps=[step(1, "Stock Check", "Approved"), handoff, quotation],
                                         assignees=[types.SimpleNamespace(step_order=2, user="buyer", status="Pending")],
                                         current_sequence=1, status="Pending", completed_at=None)
        saved = []
        notices = []
        with patch.object(runtime, "save", side_effect=lambda doc: saved.append(doc)), patch.object(
            runtime, "enqueue", side_effect=lambda *_args: notices.append(True)
        ):
            runtime.advance(request, instance)
        self.assertEqual(handoff.status, "Pending")
        self.assertEqual(instance.current_sequence, 2)
        self.assertEqual(request.status, "Pending Purchasing")
        self.assertEqual(len(saved), 2)
        self.assertEqual(len(notices), 1)

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

    def test_handoff_action_is_limited_to_pending_assignees(self):
        request = types.SimpleNamespace(status="Pending Purchasing", current_instance="PAI-1")
        instance = types.SimpleNamespace(steps=[step(2, "Purchase Handoff")], current_sequence=2,
                                         assignees=[types.SimpleNamespace(user="buyer", step_order=2, status="Pending")])
        with patch.object(runtime, "is_modern", return_value=True), patch.object(
            runtime.frappe, "get_doc", return_value=instance, create=True
        ), patch.object(runtime, "eligible_user", return_value=True):
            self.assertEqual(runtime.actions(request, "buyer"), ["confirm_handoff"])
            self.assertEqual(runtime.actions(request, "other"), [])

    def test_user_source_resolves_selected_users_and_legacy_fallback(self):
        workflow_step = types.SimpleNamespace(approver_source="User", approver_user="legacy", step_type="Stock Check")
        with patch.object(runtime, "eligible_user", return_value=True):
            self.assertEqual(runtime.assignees(workflow_step, types.SimpleNamespace(requester="creator"), ["second", "first"]), ["first", "second"])
            self.assertEqual(runtime.assignees(workflow_step, types.SimpleNamespace(requester="creator")), ["legacy"])

    def test_user_selection_validation_rejects_duplicates_and_out_of_scope_users(self):
        self.assertEqual(runtime.normalize_workflow_users("User", ["one", "two"], None, ["one", "two"]), ["one", "two"])
        self.assertEqual(runtime.normalize_workflow_users("User", None, "one", ["one"]), ["one"])
        self.assertEqual(runtime.normalize_workflow_users("Role", ["ignored"], None, []), [])
        for selected, allowed in ((["one", "one"], ["one"]), (["outside"], ["one"]), ([], ["one"])):
            with self.subTest(selected=selected, allowed=allowed), self.assertRaises(ValueError):
                runtime.normalize_workflow_users("User", selected, None, allowed)

    def test_any_step_completes_after_first_assignee(self):
        request = types.SimpleNamespace(status="Pending Stock Check")
        current = step(1, "Stock Check", method="Any")
        instance = types.SimpleNamespace(name="PAI-1", steps=[current], current_sequence=1, status="Pending",
                                         assignees=[types.SimpleNamespace(user="one", step_order=1, status="Pending"),
                                                    types.SimpleNamespace(user="two", step_order=1, status="Pending")])
        with patch.object(runtime, "eligible_user", return_value=True), patch.object(runtime, "save"), patch.object(
            runtime, "advance"
        ) as advance, patch.object(runtime.frappe, "get_all", return_value=[], create=True):
            self.assertTrue(runtime.finish_step(request, instance, "one", "Checked"))
        self.assertEqual(current.status, "Approved")
        self.assertEqual([row.status for row in instance.assignees], ["Approved", "Skipped"])
        advance.assert_called_once_with(request, instance)

    def test_all_step_waits_for_every_assignee_and_keeps_other_email(self):
        request = types.SimpleNamespace(status="Pending Stock Check")
        current = step(1, "Stock Check", method="All")
        first = types.SimpleNamespace(user="one", step_order=1, status="Pending", acted_at=None, comment=None)
        second = types.SimpleNamespace(user="two", step_order=1, status="Pending", acted_at=None, comment=None)
        instance = types.SimpleNamespace(name="PAI-1", steps=[current], current_sequence=1, status="Pending", assignees=[first, second])
        notices = [types.SimpleNamespace(name="n1", recipient="one"), types.SimpleNamespace(name="n2", recipient="two")]
        with patch.object(runtime, "eligible_user", return_value=True), patch.object(runtime, "save"), patch.object(
            runtime, "advance"
        ) as advance, patch.object(runtime.frappe, "get_all", return_value=notices, create=True), patch.object(
            runtime.frappe.db, "set_value", create=True
        ) as set_value:
            self.assertFalse(runtime.finish_step(request, instance, "one", "Checked"))
            self.assertEqual(current.status, "Pending")
            self.assertEqual((first.status, second.status), ("Approved", "Pending"))
            self.assertEqual([call.args[1] for call in set_value.call_args_list], ["n1"])
            advance.assert_not_called()
            self.assertTrue(runtime.finish_step(request, instance, "two", "Confirmed"))
        self.assertEqual(current.status, "Approved")
        self.assertEqual((first.status, second.status), ("Approved", "Approved"))
        advance.assert_called_once_with(request, instance)

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

    def test_handoff_email_is_active_while_waiting_for_confirmation(self):
        request = types.SimpleNamespace(status="Pending Purchasing", current_instance="PAI-1", company="C1", department="D1")
        handoff = step(2, "Purchase Handoff", email=1)
        instance = types.SimpleNamespace(name="PAI-1", status="Pending", steps=[handoff], current_sequence=2,
                                         assignees=[types.SimpleNamespace(step_order=2, user="buyer", status="Pending")])
        outbox = types.SimpleNamespace(step_order=2, recipient="buyer")
        with patch.object(runtime, "eligible_user", return_value=True):
            self.assertTrue(runtime.notification_active(request, instance, outbox))
        instance.current_sequence = 3
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

    def test_multi_user_migration_backfills_workflow_assignments_only(self):
        class Workflow:
            def __init__(self):
                self.assignees = []
                self.steps = [
                    types.SimpleNamespace(step_order=1, step_type="Stock Check", approval_method="All", approver_source="User", approver_user="checker"),
                    types.SimpleNamespace(step_order=2, step_type="Quote Approval", approval_method="All", approver_source="User", approver_user="approver"),
                    types.SimpleNamespace(step_order=3, step_type="Quotation", approval_method="All", approver_source="User", approver_user="buyer"),
                ]
                self.saved = 0

            def append(self, fieldname, values):
                getattr(self, fieldname).append(types.SimpleNamespace(**values))

            def save(self, **_kwargs):
                self.saved += 1

        workflow = Workflow()
        with patch.object(multi_user_migration.frappe, "get_all", return_value=[types.SimpleNamespace(name="WF-1")], create=True), patch.object(
            multi_user_migration.frappe, "get_doc", return_value=workflow, create=True
        ):
            multi_user_migration.backfill_workflows()
            multi_user_migration.backfill_workflows()
        self.assertEqual([(row.step_order, row.user) for row in workflow.assignees], [(1, "checker"), (2, "approver"), (3, "buyer")])
        self.assertEqual([row.approval_method for row in workflow.steps], ["Any", "All", "Any"])
        self.assertEqual(workflow.saved, 1)

    def test_multi_user_metadata_stores_assignments_on_workflow_parent(self):
        payload = json.loads((path.parent / "metadata" / "purchase_approval.json").read_text(encoding="utf-8"))
        workflow = next(row for row in payload["doctypes"] if row["name"] == "PA Approval Workflow")
        step = next(row for row in payload["doctypes"] if row["name"] == "PA Approval Workflow Step")
        assignment = next(row for row in payload["doctypes"] if row["name"] == "PA Approval Workflow Assignee")
        self.assertEqual(next(row["options"] for row in workflow["fields"] if row["fieldname"] == "assignees"), assignment["name"])
        self.assertFalse(any(row["fieldname"] == "approver_users" for row in step["fields"]))
        self.assertEqual({row["fieldname"] for row in assignment["fields"]}, {"step_order", "user"})

    def test_multi_user_migration_merges_non_overlapping_script_edits(self):
        base = 'def managed():\n    return "old"\n\ndef custom():\n    return "default"\n'
        target = base.replace('return "old"', 'return "new"')
        current = base.replace('return "default"', 'return "site"') + "# local footer\n"
        merged = multi_user_migration.merge_managed_script(base, target, current)
        self.assertIn('return "new"', merged)
        self.assertIn('return "site"', merged)
        self.assertIn("# local footer", merged)

    def test_multi_user_migration_rejects_overlapping_script_edits(self):
        base = 'def managed():\n    return "old"\n'
        target = base.replace('return "old"', 'return "new"')
        current = base.replace('return "old"', 'return "site"')
        self.assertIsNone(multi_user_migration.merge_managed_script(base, target, current))

    def test_multi_user_migration_baselines_match_v209_script_hashes(self):
        import hashlib

        baseline = json.loads((path.parent / "patches" / "multi_user_workflow_base.json").read_text(encoding="utf-8"))
        for name, expected in multi_user_migration.OLD_SERVER_SCRIPT_SHA256.items():
            self.assertEqual(hashlib.sha256(baseline[name].encode("utf-8")).hexdigest(), expected)

    def test_multi_user_migration_updates_conflicted_scripts_without_losing_other_edits(self):
        payload = json.loads((path.parent / "metadata" / "purchase_approval.json").read_text(encoding="utf-8"))
        baseline = json.loads((path.parent / "patches" / "multi_user_workflow_base.json").read_text(encoding="utf-8"))
        names = set(multi_user_migration.OLD_SERVER_SCRIPT_SHA256)
        current = {
            name: source.replace(
                "# All business writes use the request lock and Frappe's POST transaction.",
                "# All business writes use the request lock and Frappe's POST transaction. Site customization.",
            )
            for name, source in baseline.items()
        }
        updated = []
        with patch.object(multi_user_migration.frappe.db, "exists", side_effect=lambda _doctype, name: name in names, create=True), patch.object(
            multi_user_migration.frappe.db,
            "get_value",
            side_effect=lambda _doctype, name, *_args, **_kwargs: current[name],
            create=True,
        ), patch.object(multi_user_migration.frappe.db, "set_value", side_effect=lambda _doctype, name, field, source, **_kwargs: updated.append((name, source)), create=True):
            multi_user_migration.update_server_scripts(payload)
        self.assertEqual({name for name, _source in updated}, names)
        for name, source in updated:
            self.assertIn("Site customization.", source)
        self.assertIn("for assigned in doc.assignees:", dict(updated)["pa_get_approval_workflow"])
        self.assertIn("normalize_workflow_users", dict(updated)["pa_save_approval_workflow"])
        self.assertIn("if completed:", dict(updated)["pa_receive_purchase_request"])


if __name__ == "__main__":
    unittest.main()
