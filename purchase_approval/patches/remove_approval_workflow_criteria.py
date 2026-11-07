"""Remove retired workflow criteria and update managed script sources.

This forward-only migration intentionally discards the retired criteria values.
Historical approval snapshots stay untouched for audit purposes.
"""

import hashlib

import frappe

from purchase_approval.install import message, metadata


DOCTYPE = "PA Approval Workflow"
REMOVED_FIELDS = ("purchase_type", "amount_from", "has_amount_to", "amount_to")
OBSOLETE_TRANSLATIONS = (
    "field.amount_from",
    "field.amount_to",
    "field.has_amount_to",
    "workflow.all_types",
    "workflow.range",
    "workflow.range_open",
)
UPDATED_TRANSLATIONS = {
    "common.auto_workflow",
    "error.no_workflow",
    "error.ambiguous",
    "workflow.conditions",
}
OLD_SERVER_SCRIPT_SHA256 = {
    'pa_approval_action': 'f8c4da3c3030d98c20c183c83cfcd6c30869a51df85d1cd56ab163034b20c9c9',
    'pa_cancel_purchase_request': '78f30ef3b7baed8d2ce82dfd0ccad3f04ec355286db4cb4ca0cf41a83323db2b',
    'pa_create_purchase_request': 'c2533938d4e360cc0474a2ab756b4f7584ca085e69bc0908f6f36505c271737c',
    'pa_deactivate_organization': '5663eae7b9e39f2cf5d7a35e1e94178e373528333573e67282837c09a3dc549a',
    'pa_delete_guard_pa_approval_history': '0c91ffbf96fe0cbdf7e8a1a9a0cfa376025ea62201d95554743f8012025d8a06',
    'pa_delete_guard_pa_approval_instance': '0c91ffbf96fe0cbdf7e8a1a9a0cfa376025ea62201d95554743f8012025d8a06',
    'pa_delete_guard_pa_purchase_request': '0c91ffbf96fe0cbdf7e8a1a9a0cfa376025ea62201d95554743f8012025d8a06',
    'pa_finalize_purchase_request': '7aa02215d46523a275a0fc9c4b0e2d82495b01c1a78afbf0fddd737235b5a72b',
    'pa_get_approval_workflow': '46eba6326d4b2638d976a5b8204a7dbe5462e68889335ca7ff95353ac6944b72',
    'pa_get_context': '5d42c378da39615a9c7413427ed55e9e51af5a8d296354cd1a9ae2f490a77ca9',
    'pa_get_dashboard': '81b2c781ba942901b0180c2d52eda10809a2bfbbca171e4af39d9d6e1a95d629',
    'pa_get_mail_settings': 'd72e5172663f2a9d6707b4d8bc1a33fda16cd3bbacad7929eb7ef8871bd34ce9',
    'pa_get_organization': 'c5f7df65820a47d0a1dacf127a6f3d3abc56c251cbdc20211f48a927a3ef00ee',
    'pa_get_purchase_request': 'eedb55b29b827935616f1297b3e2143cbcae90ae44135880f2c146e77e242107',
    'pa_get_purchase_request_pdf': 'a29c635b7db56ccdeae3d0f06526546cb64b1e5200b44e199add8c5d7590399c',
    'pa_history_guard': '0a4292bb4172912ad8cf552cb3698bad888c6af90a8266636e7d5608d5a6ed39',
    'pa_instance_guard': '0a4292bb4172912ad8cf552cb3698bad888c6af90a8266636e7d5608d5a6ed39',
    'pa_item_suggestions': '896ed6a211a895427771e3516d99f18a8eb99264bf6d33d24eaadd18a017d199',
    'pa_list_approval_workflows': '9e239f99d08f63114eb73fdb853195dff978f86f8576e1fcdad0ac1aec2755aa',
    'pa_list_organizations': 'b60a592e53c2cdc7e79528e6054cbfe39db59469e1600e20d2cba903dc87096f',
    'pa_list_purchase_requests': 'd73d30f2bc6de757b34945d7944500d439e70670fa8ff77232c0a3658c0582d5',
    'pa_notification_worker': 'e8d0814992baefe22e9ba85744c571d917a1cbc02a5dbec056a59aa4d4ebb6bb',
    'pa_org_delete_guard_ktg_company': '4498ec1d913148e2afaacd14737eb4c7db4f532fb62966e77adece28bc96175a',
    'pa_org_delete_guard_ktg_department': '4498ec1d913148e2afaacd14737eb4c7db4f532fb62966e77adece28bc96175a',
    'pa_org_validate_ktg_company': '1bede2132211d12058b940b0a8443c212d28bb12cf09223c3da11c82bb6bd5ee',
    'pa_org_validate_ktg_department': '1bede2132211d12058b940b0a8443c212d28bb12cf09223c3da11c82bb6bd5ee',
    'pa_reassign_approver': '339905b5ac7a24ae6a70799d779b4de285387d49b345656f00cd99cf00171f85',
    'pa_receive_purchase_request': '7c5f85082aee58bd2639178efe1efb5a5a47cd00b9134cf3b6696cae999ee0fe',
    'pa_request_validate': 'd67685d4161cdf777f1c5b95f2fc9f2af44397fbeb2b61a85387d859ac095538',
    'pa_save_approval_workflow': '37745528534e0cdba66596f98d32042094694b71f85d614128e2c9f9fda0bee7',
    'pa_save_mail_settings': '34d1db6b4dc8c22021c6986ea45e9526fb87483d0566994c98d98137b57610e1',
    'pa_save_organization': 'd64a75b18834b9d976dcf539479ffd170609d9db93d9baf21c5cd0d911fbfc01',
    'pa_save_purchase_request': '920b5e8b832160a4077e459ea5188b710501a60300a4f50531e55842b5f1da4c',
    'pa_settings_validate': '1c380e45a7728865cc353f395fe9dfe8e01d845ef1a5eee34e2df51f81ab7f19',
    'pa_submit_purchase_request': '643bda3ea6945a5bd65437f4c43fb6e7ab4f1f764fdc1effb595e407b710c5c9',
    'pa_supplier_validate': '1fa7cfddf8c38967639bec07103eafe3898f7f21d05cb366a8023633aee8ee13',
    'pa_workflow_assignees': 'db45583b3716e842f3596a240337e824625ad5ec64405718082236f6e722ff5b',
    'pa_workflow_options': 'd4b76e9d5ed4540fcc0f9ab17a0ce674e8b36107a0e060c520e04260e8e0aad3',
    'pa_workflow_validate': 'b362b3f341393739380f77dc9b5f46ec0df592334a47c6e197b613e37de22e32',
}
OLD_CLIENT_SCRIPT_SHA256 = {
    'pa_settings_form': '4b4290d5ccc98a71ffb9afeb48b0186b90cb8dcaabd916e42048248eb6a0a236',
    'pa_workflow_form': 'd60f8098a5c8b3814401e01b87bbd8cb9ec1a10812a5e003828cd3cbce9db7b9',
    'pa_request_form': 'a7aa70d45c263d4f500db24b32264dd51eb9e3b40bf410919e7c72d95c1c3e19',
}


