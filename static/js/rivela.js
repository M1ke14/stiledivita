/* Guida alla vita sostenibile: il testo compare mentre scorri.
   Titoli: le parole salgono da sotto una riga. Paragrafi e liste: entrano
   sfocati e si mettono a fuoco. Foto: si scoprono dal basso.
   Senza JavaScript, senza IntersectionObserver o con "riduci movimento"
   non succede niente e tutto resta visibile. */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var main = document.querySelector('main');
  if (!main) { root.classList.remove('rv-pre'); return; }

  // Le parti che cambiano con un clic (voci, schede, mappa) restano immediate.
  function escluso(el) {
    return !!el.closest('[data-panel], [data-voce-panel], [data-scheda-panel], .leaflet-container, .tabella-fonti, [role="tablist"], .voci-grid, .lista-rete');
  }

  /* Titoli: ogni parola in una maschera */
  function spezza(el) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parti = n.textContent.split(/(\s+)/);
          if (parti.length === 1 && !parti[0]) return;
          var frag = document.createDocumentFragment();
          parti.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            var w = document.createElement('span');
            w.className = 'rv-w';
            var s = document.createElement('span');
            s.style.setProperty('--i', Math.min(i++, 14));
            s.textContent = p;
            w.appendChild(s);
            frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) {
          walk(n);
        }
      });
    })(el);
  }

  var titoli = Array.prototype.filter.call(main.querySelectorAll('h1, h2'), function (el) { return !escluso(el); });
  var blocchi = Array.prototype.filter.call(
    main.querySelectorAll('p, ol > li, ul > li, nav[aria-label="Indice dei capitoli"] > a, .apertura-testo > div, section > div > div > a, h3'),
    function (el) {
      if (escluso(el)) return false;
      if (el.closest('h1, h2, figure')) return false;
      // un blocco dentro un altro blocco già animato si muove col genitore
      var su = el.parentElement && el.parentElement.closest('li, nav[aria-label="Indice dei capitoli"] > a, .apertura-testo > div, section > div > div > a');
      return !su || su === el;
    }
  );
  var foto = Array.prototype.filter.call(main.querySelectorAll('figure'), function (el) { return !escluso(el); });

  titoli.forEach(function (el) { spezza(el); el.classList.add('rv-parole'); });
  blocchi.forEach(function (el) { el.classList.add('rv-blocco'); });
  foto.forEach(function (el) { el.classList.add('rv-foto'); });
  root.classList.add('rv-on');
  root.classList.remove('rv-pre');

  // Gli elementi che entrano insieme partono uno dopo l'altro, al massimo sei passi.
  var coda = [];
  var programmato = false;
  function svuota() {
    programmato = false;
    coda.sort(function (a, b) {
      var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
      return (ra.top - rb.top) || (ra.left - rb.left);
    });
    coda.forEach(function (el, n) {
      el.style.setProperty('--d', Math.min(n, 6) * 70 + 'ms');
      el.classList.add('is-in');
    });
    coda = [];
  }

  var io = new IntersectionObserver(function (voci) {
    voci.forEach(function (v) {
      if (!v.isIntersecting) return;
      io.unobserve(v.target);
      coda.push(v.target);
    });
    if (coda.length && !programmato) { programmato = true; setTimeout(svuota, 16); }
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });

  titoli.concat(blocchi, foto).forEach(function (el) { io.observe(el); });

  // Chi arriva con la tastiera o da un link interno non deve trovare testo nascosto.
  function mostraTutto() {
    titoli.concat(blocchi, foto).forEach(function (el) { el.classList.add('is-in'); io.unobserve(el); });
  }
  document.addEventListener('focusin', function (e) {
    var el = e.target.closest && e.target.closest('.rv-parole, .rv-blocco, .rv-foto');
    if (el) el.classList.add('is-in');
  });
  window.addEventListener('beforeprint', mostraTutto);
})();
