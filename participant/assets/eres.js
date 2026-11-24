'use strict';
for (const snippet of document.querySelectorAll('.eres-home pre, .eres-home blockquote')) {
  const copy = document.createElement('button');
  copy.className = 'copy-exercise';
  copy.textContent = snippet.tagName === 'PRE' ? 'Copier le SQL' : 'Copier le prompt';
  snippet.after(copy);
  copy.addEventListener('click', async () => {
    const feedback = document.getElementById('copy-feedback');
    try {
      await navigator.clipboard.writeText(snippet.textContent.trim());
      feedback.textContent = 'Texte copié.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(snippet);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      feedback.textContent = 'Texte sélectionné. Utilisez Ctrl+C ou Cmd+C pour le copier.';
    }
    copy.after(feedback);
  });
}
