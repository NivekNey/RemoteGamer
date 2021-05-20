"""The command line module for the package."""
import argparse
import logging
from remotegamer import task

parser = argparse.ArgumentParser()
parser.add_argument("task")
parser.add_argument("--host", default="*")
parser.add_argument("--port", type=int, default=5566)
parser.add_argument("--debug", action="store_true")

MAPPING = dict(
    controller=task.Controller,
    station=task.Station,
)


def main():
    """Main function."""
    args = parser.parse_args()
    task_obj = MAPPING[args.task](host=args.host, port=args.port)
    log_level = "DEBUG" if args.debug else "INFO"
    logger = logging.getLogger("remotegamer")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(log_level)
    task_obj.start()
