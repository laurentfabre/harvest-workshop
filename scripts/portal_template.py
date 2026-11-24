"""The workshop workspace shell; content and state remain in the shared sources."""
import html
import json


def portal_markup(workshop, dataset, bindings, sql):
    def safe(value):
        return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')
    version = html.escape(workshop['version'])
    return '''<body class="studio">
<a class="skip" href="#main">Aller au contenu</a>
<header class="topbar">
  <a class="brand-home" href="index.html" aria-label="Revenir à mon parcours"><img src="assets/harvest.svg" alt="Harvest"></a>
  <span class="brand-divider"></span><span class="workshop-wordmark">L’atelier<span>DATA & AI</span></span>
  <div class="topbar-right"><button class="header-learn" data-open-semantics aria-haspopup="dialog"><span aria-hidden="true">✧</span> Comprendre les données</button><button class="notebook-button" data-note="team" aria-haspopup="dialog"><span aria-hidden="true">▤</span> Mon carnet</button><img class="db" src="assets/databricks.svg" alt="Databricks"></div>
</header>
<div class="workspace">
  <nav class="journey" aria-label="Parcours et étapes">
    <div class="journey-heading"><span class="eyebrow">Votre parcours</span><span class="session-live"><i></i> Atelier</span></div>
    <label class="sr" for="track">Choisir un parcours</label>
    <select id="track"><option value="contracts">Mission A · Les contrats</option><option value="funds">Mission B · Les fonds</option></select>
    <p class="journey-caption">Une question. Des preuves.<br>Votre prochaine décision.</p>
    <div id="steps"></div>
    <div class="journey-bottom"><span class="eyebrow">Votre espace Databricks</span>
    <button id="open-settings" class="quiet" aria-haspopup="dialog">Mes accès <span aria-hidden="true">↗</span></button>
    <a class="guide-link" href="guide.html" target="_blank" rel="noopener">Guide imprimable <span aria-hidden="true">↗</span></a>
    <div class="session-format"><strong>3 h</strong><span>Deux cas pratiques<br>Parcours individuel</span></div></div>
  </nav>
  <main id="main" tabindex="-1">
    <a class="mission-return" href="index.html">← Mon parcours</a>
    <div class="stage-heading"><div><p id="current" class="eyebrow"></p><h1 id="step-title" tabindex="-1"></h1></div><div class="stage-meta"><span id="stage-time"></span><span id="stage-position"></span></div></div>
    <p id="decision" class="stage-question"></p>
    <div id="content"></div>
    <div class="stage-actions"><button id="prev" class="back">← Précédent</button><span id="next-hint"></span><button class="primary" id="next">Suivant →</button></div>
    <footer class="workspace-footer"><span><i class="green-dot"></i> Données synthétiques · Lecture seule</span><span>Édition ''' + version + '''</span></footer>
  </main>
</div>
<dialog id="notes-dialog" class="side-panel" aria-labelledby="notes-title">
  <div class="panel-heading"><div><p class="eyebrow">Votre travail, vos preuves</p><h2 id="notes-title">Votre carnet</h2></div><button class="icon-button" data-close="notes-dialog" aria-label="Fermer le carnet">×</button></div>
  <div class="panel-body"><p id="notes-context" class="context-label"></p><label for="notes-track">Parcours du carnet</label><select id="notes-track"><option value="contracts">A · Agrégation de contrats</option><option value="funds">B · Données de fonds</option></select><p class="note-reminder">Enregistré dans ce navigateur. Exportez vos notes pour les retrouver ailleurs ou les partager.</p><div id="notes"></div>
  <div class="export-area"><p class="eyebrow">Emporter votre travail</p><div class="actions"><button id="export-json" class="primary">Exporter JSON</button><button id="export-md">Exporter Markdown</button><button id="print-notes">Imprimer le carnet</button></div><label for="import">Restaurer un export JSON</label><input id="import" type="file" accept="application/json,.json"></div></div>
</dialog>
<dialog id="settings-dialog" class="settings-panel" aria-labelledby="settings-title"><div class="panel-heading"><div><p class="eyebrow">VOS OUTILS POUR L’ATELIER</p><h2 id="settings-title">Mes accès</h2></div><button class="icon-button" data-close="settings-dialog" aria-label="Fermer les réglages">×</button></div><div class="panel-body"><p class="muted">Ouvrez votre outil dans un nouvel onglet, puis revenez ici pour suivre le parcours.</p><div class="access-links" id="links"></div><a class="access-guide" href="guide.html" target="_blank" rel="noopener">Ouvrir le guide imprimable ↗</a><details class="disclosure settings-details"><summary>Paramètres de mon essai <span class="disclosure-plus" aria-hidden="true">+</span></summary><div class="disclosure-body"><p class="muted">Utilisez les liens de votre propre essai. Le changement d’environnement conserve vos carnets précédents. Aucun secret à saisir.</p><label for="schema-receipt">Reçu du notebook ERES</label><textarea id="schema-receipt" rows="2" maxlength="4000" placeholder="Collez le JSON de la cellule « Reçu de mon schéma »"></textarea><button type="button" id="read-receipt">Reporter le catalogue et le schéma</button><form id="bindings"></form></div></details></div></dialog>
<dialog id="semantic-dialog" class="semantic-panel" aria-labelledby="semantic-title"><div class="panel-heading"><div><p class="eyebrow">Laboratoire · ontologie & sémantique</p><h2 id="semantic-title">Même donnée. Un sens partagé.</h2></div><button class="icon-button" data-close="semantic-dialog" aria-label="Fermer le laboratoire">×</button></div><div class="panel-body" id="semantic-body"></div></dialog>
<div id="status" class="toast" role="status" aria-live="polite"></div>
<script>window.WORKSHOP=''' + safe(workshop) + ';window.SQL=' + safe(sql) + ';window.DATASET=' + safe(dataset['version']) + ';window.BINDINGS=' + safe(bindings) + ''';</script><script src="assets/semantics.js"></script><script src="assets/experience.js"></script><script src="assets/portal.js"></script></body></html>'''
