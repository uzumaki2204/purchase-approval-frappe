(() => {
const embeddedCatalog = {"messages":{"vi":{"nav.logout":"Đăng xuất","nav.work":"Công việc","nav.procurement":"Mua hàng","nav.administration":"Quản trị"}}};
const paDeskSidebarLabels = embeddedCatalog.messages.vi;
let paDeskSidebarContext = null;

function renderPurchaseApprovalLogout(visible) {
  const bottom = document.querySelector('.body-sidebar .body-sidebar-bottom');
  if (!bottom) return;
  const existing = bottom.querySelector('.pa-sidebar-logout');
  if (!visible) {
    existing?.remove();
    return;
  }
  if (existing) return;

  const container = document.createElement('div');
  container.className = 'sidebar-item-container pa-sidebar-logout';
  const row = document.createElement('div');
  row.className = 'standard-sidebar-item';
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'item-anchor btn-reset';
  button.setAttribute('aria-label', paDeskSidebarLabels['nav.logout']);
  button.title = paDeskSidebarLabels['nav.logout'];
  const icon = document.createElement('span');
  icon.className = 'sidebar-item-icon';
  icon.setAttribute('aria-hidden', 'true');
  icon.innerHTML = frappe.utils.icon('log-out', 'sm');
  const label = document.createElement('span');
  label.className = 'sidebar-item-label';
  label.textContent = paDeskSidebarLabels['nav.logout'];
  button.append(icon, label);
  button.addEventListener('click', () => frappe.app.logout());
  row.append(button);
  container.append(row);
  bottom.insertBefore(container, bottom.querySelector('.dropdown-navbar-user'));
}

function setPurchaseApprovalSidebarContext(context) {
  paDeskSidebarContext = context?.user === frappe.session?.user && context.capabilities
    ? {user: context.user, super_user: Boolean(context.super_user), capabilities: context.capabilities}
    : null;
  keepDeskLinksInTab();
}

function purchaseApprovalSidebarItemAllowed(group, anchor) {
  const access = paDeskSidebarContext;
  if (!access || access.user !== frappe.session?.user || !anchor) return false;
  if (group === 'administration') return Boolean(access.capabilities.administration);

  if (anchor.dataset.linkType === 'DocType') return group === 'work' && access.super_user;
  const href = anchor.getAttribute('href');
  if (!href) return false;
  const url = new URL(href, location.origin);
  if (!/^\/desk\/(?:build\/)?purchase-approval\/?$/.test(url.pathname)) return false;
  const view = url.searchParams.get('view');
  if (group === 'work') {
    return view === 'dashboard' || view === 'requests'
      || (view === 'edit' && Boolean(access.capabilities.create))
      || (view === 'approvals' && Boolean(access.capabilities.approvals));
  }
  return (view === 'purchasing' && Boolean(access.capabilities.purchasing))
    || (['receiving', 'received'].includes(view) && Boolean(access.capabilities.receiving));
}

function filterPurchaseApprovalDeskSidebar() {
  if (paDeskSidebarContext?.user !== frappe.session?.user) paDeskSidebarContext = null;
  const groups = new Map([
    [paDeskSidebarLabels['nav.work'], 'work'],
    [paDeskSidebarLabels['nav.procurement'], 'procurement'],
    [paDeskSidebarLabels['nav.administration'], 'administration'],
  ]);
  for (const section of document.querySelectorAll('.body-sidebar .section-item')) {
    const group = groups.get(section.getAttribute('item-name'));
    if (!group) continue;
    const container = section.querySelector(':scope > .nested-container');
    const items = [...(container?.children || [])].filter(item => item.classList.contains('sidebar-item-container'));
    let visible = 0;
    for (const item of items) {
      const anchor = item.querySelector(':scope > .standard-sidebar-item > a.item-anchor');
      const allowed = purchaseApprovalSidebarItemAllowed(group, anchor);
      item.classList.toggle('pa-role-hidden', !allowed);
      if (allowed) visible++;
    }
    section.classList.toggle('pa-role-hidden', visible === 0);
  }
}

/* Shared Desk shell for the Purchase Approval page and its native DocTypes. */
const paNativeDocTypes = new Set([
  'PA Purchase Request',
  'PA Unit',
  'PA Supplier',
  'PA Approval Workflow',
  'PA Notification Outbox',
  'PA Translation',
  'PA Settings',
]);
const paPagePaths = new Set([
  '/desk/purchase-approval',
  '/desk/purchase-approval/',
  '/desk/build/purchase-approval',
  '/desk/build/purchase-approval/',
  '/desk/purchase-approval/trung-tâm-mua-hàng',
  '/desk/build/purchase-approval/trung-tâm-mua-hàng',
]);
let paNavigationScheduled = false;
let paNavigationContextRequest = null;

function purchaseApprovalDeskRoute() {
  const route = frappe.get_route?.() || [];
  if (['List', 'Form', 'Tree'].includes(route[0]) && paNativeDocTypes.has(route[1])) {
    return {kind: 'doctype', doctype: route[1]};
  }
  if (paPagePaths.has(decodeURI(location.pathname))) return {kind: 'page'};
  return null;
}

function purchaseApprovalMenuLinkMatches(anchor, route) {
  const url = new URL(anchor.href, location.origin);
  if (route.kind === 'doctype') {
    if (anchor.dataset.linkType !== 'DocType') return false;
    const slug = route.doctype.toLowerCase().replaceAll(' ', '-');
    return decodeURI(url.pathname).split('/').includes(slug);
  }
  if (anchor.dataset.linkType !== 'URL' || !paPagePaths.has(decodeURI(url.pathname))) return false;
  const current = new URL(location.href);
  const viewFor = value => {
    const view = value.searchParams.getAll('view').at(-1) || value.searchParams.get('pa_compat')
      || (value.searchParams.get('request') ? 'detail' : 'dashboard');
    return ({detail: 'requests', pricing: 'purchasing', 'workflow-edit': 'workflows', 'organization-edit': 'organizations'})[view] || view;
  };
  const view = viewFor(current);
  return view === viewFor(url) && (view !== 'organizations'
    || (current.searchParams.get('kind') || 'company') === (url.searchParams.get('kind') || 'company'));
}

function loadPurchaseApprovalNavigationContext() {
  const user = frappe.session?.user;
  if (!user || user === 'Guest' || paDeskSidebarContext?.user === user || paNavigationContextRequest) return;
  paNavigationContextRequest = fetch('/api/method/pa_get_context', {credentials: 'same-origin'})
    .then(response => response.ok ? response.json() : null)
    .then(result => {
      if (result?.message?.user === frappe.session?.user) setPurchaseApprovalSidebarContext(result.message);
    })
    .catch(() => {})
    .finally(() => {paNavigationContextRequest = null;});
}

function keepDeskLinksInTab() {
  const route = purchaseApprovalDeskRoute();
  const ownsRoute = Boolean(route);
  if (document.body.classList.contains('pa-only-sidebar') !== ownsRoute) {
    document.body.classList.toggle('pa-only-sidebar', ownsRoute);
  }
  renderPurchaseApprovalLogout(ownsRoute);
  if (!ownsRoute) {
    for (const row of document.querySelectorAll('.body-sidebar [data-pa-active]')) {
      row.classList.remove('active-sidebar');
      row.removeAttribute('data-pa-active');
      row.querySelector('a[aria-current="page"]')?.removeAttribute('aria-current');
    }
    return;
  }
  const sidebar = frappe.app?.sidebar;
  if (!sidebar) return;
  if (sidebar.current_module !== 'Purchase Approval') sidebar.setup('Purchase Approval');
  const anchors = [...document.querySelectorAll('.body-sidebar .section-item a.item-anchor[href]')];
  const selected = anchors.find(anchor => purchaseApprovalMenuLinkMatches(anchor, route));
  const selectedRow = selected?.closest('.standard-sidebar-item');
  for (const anchor of anchors) {
    anchor.target = '_self';
    const row = anchor.closest('.standard-sidebar-item');
    if (!row) continue;
    const active = row === selectedRow;
    if (row.classList.contains('active-sidebar') !== active) row.classList.toggle('active-sidebar', active);
    if (active) {
      if (!row.hasAttribute('data-pa-active')) row.setAttribute('data-pa-active', '1');
      if (anchor.getAttribute('aria-current') !== 'page') anchor.setAttribute('aria-current', 'page');
    } else {
      row.removeAttribute('data-pa-active');
      if (anchor.hasAttribute('aria-current')) anchor.removeAttribute('aria-current');
    }
  }
  if (selectedRow) sidebar.active_item = $(selectedRow);
  for (const [index, section] of [...document.querySelectorAll('.body-sidebar .section-item')].entries()) {
    const button = section.querySelector('button.drop-icon');
    const children = section.querySelector('.nested-container');
    if (!button || !children) continue;
    children.id = 'pa-desk-section-' + index;
    button.setAttribute('aria-controls', children.id);
    button.setAttribute('aria-label', section.getAttribute('item-name') || '');
    button.setAttribute('aria-expanded', String(!children.classList.contains('hidden')));
  }
  if (paDeskSidebarContext?.user === frappe.session?.user) filterPurchaseApprovalDeskSidebar();
  loadPurchaseApprovalNavigationContext();
}

function schedulePurchaseApprovalNavigation() {
  if (paNavigationScheduled) return;
  paNavigationScheduled = true;
  queueMicrotask(() => {
    paNavigationScheduled = false;
    keepDeskLinksInTab();
  });
}

window.PADeskNavigation = {
  sync: keepDeskLinksInTab,
  setContext: setPurchaseApprovalSidebarContext,
};
$(function () {
  frappe.router.on('change', schedulePurchaseApprovalNavigation);
  $(document).on('sidebar_setup.pa_navigation', schedulePurchaseApprovalNavigation);
  window.addEventListener('popstate', schedulePurchaseApprovalNavigation);
  const observer = new MutationObserver(records => {
    if (records.some(record => record.target === document.body
      || record.target instanceof Element && (record.target.closest('.body-sidebar')
        || [...record.addedNodes].some(node => node instanceof Element
          && (node.matches('.body-sidebar') || node.querySelector('.body-sidebar')))))) {
      schedulePurchaseApprovalNavigation();
    }
  });
  observer.observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ['class']});
  schedulePurchaseApprovalNavigation();
});

})();
