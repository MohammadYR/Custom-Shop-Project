/* Global admin enhancements (safe, lightweight, and defensive)
   - Slash (/) focuses the global search
   - Double-click any table cell to copy its text (toast feedback)
   - Remember changelist filters collapse state per page
*/
(function () {
  'use strict';
  try { console.log('[admin] custom admin.js loaded'); } catch (_) {}

  const on = (el, evt, cb, opts) => el && el.addEventListener(evt, cb, opts || false);
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  // Simple toast
  const ensureToastHost = () => {
    let host = document.getElementById('admin-toast-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'admin-toast-host';
      document.body.appendChild(host);
    }
    return host;
  };

  const showToast = (message, ttl = 1500) => {
    const host = ensureToastHost();
    const item = document.createElement('div');
    item.className = 'admin-toast';
    item.textContent = message;
    host.appendChild(item);
    setTimeout(() => item.classList.add('show')); // animate in
    setTimeout(() => {
      item.classList.remove('show');
      setTimeout(() => item.remove(), 200);
    }, ttl);
  };

  // Focus search with '/'
  on(window, 'keydown', (e) => {
    if (e.key !== '/') return;
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) return;
    const search = $('input[type="search"], input[name="q"], #searchbar');
    if (search) {
      e.preventDefault();
      search.focus();
      if (search.select) search.select();
      showToast('Focused search');
    }
  });

  // Double-click to copy table cell text
  const copyToClipboard = async (text) => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) {}
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      return true;
    } finally {
      ta.remove();
    }
  };

  const setupCopyOnDblClick = () => {
    const table = document.querySelector('#changelist-form .results, .content-wrapper .card .table');
    if (!table) return;
    on(table, 'dblclick', async (e) => {
      const cell = e.target && (e.target.closest('td') || e.target.closest('th'));
      if (!cell) return;
      const txt = (cell.innerText || '').trim();
      if (!txt) return;
      const ok = await copyToClipboard(txt);
      if (ok) showToast('Copied');
    });
  };

  // Remember filters collapse state (best-effort; works with Jazzmin cards)
  const setupFilterMemory = () => {
    const filterCard = document.querySelector('#changelist-filter, .card:has(#changelist-filter)');
    if (!filterCard) return;
    const key = 'admin_filters_' + location.pathname + location.search.replace(/[^a-z0-9]+/gi, '_');
    const collapsedClass = 'filters-collapsed';

    const apply = () => {
      const val = localStorage.getItem(key);
      if (val === '1') filterCard.classList.add(collapsedClass);
    };
    apply();

    // Inject a small toggle button if not present
    let header = filterCard.querySelector('.card-header, h2, h3') || filterCard.firstElementChild;
    if (header) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-sm btn-outline-secondary ms-auto admin-filter-toggle';
      btn.textContent = 'Toggle filters';
      header.appendChild(btn);
      on(btn, 'click', () => {
        const isCollapsed = filterCard.classList.toggle(collapsedClass);
        localStorage.setItem(key, isCollapsed ? '1' : '0');
      });
    }
  };

  // Initialize when ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setupCopyOnDblClick();
      setupFilterMemory();
    });
  } else {
    setupCopyOnDblClick();
    setupFilterMemory();
  }
})();
