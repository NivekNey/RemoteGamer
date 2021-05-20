"""Shows what your physical pad is doing."""
import inputs

while True:
    events = inputs.get_gamepad()
    for event in events:
        if event.ev_type == "Sync":
            continue
        print(event.ev_type, event.code, event.state)
