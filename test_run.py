"""Try converter."""
import inputs
from remotegamer import converter

my_converter = converter.ToXboxConverter()

while True:
    events = inputs.get_gamepad()
    for event in events:
        if event.ev_type == "Sync":
            continue
        my_converter.convert(event.ev_type, event.code, event.state)
