import time

from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

from src.drone import Drone

def take_off_simple(mc: MotionCommander):
    time.sleep(3)
    mc.stop()

def move_linear_simple(mc: MotionCommander):
    time.sleep(3)
    mc.forward(0.5)
    time.sleep(3)
    # mc.back(0.5)
    mc.turn_left(180)
    time.sleep(3)
    mc.forward(0.5)
    time.sleep(3)
    mc.stop()

def move_square(mc: MotionCommander):
    time.sleep(3)

    for i in range(4):
        mc.forward(0.75)
        time.sleep(3)
        mc.turn_left(90)
        time.sleep(3)

    time.sleep(1)
    mc.stop()

def move_cube(mc: MotionCommander):
    time.sleep(3)

    for i in range(4):
        mc.forward(0.75)
        time.sleep(3)
        if i % 2 == 0:
            mc.up(0.35)
            time.sleep(3)
        else:
            mc.down(0.35)
            time.sleep(3)

        mc.turn_left(90)
        time.sleep(3)

    time.sleep(2)
    mc.stop()

def move_cricle(mc: MotionCommander):
    time.sleep(3)

    mc.circle_left(0.75)
    time.sleep(2)
    mc.up(0.5)
    time.sleep(2)
    mc.circle_right(0.75)
    time.sleep(2)
    mc.down(0.5)

    time.sleep(3)
    mc.stop()



if __name__ == "__main__":
    uri = uri_helper.uri_from_env(default="radio://0/80/2M/E7E7E7E7E7")
    d = Drone(uri)
    d.fly(take_off_simple, log=True)
    d.fly(move_linear_simple, log=True)
    d.fly(move_square, log=True)
    d.fly(move_cube, log=True)
    d.fly(move_cricle, log=True)
