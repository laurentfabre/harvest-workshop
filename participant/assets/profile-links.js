'use strict';

// The extracted kit can have a separate storage area for each file. Pass the
// participant and checkpoint in navigation and keep evidence in the workbook.
const workshopProfile = (() => {
  const {edition, ids, stages, names} = JSON.parse(document.getElementById('profile-context').textContent);
  const params = new URLSearchParams(location.search);
  if (location.hash === '#revue') document.querySelector('details#revue')?.setAttribute('open', '');
  const id = params.get('p');
  if (!ids.includes(id)) return null;
  for (const code of document.querySelectorAll('[data-person-code]')) code.textContent = id;
  const requested = params.get('etape');
  const current = Object.hasOwn(stages, requested) ? requested : null;
  function link(target) {
    const url = new URL(target, location.href);
    url.searchParams.set('p', id);
    const page = url.pathname.split('/').pop();
    if (page === 'index.html' && current) url.hash = current;
    if (page === 'missions.html') url.searchParams.set('etape', 'fonds');
    if (page === 'eres.html') url.searchParams.set('etape', url.hash === '#positions' ? 'lot' : current || 'lot');
    if (page === 'trial.html') url.searchParams.set('etape', 'essai');
    if (page === 'guide.html' && current) url.searchParams.set('etape', current);
    return url.href;
  }
  for (const anchor of document.querySelectorAll('a[href]')) {
    const href = anchor.getAttribute('href');
    if (/^(index|missions|guide|eres|trial)\.html(?:#|$)/.test(href)) anchor.href = link(href);
  }
  if (current && !location.pathname.endsWith('/guide.html')) {
    const checkpoint = document.createElement('aside');
    checkpoint.className = 'checkpoint';
    checkpoint.setAttribute('aria-label','Mon point de reprise');
    const label = document.createElement('span');
    label.textContent = names[id]+' · '+stages[current];
    const back = document.createElement('a');
    back.href = link('index.html');
    back.textContent = 'Consigner ma preuve →';
    checkpoint.append(label,back);
    document.body.append(checkpoint);
    document.body.classList.add('with-checkpoint');
  }
  return {id, edition, link};
})();
