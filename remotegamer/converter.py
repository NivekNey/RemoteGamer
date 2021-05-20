"""Module to convert events to virtual gamepad actions."""
import vgamepad as vg
import logging


class Converter:
    """Convert events into vgamepad actions.

    ```python
    my_converter = Converter()
    my_converter.convert(ev_type, code, state)
    ```
    """

    # storing states for continuous codes
    code_state = dict()

    def __init__(self) -> None:
        self.logger = logging.getLogger("remotegamer")

    def convert(self, ev_type: str, code: str, state: int):
        self.logger.debug(
            f"Converting event ev_type={ev_type} code={code} state={state}"
        )

        if ev_type == "Absolute":
            self.abs_event(code, state)
        elif ev_type == "Key":
            self.key_event(code, state)
        else:
            self.logger.warn(f"unknown event type: {ev_type}")

        self.pad.update()

    def abs_event(self, code: str, state: int):
        """Smooth/continuous inputs."""
        raise NotImplementedError()

    def key_event(self, code: str, state: int):
        """Square/step inputs."""
        raise NotImplementedError()


class ToXboxConverter(Converter):
    """Converter implementation, the virtual gamepad used is Xbox."""

    # code string to vg property
    code_to_vg = dict(
        BTN_SOUTH=vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        BTN_EAST=vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        BTN_WEST=vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        BTN_NORTH=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        ABS_HAT0X_NEG=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        ABS_HAT0X_POS=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        ABS_HAT0Y_NEG=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        ABS_HAT0Y_POS=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        BTN_TR=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        BTN_TL=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        BTN_THUMBR=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        BTN_THUMBL=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        BTN_START=vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        BTN_SELECT=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    )

    # convert fake state to string
    int_to_str = {1: "POS", -1: "NEG"}

    # virtual gamepad
    pad = vg.VX360Gamepad()

    def is_xbox_button(self, code: str, state: int):
        """Xbox button doesn't have its own code. Instead it's a sequence."""
        return (code, state) in [
            # open seq
            ("ABS_X", 0),
            ("ABS_Y", -1),
            ("ABS_RX", 0),
            ("ABS_RY", -1),
            # close seq
            ("ABS_Y", 0),
            ("ABS_RY", 0),
            ("ABS_Y", -1),
            ("ABS_RY", -1),
        ]

    def abs_event(self, code: str, state: int):
        """Absolute events."""
        # skip input if xbox button pressed
        if self.is_xbox_button(code, state):
            self.logger.info("xbox_button")
            return

        self.code_state[code] = state
        if code in ("ABS_X", "ABS_Y"):
            x_value = self.code_state.get("ABS_X", 0)
            y_value = self.code_state.get("ABS_Y", 0)
            self.logger.info(f"left_joystick {(x_value, y_value)}")
            self.pad.left_joystick(x_value, y_value)
        elif code in ("ABS_RX", "ABS_RY"):
            x_value = self.code_state.get("ABS_RX", 0)
            y_value = self.code_state.get("ABS_RY", 0)
            self.logger.info(f"right_joystick {(x_value, y_value)}")
            self.pad.right_joystick(x_value, y_value)
        elif code == "ABS_Z":
            self.logger.info(f"left_trigger {state}")
            self.pad.left_trigger(state)
        elif code == "ABS_RZ":
            self.logger.info(f"right_trigger {state}")
            self.pad.right_trigger(state)
        elif code in ("ABS_HAT0X", "ABS_HAT0Y"):
            # these codes are dpad codes, but they appear in Absolute event
            suffix = self.int_to_str.get(state)
            if suffix:  # d-pad pressed
                new_code = f"{code}_{suffix}"
                self.key_event(new_code, state)
            else:  # d-pad released
                for suffix in self.int_to_str.values():
                    new_code = f"{code}_{suffix}"
                    self.key_event(new_code, 0)
        else:
            self.logger.warn(f"unknown abolute code: {code} with state {state}")

    def key_event(self, code: str, state: int):
        """Button events."""
        button = self.code_to_vg[code]
        if state:  # state == 1
            self.logger.info(f"press_button {code}")
            self.pad.press_button(button)
        else:
            self.logger.info(f"release_button {code}")
            self.pad.release_button(button)
