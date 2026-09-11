import logging
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input

LOG = logging.getLogger(__name__)


class MicrophoneToggle(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = self.plugin_base.backend
        self.mic_enabled = False

        self.add_event_assigner(EventAssigner(
            id="microphone_toggle_pressed",
            ui_label="Toggle Microphone",
            default_events=[Input.Key.Events.DOWN, Input.Dial.Events.DOWN],
            callback=self.on_pressed
        ))

    def on_ready(self):
        self.update_status()

    def update_status(self):
        if not self.backend:
            return

        mic_state = self.backend.get_mic_enabled()
        self.mic_enabled = bool(mic_state)

        icon_file = "mic.png" if self.mic_enabled else "mic_off.png"
        self.set_media(media_path=self.get_asset_path(icon_file), size=0.75)

        status_text = "Mic On" if self.mic_enabled else "Mic Off"
        self.set_bottom_label(status_text)


        LOG.debug(f"MicrophoneToggle updated: mic_enabled={self.mic_enabled}")

    def on_pressed(self, data) -> None:
        LOG.debug("MicrophoneToggle: pressione ricevuta, invio toggle")
        if self.backend:
            self.backend.toggle_microphone()

    def on_tick(self):
        self.update_status()
