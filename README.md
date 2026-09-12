# Google Meet Plugin for StreamController

A cross-platform plugin for **StreamController** that allows you to control Google Meet directly from your Stream Deck or any StreamController supported controller, providing real-time meeting status synchronization and visual feedback.

---

## 🚀 Features

* **Real-Time Synchronization**: Instant state updates for microphone, camera, and screen sharing.
* **One-Touch Controls**:
  * Microphone Toggle.
  * Camera Toggle.
  * Hand Raise Toggle (**TO DO**).
  * Screen Share Toggle.
  * Leave Call. (**TO DO**) 
* **Unified Status Button**: Visually displays whether you are in an active meeting alongside key session details.
* **Resource Efficient**: The plugin and WebSocket remain completely idle until an active Google Meet tab is detected, using zero CPU/RAM when idle (**TO DO**).
* **Modular Architecture**: Web extension built using ES Modules (Manifest V3) paired with a local Python WebSocket server.

---

## 🛠️ Project Architecture

The system consists of two primary components communicating via a local WebSocket (`ws://127.0.0.1:8765`) (**USER SELECTED PORT TO BE IMPLEMENTED**):

```text
├── com_googlemeet_controller/        # StreamController Plugin (Python)
│   └── meet-extension/               # Web Extension (Manifest V3)
│       ├── manifest.json             # Extension configuration & permissions
│       ├── background.js             # Service worker & WebSocket manager
│       ├── content_loader.js         # Entrypoint for loading ES modules
│       ├── content.js                # Core script for DOM state aggregation
│       └── src/google-meet/          # Specific DOM interaction modules
│           ├── core/                 # Abstract controllers & DOM utilities
│           ├── microphone.js         # Microphone state & action handling
│           ├── camera.js             # Camera state & action handling
│           ├── meeting-info.js       # Meeting ID & title extraction
│           └── screen-share.js       # Screen share tracking
├── main.py                           # Main plugin entrypoint
├── backend.py                        # BackendBase wrapper
├── GoogleMeetController.py           # Local WebSocket server
└── actions/                          # Stream Deck action definitions & graphics
└── assets/                           # Assets used for the icons

```
## 📦 Installation

1. StreamController Plugin

    Clone or copy the com_googlemeet_controller folder into your StreamController plugins directory.

    Restart StreamController to load the new plugin.

2. Browser Extension (Firefox / Chrome)

    Open your browser's extension management page:

        Chrome: chrome://extensions (enable Developer mode in the top right).

        Firefox: about:debugging#/runtime/this-firefox.

    Click Load unpacked (or Load Temporary Add-on in Firefox) and select the chrome_extension folder.

## ⚙️ How It Works

  **Automatic Activation**: Entering a Google Meet call causes the extension to open a local WebSocket connection to the Python server managed by StreamController.

  **State Broadcasting**: Every second, the extension reads DOM attributes (mic on/off, camera status, etc.) and transmits a JSON payload with the current state.

  **Command Execution**: Pressing a button on your Stream Deck sends a command to the browser, which triggers native Google Meet keyboard shortcuts (Ctrl+D, Ctrl+E, etc.) to toggle media instantly.

  **Graceful Teardown**: Closing the Meet tab automatically drops the WebSocket connection to eliminate unnecessary resource usage and background logging.

## 📄 License

Released under the MIT License.
