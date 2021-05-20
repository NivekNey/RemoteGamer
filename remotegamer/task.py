import zmq
import logging
import signal
from remotegamer import converter


class Task:
    def __init__(self, host: str = "*", port: int = 5566) -> None:
        self.host = host
        self.port = port
        self.logger = logging.Logger(self.__class__.__name__)
        self.logger.addHandler(logging.StreamHandler())
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


class Remote(Task):
    """Receive controller inputs and stream to Station."""

    # zmq client
    zmq_action = "connect"

    def start(self):
        import inputs

        self.logger.warn("Remote started, connecting to Station")

        while True:
            # support keyboard interrupt
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # get all events since last poll
            events = inputs.devices.gamepads[-1].read()
            for event in events:
                # Sync events seem useless, skip
                if event.ev_type == "Sync":
                    continue

                # process payload
                payload = (event.ev_type, event.code, event.state)
                self.logger.debug(f"captured event: {payload}")
                self.socket.send_pyobj(payload)


class Station(Task):
    """Convert and perform the events received from Remote."""

    # zmq server
    zmq_action = "bind"

    def start(self):
        self.logger.warn("Station started, ready for remote to connect")
        my_converter = converter.ToXboxConverter()
        while True:
            # support keyboard interrupt
            signal.signal(signal.SIGINT, signal.SIG_DFL)

            # process payload
            ev_type, code, state = self.socket.recv_pyobj()
            my_converter.convert(ev_type, code, state)
