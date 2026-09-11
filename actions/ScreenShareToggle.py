import logging
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input

LOG = logging.getLogger(__name__)


class ScreenShareToggle(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = self.plugin_base.backend
        self.screen_sharing = False

        self.add_event_assigner(EventAssigner(
            id="screenshare_toggle_pressed",
            ui_label="Toggle Screen Sharing",
            default_events=[Input.Key.Events.DOWN, Input.Dial.Events.DOWN],
            callback=self.on_pressed
        ))

    def on_ready(self):
        self.update_status()

    def update_status(self):
        if not self.backend:
            return

        screen_share_state = self.backend.get_screen_sharing()
        self.screen_sharing = bool(screen_share_state)

        icon_file = "computer_arrow_up_green.png" if self.screen_sharing else "computer_arrow_up_white.png"
        self.set_media(media_path=self.get_asset_path(icon_file), size=0.75)

        status_text = "Sharing" if self.screen_sharing else "Not Sharing"
        self.set_bottom_label(status_text)

        LOG.debug(f"ScreenShareToggle updated: screen_sharing={self.screen_sharing}")

    def on_pressed(self, data) -> None:
        LOG.debug("ScreenshareToggle: pressione ricevuta, invio toggle")
        if self.backend:
            self.backend.toggle_screen_share()

    def on_tick(self):
        self.update_status()
