/* Guida alla vita sostenibile: ricerca nel browser.
   Scarica una volta cerca.json (generato con il sito) e filtra lì.
   Niente viene inviato a server esterni. */
(function () {
  'use strict';

  var root = document.querySelector('[data-cerca]');
  if (!root) return;
  var input = root.querySelector('input[type="search"]');
  var stato = root.querySelector('[data-stato]');
  var lista = root.querySelector('[data-risultati]');
  var indice = null;
  var caricamento = null;
  var MAX = 40;

  function norma(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, ' ');
  }

  function carica() {
    if (caricamento) return caricamento;
    stato.textContent = 'Carico l’indice…';
    caricamento = fetch(root.getAttribute('data-indice'))
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (dati) {
        indice = dati.map(function (v) { v._t = norma(v.t); v._x = norma(v.x); return v; });
        return indice;
      })
      .catch(function () {
        caricamento = null;
        stato.textContent = 'Non riesco a caricare l’indice. Ricarica la pagina e riprova.';
        throw new Error('indice');
      });
    return caricamento;
  }

  function estratto(testo, parola) {
    var i = norma(testo).indexOf(parola);
    if (i < 0 || testo.length <= 160) return testo.slice(0, 160) + (testo.length > 160 ? '…' : '');
    var da = Math.max(0, i - 60);
    return (da > 0 ? '…' : '') + testo.slice(da, da + 160) + (da + 160 < testo.length ? '…' : '');
  }

  function mostra(q) {
    var parole = norma(q).split(/\s+/).filter(Boolean);
    lista.innerHTML = '';
    if (norma(q).trim().length < 2) { stato.textContent = 'Scrivi almeno due lettere.'; return; }
    var trovati = [];
    indice.forEach(function (v) {
      var punti = 0;
      for (var i = 0; i < parole.length; i++) {
        var p = parole[i];
        if (v._t.indexOf(p) >= 0) punti += 3;
        else if (v._x.indexOf(p) >= 0) punti += 1;
        else return;
      }
      if (v.g === 'Fonti') punti -= 1;
      trovati.push({ v: v, punti: punti });
    });
    trovati.sort(function (a, b) { return b.punti - a.punti; });
    if (!trovati.length) {
      stato.textContent = 'Nessun risultato per «' + q.trim() + '». Prova con una parola sola o guarda il glossario.';
      return;
    }
    stato.textContent = trovati.length === 1 ? '1 risultato' : trovati.length + ' risultati' + (trovati.length > MAX ? ', ecco i primi ' + MAX : '');
    trovati.slice(0, MAX).forEach(function (r) {
      var li = document.createElement('li');
      li.className = 'risultato';
      var a = document.createElement('a');
      a.href = r.v.u;
      var g = document.createElement('span'); g.className = 'risultato-gruppo'; g.textContent = r.v.g;
      var t = document.createElement('span'); t.className = 'risultato-titolo'; t.textContent = r.v.t;
      var x = document.createElement('span'); x.className = 'risultato-testo'; x.textContent = estratto(r.v.x, parole[0]);
      a.appendChild(g); a.appendChild(t); if (r.v.x) a.appendChild(x);
      li.appendChild(a);
      lista.appendChild(li);
    });
  }

  var timer;
  input.addEventListener('focus', function () { carica().catch(function () {}); });
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      carica().then(function () { mostra(input.value); }).catch(function () {});
      if (history.replaceState) history.replaceState(null, '', input.value ? '?q=' + encodeURIComponent(input.value) : location.pathname);
    }, 120);
  });

  var iniziale = new URLSearchParams(location.search).get('q');
  if (iniziale) { input.value = iniziale; carica().then(function () { mostra(iniziale); }).catch(function () {}); }
  else input.focus();
})();
