import json
from pathlib import Path

_root = Path(__file__).parent
_catalog = json.loads((_root / 'ui-translations.json').read_text(encoding='utf-8'))
app_name = 'purchase_approval'
app_title = _catalog['messages']['nav.purchase_approval']
app_publisher = 'Onichan'
app_description = _catalog['messages']['app.title']
app_email = ''
app_license = 'Proprietary'
app_logo_url = '/assets/purchase_approval/images/purchase-approval-desk-icon.svg'
add_to_apps_screen = [{
    'name': app_name,
    'title': app_title,
    'logo': app_logo_url,
    'route': '/desk/purchase-approval/trung-tâm-mua-hàng',
    'sequence_id': 40,
    'has_permission': 'purchase_approval.access.can_open',
}]

app_include_js = ['/assets/purchase_approval/js/desk-navigation.js']
app_include_css = ['/assets/purchase_approval/css/desk-navigation.css']

before_install = 'purchase_approval.install.before_install'
after_install = 'purchase_approval.install.after_install'
after_migrate = 'purchase_approval.install.after_migrate'
