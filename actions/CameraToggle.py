import logging
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input

LOG = logging.getLogger(__name__)


class CameraToggle(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = self.plugin_base.backend
        self.camera_enabled = False

        self.add_event_assigner(EventAssigner(
            id="camera_toggle_pressed",
            ui_label="Toggle Camera",
            default_events=[Input.Key.Events.DOWN, Input.Dial.Events.DOWN],
            callback=self.on_pressed
        ))

    def on_ready(self):
        self.update_status()

    def update_status(self):
        if not self.backend:
            return

        camera_state = self.backend.get_camera_enabled()
        self.camera_enabled = bool(camera_state)

        icon_file = "videocam.png" if self.camera_enabled else "videocam_off.png"
        self.set_media(media_path=self.get_asset_path(icon_file), size=0.75)

        status_text = "Cam On" if self.camera_enabled else "Cam Off"
        self.set_bottom_label(status_text)

        LOG.debug(f"CameraToggle updated: camera_enabled={self.camera_enabled}")

    def on_pressed(self, data) -> None:
        LOG.debug("CameraToggle: pressione ricevuta, invio toggle")
        if self.backend:
            self.backend.toggle_camera()

    def on_tick(self):
        self.update_status()
