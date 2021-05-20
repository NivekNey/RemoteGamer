import argparse
import os
from remotegamer import task

parser = argparse.ArgumentParser()
parser.add_argument("task")
parser.add_argument("--host", default="*")
parser.add_argument("--port", type=int, default=5566)


def main():
    args = parser.parse_args()
    task_obj: task.Task = getattr(task, args.task)(host=args.host, port=args.port)
    log_level = os.environ.get("LOG_LEVEL", "info").upper()
    task_obj.logger.setLevel(log_level)
    task_obj.start()
