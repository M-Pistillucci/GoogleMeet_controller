import { safeClick } from './dom-utils.js';

export class ButtonController {
  constructor({ selector, iconNames, keywords, shortcut }) {
    this.selector = selector;
    this.iconNames = iconNames;
    this.keywords = keywords;
    this.shortcut = shortcut;
  }

  getButton() {
    const candidates = Array.from(document.querySelectorAll(this.selector));
    if (candidates.length === 0) return null;

    // 1. Match tramite nome interno dell'icona (indipendente dalla lingua)
    if (this.iconNames?.length) {
      const byIcon = candidates.find(el => {
        const iconText = el.textContent.trim().toLowerCase();
        return this.iconNames.some(name => iconText.includes(name));
      });
      if (byIcon) return byIcon;
    }

    // 2. Match tramite aria-keyshortcuts standard (indipendente dalla lingua)
    if (this.shortcut) {
      const byShortcut = candidates.find(el => {
        const ks = (el.getAttribute('aria-keyshortcuts') || '').toLowerCase();
        return ks.includes(this.shortcut.toLowerCase());
      });
      if (byShortcut) return byShortcut;
    }

    // 3. Fallback legacy: aria-label (dipendente dalla lingua)
    if (this.keywords?.length) {
      const byLabel = candidates.find(el => {
        const label = (el.getAttribute('aria-label') || '').toLowerCase();
        return this.keywords.some(kw => label.includes(kw));
      });
      if (byLabel) {
        console.warn('[ButtonController] Trovato solo tramite aria-label (fallback fragile)');
        return byLabel;
      }
    }

    console.warn(`[ButtonController] Nessun bottone trovato per selector: ${this.selector}`);
    return null;
  }

  getState() {
    const btn = this.getButton();
    if (!btn) return false;
    return btn.getAttribute('data-is-muted') === 'false';
  }

  async toggle() {
    const btn = this.getButton();
    console.log("[ButtonController] toggle su:", btn);
    if (btn) {
      safeClick(btn);
    } else {
      console.warn("[ButtonController] Nessun bottone da cliccare");
    }
  }
}
