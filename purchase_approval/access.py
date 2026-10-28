import json
from pathlib import Path
import frappe

def can_open():
    if frappe.session.user == 'Administrator':
        return True
    catalog = json.loads(Path(__file__).with_name('ui-translations.json').read_text(encoding='utf-8'))
    return bool(set(frappe.get_roles()) & set(catalog['roles']))
