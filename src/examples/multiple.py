import pathlib
import threading

from cflib.utils import uri_helper

from src.control.drone import Drone
import src.examples.flying as examples

URIS = [
    uri_helper.uri_from_env(default=uri)
    for uri in [
        "radio://0/80/2M/E7E7E7E701",
        "radio://0/80/2M/E7E7E7E702",
        "radio://0/80/2M/E7E7E7E703",
    ]
]


def control_drone(uri: str, id: int, log_file: pathlib.Path):
    d = Drone(uri=uri, id=id, log_file=log_file)
    d.fly(examples.take_off_simple)
    # d.sync_log_simple()


if __name__ == "__main__":
    threads: list[threading.Thread] = []

    for id, uri in enumerate(URIS):
        filepath = pathlib.Path(f"logs/log_{id}.txt").resolve()
        thread = threading.Thread(target=control_drone, args=(uri, id, filepath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
