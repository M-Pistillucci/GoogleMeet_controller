from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input


class SimpleAction(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # (we'll look at this in the next step)
        self.add_event_assigner(EventAssigner(
            id="simple_action_pressed",
            ui_label="Pressed",
            default_events=[Input.Key.Events.DOWN, Input.Dial.Events.DOWN],
            callback=self.on_pressed
        ))

    def on_ready(self) -> None:
        self.set_media(media_path=self.get_asset_path("info.png"), size=0.75)

    def on_pressed(self, data) -> None:
        print("Pressed")
