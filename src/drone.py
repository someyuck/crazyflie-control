import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger


# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class Drone:
    def __init__(self, uri: str = "radio://0/80/2M/E7E7E7E7E7"):
        self.uri = uri
        cflib.crtp.init_drivers()

        lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
        lg_stab.add_variable("stabilizer.roll", "float")
        lg_stab.add_variable("stabilizer.pitch", "float")
        lg_stab.add_variable("stabilizer.yaw", "float")

        self.scf: SyncCrazyflie | None = None

    def execute(self, fn):
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as self.scf:
            fn()


def simple_connect():
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")


def simple_log(scf, logconf):
    with SyncLogger(scf, logconf) as logger:
        for log_entry in logger:
            timestamp = log_entry[0]
            data = log_entry[1]
            logconf_name = log_entry[2]

            print("[%d][%s]: %s" % (timestamp, logconf_name, data))
            break


if __name__ == "__main__":
    # URI to the Crazyflie to connect to
    uri = "radio://0/80/2M/E7E7E7E7E7"
    d = Drone(uri)
    # d.execute(simple_connect)
    d.execute(simple_log)
