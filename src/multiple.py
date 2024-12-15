import pathlib
import threading

from cflib.utils import uri_helper

from src.drone import Drone
import src.flying_examples as examples

URIS = [
    "radio://0/80/2M/E7E7E7E701",
    "radio://0/80/2M/E7E7E7E702",
    "radio://0/80/2M/E7E7E7E703",
]

URIS = [uri_helper.uri_from_env(uri) for uri in URIS]


def control_drone(uri: str, id: int, log_file: pathlib.Path):
    d = Drone(uri=uri, id=id, log_file=log_file)
    d.fly(examples.take_off_simple)


if __name__ == "__main__":
    threads: list[threading.Thread] = []

    for id, uri in enumerate(URIS):
        filepath = pathlib.Path(f"log_{id}.txt").resolve()
        thread = threading.Thread(target=control_drone, args=(uri, id, filepath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
