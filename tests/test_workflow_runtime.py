"""Checks for workflow ordering, automatic handoff and assignment boundaries."""

import importlib.util
import hashlib
import json
import re
import sys
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


fake_frappe = types.ModuleType("frappe")
fake_frappe.db = types.SimpleNamespace(get_value=lambda *_args, **_kwargs: None)
fake_frappe.utils = types.SimpleNamespace(now=lambda: "2026-11-07 10:00:00")
fake_frappe.throw = lambda text: (_ for _ in ()).throw(ValueError(text))
fake_frappe.whitelist = lambda **_kwargs: lambda fn: fn
fake_frappe.flags = types.SimpleNamespace(get=lambda _key: False)
fake_frappe.DuplicateEntryError = type("DuplicateEntryError", (Exception,), {})
sys.modules.setdefault("frappe", fake_frappe)
path = Path(__file__).resolve().parents[1] / "purchase_approval" / "workflow_runtime.py"
spec = importlib.util.spec_from_file_location("pa_workflow_runtime_test", path)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
sys.path.insert(0, str(path.parents[1]))
from purchase_approval.patches import configurable_request_workflow as migration
from purchase_approval.patches import multi_user_workflow as multi_user_migration
from purchase_approval.patches import add_workflow_roles_menu as roles_menu_migration
from purchase_approval.patches import add_pa_workflow_role_registry as role_schema_migration
from purchase_approval.patches import upgrade_legacy_finalize_script as finalize_migration
from purchase_approval.patches import activate_step_notifications as notification_migration
from purchase_approval.patches import repair_purchase_request_status_options as status_migration
from purchase_approval import install, notification_delivery, quotation_preflight, role_permissions, workflow_api, workflow_roles


def localized_error(key):
    messages = json.loads((path.parent / "ui-translations.json").read_text(encoding="utf-8"))["messages"]
    return re.escape(messages[key])


def step(order, kind, status="Pending", email=0, method="Any"):
    return types.SimpleNamespace(
        step_order=order, step_type=kind, status=status, send_email=email,
        approval_method=method, completed_at=None,
    )


