'use strict';
// Functions use the portal's shared content/state after portal.js has initialized.
const semanticReveal = {contracts:false, funds:false};
function semanticEntry() {
  return `<section class="semantic-entry"><span class="semantic-entry-mark" aria-hidden="true">✧</span><div><span class="eyebrow">LE DÉCLIC · ONTOLOGIE & SÉMANTIQUE</span><h2>Pour se comprendre, il faut parler des mêmes choses.</h2><p>Les objets et leurs liens. Les mots et leurs règles. Découvrez la différence, en manipulant un exemple.</p></div><button class="primary" data-open-semantics aria-haspopup="dialog">Explorer le mini-lab <span aria-hidden="true">→</span></button></section>`;
}
function semanticNumber(value, unit='') {
  if(value===null || value===undefined) return 'Inconnu';
  return new Intl.NumberFormat('fr-FR',{maximumFractionDigits:2}).format(value)+(unit?' '+unit:'');
}
function semanticComparison() {
  const q=W.semantic_results.queries, a=track==='contracts', raw=q[a?'SA0':'SB0'][0], shared=q[a?'SA1':'SB1'][0];
  const cards=a?[
    ['Lecture rapide','Normalisé présent',raw.treated_as_preserved,'contrats',semanticNumber(raw.normalized_eur,'€')+' normalisés — une autre mesure.','SA0'],
    ['Définition partagée','Valeur fournisseur conservée',shared.preserved_contracts,'contrats',semanticNumber(shared.preserved_supplier_eur,'€')+' fournisseur · '+semanticNumber(shared.preservation_pct,'%')+' sur '+shared.population+' contrats. Complétude fournisseur : '+shared.known_supplier_amounts+'/'+shared.population+' ('+semanticNumber(shared.supplier_coverage_pct,'%')+').','SA1']
  ]:[
    ['Lecture rapide','Aucune observation reçue',raw.absent_observations,'fonds',raw.joined_rows+' lignes après jointure sur les calculs : ce n’est pas un nombre de fonds.','SB0'],
    ['Définition partagée','Attendue, échue, non reçue',shared.overdue_missing,'fonds',shared.expected_funds+' VL attendues · '+semanticNumber(shared.overdue_pct,'%')+' en retard · '+shared.population+' fonds au total.','SB1']
  ];
  return '<div class="comparison-grid">'+cards.map((c,i)=>'<article class="comparison-card '+(i?'shared':'')+'"><span class="eyebrow">'+esc(c[0])+' · '+c[5]+'</span><h3>'+esc(c[1])+'</h3><p class="comparison-value">'+semanticNumber(c[2])+' <span>'+esc(c[3])+'</span></p><p>'+esc(c[4])+'</p></article>').join('')+'</div><p class="comparison-explanation">'+(a?'C002 a un normalisé, mais sa valeur a changé. C005 reste conservé malgré une estimation différente. On ne compare pas des performances : on précise ce que l’on compte.':'F004 n’attend pas de VL ; F005 n’est pas encore échu. SB2 distingue '+q.SB2[0].recompute_candidates+' calculs candidats sur '+q.SB2[0].affected_funds+' fonds : une relation un-à-plusieurs exige deux grains.')+'</p>';
}
function semanticEntity(id) {
  const s=W.semantic_lab.tracks[track], n=s.entities.find(n=>n.id===id);
  const plain={provider:['Qui transmet la valeur ?','Le fournisseur est la référence pour la valeur d’un contrat.'],contract:['De quel contrat parle-t-on ?','On suit un contrat précis, à une date précise.'],conversion:['Qu’est-il arrivé au montant ?','On observe la valeur après conversion, avec la règle de conversion utilisée.'],value:['Quelle valeur compare-t-on ?','Le montant du fournisseur, le montant converti et l’estimation ont trois rôles différents.'],fund:['De quel fonds parle-t-on ?','Un fonds peut être utilisé dans plusieurs calculs. Compter les calculs ne revient pas à compter les fonds.'],expectation:['Quand la valeur doit-elle arriver ?','Le calendrier indique si une valeur est attendue, et à quelle heure.'],observation:['Qu’a-t-on vraiment reçu ?','Une valeur liquidative (VL), une heure de réception et une version. Une valeur absente ne vaut pas zéro.'],calculation:['Qui utilise cette valeur ?','Un calcul s’appuie sur une version de la valeur. Une nouvelle version peut conduire à le réexaminer.']}[id];
  $('#semantic-entity-detail').innerHTML='<span class="eyebrow">'+esc(n.label)+'</span><h3>'+plain[0]+'</h3><p>'+plain[1]+'</p>'+disclosure('Voir l’identité et la source','<dl><dt>Grain & identité</dt><dd>'+esc(n.grain)+'</dd><dt>Source réelle</dt><dd>'+esc(bound(n.source))+'</dd></dl>');
  document.querySelectorAll('[data-entity]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.entity===id)));
  document.querySelectorAll('[data-edge]').forEach(e=>{const r=s.relations[Number(e.dataset.edge)];e.classList.toggle('connected',r.from===id||r.to===id);});
}
function semanticTrace(id) {
  const data=W.semantic_results, a=track==='contracts';
  const item=data[a?'contracts':'funds'].find(r=>r[a?'contract_id':'fund_id']===id);
  const cells=a?[
    ['Contrat / fournisseur',item.contract_id+' · '+item.provider_id],['Source / mapping',item.source_file+' · '+item.mapping_version],
    ['Fournisseur',item.supplier_cents===null?'NULL · preuve absente':semanticNumber(item.supplier_cents/100,'€')],
    ['Normalisé',item.normalized_cents===null?'NULL · preuve absente':semanticNumber(item.normalized_cents/100,'€')],
    ['Estimation séparée',item.analytical_cents===null?'NULL · preuve absente':semanticNumber(item.analytical_cents/100,'€')],['Statut commun',item.review_status]
  ]:[
    ['Fonds / date',item.fund_id+' · '+item.nav_date],['Calendrier',item.expected?'VL attendue':'Aucune VL attendue'],['Échéance UTC',item.deadline_utc],
    ['Observation',item.received_at_utc?item.received_at_utc+' UTC · v'+item.source_version:'Aucune observation'],['Statut commun',item.arrival_status],
    ['Calculs liés',data.calculations.filter(c=>c.fund_id===id).map(c=>c.calculation_id+' · v'+c.consumed_source_version+' consommée · '+c.calculation_status).join(' ; ')||'Aucun calcul dans le snapshot']
  ];
  $('#semantic-trace').innerHTML='<dl class="trace-grid">'+cells.map(([k,v])=>'<div><dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd></div>').join('')+'</dl>';
}
let semanticStep=0;
const semanticChoices={contracts:null,funds:null};
function showSemanticStep(index,focus=true) {
  semanticStep=index;
  document.querySelectorAll('[data-lab-page]').forEach(p=>p.hidden=Number(p.dataset.labPage)!==index);
  document.querySelectorAll('[data-lab-step]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.labStep)===index)));
  $('#semantic-body').scrollTop=0;
  if(focus)document.querySelector('[data-lab-page="'+index+'"] h3').focus({preventScroll:true});
}
function renderSemantic() {
  const lab=W.semantic_lab,s=lab.tracks[track],a=track==='contracts',instances=W.semantic_results[a?'contracts':'funds'];
  semanticStep=0;
  $('#semantic-title').textContent='Les données prennent du sens.';
  $('#semantic-body').innerHTML=`
    <div class="lab-context"><span>MISSION ${a?'A · CONTRATS':'B · FONDS'}</span><span>2 min pour comprendre · 8 min pour explorer</span></div>
    <div class="lab-tabs" role="group" aria-label="Découvrir le sens des données">
      <button data-lab-step="0" aria-pressed="true"><b>01</b><span>Relier les objets</span></button>
      <button data-lab-step="1" aria-pressed="false"><b>02</b><span>Définir la règle</span></button>
      <button data-lab-step="2" aria-pressed="false"><b>03</b><span>Partager le sens</span></button>
    </div>
    <section data-lab-page="0" class="lab-page">
      <div class="lab-page-title"><span class="concept-tag">L’ONTOLOGIE</span><h3 tabindex="-1">Une carte de votre métier.</h3><p>Quels sont les objets ? Comment sont-ils liés ?<br>Cliquez sur un objet pour comprendre son rôle.</p></div>
      <div class="ontology-nodes" role="group" aria-label="Objets du modèle métier">${s.entities.map((n,i)=>`${i?`<div class="ontology-edge" data-edge="${i-1}"><span>${(a?['émet','a une','compare']:['suit une','peut recevoir','alimente'])[i-1]}</span><i aria-hidden="true">→</i></div>`:''}<button data-entity="${n.id}" aria-pressed="false" aria-controls="semantic-entity-detail"><span class="entity-symbol" aria-hidden="true">${(a?['▦','▤','⇄','€']:['◈','◷','€','ƒ'])[i]}</span><strong>${esc(n.label)}</strong><small>${(a?['La source','L’objet métier','La transformation','Trois rôles distincts']:['L’objet métier','Le calendrier','L’observation','L’usage'])[i]}</small></button>`).join('')}</div>
      <div id="semantic-entity-detail" class="entity-detail" aria-live="polite"></div>
      ${disclosure('Suivre un exemple du jeu de données','<label for="semantic-case">Suivre un cas concret</label><select id="semantic-case">'+instances.map(r=>{const id=r[a?'contract_id':'fund_id'];return '<option value="'+id+'">'+id+' · '+esc(r[a?'review_status':'arrival_status'])+'</option>';}).join('')+'</select><div id="semantic-trace" aria-live="polite"></div>')}
      ${disclosure('Les relations en détail','<ol class="relation-list">'+s.relations.map(r=>'<li><strong>'+esc(r.label)+'</strong><span class="cardinality">'+esc(r.cardinality)+'</span><p>'+esc(r.rule)+'</p></li>').join('')+'</ol>')}
      <div class="lab-bottom"><p><b>À retenir</b> · L’ontologie relie les choses dont on parle.</p><button class="primary" data-lab-next="1">Et les chiffres ? <span aria-hidden="true">→</span></button></div>
    </section>
    <section data-lab-page="1" class="lab-page" hidden>
      <div class="lab-page-title"><span class="concept-tag">LA COUCHE SÉMANTIQUE</span><h3 tabindex="-1">Un même mot. Une même règle.</h3><p>${a?'Un montant converti est-il forcément un montant conservé ?':'Une valeur absente est-elle forcément en retard ?'}</p></div>
      <div class="prediction"><span class="eyebrow">À VOTRE AVIS ?</span><p>${a?'La présence d’un montant suffit-elle pour dire « conservé » ?':'Faut-il signaler toutes les valeurs absentes comme des incidents ?'}</p><div class="prediction-choices" role="group" aria-label="Votre hypothèse"><button data-prediction="yes" aria-pressed="false">Oui, cela suffit</button><button data-prediction="no" aria-pressed="false">Non, il manque une règle</button><button data-prediction="unsure" aria-pressed="false">Je découvre</button></div></div>
      <div class="rule-recipe"><span class="eyebrow">${a?'CONSERVÉ, CELA VEUT DIRE…':'EN RETARD ET NON REÇU, CELA VEUT DIRE…'}</span><div>${(a?['Montants connus','Valeurs identiques','Aucune erreur']:['Valeur attendue','Échéance passée','Valeur non reçue']).map((x,i)=>(i?'<i aria-hidden="true">+</i>':'')+'<span><b aria-hidden="true">✓</b>'+x+'</span>').join('')}</div></div>
      <button id="reveal-semantics" class="primary" aria-expanded="${semanticReveal[track]}" aria-controls="semantic-comparison">${semanticReveal[track]?'Masquer les résultats':'Révéler la comparaison'}</button>
      <div id="semantic-comparison" ${semanticReveal[track]?'':'hidden'}><p id="prediction-feedback" class="prediction-feedback" role="status"></p>${semanticComparison()}</div>
      <p class="semantic-provenance">Exemple synthétique · 20 octobre 2026 à 10:00 UTC · Résultats des SQL fournis, calculés à la préparation de l’atelier.</p>
      <div class="lab-bottom"><p><b>À retenir</b> · La sémantique précise ce que l’on compte.</p><button class="primary" data-lab-next="2">Réutiliser cette règle <span aria-hidden="true">→</span></button></div>
    </section>
    <section data-lab-page="2" class="lab-page" hidden>
      <div class="lab-page-title"><span class="concept-tag">LE SENS PARTAGÉ</span><h3 tabindex="-1">Une définition. Plusieurs usages.</h3><p>Vous formulez la règle métier. Genie et votre app doivent utiliser cette même règle.</p></div>
      <div class="reuse-path"><div><span aria-hidden="true">≡</span><strong>La règle métier</strong><small>Définie dans votre enquête</small></div><i aria-hidden="true">→</i><div><span aria-hidden="true">✧</span><strong>La question à Genie</strong><small>Avec la définition explicite</small></div><i aria-hidden="true">→</i><div><span aria-hidden="true">▦</span><strong>Votre application</strong><small>Un chiffre qui s’explique</small></div></div>
      <div class="takeaway"><strong>L’ontologie relie. La sémantique définit.</strong><p>Ensemble, elles aident chacun à comprendre d’où vient la réponse. Une définition partagée doit toujours être vérifiée.</p></div>
      <label for="semantic-reflection">Avec vos mots, qu’est-ce qui change ?</label><textarea id="semantic-reflection" placeholder="Avant, je pensais… Avec cette règle, je comprends…">${esc(record().fields.semantics||'')}</textarea><p class="note-reminder">Sauvegardé dans votre carnet, dans ce navigateur.</p>
      ${disclosure('Les définitions métier de ce parcours','<div class="measure-grid">'+s.measures.map(m=>'<article><h4>'+esc(m.label)+'</h4>'+p(m.definition)+'<p class="measure-meta">'+esc(m.unit)+' · '+esc(m.grain)+'</p><p class="muted">'+esc(m.limit)+'</p></article>').join('')+'</div>')}
      ${disclosure('Poser la question avec le contrat','<p id="question-semantic">'+esc(s.genie_prompt)+'</p><button class="copy-button" data-copy="question-semantic">Copier la question avec le contrat</button>')}
      ${disclosure('Exécuter et inspecter les SQL',s.sql_ids.map(id=>code(id,SQL[id],'sql-sem-'+id)).join(''))}
      ${disclosure('Votre défi dans les 20 minutes d’enquête',list(s.exercise)+p(s.handoff)+p(s.debrief))}
      ${disclosure('Implémentation et limites',p(lab.implementation)+p(lab.limits)+p(lab.disclosure)+'<a href="semantic/metric-views.sql" download>Définitions Unity Catalog metric views</a> · <a href="semantic/metric-queries.sql" download>Requêtes MEASURE() après déploiement</a>')}
      <div class="lab-bottom"><p>La suite se passe dans votre enquête.</p><button class="primary" data-semantic-done>Revenir à mon parcours <span aria-hidden="true">→</span></button></div>
    </section>`;
  semanticEntity(s.entities[0].id);semanticTrace(instances[0][a?'contract_id':'fund_id']);
  $('#semantic-case').onchange=e=>semanticTrace(e.target.value);
  $('#semantic-reflection').oninput=e=>{record().fields.semantics=e.target.value;save();renderNotes();};
  $('#reveal-semantics').onclick=()=>{semanticReveal[track]=!semanticReveal[track];updateSemanticReveal();};
  syncPrediction();updateSemanticReveal();
}
function syncPrediction() {
  document.querySelectorAll('[data-prediction]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.prediction===semanticChoices[track])));
}
function updateSemanticReveal() {
  $('#semantic-comparison').hidden=!semanticReveal[track];
  const button=$('#reveal-semantics');button.setAttribute('aria-expanded',String(semanticReveal[track]));button.textContent=semanticReveal[track]?'Masquer les résultats':'Révéler la comparaison';
  const choice=semanticChoices[track];
  $('#prediction-feedback').textContent=choice==='no'?'Vous avez repéré l’ambiguïté. Voici ce que la règle change.':choice==='yes'?'L’exemple révèle une nuance : la présence ou l’absence seule ne suffit pas.':'Comparons les deux définitions sur exactement les mêmes données.';
}
document.addEventListener('click',e=>{
  const opener=e.target.closest('[data-open-semantics]');if(opener){renderSemantic();if(opener.dataset.openEntity)semanticEntity(opener.dataset.openEntity);openPanel('semantic-dialog');}
  const node=e.target.closest('[data-entity]');if(node)semanticEntity(node.dataset.entity);
  const nav=e.target.closest('[data-lab-step], [data-lab-next]');if(nav)showSemanticStep(Number(nav.dataset.labStep??nav.dataset.labNext));
  const prediction=e.target.closest('[data-prediction]');if(prediction){semanticChoices[track]=prediction.dataset.prediction;syncPrediction();updateSemanticReveal();}
  if(e.target.closest('[data-semantic-done]'))$('#semantic-dialog').close();
});
