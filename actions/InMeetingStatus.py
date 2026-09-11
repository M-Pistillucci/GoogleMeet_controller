import logging
from PIL import Image
from src.backend.PluginManager.ActionCore import ActionCore

LOG = logging.getLogger(__name__)

class InMeetingStatus(ActionCore):
    """
    StreamController Action that monitors whether the user is currently in a Google Meet call.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = self.plugin_base.backend
        self.in_meeting = False

    def on_ready(self):
        """Called when the action is initialized and ready to register listeners."""
        self.update_status()

    def _generate_background(self, color: tuple) -> Image.Image:
        """Crea un'immagine a tinta unita della dimensione richiesta dal deck."""
        # Recupera le dimensioni in pixel del tasto sul deck corrente
        size = self.deck_controller.deck.key_image_format()["size"]
        return Image.new("RGB", size, color)

    def update_status(self):
        """Fetches current meeting status from the backend and updates key rendering."""
        if not self.backend:
            return

        in_meeting_state = self.backend.get_in_meeting()
        self.in_meeting = bool(in_meeting_state)

        icon_file = "Red_circle.gif" if self.in_meeting else "phone_disabled.png"
        self.set_media(media_path=self.get_asset_path(icon_file), size = 0.75)

        # Imposta testo ed etichetta
        status_text = "In Call" if self.in_meeting else "No Call"
        self.set_bottom_label(status_text)

        LOG.debug(f"InMeetingStatus updated: in_meeting={self.in_meeting}")

    def on_key_down(self):
        """Aggiorna lo stato manualmente alla pressione del tasto."""
        self.update_status()

    def on_tick(self):
        """Controllo periodico per mantenere lo stato sincronizzato."""
        self.update_status()
