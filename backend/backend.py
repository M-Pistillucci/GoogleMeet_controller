import logging
from typing import Dict, Optional, Any

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from streamcontroller_plugin_tools import BackendBase
from GoogleMeetController import GoogleMeetController


class Backend(BackendBase):
    """
    Backend wrapper for Google Meet Controller.
    """

    def __init__(self):
        self.controller: Optional[GoogleMeetController] = None
        try:
            host = "127.0.0.1"
            port = 8765
            self.controller = GoogleMeetController(host=host, port=port)
            self.controller.start()
            LOG.info("Google Meet WebSocket Server avviato con successo")
        except Exception as e:
            LOG.error(f"Errore nell'avvio del controller Google Meet: {e}")

        super().__init__()

    def get_connected(self) -> bool:
        return self.controller.is_connected() if self.controller else False

    def get_state(self) -> Optional[Dict[str, Any]]:
        try:
            return self.controller.get_state() if self.controller else None
        except Exception as e:
            LOG.error(f"Errore recupero stato: {e}")
            return None

    def get_in_meeting(self) -> bool:
        try:
            return self.controller.is_in_meeting() if self.controller else False
        except Exception as e:
            LOG.error(f"Errore recupero stato: {e}")
            return False

    def get_mic_enabled(self) -> Optional[bool]:
        state = self.get_state()
        return state.get("mic_enabled", False) if state else None

    def get_camera_enabled(self) -> Optional[bool]:
        state = self.get_state()
        return state.get("camera_enabled", False) if state else None

    def get_hand_raised(self) -> Optional[bool]:
        state = self.get_state()
        return state.get("hand_raised", False) if state else None


    def get_participant_count(self) -> Optional[int]:
        state = self.get_state()
        return state.get("participant_count", 0) if state else None

    def toggle_microphone(self) -> bool:
        try:
            if self.controller:
                self.controller.toggle_microphone()
                return True
        except Exception as e:
            LOG.error(f"Errore toggle microfono: {e}")
        return False

    def toggle_camera(self) -> bool:
        try:
            if self.controller:
                self.controller.toggle_camera()
                return True
        except Exception as e:
            LOG.error(f"Errore toggle fotocamera: {e}")
        return False

    def toggle_hand(self) -> bool:
        try:
            if self.controller:
                self.controller.toggle_hand()
                return True
        except Exception as e:
            LOG.error(f"Errore toggle mano: {e}")
        return False

    def get_screen_sharing(self) -> Optional[bool]:
        state = self.get_state()
        return state.get("screen_sharing", False) if state else None

    def toggle_screen_share(self) -> bool:
        try:
            if self.controller:
                self.controller.toggle_screen_share()
                return True
        except Exception as e:
            LOG.error(f"Errore toggle screen share: {e}")
        return False

    def send_reaction(self, reaction: str) -> bool:
        try:
            if self.controller:
                self.controller.send_reaction(reaction)
                return True
        except Exception as e:
            LOG.error(f"Errore invio reazione: {e}")
        return False

    def leave_call(self) -> bool:
        try:
            if self.controller:
                self.controller.leave_call()
                return True
        except Exception as e:
            LOG.error(f"Errore uscita chiamata: {e}")
        return False

    def get_authorized_instances(self):
        return self.controller.get_authorized_instances() if self.controller else []

    def approve_instance(self, extension_id: str, instance_id: str):
        if self.controller:
            self.controller.approve_instance(extension_id, instance_id)

    def deny_instance(self, extension_id: str, instance_id: str):
        if self.controller:
            self.controller.deny_instance(extension_id, instance_id)

    def revoke_instance(self, extension_id: str, instance_id: str):
        if self.controller:
            self.controller.revoke_instance(extension_id, instance_id)

    def get_pending_pairing_requests(self):
        return self.controller.get_pending_pairing_requests() if self.controller else []


# Istanza usata da StreamController per stabilire il server RPyC
backend = Backend()
