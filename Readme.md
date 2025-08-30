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

## Logging Configuration

The vortran library uses Python's standard logging module. By default, no log messages are shown. To see log output, configure logging in your application:

### Basic Logging Setup

```python
import logging
import vortran

# Show INFO level and above (device discovery, connections)
logging.basicConfig(level=logging.INFO)

# Or show DEBUG level for detailed USB communication
logging.basicConfig(level=logging.DEBUG)

lasers = vortran.get_lasers()  # Will now show log messages
```

### Advanced Logging Configuration

```python
import logging
import vortran

# Configure specific logger levels
logging.getLogger('vortran.usb').setLevel(logging.INFO)      # USB device discovery
logging.getLogger('vortran.laser').setLevel(logging.DEBUG)   # Laser operations
logging.getLogger('vortran.usb_connection').setLevel(logging.WARNING)  # Only errors

# Custom formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger('vortran')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

### Log Levels

- **DEBUG**: Detailed USB communication, retry attempts
- **INFO**: Device discovery, connection status
- **WARNING**: Parse errors, failed operations with retries
- **ERROR**: Connection failures, USB communication errors

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

### Running Tests

Install test dependencies:
```bash
uv pip install -e ".[test]"
```

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src/vortran --cov-report=term-missing
```

### Contributing

If you want to contribute, please install and use `pre-commit`:

```bash
uv pip install pre-commit
pre-commit install
```

