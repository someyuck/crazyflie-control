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

        self.lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
        self.lg_stab.add_variable("stabilizer.roll", "float")
        self.lg_stab.add_variable("stabilizer.pitch", "float")
        self.lg_stab.add_variable("stabilizer.yaw", "float")

        self.scf: SyncCrazyflie | None = None

    def set_param_async(self, groupstr: str, namestr: str, value):
        """call this function with the param's default value at the end to reset"""

        def param_stab_est_callback(name, value):
            print(f"param {name} = {value}")

        cf = self.scf.cf
        full_name = groupstr + "." + namestr
        self.scf.cf.param.add_update_callback(
            group=groupstr, name=namestr, cb=param_stab_est_callback
        )
        time.sleep(1)
        cf.param.set_value(full_name, value)

    def sync_log(self):
        def _sync_log():
            with SyncLogger(self.scf, self.lg_stab) as logger:
                for log_entry in logger:
                    timestamp = log_entry[0]
                    data = log_entry[1]
                    logconf_name = log_entry[2]

                    print(f"[{timestamp}][{logconf_name}]: {data}")
                    break

        self.execute(_sync_log)

    def async_log(self):
        def _async_log_callback(timestamp: int, data: str, logconf: LogConfig):
            print(f"[{timestamp}][{logconf.name}]: {data}")

        self.scf.cf.log.add_config(self.lg_stab)
        self.lg_stab.data_received_cb.add_callback(_async_log_callback)
        self.lg_stab.start()
        time.sleep(5)
        self.lg_stab.stop()

    def execute(self, fn, **kwags):
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as self.scf:
            fn(**kwags)

            self.set_param_async("stabilizer", "estimator", 2)
            self.set_param_async("stabilizer", "estimator", 1)


def simple_connect():
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")


if __name__ == "__main__":
    # URI to the Crazyflie to connect to
    uri = "radio://0/80/2M/E7E7E7E7E7"
    d = Drone(uri)
    # d.execute(simple_connect)
    # d.sync_log()
    # d.async_log()
