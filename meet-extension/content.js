import { getMicrophoneState, toggleMicrophone } from './src/google-meet/microphone.js';
import { getCameraState, toggleCamera } from './src/google-meet/camera.js';
import { getMeetingDetails } from './src/google-meet/meeting-info.js';
import { isSharingScreen, toggleScreenShare } from './src/google-meet/screen-share.js';

function collectFullState() {
  const meetingDetails = getMeetingDetails();

  return {
    ...meetingDetails,
    mic_enabled: meetingDetails.in_meeting ? getMicrophoneState() : false,
    camera_enabled: meetingDetails.in_meeting ? getCameraState() : false,
    hand_raised: false, // da collegare a hand.js
    screen_sharing: meetingDetails.in_meeting ? isSharingScreen() : false
  };
}

// Invia periodicamente lo stato aggiornato a background.js
setInterval(() => {
  chrome.runtime.sendMessage({
    type: 'state',
    data: collectFullState()
  });
}, 1000);

// Ascolta i comandi provenienti da background.js / WebSocket
chrome.runtime.onMessage.addListener((msg) => {
  console.log("[Content] Comando ricevuto:", msg);
  if (msg.action === 'toggle_mic') toggleMicrophone();
  if (msg.action === 'toggle_camera') toggleCamera();
  if (msg.action === 'toggle_screen_share') toggleScreenShare();
});
