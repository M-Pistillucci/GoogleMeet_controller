// screen-share.js

function getScreenShareButton() {
  // Trova il bottone tramite il nome dell'icona (stabile, non tradotto)
  return Array.from(document.querySelectorAll('button')).find(btn => {
    const icon = btn.querySelector('i.google-symbols, i[class*="google-symbols"]');
    return icon && icon.textContent.trim() === 'computer_arrow_up';
  }) || null;
}

export function isSharingScreen() {
  const btn = getScreenShareButton();
  if (!btn) return false;
  // Presente SOLO quando si sta presentando (indipendente dalla lingua)
  return btn.hasAttribute('aria-haspopup');
}

export function toggleScreenShare() {
  const btn = getScreenShareButton();
  if (btn) btn.click();
}
