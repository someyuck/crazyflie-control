import logging
import time
from threading import Event

import colorama
from colorama import Fore, Style
colorama.init()

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper


class Drone:
    """
    Basic class to control a CrazyFlie drone. To move the drone,
    write a function taking in a MotionCommander instance, and call
    `move()` on it.
    """

    def __init__(
        self,
        uri: str = uri_helper.uri_from_env(default="radio://0/80/2M/E7E7E7E7E7"),
        log_file: str | None = None,
    ):
        self.uri = uri
        cflib.crtp.init_drivers()

        self.log_file = log_file

        # Only output errors from the logging framework
        logging.basicConfig(level=logging.ERROR)

        self.logconf = LogConfig(name="Stabilizer", period_in_ms=10)
        self.logconf.add_variable("stateEstimate.x", "float")
        self.logconf.add_variable("stateEstimate.y", "float")
        self.logconf.add_variable("stateEstimate.z", "float")
        self.logconf.add_variable("stabilizer.roll", "float")
        self.logconf.add_variable("stabilizer.pitch", "float")
        self.logconf.add_variable("stabilizer.yaw", "float")

        self.scf: SyncCrazyflie | None = None

        self.default_height = 0.5
        self.box_limit = 0.5

        self.deck_attached_event = Event()

    def set_param_async(self, groupstr: str, namestr: str, callback=None, value=None):
        """call this function with the param's default value at the end to reset"""

        def param_stab_log_callback(name, value):
            if self.log_file is not None:
                with open(self.log_file, "a") as outfile:
                    print(f"param {name} = {value}", file=outfile)
            else:
                print(Fore.GREEN + f"param {name} = {value}" + Style.RESET_ALL)

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
                print(Fore.GREEN + "Deck is attached!" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Deck is NOT attached!" + Style.RESET_ALL)

        self.set_param_async(
            groupstr="deck", namestr="bcFlow2", callback=param_deck_flow_cb, value=None
        )

    def sync_log_simple(self):
        def _sync_log():
            with SyncLogger(self.scf, self.logconf) as logger:
                for log_entry in logger:
                    timestamp = log_entry[0]
                    data = log_entry[1]
                    logconf_name = log_entry[2]

                    # TODO: can also set position props here

                    print(Fore.GREEN + f"[{timestamp}][{logconf_name}]: {data}" + Style.RESET_ALL)
                    break

        self.execute(_sync_log)

    def _async_log_callback(self, timestamp: int, data: str, logconf: LogConfig):
        print(Fore.GREEN + f"[{timestamp}][{logconf.name}]: {data}" + Style.RESET_ALL)

    def async_log_simple(self):
        self.scf.cf.log.add_config(self.logconf)
        self.logconf.data_received_cb.add_callback(self._async_log_callback)
        self.logconf.start()
        time.sleep(5)
        self.logconf.stop()

    def execute(self, fn, check_flow_deck: bool = True, log: bool = True, **kwags):
        with SyncCrazyflie(self.uri, cf=Crazyflie(rw_cache="./cache")) as self.scf:
            if log:
                self.scf.cf.log.add_config(self.logconf)
                self.logconf.data_received_cb.add_callback(self._async_log_callback)

            if check_flow_deck:
                self.set_flow_deck_checker()
                if not self.deck_attached_event.wait(timeout=5):
                    raise RuntimeError("No flow deck detected!")

            if log:
                self.logconf.start()
            fn(**kwags)
            if log:
                self.logconf.start()

            # self.set_param_async("stabilizer", "estimator", 2)
            # self.set_param_async("stabilizer", "estimator", 1)

    def fly(self, fn, log: bool = True, **kwags):
        def _fly(**kwags):
            with MotionCommander(self.scf, default_height=self.default_height) as mc:
                fn(mc, **kwags)

        self.execute(fn=_fly, log=log, **kwags)


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
    # d.sync_log_simple()
    # d.async_log_simple()
    d.fly(take_off_simple)
