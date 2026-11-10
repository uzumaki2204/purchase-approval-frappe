const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'purchase_approval', 'purchase_approval', 'page', 'purchase_approval', 'purchase_approval.js'),
  'utf8',
);
const start = source.indexOf('const call = async (action');
const end = source.indexOf('const boot =', start);
assert.ok(start > 0 && end > start);
const createCall = new Function('frappe', 'catalog', 't', 'context', `${source.slice(start, end)}return call;`);
const catalog = {
  messages: {
    vi: {
      'error.workflow_in_use': 'Quy trình đã được dùng trong đề nghị hoặc phiên duyệt.',
      'error.server': 'Không thể hoàn tất yêu cầu.',
    },
    en: {},
  },
};
const t = key => catalog.messages.vi[key];

async function check(error, expected) {
  const call = createCall({call: async () => {throw error;}}, catalog, t, {messages: {}});
  await assert.rejects(
    call('purchase_approval.workflow_api.delete_approval_workflow'),
    result => result.message === expected,
  );
}

(async () => {
  await check({responseText: 'frappe.exceptions.ValidationError: error.workflow_in_use'}, catalog.messages.vi['error.workflow_in_use']);
  await check({responseJSON: {_server_messages: catalog.messages.vi['error.workflow_in_use']}}, catalog.messages.vi['error.workflow_in_use']);
  await check({message: 'unexpected failure'}, catalog.messages.vi['error.server']);
  process.stdout.write('API error localization OK\n');
})().catch(error => {process.stderr.write(`${error.stack}\n`); process.exitCode = 1;});
