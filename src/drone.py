import logging
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class Drone:
    """
    Basic class to control a CrazyFlie drone. To move the drone,
    write a function taking in a MotionCommander instance, and call
    `move()` on it.
    """

    def __init__(
        self, uri: str = uri_helper.uri_from_env(default="radio://0/80/2M/E7E7E7E7E7")
    ):
        self.uri = uri
        cflib.crtp.init_drivers()

        self.lg_stab = LogConfig(name="Stabilizer", period_in_ms=10)
        self.lg_stab.add_variable("stabilizer.roll", "float")
        self.lg_stab.add_variable("stabilizer.pitch", "float")
        self.lg_stab.add_variable("stabilizer.yaw", "float")

        self.scf: SyncCrazyflie | None = None

        self.default_height = 0.5
        self.box_limit = 0.5

        self.deck_attached_event = Event()

    def set_param_async(self, groupstr: str, namestr: str, callback=None, value=None):
        """call this function with the param's default value at the end to reset"""

        def param_stab_log_callback(name, value):
            print(f"param {name} = {value}")

        self.scf.cf.param.add_update_callback(
            group=groupstr,
            name=namestr,
            cb=callback if callback is not None else param_stab_log_callback,
        )
        time.sleep(1)

        if value is not None:
            full_name = groupstr + "." + namestr
            self.scf.cf.param.set_value(full_name, value)

    def set_flow_deck_checker(self):
        def param_deck_flow_cb(_, value_str: str):
            value = int(value_str)
            # print(value)
            if value:
                # TODO: check
                self.deck_attached_event.set()
                print("Deck is attached!")
            else:
                print("Deck is NOT attached!")

        self.set_param_async(
            groupstr="deck", namestr="bcFlow2", callback=param_deck_flow_cb, value=None
        )

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

    def execute(self, fn, check_flow_deck: bool = True, **kwags):
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache="./cache")) as self.scf:
            if check_flow_deck:
                self.set_flow_deck_checker()
                if not self.deck_attached_event.wait(timeout=5):
                    raise RuntimeError("No flow deck detected!")

            fn(**kwags)

            # self.set_param_async("stabilizer", "estimator", 2)
            # self.set_param_async("stabilizer", "estimator", 1)

    def move(self, fn, **kwags):
        def _move(**kwags):
            with MotionCommander(self.scf, default_height=self.default_height) as mc:
                fn(mc, **kwags)

        self.execute(_move, **kwags)


def simple_connect():
    print("Yeah, I'm connected! :D")
    time.sleep(3)
    print("Now I will disconnect :'(")


def take_off_simple(mc: MotionCommander):
    time.sleep(3)
    mc.stop()


if __name__ == "__main__":
    # URI to the Crazyflie to connect to
    uri = uri_helper.uri_from_env(default="radio://0/80/2M/E7E7E7E7E7")
    d = Drone(uri)
    # d.execute(simple_connect)
    # d.sync_log()
    # d.async_log()
    d.move(take_off_simple)
