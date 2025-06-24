# Stradus SDK for Vortran lasers

## Installation

If you don't have python already on your system you can install it using [uv](https://docs.astral.sh/uv/#installation).

Install the package using uv directly from the cloned git repository:

    uv pip install -e .

## Use

The code below shows how to use the package (note: currently not tested)

```python
import vortran

lasers = vortran.get_lasers()

laser = lasers[0]

is_open = laser.open_connection()

laser.enable_power_control_mode()
laser.power = 50

base_temp = laser.base_plate_temperature

laser.on()
time.sleep(1)
laser.off()
```

## Development

If you want to contribute, please install and use `pre-commit`.

You can do this by doing

    uv pip install pre-commit

and then running the following command inside the git repo

    pre-commit install

