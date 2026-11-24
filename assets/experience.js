'use strict';
// Presentation helpers. Business examples continue to use the shared workshop snapshot.
function welcomeExperience() {
  const a=track==='contracts';
  const nodes=a?[
    ['provider','▦','Fournisseur','Qui transmet ?'],['contract','▤','Contrat','De quoi parle-t-on ?'],['value','€','Valeur','Que compare-t-on ?']
  ]:[['fund','◈','Fonds','De quoi parle-t-on ?'],['expectation','◷','Échéance','Quand l’attend-on ?'],['observation','€','Valeur','Est-elle arrivée ?']];
  return `<section class="welcome">
    <div class="welcome-copy"><span class="hero-kicker"><i></i> L’ATELIER DATA & AI · HARVEST × DATABRICKS</span>
      <h2>Vos données.<br>Du sens.<br><em>Des décisions.</em></h2>
      <p>Posez une question avec vos mots.<br>Transformez la réponse en une application utile.</p>
      <div class="hero-actions"><button class="lime-button" data-go="1">Commencer l’enquête <span aria-hidden="true">→</span></button>
      <button class="hero-discover" data-open-semantics>Comprendre en 2 minutes <span aria-hidden="true">↗</span></button></div>
      <div class="hero-facts"><span>${W.duration / 60} heures</span><span>Parcours individuel</span><span>Aucun code pour commencer</span></div>
    </div>
    <div class="sense-scene"><div class="scene-caption"><span class="live-dot"></span> UNE QUESTION MÉTIER, UN SENS COMMUN</div>
      <div class="scene-question"><span aria-hidden="true">“</span>${a?'Ces valeurs ont-elles<br>été conservées ?':'Cette valeur est-elle<br>vraiment en retard ?'}</div>
      <div class="scene-map" aria-label="${a?'Un fournisseur transmet un contrat avec une valeur':'Un fonds suit une échéance à laquelle une valeur est attendue'}"><div class="scene-line"></div>
        ${nodes.map((n,i)=>(i?'<span class="scene-link">'+(a?['transmet','porte une']:['suit une','attend une'])[i-1]+'</span>':'')+`<button data-open-semantics data-open-entity="${n[0]}" class="scene-node"><span class="node-icon" aria-hidden="true">${n[1]}</span><strong>${n[2]}</strong><small>${n[3]}</small></button>`).join('')}
      </div>
      <div class="scene-definition"><span class="definition-icon" aria-hidden="true">=</span><div><small>LA RÈGLE PARTAGÉE</small><strong>${a?'Conservée = identique à la source':'En retard = attendue et non reçue'}</strong><p>${a?'Montants connus, conversion sans erreur.':'L’échéance doit déjà être passée.'}</p></div><span class="definition-check" aria-hidden="true">✓</span></div>
      <div class="scene-outcomes"><span>Une question dans Genie</span><i>→</i><span>Une app qui l’explique</span></div>
      <p class="scene-footnote">Exemple pédagogique · Cliquez sur un objet pour explorer.</p>
    </div>
  </section>`;
}

function missionExperience() {
  const missionTime=track==='funds' ? W.agenda.find(block=>block.id==='funds').minutes+' min' : 'Prolongement facultatif';
  return `<div class="section-heading"><div><span class="eyebrow">VOTRE TERRAIN DE JEU</span><h2>Fonds et conversion des contrats</h2></div><span class="section-note">${missionTime}</span></div>
  <div class="track-grid">${W.tracks.map(x=>{const a=x.id==='contracts',d=meta[x.id];return `<button class="track-card ${track===x.id?'selected':''}" data-track="${x.id}" aria-pressed="${track===x.id}">
    <div class="mission-art ${a?'contract-art':'fund-art'}" aria-hidden="true">${a?'<div class="mini-document"><span>VALEUR FOURNISSEUR</span><b>€</b><i></i><i></i></div><span class="art-arrow">→</span><div class="mini-document converted"><span>VALEUR CONVERTIE</span><b>€ <small>?</small></b><i></i><i></i></div>':'<div class="fund-bars"><i></i><i></i><i></i><i class="missing">?</i><i></i><i></i></div><span class="fund-art-label">Reçue. Attendue. En retard ?</span>'}</div>
    <div class="mission-copy"><div class="track-card-top"><span class="track-letter">MISSION ${d.letter}</span><span class="track-selection">${track===x.id?'✓ Mission sélectionnée':'Choisir cette mission →'}</span></div><strong class="track-title">${a?'Retrouver la valeur juste.':'Repérer le vrai retard.'}</strong><span class="track-description">${a?'Un montant a été converti. Est-il toujours fidèle à ce que le fournisseur a transmis ?':'Une valeur manque. Faut-il agir maintenant, ou simplement attendre ?'}</span><span class="track-output">${d.output}<span aria-hidden="true">↗</span></span></div></button>`;}).join('')}</div>`;
}

function beginnerHint() {
  const hints=[null,
    ['Votre première question, en 3 gestes.','Copiez une question ci-dessous. Ouvrez Genie, l’assistant qui interroge vos données. Collez la question et échangez avec lui comme avec un collègue.'],
    ['Décrivez l’app que vous aimeriez utiliser.','Builder crée une première application à partir de vos instructions. Copiez le texte de la version 1, puis améliorez le résultat avec la version 2.'],
    ['Demandez : « Pourquoi ce chiffre ? »','Comparez l’app avec la réponse de Genie. Exécutez la requête SQL pour vérifier le calcul.'],
    ['Racontez ce que vous avez appris.','Montrez votre application, une réponse vérifiée et une limite. Terminez par une prochaine action concrète.']];
  const h=hints[step];return h?`<aside class="beginner-hint"><span class="hint-spark" aria-hidden="true">✦</span><div><strong>${h[0]}</strong><p>${h[1]}</p></div></aside>`:'';
}
