'use strict';
const W=window.WORKSHOP,SQL=window.SQL,DATASET=window.DATASET;
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const STORAGE='harvest-workshop-v1'+(workshopProfile ? ':'+workshopProfile.edition+':'+workshopProfile.id : '');
const owner=workshopProfile ? {participant:workshopProfile.id,edition:workshopProfile.edition} : {};
const states=['NOT RUN','PASS','FAIL','BLOCKED','NOT APPLICABLE'];
let state={format:'harvest-workbook-v1',...owner,version:W.version,dataset:DATASET,bindings:{...window.BINDINGS},records:{}},track=workshopProfile?'funds':'contracts',step=0;
const steps=['Préparer','Enquêter','Construire','Vérifier','Décider'];
const stepHints=['Votre mission & vos outils','Questionner avec Genie','Donner forme à votre idée','Confronter les résultats','Défendre votre décision'];
const stageTimes=[
  W.agenda.find(block=>block.id==='prepare').minutes+' min · ensemble',
  '20 min · enquête',
  '25 min · création et itération',
  '15 min · preuves',
  W.agenda.find(block=>block.id==='decide').minutes+' min · restitution collective',
];
const meta={contracts:{letter:'A',category:'AGRÉGATION DE CONTRATS',title:'Préserver la valeur fournisseur.',short:'Contrats',description:'Distinguez ce qui a été conservé, transformé ou perdu dans la conversion.',output:'Une app de revue des conversions',symbol:'≋'},funds:{letter:'B',category:'DONNÉES DE FONDS',title:'Repérer ce qui manque.',short:'Fonds',description:'Distinguez l’absence, l’attente normale et les calculs à réexaminer.',output:'Une app de fraîcheur et d’impact',symbol:'↗'}};
try{const prior=JSON.parse(localStorage.getItem(STORAGE)||'null');if(prior)state=validateImport(prior);}catch(e){setTimeout(()=>notice('Stockage indisponible ou notes incompatibles : exporter le carnet avant de quitter.'),0);}
function key(){return JSON.stringify([state.bindings.environment||'non-configure',DATASET,track]);}
function record(){return state.records[key()]??={fields:{},checks:{}};}
function save(){try{localStorage.setItem(STORAGE,JSON.stringify(state));}catch(e){notice('Sauvegarde navigateur indisponible : utiliser Exporter JSON.');}}
let noticeTimer;
function notice(msg,transient=false){clearTimeout(noticeTimer);const status=$('#status');(document.querySelector('dialog[open]')||document.body).append(status);status.textContent=msg;status.classList.toggle('visible',Boolean(msg));if(transient)noticeTimer=setTimeout(()=>{status.classList.remove('visible');status.textContent='';},6000);}
function t(){return W.tracks.find(x=>x.id===track);}
function identifier(x){return /^[A-Za-z0-9_-]+$/.test(x);}
function https(x){try{return new URL(x).protocol==='https:';}catch{return false;}}
function bound(text){const b=state.bindings;const ns=identifier(b.catalog)&&identifier(b.schema)?'`'+b.catalog+'`.`'+b.schema+'`.':'{{ns}}';return text.replaceAll('{{ns}}',ns).replaceAll('{{app_space_url}}',https(b.app_space_url)?b.app_space_url:'{{app_space_url}}').replaceAll('{{identity_mode}}',b.identity_mode||'non-verifie');}
function serviceLink(label,url){return https(url)?'<a class="primary" href="'+esc(url)+'" target="_blank" rel="noopener">Ouvrir '+label+' ↗</a>':'<button class="primary" data-open-settings>Configurer '+label+' ↗</button>';}
function p(text){return '<p>'+esc(bound(text))+'</p>';}
function list(items){return '<ol>'+items.map(x=>'<li>'+esc(bound(x))+'</li>').join('')+'</ol>';}
function block(title,body,extra=''){return '<section class="card '+extra+'"><h2>'+esc(title)+'</h2>'+body+'</section>';}
function disclosure(title,body,extra=''){return '<details class="disclosure '+extra+'"><summary>'+esc(title)+'<span class="disclosure-plus" aria-hidden="true">+</span></summary><div class="disclosure-body">'+body+'</div></details>';}
function code(title,value,id,description=''){return '<section class="code-card"><div class="code-heading"><div><span class="eyebrow">'+(id.startsWith('sql')?'SQL DE RÉFÉRENCE':'PROMPT BUILDER')+'</span><h2>'+esc(title)+'</h2></div><button data-copy="'+id+'" class="copy-button" aria-label="Copier '+esc(title)+'">Copier <span aria-hidden="true">⧉</span></button></div>'+p(description)+disclosure('Lire le texte complet','<pre tabindex="0" id="'+id+'">'+esc(bound(value))+'</pre>','code-reveal')+'</section>';}
function route(){const m=location.hash.match(/^#(contracts|funds)\/([0-4])$/);if(m){track=m[1];step=Number(m[2]);}}
function go(index,newTrack=track){save();track=newTrack;step=index;history.pushState(null,'','#'+track+'/'+step);render();$('#step-title').focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
const panelTriggers=new WeakMap();
function openPanel(id,field){const dialog=document.getElementById(id);if(!dialog.open){panelTriggers.set(dialog,document.activeElement);dialog.showModal();}document.body.classList.add('panel-open');dialog.append($('#status'));if(field){const input=document.querySelector('[data-field="'+field+'"]');if(input){input.closest('details').open=true;input.focus();}}}
function renderSettings(){const labels={environment:'Environnement',workspace_url:'Workspace',catalog:'Catalogue',schema:'Schéma',warehouse_id:'Warehouse SQL',genie_contracts_url:'Genie · contrats',genie_funds_url:'Genie · fonds',app_space_url:'Genie App Builder',identity_mode:'Mode de lecture et identité',owner:'Responsable',expires_on:'Fin de mise à disposition',app_space_name:'App Space'};$('#bindings').innerHTML=Object.entries(state.bindings).map(([k,v])=>'<div class="setting-field"><label for="bind-'+k+'">'+esc(labels[k]||k)+'</label><input id="bind-'+k+'" name="'+k+'" value="'+esc(v)+'" autocomplete="off"></div>').join('')+'<button class="primary" type="submit">Appliquer les liens</button>';}
function render(){
 const m=meta[track],b=state.bindings;
 document.body.dataset.track=track;document.body.dataset.step=step;
 $('#track').value=track;$('#notes-track').value=track;
 $('#steps').innerHTML=steps.map((x,i)=>'<button data-step="'+i+'"'+(i===step?' aria-current="step"':'')+'><span class="stage-number">'+String(i+1).padStart(2,'0')+'</span><span><strong>'+x+'</strong><small>'+stepHints[i]+'</small></span><span class="stage-arrow" aria-hidden="true">↗</span></button>').join('');
 $('#current').textContent='PARCOURS '+m.letter+' / '+m.category;
 $('#step-title').textContent=steps[step];$('#decision').textContent=t().question;
 $('#stage-time').textContent=stageTimes[step];$('#stage-position').textContent=String(step+1).padStart(2,'0')+' / 05';
 $('#links').innerHTML=[['Workspace',b.workspace_url],['Genie du parcours',track==='contracts'?b.genie_contracts_url:b.genie_funds_url],['Genie App Builder',b.app_space_url]].map(([n,u])=>https(u)?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+n+' <span aria-hidden="true">↗</span></a>':'<span class="muted">'+n+' · à configurer</span>').join('');
 let html='';
 if(step===0){
  html=welcomeExperience()+missionExperience()+semanticEntry();
  html+='<div class="prep-grid">'+block('Votre mission',p(t().decision)+'<div class="role-note">'+esc(t().roles)+'</div>','mission-card')+block('Avant de démarrer','<ul class="prep-list"><li><span>01</span>Ouvrez les liens Databricks de votre session.</li><li><span>02</span>Vérifiez le schéma personnel affiché dans votre notebook.</li><li><span>03</span>Ouvrez le carnet et notez votre nom et votre essai.</li></ul><button class="text-button" data-note="team">Ouvrir mon carnet <span aria-hidden="true">↗</span></button>','ready-card')+'</div>';
  let minute=0;html+=disclosure('Le programme de votre demi-journée','<ol class="agenda">'+W.agenda.map(a=>{const start=minute;minute+=a.minutes;return '<li><span>'+start+'—'+minute+'<small>MIN</small></span><div><strong>'+esc(a.title)+'</strong><p>'+esc(a.detail)+'</p></div></li>';}).join('')+'</ol>');
  html+=disclosure('Préparer les accès et comprendre les outils',list(W.preflight)+p(W.surfaces)+'<button data-open-settings class="text-button">Vérifier les liens de session ↗</button>');
 }
 if(step===1){
  html='<div class="task-banner"><span class="task-icon" aria-hidden="true">?</span><div><span class="eyebrow">VOTRE OBJECTIF</span><p>Obtenir une réponse. Puis comprendre d’où elle vient.</p></div>'+serviceLink('Genie',track==='contracts'?b.genie_contracts_url:b.genie_funds_url)+'</div><div class="question-list">'+t().questions.map((q,i)=>'<article class="question-card"><span class="question-number">0'+(i+1)+'</span><div><span class="eyebrow">'+['EXPLORER','QUANTIFIER','CHALLENGER'][i]+'</span><p id="question-'+i+'">'+esc(q)+'</p></div><button class="copy-button" data-copy="question-'+i+'" aria-label="Copier la question '+(i+1)+'">Copier <span aria-hidden="true">⧉</span></button></article>').join('')+'</div>';
  html+=block('Avant de passer à Builder',p(t().handoff)+'<button class="text-button" data-note="genie">Consigner mes preuves ↗</button>','handoff-card');
  html+=disclosure('Le contrat de données du parcours',p(t().contract))+disclosure('Les règles communes et les limites',p(W.shared_contract));
 }
 if(step===2){
  html='<div class="task-banner"><span class="task-icon" aria-hidden="true">↗</span><div><span class="eyebrow">VOTRE OBJECTIF</span><p>Une première version. Une amélioration fondée sur vos observations.</p></div>'+serviceLink('Builder',b.app_space_url)+'</div><div class="context-strip"><span><i class="green-dot"></i> '+esc(b.environment)+'</span><span>Lecture seule</span><button data-open-settings class="text-button">Vérifier mes liens ↗</button></div>';
  html+=code('01 · Donner forme à votre enquête',t().prompt1,'prompt1','Joignez la conversation Genie, le SQL inspecté et le contrat que vous avez validé.');
  html+=code('02 · Améliorer ce que vous avez observé',t().prompt2,'prompt2','Appuyez-vous sur un écart réel : une valeur, un libellé, une unité ou un cas limite.');
  html+=block('Gardez une trace de votre progression','<div class="handoff-steps"><span><b>01</b> Lien de l’aperçu</span><span><b>02</b> Écart observé</span><span><b>03</b> Version améliorée</span></div><button class="text-button" data-note="observations">Noter mon observation ↗</button>');
  html+=disclosure('Le périmètre à préserver',p(W.disclosure)+p('Conserver les versions avant/après. Tester l’application publiée séparément de son aperçu. Aucun résultat de ce portail n’est une réponse live.'));
 }
 if(step===3){
  html='<div class="task-banner"><span class="task-icon" aria-hidden="true">≍</span><div><span class="eyebrow">VOTRE OBJECTIF</span><p>Le même périmètre, trois lectures : SQL, Genie et votre app.</p></div><button class="secondary" data-note="evidence">Noter les preuves ↗</button></div>';
  html+='<div class="section-heading"><div><span class="eyebrow">LA RÉFÉRENCE INDÉPENDANTE</span><h2>Inspectez. Exécutez. Comparez.</h2></div></div><div class="sql-grid">'+t().sql_ids.map((id,i)=>code(id,SQL[id],'sql-'+id,['La population et les statuts.','Les valeurs et les cas individuels.','Un filtre sans résultat.'][i])).join('')+'</div>';
  html+=block('Votre registre de vérification','<p class="muted">Ces statuts sont vos observations. Ils n’exécutent aucun test automatique.</p><div class="checks-list">'+t().checks.map((c,i)=>'<article class="check"><div class="check-top"><span class="check-index">0'+(i+1)+'</span><h3>'+esc(c.case)+'</h3><label class="sr" for="check-'+c.id+'">Statut observé · '+esc(c.case)+'</label><select id="check-'+c.id+'" data-check="'+c.id+'" data-state="'+esc(record().checks[c.id]||'NOT RUN')+'">'+states.map(s=>'<option'+((record().checks[c.id]||'NOT RUN')===s?' selected':'')+'>'+s+'</option>').join('')+'</select></div><p>'+esc(c.expected)+'</p></article>').join('')+'</div><p class="muted">Même dataset, identité, date, filtres et définitions. Justifiez les statuts dans le carnet ; NOT APPLICABLE exige une raison.</p>');
 }
 if(step===4){
  html='<section class="decision-hero"><span class="eyebrow">DE LA PREUVE À L’ACTION</span><h2>Votre décision.<br><em>Votre prochaine étape.</em></h2><p>'+esc(W.presentation)+'</p><button class="lime-button" data-note="decision">Préparer ma restitution ↗</button></section>';
  html+='<div class="deliverable-grid">'+[['01','Ce que vous avez construit','Deux apps, leurs liens et leurs versions.'],['02','Ce que vous pouvez prouver','Une comparaison SQL / Genie / app et une limite assumée.'],['03','Ce qui vient ensuite','Une prochaine action, un responsable et une date.']].map(x=>'<section><span class="eyebrow">'+x[0]+'</span><h2>'+x[1]+'</h2><p>'+x[2]+'</p></section>').join('')+'</div>';
  html+=block('Emportez la suite','<div class="resource-grid">'+[['guide.html','Guide de l’atelier','Toutes les consignes, imprimables'],['lab.py','Notebook Databricks','Références métier et comparaisons sémantiques'],['decision-workbook.md','Carnet Markdown','Un support à partager'],['decision-workbook.csv','Registre CSV','Décisions et prochains jalons'],['data/dataset.json','Données & schémas','Le jeu synthétique complet'],['references.json','Résultats de référence','Les attendus pour comparer'],['semantic/model.json','Modèle métier & métriques','Objets, relations et définitions'],['semantic/'+track+'.md','Mini-lab du parcours','Exercices et SQL avant/après']].map(([url,title,desc])=>'<a href="'+url+'"'+(url.endsWith('html')?' target="_blank" rel="noopener"':' download')+'><div><strong>'+title+'</strong><small>'+desc+'</small></div><span aria-hidden="true">↗</span></a>').join('')+'</div>');
  html+=disclosure('Aller plus loin après l’atelier',p(t().extension));
 }
 if(step>0)html=beginnerHint()+html+semanticEntry();
 html+='<div class="support-row">'+disclosure('Un blocage ? Voici votre point d’appui.',p(t().fallback))+disclosure('Ce que ce jeu permet de démontrer',p(W.disclosure))+'</div>';
 $('#content').innerHTML=html;
 $('#prev').disabled=step===0;$('#next').disabled=false;$('#next').innerHTML=step<4?steps[step+1]+' <span aria-hidden="true">→</span>':'Parcours '+(track==='contracts'?'B':'A')+' <span aria-hidden="true">→</span>';$('#next-hint').textContent=step<4?'À suivre · '+stepHints[step+1]:'Ouvrir l’autre mission.';
 renderNotes();renderSettings();
 if(workshopProfile){
   const printLink=$('#content a[href="guide.html"]');
   if(printLink)printLink.href=workshopProfile.link('guide.html');
   if(step===4){
     $('#next').textContent='Mon parcours →';
     $('#next-hint').textContent='Retrouver mon suivi personnel.';
   }
 }
 document.querySelector('.journey').setAttribute('aria-label','Parcours et étapes · étape '+(step+1)+' sur 5');
}
function renderNotes(){
 $('#notes-context').textContent=(state.bindings.environment||'non-configure')+' / '+t().label;
 $('#notes').innerHTML=W.workbook_fields.map((f,i)=>'<details class="note-field"'+(i<2?' open':'')+'><summary><span class="note-dot '+(record().fields[f.id]?'filled':'')+'"></span>'+esc(f.label)+'</summary><label class="sr" for="note-'+f.id+'">'+esc(f.label)+'</label><textarea id="note-'+f.id+'" data-field="'+f.id+'" placeholder="Vos notes, liens et observations…">'+esc(record().fields[f.id]||'')+'</textarea></details>').join('');
 document.querySelectorAll('[data-field]').forEach(x=>x.oninput=()=>{record().fields[x.dataset.field]=x.value;x.closest('details').querySelector('.note-dot').classList.toggle('filled',Boolean(x.value.trim()));save();});
}
function validateImport(value){
  if(!value||value.format!=='harvest-workbook-v1'||value.dataset!==DATASET||!value.records||typeof value.records!=='object'||!value.bindings||typeof value.bindings!=='object')throw Error('Format ou version de données incompatible.');
  if(value.participant!==owner.participant || value.edition!==owner.edition)throw Error('Ce carnet appartient à un autre profil ou à une autre édition.');
  const clean={format:value.format,...owner,version:W.version,dataset:DATASET,bindings:{...window.BINDINGS},records:{}};
  for(const k of Object.keys(clean.bindings)){if(typeof value.bindings[k]==='string')clean.bindings[k]=value.bindings[k];if(k.endsWith('_url')&&clean.bindings[k]&&!https(clean.bindings[k]))throw Error('Lien non HTTPS.');}
  for(const [k,r] of Object.entries(value.records)){
    const parsed=JSON.parse(k);if(!Array.isArray(parsed)||parsed.length!==3||parsed[1]!==DATASET||!W.tracks.some(t=>t.id===parsed[2])||typeof parsed[0]!=='string')throw Error('Contexte de carnet invalide.');
    const rec={fields:{},checks:{}};
    for(const f of W.workbook_fields)if(typeof r.fields?.[f.id]==='string')rec.fields[f.id]=r.fields[f.id];
    for(const c of W.tracks.find(t=>t.id===parsed[2]).checks)if(states.includes(r.checks?.[c.id]))rec.checks[c.id]=r.checks[c.id];
    clean.records[k]=rec;
  }return clean;
}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
function markdown(){return '# Harvest — carnet de décisions\n\nVersion '+W.version+' · '+DATASET+'\n\n'+Object.entries(state.records).map(([k,r])=>'## '+JSON.parse(k).join(' · ')+'\n\n'+W.workbook_fields.map(f=>'### '+f.label+'\n\n'+(r.fields[f.id]||'À compléter')+'\n').join('\n')+'\n### Vérifications\n\n'+Object.entries(r.checks).map(([id,s])=>'- '+id+' : '+s).join('\n')).join('\n\n');}

$('#export-json').onclick=()=>download('harvest-carnet.json',JSON.stringify(state,null,2),'application/json');
$('#export-md').onclick=()=>download('harvest-carnet.md',markdown(),'text/markdown');
$('#import').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>2000000)throw Error('Fichier trop volumineux.');const incoming=validateImport(JSON.parse(await file.text()));
  const conflicts=Object.keys(incoming.records).filter(k=>state.records[k]&&(Object.values(state.records[k].fields).some(Boolean)||Object.values(state.records[k].checks).some(x=>x!=='NOT RUN'))&&JSON.stringify(state.records[k])!==JSON.stringify(incoming.records[k]));
  if(conflicts.length&&!confirm('Remplacer '+conflicts.length+' carnet(s) de même contexte ? Exportez d’abord vos notes si nécessaire.'))return;
  state.records={...state.records,...incoming.records};state.bindings=incoming.bindings;save();render();notice('Carnet restauré ; les autres contextes sont conservés.',true);
}catch(err){notice('Import refusé : '+err.message);}finally{e.target.value='';}};
$('#print-notes').onclick=()=>{const w=window.open('','_blank');if(!w){notice('Autoriser une fenêtre pour imprimer le carnet, ou exporter Markdown.');return;}w.document.write('<!doctype html><html lang="fr"><meta charset="utf-8"><title>Carnet Harvest</title><style>body{font:14px system-ui;margin:35px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Carnet Harvest</h1><pre>'+esc(markdown())+'</pre></html>');w.document.close();w.focus();w.print();};
$('#track').onchange=e=>go(step,e.target.value);
$('#notes-track').onchange=e=>{save();track=e.target.value;history.replaceState(null,'','#'+track+'/'+step);render();};
$('#steps').onclick=e=>{const b=e.target.closest('button[data-step]');if(b)go(Number(b.dataset.step));};
$('#prev').onclick=()=>go(Math.max(0,step-1));
$('#next').onclick=()=>{
 if(step<4)return go(step+1);
 if(workshopProfile){location.href=workshopProfile.link('index.html').split('#')[0]+'#decision';return;}
 go(0,track==='contracts'?'funds':'contracts');
};
$('#open-settings').onclick=()=>openPanel('settings-dialog');
for(const d of document.querySelectorAll('dialog'))d.addEventListener('close',()=>{if(document.querySelector('dialog[open]'))return;document.body.classList.remove('panel-open');document.body.append($('#status'));const trigger=panelTriggers.get(d);(trigger?.isConnected?trigger:d.id==='notes-dialog'?($('#content [data-note]')||$('#step-title')):d.id==='settings-dialog'?$('#open-settings'):$('#step-title')).focus({preventScroll:true});});
document.addEventListener('click',async e=>{
 const close=e.target.closest('[data-close]');if(close){document.getElementById(close.dataset.close).close();return;}
 const routeButton=e.target.closest('[data-go]');if(routeButton){go(Number(routeButton.dataset.go));return;}
 const trackButton=e.target.closest('button[data-track]');if(trackButton){go(0,trackButton.dataset.track);return;}
 if(e.target.closest('[data-open-settings]')){openPanel('settings-dialog');return;}
 const note=e.target.closest('[data-note]');if(note){openPanel('notes-dialog',note.dataset.note);return;}
 const btn=e.target.closest('[data-copy]');if(!btn)return;
 const value=document.getElementById(btn.dataset.copy).textContent;
 if(value.includes('{{')||(btn.dataset.copy==='prompt1'&&value.includes('non-verifie'))){notice('Compléter les liens de session et confirmer l’identité avant de copier ce texte.');return;}
 try{await navigator.clipboard.writeText(value);const label=btn.innerHTML;btn.innerHTML='Copié ✓';notice('Copié. Collez le texte dans '+(btn.dataset.copy.startsWith('question')?'Genie':btn.dataset.copy.startsWith('sql')?'l’éditeur SQL':'Builder')+'.',true);setTimeout(()=>{if(btn.isConnected)btn.innerHTML=label;},1800);}catch{const pre=document.getElementById(btn.dataset.copy);const d=pre.closest('details');if(d)d.open=true;const range=document.createRange();range.selectNodeContents(pre);getSelection().removeAllRanges();getSelection().addRange(range);notice('Copie automatique indisponible : texte sélectionné, utilisez Ctrl/Cmd+C.');}
});
$('#content').addEventListener('change',e=>{if(e.target.matches('[data-check]')){record().checks[e.target.dataset.check]=e.target.value;e.target.dataset.state=e.target.value;save();}});
$('#read-receipt').onclick=()=>{
  let receipt;
  try { receipt=JSON.parse($('#schema-receipt').value); }
  catch { notice('Collez le JSON affiché par le notebook du petit lot.'); return; }
  const schemaMatch=typeof receipt?.schema==='string' && /^atelier_eres_([a-z][a-z0-9_]{0,29})_20261123_[a-f0-9]{8}$/.exec(receipt.schema);
  if(receipt?.format!=='harvest-schema-v1' || typeof receipt.participant!=='string' ||
     !/^[a-z][a-z0-9_]{0,29}$/.test(receipt.participant) || typeof receipt.catalog!=='string' ||
     !identifier(receipt.catalog) || !schemaMatch || schemaMatch[1]!==receipt.participant){
    notice('Ce reçu ne correspond pas au schéma du petit lot ERES.'); return;
  }
  if(workshopProfile && receipt.participant!==workshopProfile.id){
    notice('Ce reçu appartient à un autre participant.'); return;
  }
  $('#bind-catalog').value=receipt.catalog;
  $('#bind-schema').value=receipt.schema;
  $('#schema-receipt').value='';
  notice('Catalogue et schéma renseignés. Vérifiez vos liens puis appliquez les paramètres.');
};
$('#bindings').onsubmit=e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));for(const [k,v]of Object.entries(data)){if(k.endsWith('_url')&&v&&!https(v)){notice('Les liens doivent commencer par https://.');return;}}state.bindings=data;save();render();$('#settings-dialog').close();notice('Liens appliqués. Les carnets précédents sont conservés dans l’export.',true);};
window.addEventListener('hashchange',()=>{route();render();$('#step-title').focus({preventScroll:true});});
route();render();
