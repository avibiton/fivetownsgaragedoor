/* Five Towns Garage Door — minimal progressive enhancement (no dependencies). */
(function () {
  'use strict';
  var doc = document;
  var body = doc.body;

  /* ---- Mobile menu ---- */
  var menuBtn = doc.querySelector('.menu-btn');
  var nav = doc.getElementById('site-nav');
  function setMenu(open) {
    if (!menuBtn || !nav) return;
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('is-open', open);
    body.classList.toggle('nav-open', open);
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      setMenu(menuBtn.getAttribute('aria-expanded') !== 'true');
    });
  }

  /* ---- Dropdown submenus (click/keyboard; hover handled in CSS on desktop) ---- */
  var toggles = doc.querySelectorAll('.nav__toggle');
  function closeSubs(except) {
    toggles.forEach(function (t) {
      if (t === except) return;
      t.setAttribute('aria-expanded', 'false');
      t.parentNode.classList.remove('is-open');
    });
  }
  toggles.forEach(function (t) {
    t.addEventListener('click', function () {
      var open = t.getAttribute('aria-expanded') !== 'true';
      closeSubs(t);
      t.setAttribute('aria-expanded', open ? 'true' : 'false');
      t.parentNode.classList.toggle('is-open', open);
    });
  });
  doc.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.nav__item')) closeSubs(null);
  });
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openToggle = doc.querySelector('.nav__toggle[aria-expanded="true"]');
    if (openToggle) { closeSubs(null); openToggle.focus(); return; }
    if (menuBtn && menuBtn.getAttribute('aria-expanded') === 'true') { setMenu(false); menuBtn.focus(); }
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1100 && body.classList.contains('nav-open')) setMenu(false);
  });

  /* ---- Service request form: composes an email in the visitor's mail app.
         No backend endpoint exists; see README "Service request form". ---- */
  var form = doc.getElementById('service-request');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var f = form.elements;
      var subject = 'Service Request — ' + (f.service.value || 'Garage Door') + (f.town.value ? ' — ' + f.town.value : '');
      var lines = [
        'Name: ' + f.name.value,
        'Phone: ' + f.phone.value,
        'Email: ' + (f.email.value || '—'),
        'Town: ' + (f.town.value || '—'),
        'Service needed: ' + (f.service.value || '—'),
        '',
        f.message.value
      ];
      window.location.href = 'mailto:service@fivetownsgaragedoor.com?subject=' +
        encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      var status = doc.getElementById('form-status');
      if (status) status.hidden = false;
    });
  }
})();
