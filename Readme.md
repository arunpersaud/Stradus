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

## Configuration

### USB Library Configuration (Windows only)

The library automatically finds libusb in this order:

1. **Custom path** via `VORTRAN_LIBUSB_PATH` environment variable
2. **libusb package** installed via pip (`pip install libusb`)
3. **Default relative paths** in your project directory

#### Setting Custom Path

**Linux/macOS (bash):**
```bash
export VORTRAN_LIBUSB_PATH="/path/to/your/libusb-1.0.dll"
```

**Windows (PowerShell):**
```powershell
$env:VORTRAN_LIBUSB_PATH = "C:\path\to\your\libusb-1.0.dll"
```

**Windows (Command Prompt):**
```cmd
set VORTRAN_LIBUSB_PATH=C:\path\to\your\libusb-1.0.dll
```

#### Default Paths

If no custom path is set and libusb package is not installed, the library looks for:
- 32-bit: `USB/libusb/x86/libusb-1.0.dll`
- 64-bit: `USB/libusb/x64/libusb-1.0.dll`

#### Recommended Setup

For easiest setup, simply install the libusb package:
```bash
pip install libusb
```

## Development

If you want to contribute, please install and use `pre-commit`.

You can do this by doing

    uv pip install pre-commit

and then running the following command inside the git repo

    pre-commit install

