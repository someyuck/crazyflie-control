# crazyflie-control
Some programs to control a CrazyFlie, using Bitcraze's cflib.

## Dependencies

Create a conda environment from the `env.yml` provided in the `envs/` directory, by runninng the following.
```bash
conda env create -f ./envs/env.yml
```

Alternatively, if you want to create it from history, run the following.
```bash
conda env create -f ./envs/env-history.yml
```

Then (after activating the environment) run `pip install cflib` to install Bitcraze's CrazyFlie control API.


## Running

To fly a CrazyFlie, write a function taking in a `MotionCommander` instance, describing
your motion logic in it, and then call `Drone.fly()` on it. Some examples are given in `src/examples/flying.py`.

Run `python -m src.examples.flying` to run the examples (modify the file to choose which flying function to call).

To control multiple drones using a single CrazyRadio dongle, each drone must have a different radio address.
Change this using the `cfclient`, modify the `URIS` list in the code with the actual addresses of your CrazyFlies,
and then Run `python -m src.examples.multiple`.

To read Motion Capture (MOCAP) data that is being published to some topic (on my setup done by `vrpn_mocap` for ROS2 Jazzy, 
dependencies listed in env files), run `python -m src.ros_utils.process_mocap_topic --topic=<topic_name>`. `<topic_name>` 
is the complete name of the topic to listen to (`"/vrpn_mocap/{tracker_name}/pose"` in my setup). Modify the code to use it 
to control the drone instead of just printing the pose information back.
