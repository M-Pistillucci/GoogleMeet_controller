/**
 * Utility per la manipolazione e l'ispezione del DOM di Google Meet.
 */

/**
 * Attende che un elemento appaia nel DOM (utile per le pagine dinamiche di Meet)
 * @param {string} selector - Selettore CSS dell'elemento da cercare
 * @param {number} timeout - Tempo massimo di attesa in ms (default 5000ms)
 * @returns {Promise<Element>}
 */
export function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      return resolve(element);
    }

    const observer = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) {
        resolve(el);
        observer.disconnect();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Elemento ${selector} non trovato entro ${timeout}ms`));
    }, timeout);
  });
}

/**
 * Cerca un elemento basandosi su una lista di selettori di fallback
 * @param {Array<string>} selectors - Lista di selettori CSS da provare
 * @returns {Element|null}
 */
export function querySelectorFallback(selectors) {
  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el) return el;
  }
  return null;
}

/**
 * Simula il click sicuro su un elemento se presente
 * @param {Element|string} target - Elemento DOM o selettore CSS
 * @returns {boolean} True se il click è stato eseguito
 */
export function safeClick(target) {
  const el = typeof target === 'string' ? document.querySelector(target) : target;
  if (el && typeof el.click === 'function') {
    el.click();
    return true;
  }
  return false;
}
