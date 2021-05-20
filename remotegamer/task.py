import zmq
import logging
import signal


class Task:
    def __init__(self, host: str = "*", port: int = 5566) -> None:
        self.host = host
        self.port = port
        self.socket = None
        self.logger = logging.Logger(self.__class__.__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f"host: {host}")
        self.logger.info(f"port: {port}")
        self.init_zmq()

    def init_zmq(self):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()


class Capture(Task):
    """Receive controller inputs and stream to Replay."""

    def init_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        address = f"tcp://{self.host}:{self.port}"
        self.logger.info(f"address: {address}")
        self.socket.bind(address)

    def start(self):
        import inputs

        while True:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            events = inputs.get_gamepad()
            for event in events:
                if event.ev_type == "Sync":
                    continue
                payload = (event.ev_type, event.code, event.state)
                self.logger.debug(f"capture event: {payload}")
                self.socket.send_pyobj(payload)


class Replay(Task):
    """Replay the events received from Capture."""

    def __init__(self, host: str, port: int) -> None:
        import vgamepad as vg

        self.pad = vg.VX360Gamepad()
        self.emitters = dict(Absolute=self.evt_absolute, Key=self.evt_button)
        self.code_to_vg = dict(
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
        self.int_to_str = {1: "POS", -1: "NEG"}
        self.state = dict()
        super().__init__(host=host, port=port)

    def init_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        address = f"tcp://{self.host}:{self.port}"
        self.logger.info(f"address: {address}")
        self.socket.connect(address)

    def start(self):
        while True:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            payload = self.socket.recv_pyobj()
            self.logger.debug(f"replay event: {payload}")
            self.replay_event(payload)

    def replay_event(self, payload):
        ev_type, code, state = payload
        emitter = self.emitters.get(ev_type)
        if emitter:
            emitter(code, state)
        else:
            self.logger.warn(f"unknown event type: {ev_type}")

    def is_xbox_button(self, code: str, state: str):
        return (code, state) in [
            ("ABS_X", 0),
            ("ABS_Y", -1),
            ("ABS_RX", 0),
            ("ABS_RY", -1),
            ("ABS_Y", 0),
            ("ABS_RY", 0),
            ("ABS_Y", -1),
            ("ABS_RY", -1),
        ]

    def evt_absolute(self, code: str, state: str):
        # invalid input if xbox button pressed
        if self.is_xbox_button(code, state):
            self.logger.info("xbox_button")
            return

        self.state[code] = state
        if code in ("ABS_X", "ABS_Y"):
            x_value = self.state.get("ABS_X", 0)
            y_value = self.state.get("ABS_Y", 0)
            self.logger.info(f"left_joystick {(x_value, y_value)}")
            self.pad.left_joystick(x_value, y_value)
        elif code in ("ABS_RX", "ABS_RY"):
            x_value = self.state.get("ABS_RX", 0)
            y_value = self.state.get("ABS_RY", 0)
            self.logger.info(f"right_joystick {(x_value, y_value)}")
            self.pad.right_joystick(x_value, y_value)
        elif code == "ABS_Z":
            self.logger.info(f"left_trigger {state}")
            self.pad.left_trigger(state)
        elif code == "ABS_RZ":
            self.logger.info(f"right_trigger {state}")
            self.pad.right_trigger(state)
        elif code in ("ABS_HAT0X", "ABS_HAT0Y"):
            suffix = self.int_to_str.get(state)
            if suffix:  # state is 1 or -1
                new_code = f"{code}_{suffix}"
                self.evt_button(new_code, state)
            else:  # state is 0, release all
                for suffix in self.int_to_str.values():
                    new_code = f"{code}_{suffix}"
                    self.evt_button(new_code, 0)
        else:
            self.logger.warn(f"unknown abolute code: {code} with state {state}")

    def evt_button(self, code: str, state: str):
        button = self.code_to_vg[code]
        if state:  # state == 1
            self.logger.info(f"press_button {code}")
            self.pad.press_button(button)
        else:
            self.logger.info(f"release_button {code}")
            self.pad.release_button(button)
