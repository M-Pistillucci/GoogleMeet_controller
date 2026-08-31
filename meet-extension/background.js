let socket = null;

function connect() {
  // Connessione ws:// gestita direttamente dal background script dell'estensione
  socket = new WebSocket("ws://127.0.0.1:8765");

  socket.onopen = () => {
    console.log("[Background] Connesso con successo al server Python!");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Inoltra il comando ricevuto da Python al content script dentro Google Meet
    chrome.tabs.query({ url: "*://meet.google.com/*" }, (tabs) => {
      tabs.forEach(tab => chrome.tabs.sendMessage(tab.id, data));
    });
  };

  socket.onerror = (err) => {
    console.error("[Background] Errore WebSocket:", err);
  };

  socket.onclose = () => {
    setTimeout(connect, 3000);
  };
}

connect();

// Riceve lo stato inviato da content.js e lo trasmette a Python
chrome.runtime.onMessage.addListener((message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  }
});
