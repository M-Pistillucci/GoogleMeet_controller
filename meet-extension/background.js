let socket = null;
const extensionId = chrome.runtime.id;
let instanceId = null;

async function getInstanceId() {
  const stored = await chrome.storage.local.get("instance_id");
  if (stored.instance_id) return stored.instance_id;
  const newId = crypto.randomUUID();
  await chrome.storage.local.set({ instance_id: newId });
  return newId;
}

async function connect() {
  instanceId = await getInstanceId();
  socket = new WebSocket("ws://127.0.0.1:8765");

  socket.onopen = () => {
    console.log("[Background] Connesso, invio handshake...");
    socket.send(JSON.stringify({
      type: "handshake",
      extension_id: extensionId,
      instance_id: instanceId
    }));
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "handshake_success" || data.type === "heartbeat_ack") return;

    chrome.tabs.query({ url: "*://meet.google.com/*" }, (tabs) => {
      tabs.forEach(tab => chrome.tabs.sendMessage(tab.id, data));
    });
  };

  socket.onerror = (err) => console.error("[Background] Errore WebSocket:", err);

  socket.onclose = () => {
    socket = null;
    setTimeout(connect, 3000);
  };
}

connect();

// Mantiene vivo il service worker e riconnette se il socket è caduto
chrome.alarms.create("keepAlive", { periodInMinutes: 0.4 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name !== "keepAlive") return;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "heartbeat", data: {} }));
  } else if (!socket) {
    connect();
  }
});

chrome.runtime.onMessage.addListener((message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  }
});