def _digest(value):
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def _prepare_script_updates(doctype, old_hashes, sources, conflicts):
    updates = []
    for name, old_digest in old_hashes.items():
        if not frappe.db.exists(doctype, name):
            continue
        target = sources.get(name)
        if target is None:
            continue
        current = frappe.db.get_value(doctype, name, "script") or ""
        current_digest = _digest(current)
        if current_digest == _digest(target):
            continue
        if current_digest != old_digest:
            conflicts.append(f"{doctype} {name}")
            continue
        updates.append((doctype, name, target))
    return updates


def execute():
    payload = metadata()
    server_sources = {
        row["name"]: row["script"]
        for row in payload["server_scripts"]
        if row["name"] in OLD_SERVER_SCRIPT_SHA256
    }
    client_sources = {
        row["name"]: row["script"]
        for row in payload["client_scripts"]
        if row["name"] in OLD_CLIENT_SCRIPT_SHA256
    }

    conflicts = []
    updates = _prepare_script_updates(
        "Server Script", OLD_SERVER_SCRIPT_SHA256, server_sources, conflicts
    )
    updates += _prepare_script_updates(
        "Client Script", OLD_CLIENT_SCRIPT_SHA256, client_sources, conflicts
    )
    if conflicts:
        frappe.throw(message("workflow_script_conflict", script=", ".join(conflicts)))

    for doctype, name, script in updates:
        frappe.db.set_value(doctype, name, "script", script, update_modified=False)

    current_translations = {
        row["message_key"]: row["text"]
        for row in payload["translations"]
        if row["message_key"] in UPDATED_TRANSLATIONS
    }
    for row in frappe.get_all(
        "PA Translation",
        filters={"message_key": ["in", list(UPDATED_TRANSLATIONS)]},
        fields=["name", "message_key"],
        limit_page_length=0,
    ):
        value = current_translations.get(row.message_key)
        if value is not None:
            frappe.db.set_value("PA Translation", row.name, "text", value, update_modified=False)

    stale = frappe.get_all(
        "PA Translation",
        filters={"message_key": ["in", list(OBSOLETE_TRANSLATIONS)]},
        fields=["name"],
        limit_page_length=0,
    )
    for row in stale:
        frappe.db.delete("PA Translation", {"name": row.name})

    if frappe.db.exists("DocType", DOCTYPE):
        existing = [
            field
            for field in REMOVED_FIELDS
            if frappe.db.exists("DocField", {"parent": DOCTYPE, "fieldname": field})
        ]
        if existing:
            frappe.model.delete_fields({DOCTYPE: existing}, delete=1)

    frappe.clear_cache()
