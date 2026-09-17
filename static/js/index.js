/* Progressive enhancement only: content, figures, and tables work without JS. */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('.site-nav');
    var toggle = document.getElementById('nav-toggle');
    var menu = document.getElementById('nav-menu');
    var research = document.getElementById('research-navigation');
    var researchToggle = document.getElementById('research-toggle');

    function setResearch(open) {
      if (!research || !researchToggle) return;
      research.classList.toggle('is-open', open);
      researchToggle.setAttribute('aria-expanded', String(open));
    }
    function setMenu(open) {
      if (!toggle || !menu) return;
      menu.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
      if (!open) setResearch(false);
    }

    if (toggle && menu) {
      toggle.addEventListener('click', function () { setMenu(!menu.classList.contains('is-open')); });
      window.matchMedia('(min-width: 769px)').addEventListener('change', function () { setMenu(false); });
    }
    if (research && researchToggle) {
      researchToggle.addEventListener('click', function () { setResearch(!research.classList.contains('is-open')); });
    }
    if (nav) {
      nav.querySelectorAll('a[href]').forEach(function (link) {
        link.addEventListener('click', function () { setMenu(false); });
      });
      document.addEventListener('click', function (event) {
        if (!nav.contains(event.target)) setMenu(false);
      });
      document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        if (research && research.classList.contains('is-open')) {
          setResearch(false);
          researchToggle.focus();
        } else if (menu && menu.classList.contains('is-open')) {
          setMenu(false);
          toggle.focus();
        }
      });
      nav.addEventListener('focusout', function () {
        window.setTimeout(function () {
          if (!nav.contains(document.activeElement)) setMenu(false);
        }, 0);
      });
    }

    document.querySelectorAll('[data-scroll-table]').forEach(function (shell) {
      var wrapper = shell.querySelector('.table-wrapper');
      if (!wrapper) return;
      var hintId = wrapper.getAttribute('aria-describedby');
      var hint = hintId ? document.getElementById(hintId) : null;
      var rowLabel = wrapper.querySelector('.sticky-column');
      function updateScrollState() {
        var maxScroll = wrapper.scrollWidth - wrapper.clientWidth;
        var overflow = maxScroll > 1;
        shell.dataset.scrollable = String(overflow);
        shell.dataset.atEnd = String(wrapper.scrollLeft >= maxScroll - 1);
        if (rowLabel) {
          shell.style.setProperty('--sticky-column-width', rowLabel.getBoundingClientRect().width + 'px');
        }
        if (hint) {
          hint.hidden = !overflow;
          if (overflow) wrapper.setAttribute('aria-describedby', hintId);
          else wrapper.removeAttribute('aria-describedby');
        }
      }
      wrapper.addEventListener('scroll', updateScrollState, { passive: true });
      if ('ResizeObserver' in window) {
        var observer = new ResizeObserver(updateScrollState);
        observer.observe(wrapper);
        var table = wrapper.querySelector('table');
        if (table) observer.observe(table);
      } else {
        window.addEventListener('resize', updateScrollState);
      }
      if (document.fonts) document.fonts.ready.then(updateScrollState);
      updateScrollState();
    });
  });
}());
