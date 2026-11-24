'use strict';
(() => {
  const {edition, people, stages, positions} = JSON.parse(document.getElementById('parcours-data').textContent);
  const root = document.getElementById('personal-guide');
  const message = document.getElementById('guide-message');
  const storageWarning = document.getElementById('guide-storage');
  const prefix = 'parcours-' + edition + ':';
  const memory = new Map();
  const labels = {todo:'À faire', doing:'En cours', blocked:'Bloquée', done:'Terminée'};
  const glyph = {todo:'○', doing:'◐', blocked:'!', done:'✓'};
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const blank = () => ({status:'todo', note:''});
  function read(key) {
    if (memory.has(key)) return memory.get(key);
    try { return localStorage.getItem(prefix+key); }
    catch { storageWarning.hidden = false; return null; }
  }
  function write(key, value) {
    try { localStorage.setItem(prefix+key,value); memory.delete(key); }
    catch { memory.set(key,value); storageWarning.hidden = false; }
  }
  function valid(record) {
    return record && Object.hasOwn(labels,record.status) && typeof record.note==='string' && record.note.length<=4000;
  }
  function profileKey(id, stage) { return id+'/'+stage; }
  function get(stage) {
    try { const r=JSON.parse(read(profileKey(person.id,stage)) || 'null'); return valid(r)?r:blank(); }
    catch { return blank(); }
  }
  function set(stage, record) { write(profileKey(person.id,stage),JSON.stringify(record)); }
  function personalLink(href) {
    const url=new URL(href,location.href);
    url.searchParams.set('p',person.id);
    if (selected) url.searchParams.set('etape',selected.id);
    return url.href;
  }
  function statusTag(status) {
    return '<span class="pg-tag pg-'+status+'"><i aria-hidden="true">'+glyph[status]+'</i>'+labels[status]+'</span>';
  }
  const queryPerson=new URLSearchParams(location.search).get('p');
  let person=people.find(p=>p.id===(queryPerson || read('active')));
  let selected;
  let requestedStage;
  function nextStage() { return stages.find(s=>get(s.id).status!=='done'); }
  function announce(text) { message.textContent=text; }
  function focusHeading() {
    root.querySelector('h1')?.focus({preventScroll:true});
    window.scrollTo({top:0,behavior:'instant'});
  }
  function updateLocation() {
    const url=new URL(location.href);
    if(person) url.searchParams.set('p', person.id); else url.searchParams.delete('p');
    url.hash=selected ? selected.id : '';
    if (person) write(person.id+'/current',selected?.id || '');
    try { history.replaceState(null,'',url.href); }
    catch {
      if (new URL(location.href).searchParams.get('p') !== (person?.id || null)) location.replace(url.href);
      else if (location.hash !== url.hash) location.replace(url.hash || location.pathname);
    }
  }
  function choose(id) {
    person=people.find(p=>p.id===id);
    write('active',person?.id || '');
    selected=person ? (requestedStage || stages.find(s=>s.id===read(person.id+'/current')) || nextStage()) : null;
    requestedStage=null;
    updateLocation(); announce(''); render(); focusHeading();
  }
  function selectStage(stage) {
    selected=stage; updateLocation(); render(); focusHeading();
  }
  function renderPicker() {
    const teams=[...new Set(people.map(p=>p.team))];
    root.innerHTML=`<div class="pg-intro"><div class="pg-hero-copy"><p class="pg-kicker">Paris · 24 novembre 2026 · 14 h – 17 h</p>
      <h1 tabindex="-1">Du fichier reçu<br>à la <em>décision.</em></h1><p>Suivez une position ERES jusqu’à sa publication, puis identifiez les fonds à relancer. Vous mènerez les deux enquêtes dans votre essai Databricks.</p>
      <a class="pg-start" href="#profils">Choisir mon profil <span aria-hidden="true">↓</span></a>
      </div><section class="pg-specimen" aria-label="Explorer le petit lot"><div class="pg-specimen-head"><span>Extrait du lot ERES</span><label for="pg-sample">Ligne POS
      <select id="pg-sample">${positions.map(p=>`<option value="${p.line}" ${p.line===5?'selected':''}>${p.line}</option>`).join('')}</select></label></div>
      <div id="pg-sample-result" aria-live="polite"></div></section></div>
      <div class="pg-cases"><a class="pg-case" href="#profils" data-for-stage="lot"><span>14 h 10 · Cas 1</span><strong>Quelles positions publier ?</strong><small>Agrégation ERES</small></a>
      <a class="pg-case" href="#profils" data-for-stage="fonds"><span>15 h 30 · Cas 2</span><strong>Quels fonds relancer ?</strong><small>Market Data</small></a>
      <a class="pg-case pg-setup-card" href="trial.html"><span>Avant de commencer</span><strong>Préparer mon essai →</strong><small>Notebook et lot à importer</small></a></div>
      <section id="profils" class="pg-profiles" tabindex="-1"><h2>Mon parcours d’atelier</h2><p id="pg-pick-prompt" aria-live="polite">Choisissez votre prénom. Vous retrouverez vos étapes, vos consignes métier et vos preuves dans ce navigateur.</p>
      <div class="pg-picker">${teams.map(team=>`<section><h3>${esc(team)}</h3><div class="pg-people">${people.filter(p=>p.team===team).map(p=>`<button class="pg-person" data-person="${p.id}"><span><strong>${esc(p.name)}</strong><small>${esc(p.role)}</small></span><span aria-hidden="true">→</span></button>`).join('')}</div></section>`).join('')}</div></section>`;
    showPosition();
  }
  function showPosition() {
    const row=positions.find(p=>p.line===Number(document.getElementById('pg-sample').value));
    const amount=n=>new Intl.NumberFormat('fr-FR').format(n)+' €';
    document.getElementById('pg-sample-result').innerHTML=`<p class="pg-sample-id">${esc(row.account)} · ${esc(row.day)}</p>
      <p class="pg-sample-total">${amount(row.gross)} <small>montant brut</small></p>
      <div class="pg-amount-bar" aria-hidden="true"><i style="width:${100*row.available/row.gross}%"></i><b style="width:${100*row.unavailable/row.gross}%"></b></div>
      <dl><div><dt>Disponible</dt><dd>${amount(row.available)}</dd></div><div><dt>Indisponible</dt><dd>${amount(row.unavailable)}</dd></div><div><dt>Écart à expliquer</dt><dd>${amount(row.gross-row.available-row.unavailable)}</dd></div></dl>`;
  }
  function present() {
    const dialog=document.getElementById('pg-presentation');
    const sections=stages.map(stage=>{
      const r=get(stage.id);
      return `<section><div class="pg-present-stage"><h3>${esc(stage.title)}</h3>${statusTag(r.status)}</div><p>${r.note.trim()?esc(r.note):'Aucune preuve consignée.'}</p></section>`;
    }).join('');
    document.getElementById('pg-present-body').innerHTML=`<p class="pg-kicker">${esc(person.name)} · ${esc(person.role)}</p>
      <h2 id="pg-present-title">Ma restitution</h2><p>Mes observations sur les deux cas et ma prochaine décision.</p>${sections}`;
    dialog.showModal();
  }
  function render() {
    document.querySelector('.pg-home footer a').href=person ? personalLink('guide.html') : 'guide.html';
    if(!person) { renderPicker(); return; }
    const count=stages.filter(s=>get(s.id).status==='done').length;
    const header=`<div class="pg-personbar"><div><span class="pg-monogram" aria-hidden="true">${esc(person.name[0])}</span><span><strong>${esc(person.name)}</strong><small>${esc(person.role)} · ${esc(person.team)}</small></span></div><div class="pg-person-actions"><button data-action="present">Ma restitution</button><button data-action="switch">Changer de profil</button></div></div>`;
    const rail=`<aside class="pg-rail"><div class="pg-progress"><strong>Mon avancement</strong><span>${count} / ${stages.length}</span></div><progress max="${stages.length}" value="${count}" aria-label="Étapes terminées"></progress><nav aria-label="Étapes de mon atelier"><ol>${stages.map((s,i)=>{
      const status=get(s.id).status;
      return `<li><button data-stage="${s.id}" ${selected?.id===s.id?'aria-current="step"':''}><span class="pg-marker pg-${status}" aria-hidden="true">${status==='todo'?i+1:glyph[status]}</span><span><strong>${esc(s.title)}</strong><small>${esc(s.group)} · ${labels[status]}</small></span></button></li>`;
    }).join('')}</ol></nav><label class="pg-mobile-steps" for="pg-stage">Aller à une étape<select id="pg-stage">
      <option value="" disabled ${selected?'':'selected'}>Choisir une étape</option>
      ${stages.map((stage,i)=>`<option value="${stage.id}" ${selected?.id===stage.id?'selected':''}>${i+1}. ${esc(stage.title)} · ${labels[get(stage.id).status]}</option>`).join('')}
      </select></label></aside>`;
    let body;
    if(!selected) {
      body=`<section class="pg-task"><p class="pg-kicker">Restitution</p><h1 tabindex="-1">Parcours terminé</h1><p>Vos sept étapes sont marquées comme terminées. Exportez vos observations pour conserver vos preuves et votre prochain jalon.</p><button class="pg-main" data-action="export">Exporter mon suivi</button></section>`;
    } else {
      const i=stages.indexOf(selected), r=get(selected.id), after=stages[i+1];
      const focus=person.tasks[selected.id];
      body=`<section class="pg-task"><div class="pg-task-top"><p class="pg-kicker">${esc(selected.group)} · Étape ${i+1} sur ${stages.length} · ${esc(selected.time)}</p>${statusTag(r.status)}</div>
        <h1 tabindex="-1">${esc(selected.title)}</h1><p class="pg-task-action">${esc(selected.action)}</p>
        ${focus?`<div class="pg-focus"><h2>Pour votre rôle</h2><p>${esc(focus)}</p></div>`:''}
        <div class="pg-proof"><h2>Preuve à conserver</h2><p>${esc(selected.proof)}</p></div>
        ${selected.id==='essai'?`<p>Dans le widget <code>equipe</code>, utilisez votre code personnel <code>${esc(person.id)}</code>.</p>`:''}
        <div class="pg-resources"><a class="pg-main" href="${esc(personalLink(selected.url))}">${esc(selected.link)} <span aria-hidden="true">→</span></a>${selected.extraUrl?`<a href="${esc(personalLink(selected.extraUrl))}">${esc(selected.extraLink)}</a>`:''}
        ${selected.id==='essai' ? '<a href="eres/20261123_HARVEST.zip" download>Petit lot ZIP</a><a href="notebooks/00_DEMARRER.ipynb" download>Notebook à importer</a>' : ''}</div>
        <label class="pg-note-label" for="pg-note">Ma preuve ou mon blocage</label><textarea id="pg-note" maxlength="4000" rows="2" placeholder="Lien, résultat SQL ou point à reprendre…">${esc(r.note)}</textarea>
        <div class="pg-controls">${r.status==='done'?'<button data-action="resume">Rouvrir cette étape</button>':`<button class="pg-confirm" data-action="done">Valider et continuer</button>
        ${r.status==='todo'?'<button data-action="resume">Marquer en cours</button>':''}
        ${r.status==='blocked'?'<button data-action="resume">Reprendre cette étape</button>':'<button data-action="block">Marquer comme bloquée</button>'}`}</div>
        <p class="pg-next">${after?'Étape suivante · '+esc(after.title):'Dernière étape · Exporter mon suivi'}</p></section>`;
    }
    root.innerHTML=header+'<div class="pg-layout">'+rail+'<div>'+body+`<div class="pg-backup"><span>Suivi personnel dans ce navigateur</span><button data-action="export">Exporter</button><button data-action="import">Restaurer</button><input type="file" id="pg-file" accept="application/json,.json" hidden></div></div></div>`;
  }
  function exportProgress() {
    const data={format:'harvest-parcours-v1',edition,participant:person.id,etapes:Object.fromEntries(stages.map(s=>[s.id,get(s.id)]))};
    const href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
    const a=document.createElement('a'); a.href=href; a.download='parcours-'+person.id+'.json'; a.click();
    setTimeout(()=>URL.revokeObjectURL(href),1000); announce('Copie de votre suivi exportée.');
  }
  root.addEventListener('input',e=>{
    if(e.target.id==='pg-note') set(selected.id,{...get(selected.id),note:e.target.value});
  });
  root.addEventListener('click',e=>{
    const mission=e.target.closest('[data-for-stage], .pg-start');
    if(mission) {
      requestedStage=stages.find(s=>s.id===mission.dataset.forStage);
      document.getElementById('pg-pick-prompt').textContent=requestedStage
        ? 'Choisissez votre prénom pour ouvrir « '+requestedStage.title+' ».'
        : 'Choisissez votre prénom pour commencer ou reprendre votre parcours.';
      document.getElementById('profils').focus();
      return;
    }
    const btn=e.target.closest('button'); if(!btn) return;
    if(btn.dataset.person) return choose(btn.dataset.person);
    if(btn.dataset.stage) return selectStage(stages.find(s=>s.id===btn.dataset.stage));
    const a=btn.dataset.action;
    if(a==='switch') return choose(null);
    if(a==='export') return exportProgress();
    if(a==='present') return present();
    if(a==='import') return root.querySelector('#pg-file').click();
    const statuses={resume:'doing',done:'done',block:'blocked'};
    if(!Object.hasOwn(statuses,a) || !selected) return;
    const oldTitle=selected.title;
    set(selected.id,{...get(selected.id),status:statuses[a]});
    if(a==='done') selected=nextStage();
    updateLocation(); render(); focusHeading();
    announce(oldTitle+' · '+labels[statuses[a]]);
  });
  root.addEventListener('change',async e=>{
    if(e.target.id==='pg-sample') return showPosition();
    if(e.target.id==='pg-stage') return selectStage(stages.find(s=>s.id===e.target.value));
    if(e.target.id!=='pg-file' || !e.target.files[0]) return;
    const file=e.target.files[0], id=person.id;
    try {
      if(file.size>100000) throw Error('Fichier trop volumineux.');
      const d=JSON.parse(await file.text());
      if(!d || d.format!=='harvest-parcours-v1' || d.edition!==edition || d.participant!==id)
        throw Error('Sélectionnez un export de votre profil pour cet atelier.');
      if(!d.etapes || Object.keys(d.etapes).length!==stages.length || !stages.every(s=>valid(d.etapes[s.id])))
        throw Error('Étapes ou statuts invalides.');
      if(person?.id!==id) return;
      if(stages.some(s=>{const r=get(s.id);return (r.status!=='todo'||r.note) && (r.status!==d.etapes[s.id].status||r.note!==d.etapes[s.id].note);})
         && !confirm('Remplacer votre suivi actuel par cette copie ?')) return;
      for(const stage of stages) set(stage.id,{status:d.etapes[stage.id].status,note:d.etapes[stage.id].note});
      selectStage(nextStage()); announce('Votre suivi a été restauré.');
    } catch(err) { announce('Restauration impossible. '+err.message); }
    finally { e.target.value=''; }
  });
  if(person) {
    write('active',person.id);
    selected=stages.find(s=>s.id===location.hash.slice(1)) || stages.find(s=>s.id===read(person.id+'/current')) || nextStage();
  }
  render();
})();
