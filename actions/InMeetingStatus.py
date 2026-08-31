import logging
from typing import Dict, Any

from src.backend.PluginManager.ActionCore import ActionCore

LOG = logging.getLogger(__name__)


class InMeetingStatus(ActionCore):
    """
    StreamController Action that monitors whether the user is currently in a Google Meet call.
    """

    def __init__(self, *args, **kwargs):
        # Accetta tutti i parametri posizionali e a parola chiave (incluso 'action_name')
        # e li passa alla classe base ActionBase
        super().__init__(*args, **kwargs)

        self.backend = self.plugin_base.backend
        self.in_meeting = False

    def on_ready(self):
        """Called when the action is initialized and ready to register listeners."""
        self.update_status()

    def update_status(self):
        """Fetches current meeting status from the backend and updates key rendering."""
        if not self.backend:
            return

        in_meeting_state = self.backend.get_in_meeting()

        # Default a False se viene restituito None
        self.in_meeting = bool(in_meeting_state)

        # Aggiorna lo stato visivo/icona su StreamController
        self.set_state(1 if self.in_meeting else 0)

        # Etichetta di testo sul tasto
        status_text = "In Call" if self.in_meeting else "No Call"
        self.set_bottom_label(status_text)

        LOG.debug(f"InMeetingStatus updated: in_meeting={self.in_meeting}")

    def on_key_down(self):
        """Aggiorna lo stato manualmente alla pressione del tasto."""
        self.update_status()

    def on_tick(self):
        """Controllo periodico per mantenere lo stato sincronizzato."""
        self.update_status()
