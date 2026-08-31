// Legge lo stato e lo manda a background.js
setInterval(() => {
  const micButton = document.querySelector('[data-is-muted]');
  if (micButton) {
    const isMuted = micButton.getAttribute('data-is-muted') === 'true';
    chrome.runtime.sendMessage({
      type: "state",
      data: {
        in_meeting: true,
        mic_enabled: !isMuted
      }
    });
  }
}, 1000);

// Riceve comandi da background.js ed esegue le scorciatoie
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "toggle_mic") {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const eventParams = { key: 'd', code: 'KeyD', keyCode: 68, bubbles: true, cancelable: true };
    if (isMac) eventParams.metaKey = true; else eventParams.ctrlKey = true;

    document.dispatchEvent(new KeyboardEvent('keydown', eventParams));
  }
});
