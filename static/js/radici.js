/* Guida alla vita sostenibile: piccoli comportamenti interattivi, senza librerie.
   Senza JavaScript tutto il contenuto resta visibile. */
(function () {
  'use strict';

  function $all(root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); }
  function setHash(id) { if (history.replaceState) history.replaceState(null, '', '#' + id); }

  /* Voci di Cibo e Casa: reparto, poi voce */
  $all(document, '[data-voci]').forEach(function (root) {
    var tabs = $all(root, '[data-cat]').filter(function (el) { return el.tagName === 'BUTTON'; });
    var lists = $all(root, '[data-cat-list]');
    var panels = $all(root, '[data-voce-panel]');
    var links = $all(root, 'a[data-voce]');

    function open(id, scroll) {
      var panel = root.querySelector('[data-voce-panel="' + id + '"]');
      if (!panel) return false;
      var cat = panel.getAttribute('data-cat');
      tabs.forEach(function (t) { t.setAttribute('aria-selected', String(t.getAttribute('data-cat') === cat)); });
      lists.forEach(function (l) { l.classList.toggle('is-open', l.getAttribute('data-cat-list') === cat); });
      panels.forEach(function (p) { p.classList.toggle('is-open', p === panel); });
      links.forEach(function (a) {
        if (a.classList.contains('voce-btn')) a.setAttribute('aria-pressed', String(a.getAttribute('data-voce') === id));
      });
      if (scroll) panel.scrollIntoView({ block: 'start' });
      return true;
    }

    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        var first = root.querySelector('[data-cat-list="' + t.getAttribute('data-cat') + '"] [data-voce]');
        if (first) { open(first.getAttribute('data-voce')); setHash(first.getAttribute('data-voce')); }
      });
    });
    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var id = a.getAttribute('data-voce');
        open(id, a.classList.contains('ghost-btn'));
        setHash(id);
      });
    });

    var fromHash = location.hash.slice(1);
    if (!(fromHash && open(fromHash, true)) && panels[0]) open(panels[0].getAttribute('data-voce-panel'));
  });

  /* Schede di Conoscere la rete: un pannello alla volta */
  $all(document, '[data-schede]').forEach(function (root) {
    var panels = $all(root, '[data-scheda-panel]');
    var links = $all(root, '[data-scheda]');

    function open(id, scroll) {
      var panel = root.querySelector('[data-scheda-panel="' + id + '"]');
      if (!panel) return false;
      panels.forEach(function (p) { p.classList.toggle('is-open', p === panel); });
      links.forEach(function (a) {
        if (a.getAttribute('role') === 'tab') a.setAttribute('aria-selected', String(a.getAttribute('data-scheda') === id));
      });
      if (scroll) panel.scrollIntoView({ block: 'start' });
      return true;
    }

    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var id = a.getAttribute('data-scheda');
        open(id, a.classList.contains('ghost-btn') || window.innerWidth < 900);
        setHash(id);
      });
    });

    var fromHash = location.hash.slice(1);
    if (!(fromHash && open(fromHash, true)) && panels[0]) open(panels[0].getAttribute('data-scheda-panel'));
  });

  /* Filtro per categoria (capitolo Digitale) */
  $all(document, '[data-filtro]').forEach(function (root) {
    var buttons = $all(root, '[data-filtro-cat]');
    var cards = $all(root, 'article[data-cat]');
    var conta = root.querySelector('[data-conta]');
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        var cat = b.getAttribute('data-filtro-cat');
        var n = 0;
        buttons.forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
        cards.forEach(function (c) {
          var show = cat === 'tutte' || c.getAttribute('data-cat') === cat;
          c.hidden = !show;
          if (show) n++;
        });
        if (conta) conta.textContent = n;
      });
    });
  });
})();
