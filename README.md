# crazyflie-control
Some programs to control a CrazyFlie, using Bitcraze's cflib.

## Dependencies

Create a conda environment from the `env.yml` provided in the `envs/` directory, by runninng the following.
```bash
conda create -f ./envs/env.yml
```

Alternatively, if you want to create it from history, run the following.
```bash
conda create -f ./envs/env-history.yml
```

Then (after activating the environment) run `pip install cflib` to install Bitcraze's CrazyFlie control API.
