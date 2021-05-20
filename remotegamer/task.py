import zmq
import logging
import signal


class Task:
    def __init__(self, host: str = "*", port: int = 5566) -> None:
        self.host = host
        self.port = port
        self.logger = logging.getLogger("remotegamer")
        self.init_zmq()

    def init_zmq(self):
        """Establish zmq socket connection by creating `socket` property."""
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        address = f"tcp://{self.host}:{self.port}"
        self.logger.info(f"address: {address}")
        getattr(self.socket, self.zmq_action)(address)

    def start(self):
        """Go into event main event loop."""
        raise NotImplementedError()


class Controller(Task):
    """Receive controller inputs and stream to Station."""

    # zmq client
    zmq_action = "connect"

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host=host, port=port)
        self.gamepad = self.get_gamepad()

    def get_gamepad(self):
        """The gamepad instance to be listening to."""
        import inputs

        for i, gamepad in enumerate(inputs.devices.gamepads):
            print(i, gamepad)
        gamepad_i = int(input("which controller to capture? [0] ") or "0")
        gamepad = inputs.devices.gamepads[gamepad_i]
        return gamepad

    def start(self):
        """Listen to gamepad events and send over to Station."""

        self.logger.warn("Controller started, connecting to Station")

        while True:
            # support keyboard interrupt
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # get all events since last poll
            events = self.gamepad.read()

            for event in events:
                # Sync events seem useless, skip
                if event.ev_type == "Sync":
                    continue

                # process payload
                payload = (event.ev_type, event.code, event.state)
                self.logger.info(f"captured event: {payload}")
                self.socket.send_pyobj(payload)


class Station(Task):
    """Convert and perform the events received from Controller."""

    # zmq server
    zmq_action = "bind"

    def start(self):
        from remotegamer import converter

        self.logger.warn("Station started, ready for remote to connect")
        my_converter = converter.ToXboxConverter()
        while True:
            # support keyboard interrupt
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # process payload
            ev_type, code, state = self.socket.recv_pyobj()
            my_converter.convert(ev_type, code, state)
