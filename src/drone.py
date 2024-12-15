import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie


class Drone:
    def __init__(self, uri: str = "radio://0/80/2M/E7E7E7E7E7"):
        self.uri = uri
        cflib.crtp.init_drivers()

        self.scf: SyncCrazyflie | None = None

    def execute(self, fn):
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as self.scf:
            fn()


def simple_connect():
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")


if __name__ == "__main__":
    # URI to the Crazyflie to connect to
    uri = "radio://0/80/2M/E7E7E7E7E7"
    d = Drone(uri)
    d.execute(simple_connect)
