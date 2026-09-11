import logging
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input

LOG = logging.getLogger(__name__)


class DeactivateMicCamera(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = self.plugin_base.backend
        self.mic_enabled = False
        self.camera_enabled = False

        self.add_event_assigner(EventAssigner(
            id="deactivate_mic_camera_pressed",
            ui_label="Deactivate MicCamera",
            default_events=[Input.Key.Events.DOWN, Input.Dial.Events.DOWN],
            callback=self.on_pressed
        ))

    def on_ready(self):
        self.update_status()

    def update_status(self):
        if not self.backend:
            return

        mic_state = self.backend.get_mic_enabled()
        camera_state = self.backend.get_camera_enabled()

        self.mic_enabled = bool(mic_state)
        self.camera_enabled = bool(camera_state)

        if self.camera_enabled and self.mic_enabled:
            icon_file = "perm_camera_mic_ON.png"
        else:
            icon_file = "perm_camera_mic_OFF.png"

        self.set_media(media_path=self.get_asset_path(icon_file), size=0.75)

        LOG.debug(f"Mic/CameraToggle updated: mic_enabled={self.mic_enabled} | camera_enabled={self.camera_enabled} ")

    def on_pressed(self, data) -> None:
        LOG.debug("Mic/CameraToggle: pressione ricevuta, invio toggle")
        if self.backend:
            if bool(self.backend.get_mic_enabled()):
                self.backend.toggle_microphone()
            if bool(self.backend.get_camera_enabled()):
                self.backend.toggle_camera()


    def on_tick(self):
        self.update_status()
