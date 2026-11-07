import json
from pathlib import Path
import frappe

def can_open():
    if frappe.session.user == 'Guest':
        return False
    if frappe.session.user == 'Administrator':
        return True
    catalog = json.loads(Path(__file__).with_name('ui-translations.json').read_text(encoding='utf-8'))
    if set(frappe.get_roles()) & set(catalog['roles']):
        return True
    from purchase_approval.workflow_runtime import capabilities
    return any(capabilities(frappe.session.user).values())
