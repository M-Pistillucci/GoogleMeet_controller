import os
import sys
import logging
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

# Aggiunge il plugin ai sys.path
sys.path.append(os.path.dirname(__file__))

# Import moduli StreamController
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import dell'azione specifica per lo stato e di ImageManager
from actions.InMeetingStatus import InMeetingStatus
#from actions.ImageManager import ImageManager


class GoogleMeetPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        # # 1. Inizializza il gestore delle immagini (assets)
        # log.info("Inizializzazione ImageManager...")
        # ImageManager.initialize(os.path.join(self.PATH, "assets"))
        # log.info("ImageManager inizializzato")

        # 2. Avvia il processo backend principale del plugin
        log.info("Avvio backend Google Meet...")

        # StreamController si occuperà di individuare il percorso Python,
        print("launch backend")
        self.launch_backend(
            os.path.join(self.PATH, "backend", "backend.py"),
            os.path.join(self.PATH, "backend", ".venv"),
            open_in_terminal=False,
        )
        print("backend launched")
        log.info("Backend Google Meet avviato")

        # 3. Registra l'unica azione: Controllo Connessione / Stato Meeting
        in_meeting_status_holder = ActionHolder(
            plugin_base=self,
            action_base=InMeetingStatus,
            action_id_suffix="InMeetingStatus",
            action_name="Connection Status",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.SUPPORTED,
            },
        )
        self.add_action_holder(in_meeting_status_holder)

        # 4. Registra il plugin nel sistema
        self.register(
            plugin_name="Google Meet Controller",
            github_repo="https://github.com/M-Pistillucci/GoogleMeet_controller",
            plugin_version="1.0.0",
            app_version="1.5.0-beta.16",
        )

    def get_connected(self) -> bool:
        """Verifica se l'estensione del browser è attualmente connessa al backend."""
        try:
            return self.backend.get_connected()
        except Exception as e:
            log.error(f"Errore controllo connessione WebSocket: {e}")
            return False