class WorkflowRuntimeTests(unittest.TestCase):
    def test_begin_serializes_workflow_dates_before_inserting_instance(self):
        created = datetime(2026, 11, 10, 14, 57, 34)
        definition = types.SimpleNamespace(
            step_order=1, step_type="Stock Check", step_name="Check stock",
            approval_method="Any", send_email=1,
        )
        workflow = types.SimpleNamespace(
            name="WF-1", workflow_name="Workflow", modified=created,
            steps=[definition], assignees=[], reload=lambda: None,
            as_dict=lambda: {
                "name": "WF-1", "creation": created, "notify_requester": 1,
                "steps": [{"step_name": "Check stock", "modified": created}],
            },
        )
        request = types.SimpleNamespace(name="PA-1", company="C1", department="D1", revision=1)
        instance = types.SimpleNamespace(name="PAI-1", flags=types.SimpleNamespace())

        def get_doc(values):
            for key, value in values.items():
                setattr(instance, key, value)
            return instance

        def append(field, values):
            getattr(instance, field).append(types.SimpleNamespace(**values))

        def insert(**_kwargs):
            json.dumps(instance.workflow_snapshot)

        instance.append = append
        instance.insert = insert
        with patch.object(runtime.frappe.db, "sql", create=True), patch.object(
            runtime.frappe, "as_json", side_effect=lambda value: json.dumps(value, default=str), create=True
        ), patch.object(runtime.frappe, "get_doc", side_effect=get_doc, create=True), patch.object(
            runtime, "candidates", return_value=[workflow]
        ), patch.object(runtime, "assignees", return_value=["checker"]), patch.object(
            runtime, "advance"
        ), patch.object(runtime, "enqueue"):
            self.assertIs(runtime.begin(request, workflow, "Automatic"), instance)
        self.assertEqual(instance.workflow_snapshot["workflow_schema"], 2)
        self.assertEqual(instance.workflow_snapshot["notify_requester"], 1)
        self.assertEqual(instance.workflow_snapshot["creation"], str(created))
        self.assertEqual(instance.workflow_snapshot["steps"][0]["modified"], str(created))
        self.assertEqual([(row.step_order, row.user) for row in instance.assignees], [(1, "checker")])

    def test_status_migration_repairs_effective_choices_and_preserves_custom_values(self):
        old = "Draft\nPending Purchasing\nPending Approval\nApproved\nClosed\nReturned\nRejected\nCancelled\nCustom State"
        expected = "Draft\nPending Workflow Selection\nPending Stock Check\nPending Purchasing\nPending Approval\nApproved\nClosed\nReturned\nRejected\nCancelled"
        values = {"DocField": old, "Property Setter": old}
        writes = []

        def get_value(_doctype, _filters, _fields, **_kwargs):
            return types.SimpleNamespace(name="FIELD-1", options=values["DocField"])

        def set_value(doctype, _name, _field, value, **_kwargs):
            values[doctype] = value
            writes.append(doctype)

        def get_meta(_doctype):
            return types.SimpleNamespace(get_field=lambda _field: types.SimpleNamespace(options=values["Property Setter"]))

        payload = {"doctypes": [{"name": status_migration.DOCTYPE, "fields": [
            {"fieldname": "status", "options": expected}
        ]}]}
        with patch.object(status_migration, "metadata", return_value=payload), patch.object(
            status_migration.frappe.db, "get_value", side_effect=get_value
        ), patch.object(status_migration.frappe.db, "set_value", side_effect=set_value, create=True), patch.object(
            status_migration.frappe, "get_all", return_value=[types.SimpleNamespace(name="SET-1", value=old)], create=True
        ) as setters, patch.object(status_migration.frappe, "get_meta", side_effect=get_meta, create=True), patch.object(
            status_migration.frappe, "clear_cache", create=True
        ):
            status_migration.execute()
            self.assertEqual(writes, ["DocField", "Property Setter"])
            self.assertEqual(values["Property Setter"], expected + "\nCustom State")
            setters.return_value[0].value = values["Property Setter"]
            status_migration.execute()
            self.assertEqual(writes, ["DocField", "Property Setter"])

    def test_capabilities_handles_legacy_approval_step_without_step_type(self):
        assignee = types.SimpleNamespace(user="approver", status="Pending", step_order=1)
        legacy_step = types.SimpleNamespace(step_order=1, step_name="Manager", status="Pending")
        instance = types.SimpleNamespace(
            status="Pending", request="PA-1", current_sequence=1,
            steps=[legacy_step], assignees=[assignee], workflow_snapshot='{"workflow_schema": 1}',
        )
        request = types.SimpleNamespace(status="Pending Approval")

        def get_all(doctype, **_kwargs):
            return [types.SimpleNamespace(parent="PAI-1")] if doctype == "PA Approval Assignee" else []

        def get_doc(doctype, _name):
            return instance if doctype == runtime.INSTANCE else request

        with patch.object(runtime.frappe, "get_all", side_effect=get_all, create=True), patch.object(
            runtime.frappe, "get_doc", side_effect=get_doc, create=True
        ), patch.object(runtime, "eligible_user", return_value=True):
            self.assertTrue(runtime.capabilities("approver")["approvals"])
            instance.workflow_snapshot = '{"workflow_schema": 2}'
            self.assertFalse(runtime.capabilities("approver")["approvals"])
            legacy_step.step_type = "Quotation"
            self.assertTrue(runtime.capabilities("approver")["purchasing"])
            self.assertFalse(runtime.capabilities("approver")["approvals"])

    def test_finalize_patch_upgrades_known_legacy_script_only(self):
        self.assertEqual(finalize_migration.LEGACY_SHA256, "fb9e7e0a9965d95d2b1123d0b16c01f72c213c45d698051272472c14a3ec38b6")
        managed = next(row["script"] for row in install.metadata()["server_scripts"] if row["name"] == finalize_migration.SCRIPT)
        self.assertIn("if step.step_type and step.step_type != 'Quote Approval':", managed)
        old = "legacy finalized script"
        target = "current finalized script"
        with patch.object(finalize_migration, "LEGACY_SHA256", hashlib.sha256(old.encode("utf-8")).hexdigest()), patch.object(
            finalize_migration.frappe.db, "exists", return_value=True, create=True
        ), patch.object(finalize_migration.frappe.db, "get_value", return_value=old, create=True), patch.object(
            finalize_migration, "metadata", return_value={"server_scripts": [{"name": finalize_migration.SCRIPT, "script": target}]}
        ), patch.object(finalize_migration.frappe.db, "set_value", create=True) as save, patch.object(
            finalize_migration.frappe, "clear_cache", create=True
        ) as clear:
            finalize_migration.execute()
            save.assert_called_once_with("Server Script", finalize_migration.SCRIPT, "script", target, update_modified=False)
            clear.assert_called_once_with()
            self.assertIsNone(finalize_migration.replacement(old + "\n# site customization", target))
            self.assertIsNone(finalize_migration.replacement(target, target))

    def test_quotation_override_is_limited_to_active_step_and_super_users(self):
        request = types.SimpleNamespace(status="Pending Purchasing", current_instance="PAI-1", company="C1", department="D1")
        current = step(2, "Quotation")
        instance = types.SimpleNamespace(steps=[current], current_sequence=2, status="Pending", assignees=[
            types.SimpleNamespace(user="buyer", step_order=2, status="Pending")
        ])
        with patch.object(runtime, "is_modern", return_value=True), patch.object(
            runtime.frappe, "get_doc", return_value=instance, create=True
        ), patch.object(runtime, "eligible_user", return_value=True), patch.object(
            runtime, "roles", side_effect=lambda user: {"PA Super Admin"} if user == "super" else set()
        ):
            self.assertEqual(runtime.actions(request, "Administrator"), ["finalize"])
            self.assertEqual(runtime.actions(request, "super"), ["finalize"])
            self.assertEqual(runtime.actions(request, "buyer"), ["finalize"])
            self.assertEqual(runtime.actions(request, "other"), [])
            current.step_type = "Quote Approval"
            self.assertEqual(runtime.actions(request, "Administrator"), [])
            current.step_type = "Quotation"
            instance.status = "Approved"
            self.assertEqual(runtime.actions(request, "Administrator"), [])
            instance.status = "Pending"
            request.status = "Closed"
            self.assertEqual(runtime.actions(request, "Administrator"), [])
            request.status = "Pending Purchasing"
        instance.status = "Pending"
        with patch.object(runtime, "is_modern", return_value=True), patch.object(
            runtime.frappe, "get_doc", return_value=instance, create=True
        ), patch.object(runtime, "eligible_user", return_value=False):
            self.assertEqual(runtime.actions(request, "Administrator"), [])

    def test_unassigned_admin_quotation_records_actor_and_skips_other_assignee(self):
        request = types.SimpleNamespace(status="Pending Purchasing")
        current = step(2, "Quotation")
        buyer = types.SimpleNamespace(user="buyer", step_order=2, status="Pending")
        instance = types.SimpleNamespace(name="PAI-1", steps=[current], current_sequence=2,
                                         status="Pending", assignees=[buyer])
        instance.append = lambda _field, data: instance.assignees.append(types.SimpleNamespace(**data))
        with patch.object(runtime, "eligible_user", return_value=True), patch.object(
            runtime, "advance"
        ) as advance, patch.object(runtime.frappe, "get_all", return_value=[], create=True):
            self.assertTrue(runtime.finish_step(request, instance, "Administrator"))
        self.assertEqual([(row.user, row.status) for row in instance.assignees],
                         [("buyer", "Skipped"), ("Administrator", "Approved")])
        advance.assert_called_once_with(request, instance)

    def test_quotation_preflight_reports_missing_legacy_approver_before_write(self):
        request = types.SimpleNamespace(name="PA-1", company="C1", department="D1", currency="VND",
                                        requester="creator", modified="2026-11-10 10:00:00", revision=3,
                                        status="Pending Purchasing", selected_workflow="WF-1", current_instance=None)
        approval = types.SimpleNamespace(step_order=4, step_name="Duyệt báo giá", step_type="Quote Approval",
                                         approver_source="Role", approver_role="PA Approver")
        workflow = types.SimpleNamespace(name="WF-1", steps=[approval])
        data = {"name": request.name, "expected_modified": request.modified,
                "expected_revision": request.revision, "selected_workflow": workflow.name}
        with patch.object(quotation_preflight, "actor", return_value="Administrator"), patch.object(
            quotation_preflight.frappe.db, "exists", return_value=True, create=True
        ), patch.object(quotation_preflight.frappe, "get_doc", return_value=request, create=True), patch.object(
            quotation_preflight, "legacy_scope", return_value=True
        ), patch.object(quotation_preflight.runtime, "is_modern", return_value=False), patch.object(
            quotation_preflight.runtime, "candidates", return_value=[workflow]
        ), patch.object(quotation_preflight, "step_candidates", return_value=["creator", "disabled", "outside"]), patch.object(
            quotation_preflight, "legacy_approver", side_effect=lambda user, _request: user == "creator"
        ):
            result = quotation_preflight.check_quotation_approval(data)
            self.assertFalse(result["ready"])
            self.assertEqual(result["missing"], [{"step_order": 4, "step_name": "Duyệt báo giá",
                                                   "source": "Role", "target": "PA Approver"}])
            with patch.object(quotation_preflight, "legacy_approver", side_effect=lambda user, _request: user == "outside"):
                self.assertTrue(quotation_preflight.check_quotation_approval(data)["ready"])
            workflow.steps = []
            self.assertTrue(quotation_preflight.check_quotation_approval(data)["no_approval_step"])
            data["expected_revision"] = 2
            with self.assertRaises(ValueError):
                quotation_preflight.check_quotation_approval(data)

    def test_legacy_approver_requires_active_scoped_user_and_approval_role(self):
        request = types.SimpleNamespace(company="C1", department="D1", requester="creator")
        with patch.object(quotation_preflight.frappe.db, "get_value", side_effect=lambda _doctype, user, _field: user != "disabled"), patch.object(
            quotation_preflight, "legacy_scope", side_effect=lambda user, _request: user != "outside"
        ), patch.object(quotation_preflight, "is_super_user", return_value=False), patch.object(
            quotation_preflight.runtime, "roles", side_effect=lambda user: {"PA Approver"} if user != "no-role" else set()
        ):
            self.assertTrue(quotation_preflight.legacy_approver("approver", request))
            for user in ("disabled", "outside", "no-role"):
                self.assertFalse(quotation_preflight.legacy_approver(user, request))

    def test_workflow_error_uses_catalog_when_site_translation_is_missing(self):
        expected = json.loads((path.parent / "ui-translations.json").read_text(encoding="utf-8"))["messages"][
            "error.workflow_in_use"
        ]
        with patch.object(workflow_api.runtime.frappe.db, "get_value", return_value=None):
            self.assertEqual(workflow_api.runtime.tr("error.workflow_in_use"), expected)
        with patch.object(workflow_api.runtime.frappe.db, "get_value", return_value="error.workflow_in_use"):
            self.assertEqual(workflow_api.runtime.tr("error.workflow_in_use"), expected)
        with patch.object(workflow_api.runtime.frappe.db, "get_value", return_value="Site translation"):
            self.assertEqual(workflow_api.runtime.tr("error.workflow_in_use"), "Site translation")

    def test_delete_unused_workflow_checks_scope_and_references(self):
        doc = types.SimpleNamespace(name="PAWF-test", modified="2026-11-09 10:00:00")
        payload = {"name": doc.name, "expected_modified": str(doc.modified)}
        with patch.object(workflow_api, "actor", return_value="pa-admin"), patch.object(
            workflow_api, "workflow_admin_doc", return_value=doc
        ) as load, patch.object(workflow_api.frappe.db, "exists", return_value=False, create=True) as exists, patch.object(
            workflow_api.frappe, "delete_doc", create=True
        ) as delete:
            result = workflow_api.delete_approval_workflow(payload)
        load.assert_called_once_with("pa-admin", doc.name, lock=True)
        self.assertEqual(exists.call_count, 2)
        delete.assert_called_once_with("PA Approval Workflow", doc.name, ignore_permissions=True)
        self.assertEqual(result, {"name": doc.name})

    def test_delete_workflow_preserves_used_and_changed_records(self):
        doc = types.SimpleNamespace(name="PAWF-test", modified="2026-11-09 10:00:00")
        with patch.object(workflow_api, "actor", return_value="pa-admin"), patch.object(
            workflow_api, "workflow_admin_doc", return_value=doc
        ), patch.object(workflow_api.frappe.db, "exists", return_value=True, create=True), patch.object(
            workflow_api.frappe, "delete_doc", create=True
        ) as delete, patch.object(workflow_api, "fail", side_effect=ValueError) as fail:
            with self.assertRaises(ValueError):
                workflow_api.delete_approval_workflow({"name": doc.name, "expected_modified": str(doc.modified)})
            fail.assert_called_with("error.workflow_in_use")
            with self.assertRaises(ValueError):
                workflow_api.delete_approval_workflow({"name": doc.name, "expected_modified": "stale"})
            fail.assert_called_with("error.workflow_delete_conflict")
        delete.assert_not_called()

    def test_delete_workflow_requires_admin_scope(self):
        with patch.object(workflow_api, "actor", return_value="other"), patch.object(
            workflow_api, "workflow_admin_doc", side_effect=ValueError("error.permission")
        ), patch.object(workflow_api.frappe, "delete_doc", create=True) as delete:
            with self.assertRaises(ValueError):
                workflow_api.delete_approval_workflow({"name": "PAWF-test", "expected_modified": "now"})
        delete.assert_not_called()

    def test_roles_menu_patch_adds_only_one_item_after_workflows(self):
        items = [types.SimpleNamespace(url=roles_menu_migration.WORKFLOW_URL, idx=1),
                 types.SimpleNamespace(url="/desk/purchase-approval?view=settings", idx=2)]
        sidebar = types.SimpleNamespace(items=items)
        def append(_field, values):
            row = types.SimpleNamespace(**values)
            items.append(row)
            return row
        sidebar.append = append
        saved = []
        sidebar.save = lambda **kwargs: saved.append(kwargs)
        with patch.object(roles_menu_migration.frappe.db, "exists", return_value=True, create=True), patch.object(
            roles_menu_migration.frappe, "get_doc", return_value=sidebar, create=True
        ), patch.object(roles_menu_migration.frappe, "clear_cache", create=True):
            roles_menu_migration.execute()
            roles_menu_migration.execute()
        self.assertEqual([row.url for row in items], [roles_menu_migration.WORKFLOW_URL,
                         roles_menu_migration.ROLE_URL, "/desk/purchase-approval?view=settings"])
        self.assertEqual([row.idx for row in items], [1, 2, 3])
        self.assertEqual(saved, [{"ignore_permissions": True}])

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
        runtime.validate_steps([valid[1], valid[0], valid[2]])  # A general approval can precede quotation.
        for invalid in (
            [],
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

    def test_general_approval_uses_custom_role_membership_and_pending_assignee(self):
        workflow_step = types.SimpleNamespace(approver_source="Role", approver_role="PA Budget Reviewer", step_type="Quote Approval")
        request = types.SimpleNamespace(requester="creator", status="Pending Approval", current_instance="PAI-1")
        members = [types.SimpleNamespace(parent=name) for name in ("creator", "budget", "outside")]
        with patch.object(runtime.frappe, "get_all", return_value=members, create=True), patch.object(
            runtime, "eligible_user", side_effect=lambda user, _request: user != "outside"
        ):
            self.assertEqual(runtime.assignees(workflow_step, request), ["budget"])
        instance = types.SimpleNamespace(steps=[step(1, "Quote Approval")], current_sequence=1,
                                         assignees=[types.SimpleNamespace(user="budget", step_order=1, status="Pending")])
        with patch.object(runtime, "is_modern", return_value=True), patch.object(
            runtime.frappe, "get_doc", return_value=instance, create=True
        ), patch.object(runtime, "eligible_user", return_value=True):
            self.assertEqual(runtime.actions(request, "budget"), ["approve", "return", "reject"])
            self.assertEqual(runtime.actions(request, "creator"), [])

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

    def test_partial_receiving_does_not_commit_receipt_fields(self):
        request = types.SimpleNamespace(name="PA-1", received_by="first", received_at="now")
        current = step(1, "Receiving", method="All")
        assignees = [
            types.SimpleNamespace(step_order=1, user="first", status="Pending", acted_at=None, comment=""),
            types.SimpleNamespace(step_order=1, user="second", status="Pending", acted_at=None, comment=""),
        ]
        instance = types.SimpleNamespace(name="PAI-1", current_sequence=1, steps=[current], assignees=assignees)
        with patch.object(runtime, "eligible_user", return_value=True), patch.object(
            runtime.frappe.db, "get_value", return_value={"received_by": None, "received_at": None}, create=True
        ), patch.object(runtime.frappe, "get_all", return_value=[], create=True), patch.object(runtime, "save"):
            self.assertFalse(runtime.finish_step(request, instance, "first"))
        self.assertIsNone(request.received_by)
        self.assertIsNone(request.received_at)

    def test_workflow_api_persists_all_selected_users_and_legacy_first_user(self):
        payload = {
            "workflow_name": "Test",
            "company": "C1",
            "department": "D1",
            "currency": "VND",
            "selector_source": "Role",
            "selector_role": "PA Purchasing",
            "idempotency_key": "a" * 32,
            "steps": [{
                "step_name": "Check",
                "step_type": "Stock Check",
                "approval_method": "All",
                "approver_source": "User",
                "approver_user": "one",
                "approver_users": ["one", "two"],
                "send_email": 0,
            }],
        }
        saved = {}
        document = types.SimpleNamespace(insert=lambda **kwargs: saved.update(insert=kwargs))
        response = {"workflow": {"company": "C1"}}
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "require_role"
        ), patch.object(workflow_api, "workflow_admin_scope"), patch.object(
            workflow_api, "workflow_assignee_options",
            return_value=([types.SimpleNamespace(name="one"), types.SimpleNamespace(name="two")], ["PA Purchasing"]),
        ), patch.object(workflow_api.runtime, "normalize_workflow_users", return_value=["one", "two"]), patch.object(
            workflow_api.runtime, "validate_steps"
        ), patch.object(workflow_api.frappe.db, "exists", return_value=False, create=True), patch.object(
            workflow_api.frappe.db, "sql", return_value=None, create=True
        ), patch.object(workflow_api.frappe, "get_doc", return_value=document, create=True) as get_doc, patch.object(
            workflow_api, "workflow_admin_result", return_value=response
        ), patch.object(workflow_api.workflow_roles, "register") as register_role:
            result = workflow_api.save_approval_workflow(json.dumps(payload))
        stored = get_doc.call_args.args[0]
        self.assertEqual(stored["assignees"], [{"step_order": 1, "user": "one"}, {"step_order": 1, "user": "two"}])
        self.assertEqual(stored["steps"][0]["approver_user"], "one")
        self.assertNotIn("approver_users", stored["steps"][0])
        self.assertEqual(saved["insert"], {"ignore_permissions": True, "set_name": "PAWF-" + "a" * 32})
        register_role.assert_called_once_with("PA Purchasing")
        self.assertEqual(result, response)

    def test_workflow_role_creation_uses_frappe_create_permission(self):
        role = types.SimpleNamespace(name="PA Budget Reviewer", insert=lambda: None)
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ) as scope, patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True) as permission, patch.object(
            workflow_api.frappe.db, "exists", return_value=False, create=True
        ), patch.object(workflow_api.frappe, "get_doc", return_value=role, create=True) as get_doc, patch.object(
            role, "insert"
        ) as insert, patch.object(workflow_api.workflow_roles, "register") as register_role:
            result = workflow_api.create_workflow_role(json.dumps({"role_name": " PA Budget Reviewer ", "company": "C1", "department": "D1"}))
        scope.assert_called_once_with("admin", "C1", "D1")
        permission.assert_called_once_with("Role", "create", user="admin")
        self.assertEqual(get_doc.call_args.args[0]["role_name"], "PA Budget Reviewer")
        insert.assert_called_once_with()
        register_role.assert_called_once_with("PA Budget Reviewer")
        self.assertEqual(result, {"role_name": "PA Budget Reviewer"})

    def test_workflow_role_creation_access_uses_current_scope_and_frappe_permission(self):
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ) as scope, patch.object(workflow_api.frappe, "has_permission", return_value=False, create=True):
            result = workflow_api.workflow_role_creation_access(json.dumps({"company": "C1", "department": "D1"}))
        scope.assert_called_once_with("admin", "C1", "D1")
        self.assertEqual(result, {"can_create_role": False})

    def test_available_roles_match_workflow_options_and_count_eligible_users(self):
        active = [types.SimpleNamespace(name=name, full_name=name) for name in ("alice", "bob", "outside")]
        assignments = [
            types.SimpleNamespace(parent="alice", role="PA Approver"),
            types.SimpleNamespace(parent="alice", role="PA Approver"),
            types.SimpleNamespace(parent="bob", role="PA Approver"),
            types.SimpleNamespace(parent="bob", role="PA Purchasing"),
            types.SimpleNamespace(parent="alice", role="Disabled Role"),
            types.SimpleNamespace(parent="outside", role="Outside Role"),
            types.SimpleNamespace(parent="bob", role="Accounts Manager"),
            types.SimpleNamespace(parent="alice", role="Budget Reviewer"),
        ]
        def get_all(doctype, **kwargs):
            if doctype == "User":
                self.assertEqual(kwargs["filters"], {"enabled": 1})
                return active
            self.assertEqual(doctype, "Has Role")
            self.assertEqual(kwargs["filters"]["parenttype"], "User")
            allowed = set(kwargs["filters"]["parent"][1])
            return [row for row in assignments if row.parent in allowed]
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True), patch.object(
            workflow_api.frappe, "get_all", side_effect=get_all, create=True
        ), patch.object(workflow_api.frappe.db, "exists", side_effect=lambda _doctype, filters: filters["name"] != "Disabled Role", create=True), patch.object(
            workflow_api.runtime, "eligible_user", side_effect=lambda name, _target: name != "outside"
        ), patch.object(workflow_api.workflow_roles, "registered_names", return_value={"PA Approver", "PA Purchasing", "Budget Reviewer"}
        ):
            expected = workflow_api.workflow_assignee_options("admin", "C1", "D1")[1]
            result = workflow_api.list_purchase_approval_roles(json.dumps({"company": "C1", "department": "D1"}))
        self.assertIn("Accounts Manager", expected)
        self.assertEqual([row["name"] for row in result["roles"]], [role for role in expected if role != "Accounts Manager"])
        self.assertEqual(result["roles"], [
            {"name": "Budget Reviewer", "eligible_user_count": 1},
            {"name": "PA Approver", "eligible_user_count": 2},
            {"name": "PA Purchasing", "eligible_user_count": 1},
        ])

    def test_workflow_picker_includes_scoped_purchaser_without_approval_role(self):
        buyer = types.SimpleNamespace(name="purchase@demo.local", full_name="Người mua demo")
        outside = types.SimpleNamespace(name="outside@demo.local", full_name="Outside buyer")

        def get_all(doctype, **kwargs):
            if doctype == "User":
                self.assertEqual(kwargs["filters"], {"enabled": 1})
                return [buyer, outside]
            if doctype == "User Permission":
                if kwargs["filters"]["allow"] == "Department":
                    return []
                company = "C1" if kwargs["filters"]["user"] == buyer.name else "C2"
                return [types.SimpleNamespace(for_value=company)]
            if doctype == "Has Role":
                if "parent" in kwargs["filters"] and isinstance(kwargs["filters"]["parent"], str):
                    return [types.SimpleNamespace(role="PA Purchasing")]
                return [types.SimpleNamespace(role="PA Purchasing")]
            self.fail(doctype)

        with patch.object(workflow_api, "actor", return_value="Administrator"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "get_all", side_effect=get_all, create=True), patch.object(
            workflow_api.frappe.db, "get_value", return_value=1, create=True
        ), patch.object(workflow_api.frappe.db, "exists", return_value=True, create=True):
            result = workflow_api.workflow_assignees({"company": "C1", "department": "D1", "query": "người mua"})
        self.assertEqual(result["users"], [{"name": buyer.name, "full_name": buyer.full_name}])
        self.assertEqual(result["roles"], ["PA Purchasing"])
        self.assertFalse(result["has_more"])

    def test_available_roles_require_scope_and_frappe_read_permission(self):
        payload = json.dumps({"company": "C1", "department": "D1"})
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope", side_effect=ValueError("error.permission")
        ), patch.object(workflow_api.frappe, "has_permission", create=True) as permission:
            with self.assertRaisesRegex(ValueError, "error.permission"):
                workflow_api.list_purchase_approval_roles(payload)
            permission.assert_not_called()
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=False, create=True), patch.object(
            workflow_api.frappe, "get_all", create=True
        ) as get_all:
            with self.assertRaisesRegex(ValueError, localized_error("error.role_read_permission")):
                workflow_api.list_purchase_approval_roles(payload)
            get_all.assert_not_called()

    def test_existing_role_registration_checks_permission_and_role_state(self):
        payload = json.dumps({"company": "C1", "department": "D1", "role_name": "Budget Reviewer"})
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True), patch.object(
            workflow_api.frappe.db, "exists", return_value=True, create=True
        ), patch.object(workflow_api.frappe.db, "get_value", return_value=0, create=True), patch.object(
            workflow_api.workflow_roles, "register"
        ) as register:
            self.assertEqual(workflow_api.register_existing_workflow_role(payload), {"role_name": "Budget Reviewer"})
            register.assert_called_once_with("Budget Reviewer")
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=False, create=True), patch.object(
            workflow_api.workflow_roles, "register"
        ) as register:
            with self.assertRaisesRegex(ValueError, localized_error("error.role_read_permission")):
                workflow_api.register_existing_workflow_role(payload)
            register.assert_not_called()
        for exists, disabled, error in ((False, 0, "error.role_not_found"), (True, 1, "error.role_disabled")):
            with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
                workflow_api, "workflow_admin_scope"
            ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True), patch.object(
                workflow_api.frappe.db, "exists", return_value=exists, create=True
            ), patch.object(workflow_api.frappe.db, "get_value", side_effect=lambda doctype, *_args: disabled if doctype == "Role" else None, create=True), patch.object(
                workflow_api.workflow_roles, "register"
            ) as register:
                with self.assertRaisesRegex(ValueError, localized_error(error)):
                    workflow_api.register_existing_workflow_role(payload)
                register.assert_not_called()

    def test_role_registry_patches_create_schema_and_backfill_used_roles(self):
        definition = next(row for row in install.metadata()["doctypes"] if row["name"] == "PA Workflow Role")
        self.assertEqual(definition["autoname"], "field:role")
        self.assertEqual(definition["fields"][0]["options"], "Role")
        with patch.object(role_schema_migration, "ensure_doctypes") as ensure:
            role_schema_migration.execute()
        ensure.assert_called_once_with({"doctypes": [definition]})

        def get_all(doctype, **_kwargs):
            return {
                "PA Approval Workflow": [types.SimpleNamespace(selector_role="Budget Reviewer")],
                "PA Approval Workflow Step": [types.SimpleNamespace(approver_role="PA Approver")],
                "Role": [types.SimpleNamespace(name="PA Custom Reviewer")],
            }[doctype]
        with patch.object(workflow_roles, "metadata", return_value={"roles": [{"name": "PA Super Admin"}]}), patch.object(
            workflow_roles.frappe.db, "exists", side_effect=lambda doctype, name: doctype == "DocType" or name != "PA Custom Reviewer", create=True
        ), patch.object(
            workflow_roles.frappe.db, "has_column", return_value=True, create=True
        ), patch.object(workflow_roles.frappe, "get_all", side_effect=get_all, create=True), patch.object(
            workflow_roles, "register"
        ) as register:
            workflow_roles.backfill()
        self.assertEqual({call.args[0] for call in register.call_args_list}, {"PA Super Admin", "PA Approver", "Budget Reviewer"})

    def test_role_backfill_skips_missing_selector_column_on_legacy_site(self):
        queried = []

        def get_all(doctype, **_kwargs):
            queried.append(doctype)
            if doctype == "PA Approval Workflow Step":
                return [types.SimpleNamespace(approver_role="Budget Reviewer")]
            return [types.SimpleNamespace(name="PA Custom Reviewer")]

        with patch.object(workflow_roles, "metadata", return_value={"roles": [{"name": "PA Super Admin"}]}), patch.object(
            workflow_roles.frappe.db, "exists", return_value=True, create=True
        ), patch.object(
            workflow_roles.frappe.db, "has_column", side_effect=lambda _doctype, field: field == "approver_role", create=True
        ), patch.object(workflow_roles.frappe, "get_all", side_effect=get_all, create=True), patch.object(
            workflow_roles, "register"
        ) as register:
            workflow_roles.backfill()
        self.assertEqual(queried, ["PA Approval Workflow Step", "Role"])
        self.assertEqual({call.args[0] for call in register.call_args_list}, {"PA Super Admin", "PA Custom Reviewer", "Budget Reviewer"})

    def test_role_registration_is_idempotent(self):
        stored = set()
        def get_doc(values):
            return types.SimpleNamespace(insert=lambda **_kwargs: stored.add(values["role"]))
        with patch.object(workflow_roles.frappe.db, "exists", side_effect=lambda _doctype, name: name in stored, create=True), patch.object(
            workflow_roles.frappe, "get_doc", side_effect=get_doc, create=True
        ) as get_doc_call:
            workflow_roles.register("Budget Reviewer")
            workflow_roles.register("Budget Reviewer")
        self.assertEqual(stored, {"Budget Reviewer"})
        get_doc_call.assert_called_once_with({"doctype": "PA Workflow Role", "role": "Budget Reviewer"})

    def test_workflow_role_creation_rejects_missing_permission_and_duplicate_name(self):
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=False, create=True), patch.object(
            workflow_api.frappe, "get_doc", create=True
        ) as get_doc:
            with self.assertRaisesRegex(ValueError, localized_error("error.role_create_permission")):
                workflow_api.create_workflow_role(json.dumps({"role_name": "PA Budget Reviewer", "company": "C1", "department": "D1"}))
            get_doc.assert_not_called()
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True), patch.object(
            workflow_api.frappe.db, "exists", return_value=True, create=True
        ), patch.object(workflow_api.frappe, "get_doc", create=True) as get_doc:
            with self.assertRaisesRegex(ValueError, localized_error("error.role_exists")):
                workflow_api.create_workflow_role(json.dumps({"role_name": "PA Budget Reviewer", "company": "C1", "department": "D1"}))
            get_doc.assert_not_called()

    def test_workflow_role_creation_translates_duplicate_insert_race(self):
        role = types.SimpleNamespace(insert=lambda: (_ for _ in ()).throw(fake_frappe.DuplicateEntryError()))
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True), patch.object(
            workflow_api.frappe.db, "exists", return_value=False, create=True
        ), patch.object(workflow_api.frappe, "get_doc", return_value=role, create=True):
            with self.assertRaisesRegex(ValueError, localized_error("error.role_exists")):
                workflow_api.create_workflow_role(json.dumps({"role_name": "PA Budget Reviewer", "company": "C1"}))

    def test_workflow_role_name_rejects_empty_and_control_characters(self):
        with patch.object(workflow_api, "actor", return_value="admin"), patch.object(
            workflow_api, "workflow_admin_scope"
        ), patch.object(workflow_api.frappe, "has_permission", return_value=True, create=True):
            for name in (" ", "PA\nReviewer", "x" * 141):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, localized_error("error.role_name")):
                    workflow_api.create_workflow_role(json.dumps({"role_name": name, "company": "C1", "department": "D1"}))

    def test_role_options_require_an_active_user_in_scope(self):
        assignments = []
        user = types.SimpleNamespace(name="approver", full_name="Approver")
        def get_all(doctype, **_kwargs):
            return [user] if doctype == "User" else assignments if doctype == "Has Role" else []
        with patch.object(workflow_api, "workflow_admin_scope"), patch.object(
            workflow_api.frappe, "get_all", side_effect=get_all, create=True
        ), patch.object(workflow_api.runtime, "eligible_user", return_value=True), patch.object(
            workflow_api.frappe.db, "exists", return_value=True, create=True
        ):
            self.assertEqual(workflow_api.workflow_assignee_options("admin", "C1", "D1")[1], [])
            assignments.append(types.SimpleNamespace(role="PA Budget Reviewer"))
            self.assertEqual(workflow_api.workflow_assignee_options("admin", "C1", "D1")[1], ["PA Budget Reviewer"])

    def test_step_email_toggle_and_idempotency_key(self):
        request = types.SimpleNamespace(name="PA-1", requester="creator")
        instance = types.SimpleNamespace(name="PAI-1", assignees=[types.SimpleNamespace(step_order=1, user="checker", status="Pending")])
        current = step(1, "Stock Check")
        current.step_name = "Kiểm tra kho"
        created = []
        with patch.object(runtime.frappe.db, "exists", return_value=False, create=True), patch.object(
            runtime.frappe, "get_doc", side_effect=lambda doc: types.SimpleNamespace(name="OUT-1", insert=lambda **_kwargs: created.append(doc)), create=True
        ), patch.object(runtime, "tr", side_effect=lambda key: "Bước {step}" if key == "notification.step_body" else key), patch.object(
            runtime, "schedule_notification_delivery"
        ) as schedule:
            runtime.enqueue(request, instance, current)
            current.send_email = 1
            runtime.enqueue(request, instance, current)
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0]["notification_key"], "PAI-1:1:checker")
        self.assertEqual(created[0]["body"], "Bước Kiểm tra kho")
        schedule.assert_called_once_with(["OUT-1"])

    def test_notification_dispatch_is_registered_after_commit(self):
        callbacks = []
        with patch.object(runtime.frappe.db, "after_commit", types.SimpleNamespace(add=callbacks.append), create=True
        ), patch.object(runtime.frappe, "enqueue", create=True) as enqueue:
            runtime.schedule_notification_delivery(["OUT-1", "OUT-2"])
            self.assertEqual(len(callbacks), 1)
            enqueue.assert_not_called()
            callbacks[0]()
        enqueue.assert_called_once_with("purchase_approval.notification_delivery.dispatch_pending", queue="long", outbox_names=["OUT-1", "OUT-2"])

    def test_notification_patch_preserves_unrelated_script_edits(self):
        baselines = json.loads(notification_migration.BASELINES.read_text(encoding="utf-8"))
        managed = {row["name"]: row["script"] for row in install.metadata()["server_scripts"]}
        for name in notification_migration.SCRIPTS:
            blocks = "".join(baselines[name][function]["legacy"] for function in notification_migration.SCRIPTS[name])
            if name == "pa_submit_purchase_request":
                blocks = blocks.replace("request.priced_at = None", "request.priced_at = None  # site note")
            current = "def pa_execute(doc=None):\n" + blocks + "    def local_customization():\n        return 7\n"
            updated = notification_migration.upgraded_script(name, current, managed[name], baselines)
            self.assertIsNotNone(updated)
            self.assertIn("    def local_customization():\n        return 7\n", updated)
            if name == "pa_submit_purchase_request":
                self.assertIn("request.priced_at = None  # site note", updated)
            self.assertEqual(notification_migration.upgraded_script(name, updated, managed[name], baselines), updated)
            for function in notification_migration.SCRIPTS[name]:
                target_span = notification_migration.function_span(managed[name], function)
                updated_span = notification_migration.function_span(updated, function)
                if name != "pa_submit_purchase_request" or function != "submit_request":
                    self.assertEqual(notification_migration.script_lines(updated[slice(*updated_span)]),
                                     notification_migration.script_lines(managed[name][slice(*target_span)]))

    def test_notification_patch_rejects_overlapping_site_change(self):
        baselines = json.loads(notification_migration.BASELINES.read_text(encoding="utf-8"))
        name = "pa_submit_purchase_request"
        old = baselines[name]["submit_request"]["legacy"]
        modified = old.replace("request.status = 'Pending Purchasing'", "request.status = 'Custom Status'")
        current = "def pa_execute(doc=None):\n" + modified + baselines[name]["request_actions"]["legacy"] + "    def other():\n        pass\n"
        target = next(row["script"] for row in install.metadata()["server_scripts"] if row["name"] == name)
        self.assertIsNone(notification_migration.upgraded_script(name, current, target, baselines))

    def test_delivery_uses_managed_worker_and_respects_email_switch(self):
        script = types.SimpleNamespace(script_type="Scheduler Event", execute_scheduled_method=lambda: None)
        local = types.SimpleNamespace(form_dict={"existing": "value"})
        with patch.object(notification_delivery.frappe.db, "get_single_value", return_value=0, create=True), patch.object(
            notification_delivery.frappe, "get_doc", return_value=script, create=True
        ) as get_doc:
            notification_delivery.dispatch_pending()
            get_doc.assert_not_called()
        with patch.object(notification_delivery.frappe.db, "get_single_value", return_value=1, create=True), patch.object(
            notification_delivery.frappe, "get_doc", return_value=script, create=True
        ), patch.object(notification_delivery.frappe, "set_user", create=True) as set_user, patch.object(
            notification_delivery.frappe, "local", local, create=True
        ), patch.object(notification_delivery.frappe, "_dict", dict, create=True), patch.object(
            script, "execute_scheduled_method"
        ) as execute:
            observed = []
            execute.side_effect = lambda: observed.append(local.form_dict.get("pa_notification_only"))
            notification_delivery.dispatch_pending(["OUT-1"])
            set_user.assert_called_once_with("Administrator")
            execute.assert_called_once_with()
            self.assertEqual(observed, [["OUT-1"]])
            self.assertEqual(local.form_dict, {"existing": "value"})

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
        class WorkflowStep(types.SimpleNamespace):
            def get(self, key, default=None):
                return getattr(self, key, default)

        class Workflow:
            def __init__(self):
                self.assignees = []
                self.steps = [
                    WorkflowStep(step_order=1, step_type="Stock Check", approval_method="All", approver_source="User", approver_user="checker"),
                    WorkflowStep(step_order=2, step_type="Quote Approval", approval_method="All", approver_source="User", approver_user="approver"),
                    WorkflowStep(step_order=3, step_type="Quotation", approval_method="All", approver_source="User", approver_user="buyer"),
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

    def test_multi_user_migration_preserves_legacy_method_when_step_type_is_missing(self):
        class WorkflowStep(types.SimpleNamespace):
            def get(self, key, default=None):
                return getattr(self, key, default)

        class Workflow:
            def __init__(self):
                self.assignees = []
                self.steps = [WorkflowStep(step_order=1, approval_method="All", approver_source="Role")]
                self.saved = False

            def save(self, **_kwargs):
                self.saved = True

        workflow = Workflow()
        with patch.object(multi_user_migration.frappe, "get_all", return_value=[types.SimpleNamespace(name="WF-1")], create=True), patch.object(
            multi_user_migration.frappe, "get_doc", return_value=workflow, create=True
        ):
            multi_user_migration.backfill_workflows()
        self.assertEqual(workflow.steps[0].approval_method, "All")
        self.assertFalse(workflow.saved)

    def test_multi_user_migration_adds_missing_workflow_step_fields(self):
        payload = json.loads((path.parent / "metadata" / "purchase_approval.json").read_text(encoding="utf-8"))

        class DocType:
            def __init__(self):
                self.fields = [types.SimpleNamespace(fieldname="step_name", idx=1)]
                self.saved = False

            def append(self, fieldname, values):
                row = types.SimpleNamespace(**values)
                getattr(self, fieldname).append(row)
                return row

            def save(self, **_kwargs):
                self.saved = True

        doctype = DocType()
        with patch.object(multi_user_migration.frappe.db, "exists", return_value=True, create=True), patch.object(
            multi_user_migration.frappe.db, "get_value", return_value="Purchase Approval", create=True
        ), patch.object(multi_user_migration.frappe, "get_doc", return_value=doctype, create=True):
            multi_user_migration.ensure_workflow_step_fields(payload)
        definition = next(row for row in payload["doctypes"] if row["name"] == "PA Approval Workflow Step")
        self.assertEqual({row.fieldname for row in doctype.fields}, {row["fieldname"] for row in definition["fields"]})
        self.assertTrue(doctype.saved)

    def test_translation_installer_uses_one_vietnamese_row_per_key(self):
        payload = {"translations": [
            {"message_key": "action.confirm_handoff", "language": "vi", "text": "Vietnamese"},
            {"message_key": "action.confirm_handoff", "language": "en", "text": "English"},
        ]}
        inserted = []

        class Translation:
            def __init__(self, values):
                self.values = values

            def insert(self, **_kwargs):
                inserted.append(self.values)

        with patch.object(install.frappe, "get_all", return_value=[], create=True), patch.object(
            install.frappe, "get_doc", side_effect=lambda values: Translation(values), create=True
        ):
            install.ensure_translations(payload)
        self.assertEqual([(row["message_key"], row["language"]) for row in inserted], [("action.confirm_handoff", "vi")])

    def test_translation_patches_upsert_by_unique_message_key(self):
        payload = {"translations": [
            {"message_key": "action.confirm_handoff", "language": "vi", "text": "Vietnamese"},
            {"message_key": "action.confirm_handoff", "language": "en", "text": "English"},
        ]}
        updates = []
        with patch.object(multi_user_migration.frappe.db, "exists", return_value="action.confirm_handoff", create=True), patch.object(
            multi_user_migration.frappe.db,
            "set_value",
            side_effect=lambda *args, **kwargs: updates.append((args, kwargs)),
            create=True,
        ):
            multi_user_migration.update_translations(payload)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0][0][1], "action.confirm_handoff")
        self.assertEqual(updates[0][0][2], {"language": "vi", "text": "Vietnamese"})

    def test_legacy_workflow_patch_does_not_insert_duplicate_english_translation_rows(self):
        payload = {"translations": [
            {"message_key": "action.confirm_handoff", "language": "vi", "text": "Vietnamese"},
            {"message_key": "action.confirm_handoff", "language": "en", "text": "English"},
        ]}
        inserted = []

        class Translation:
            def __init__(self, values):
                self.values = values

            def insert(self, **_kwargs):
                inserted.append(self.values)

        with patch.object(migration.frappe.db, "exists", return_value=None, create=True), patch.object(
            migration.frappe, "get_doc", side_effect=lambda values: Translation(values), create=True
        ):
            migration.update_translations(payload)
        self.assertEqual([(row["message_key"], row["language"]) for row in inserted], [("action.confirm_handoff", "vi")])

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

    def test_multi_user_migration_updates_get_script_without_losing_other_edits(self):
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


