/* Mappa della pagina Dove comprare: Leaflet + dati in static/data/rete.json */
(function () {
  'use strict';
  var root = document.querySelector('[data-mappa]');
  if (!root || !window.L) return;

  var el = function (s) { return root.querySelector(s); };
  var card = document.querySelector('[data-scheda-mappa]');
  var f = function (name) { return card.querySelector('[data-f="' + name + '"]'); };
  var ITALIA = [[36.4, 6.6], [47.1, 18.6]];

  var map = L.map(el('[data-leaflet]'), { preferCanvas: true, scrollWheelZoom: false });
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  map.fitBounds(ITALIA);

  fetch(root.getAttribute('data-src'))
    .then(function (r) { return r.json(); })
    .then(init)
    .catch(function () {
      f('nome').textContent = 'La mappa non si è caricata';
      f('luogo').textContent = 'Riprova più tardi, oppure usa le mappe elencate più in basso.';
    });

  function init(data) {
    var T = data.tipi, P = data.punti;
    var state = { tipo: 'tutti', regione: '', sel: -1 };
    var layer = L.layerGroup().addTo(map);
    var markers = P.map(function (p, i) {
      var m = L.circleMarker([p[5], p[6]], {
        radius: p[1] === 'gas' ? 5 : 7,
        color: '#F7F4EE', weight: 1.5, fillColor: T[p[1]].colore, fillOpacity: 0.95
      });
      m.on('click', function () { select(i, false); });
      m.bindTooltip(p[0]);
      return m;
    });

    // pulsanti per tipo
    var tipiBox = el('[data-tipi]');
    var ids = ['tutti'].concat(Object.keys(T));
    ids.forEach(function (id) {
      var n = id === 'tutti' ? P.length : P.filter(function (p) { return p[1] === id; }).length;
      if (!n) return;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'pill'; b.setAttribute('data-tipo', id);
      b.setAttribute('aria-pressed', String(id === 'tutti'));
      b.innerHTML = (id === 'tutti' ? '' : '<span class="dot" style="background:' + T[id].colore + '"></span>') +
        (id === 'tutti' ? 'Tutto' : T[id].nome) + ' <span class="n">' + n + '</span>';
      b.addEventListener('click', function () { state.tipo = id; state.sel = -1; render(true); });
      tipiBox.appendChild(b);
    });

    var sel = el('[data-regione]');
    sel.addEventListener('change', function () { state.regione = sel.value; state.sel = -1; render(true); });

    function visibili() {
      return P.map(function (_, i) { return i; }).filter(function (i) {
        return (state.tipo === 'tutti' || P[i][1] === state.tipo) && (!state.regione || P[i][4] === state.regione);
      });
    }

    function render(fit) {
      $buttons().forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-tipo') === state.tipo)); });
      // regioni con conteggio per il tipo scelto
      var conta = {};
      P.forEach(function (p) { if (state.tipo === 'tutti' || p[1] === state.tipo) conta[p[4]] = (conta[p[4]] || 0) + 1; });
      var regioni = Object.keys(conta).sort(function (a, b) { return a.localeCompare(b, 'it'); });
      sel.innerHTML = '<option value="">Tutta Italia</option>' + regioni.map(function (r) {
        return '<option value="' + esc(r) + '"' + (r === state.regione ? ' selected' : '') + '>' + esc(r) + ' (' + conta[r] + ')</option>';
      }).join('');

      var vis = visibili();
      layer.clearLayers();
      vis.forEach(function (i) { layer.addLayer(markers[i]); });
      if (fit) {
        if (state.regione && vis.length) map.fitBounds(L.latLngBounds(vis.map(function (i) { return [P[i][5], P[i][6]]; })).pad(0.2), { maxZoom: 11 });
        else map.fitBounds(ITALIA);
      }
      lista(vis);
    }

    function $buttons() { return Array.prototype.slice.call(tipiBox.querySelectorAll('button')); }

    function ordine(a, b) {
      var r = function (t) { return t === 'csa' ? 0 : t === 'gas' ? 1 : 2; };
      return r(P[a][1]) - r(P[b][1]) || P[a][2].localeCompare(P[b][2], 'it') || P[a][0].localeCompare(P[b][0], 'it');
    }

    function lista(vis) {
      var box = el('[data-lista]') || document.querySelector('[data-lista]');
      var titolo = document.querySelector('[data-titolo-lista]');
      if (!state.regione) {
        titolo.textContent = 'Scegli una regione per vedere l’elenco (' + vis.length + ' realtà in Italia)';
        box.innerHTML = '';
        return;
      }
      titolo.textContent = state.regione + ': ' + vis.length + ' realtà, prima CSA e GAS';
      box.innerHTML = vis.slice().sort(ordine).map(function (i) {
        var p = P[i];
        return '<button type="button" class="riga-rete" data-i="' + i + '" aria-pressed="' + (i === state.sel) + '">' +
          '<span class="dot" style="background:' + T[p[1]].colore + '"></span>' +
          '<span style="display:flex;flex-direction:column;gap:2px"><span style="font-size:15px;font-weight:600;color:#1D201B">' + esc(p[0]) + '</span>' +
          '<span style="font-size:13px;color:#6B6F65">' + esc(p[2]) + (p[3] ? ' (' + esc(p[3]) + ')' : '') + '</span></span></button>';
      }).join('');
      Array.prototype.forEach.call(box.querySelectorAll('[data-i]'), function (b) {
        b.addEventListener('click', function () { select(+b.getAttribute('data-i'), true); });
      });
    }

    function select(i, pan) {
      var p = P[i];
      state.sel = i;
      if (!state.regione) { state.regione = p[4]; render(false); }
      Array.prototype.forEach.call(document.querySelectorAll('.riga-rete'), function (b) {
        b.setAttribute('aria-pressed', String(+b.getAttribute('data-i') === i));
      });
      f('tipo').textContent = T[p[1]].label;
      f('tipo').style.background = T[p[1]].colore;
      f('nome').textContent = p[0];
      f('luogo').textContent = p[2] + (p[3] ? ' (' + p[3] + ')' : '') + ', ' + p[4];
      var a = f('attivo');
      a.hidden = false;
      a.textContent = p[10] ? 'Attività confermata nel 2026 dalla fonte.' : 'Attività non verificata: molti gruppi sono informali e cambiano. Scrivi prima di andare.';
      a.style.background = p[10] ? '#E5EDE2' : '#F1E3D6';
      a.style.color = p[10] ? '#2F4A36' : '#4A2E1D';
      var fonte = f('fonte');
      fonte.hidden = !p[8]; fonte.href = p[8] || '#'; fonte.textContent = 'Scheda su ' + p[9];
      var sito = f('sito');
      sito.hidden = !p[7]; sito.href = p[7] || '#';
      if (pan) map.setView([p[5], p[6]], Math.max(map.getZoom(), 10));
      markers[i].openTooltip();
    }

    function esc(s) {
      return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
    }

    var tot = document.querySelector('[data-totale]');
    if (tot) tot.textContent = P.length.toLocaleString('it-IT');
    render(true);
  }
})();