class RolePermissionMatrixTests(unittest.TestCase):
    def test_matrix_keeps_advanced_rules_out_of_editable_rights(self):
        permissions = types.ModuleType("frappe.permissions")
        permissions.get_all_perms = lambda _role: [
            types.SimpleNamespace(parent="PA Purchase Request", name="base", permlevel=0, if_owner=0, read=1, write=1),
            types.SimpleNamespace(parent="PA Purchase Request", name="owner", permlevel=0, if_owner=1, read=1),
            types.SimpleNamespace(parent="PA Purchase Request", name="level-one", permlevel=1, if_owner=0, read=1),
            types.SimpleNamespace(parent="Other DocType", name="foreign", permlevel=0, if_owner=0, read=1),
        ]
        definitions = {
            "PA Purchase Request": types.SimpleNamespace(is_submittable=0, allow_import=1, issingle=0),
        }
        with patch.dict(sys.modules, {"frappe.permissions": permissions}):
            result = role_permissions.matrix("PA Approver", definitions)
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0]["rights"]["read"], 1)
        self.assertEqual(result["rows"][0]["rights"]["create"], 0)
        self.assertTrue(result["rows"][0]["has_advanced"])
        self.assertFalse(result["rows"][0]["locked"])
        self.assertEqual(len(result["revision"]), 64)

    def test_changes_reject_invalid_rules_before_writing(self):
        row = {
            "doctype": "PA Purchase Request", "rights": dict.fromkeys(role_permissions.RIGHTS, 0),
            "has_rule": False, "locked": False, "is_submittable": False,
            "allow_import": True, "issingle": False,
        }
        with patch.object(role_permissions, "fail", side_effect=ValueError):
            for doctype, changes in (
                ("Other DocType", {**row["rights"], "read": 1}),
                ("PA Purchase Request", {**row["rights"], "cancel": 1}),
                ("PA Purchase Request", {**row["rights"], "import": 1}),
                ("PA Purchase Request", {**row["rights"], "submit": 1, "write": 1}),
            ):
                with self.subTest(doctype=doctype, changes=changes), self.assertRaises(ValueError):
                    role_permissions.normalized_changes([{"doctype": doctype, "rights": changes}], [row])
        rights = {**row["rights"], "read": 1, "print": 1}
        self.assertEqual(role_permissions.normalized_changes([{"doctype": row["doctype"], "rights": rights}], [row]),
                         [(row["doctype"], rights, False)])
        with patch.object(role_permissions, "fail", side_effect=ValueError):
            with self.assertRaises(ValueError):
                role_permissions.normalized_changes(
                    [{"doctype": row["doctype"], "rights": row["rights"]}],
                    [{**row, "has_rule": True, "has_advanced": True, "rights": rights}],
                )

    def test_save_rejects_stale_revision_without_writing(self):
        current = {"role_name": "PA Approver", "rows": [], "revision": "current"}
        with patch.object(role_permissions, "authorize", return_value="PA Approver"), patch.object(
            role_permissions, "available_doctypes", return_value={}
        ), patch.object(role_permissions, "matrix", return_value=current), patch.object(
            role_permissions, "apply_change"
        ) as apply, patch.object(role_permissions, "fail", side_effect=ValueError):
            with self.assertRaises(ValueError):
                role_permissions.save_role_permissions({"revision": "stale", "changes": []})
        apply.assert_not_called()

    def test_save_updates_only_changed_doctype(self):
        empty = dict.fromkeys(role_permissions.RIGHTS, 0)
        row = {
            "doctype": "PA Purchase Request", "rights": empty, "has_rule": False,
            "locked": False, "has_advanced": False, "is_submittable": False,
            "allow_import": True, "issingle": False,
        }
        current = {"role_name": "PA Approver", "rows": [row], "revision": "current"}
        updated = {**current, "revision": "updated"}
        rights = {**empty, "read": 1, "print": 1}
        with patch.object(role_permissions, "authorize", return_value="PA Approver"), patch.object(
            role_permissions, "available_doctypes", return_value={}
        ), patch.object(role_permissions, "matrix", side_effect=[current, updated]), patch.object(
            role_permissions, "apply_change"
        ) as apply:
            result = role_permissions.save_role_permissions({
                "revision": "current", "changes": [{"doctype": row["doctype"], "rights": rights}],
            })
        apply.assert_called_once_with(row["doctype"], "PA Approver", rights, False)
        self.assertEqual(result["revision"], "updated")

    def test_authorize_requires_system_manager_and_registered_role(self):
        data = {"company": "Company A", "department": "", "role_name": "PA Approver"}
        with patch.object(role_permissions, "actor", return_value="pa-admin"), patch.object(
            role_permissions, "workflow_admin_scope"
        ), patch.object(role_permissions.frappe, "get_roles", return_value=["PA Company Admin"], create=True), patch.object(
            role_permissions, "fail", side_effect=ValueError
        ):
            with self.assertRaises(ValueError):
                role_permissions.authorize(data)
        with patch.object(role_permissions, "actor", return_value="pa-admin"), patch.object(
            role_permissions, "workflow_admin_scope"
        ), patch.object(role_permissions.frappe, "get_roles", return_value=["System Manager"], create=True), patch.object(
            role_permissions.frappe, "only_for", create=True
        ), patch.object(role_permissions.workflow_roles, "registered_names", return_value=set()), patch.object(
            role_permissions, "fail", side_effect=ValueError
        ):
            with self.assertRaises(ValueError):
                role_permissions.authorize(data)


if __name__ == "__main__":
    unittest.main()
