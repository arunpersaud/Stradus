from dataclasses import dataclass
from typing import Any
from pathlib import Path
import os
import site
import logging

# Note: these are imports from pyusb
import usb.core
import usb.backend.libusb1

import re
import platform

logger = logging.getLogger(__name__)


@dataclass
class VortranDevice:
    """Specify all USB values needed to talk to a Vortran laser."""

    vendor_id: int
    product_id: int
    bus: int
    address: int
    is_manager: bool = False


def _find_libusb_in_site_packages() -> Path | None:
    """Find libusb library in site-packages directory.

    Returns the path to libusb library if found, None otherwise.
    """
    # Get all site-packages directories
    site_packages = site.getsitepackages()
    if hasattr(site, "getusersitepackages"):
        site_packages.append(site.getusersitepackages())

    # Platform-specific library paths within libusb package
    if platform.system() == "Windows":
        arch = platform.architecture()
        if arch[0] == "32bit":
            lib_subpath = "libusb/_platform/_windows/x86/libusb-1.0.dll"
        elif arch[0] == "64bit":
            lib_subpath = "libusb/_platform/_windows/x64/libusb-1.0.dll"
        else:
            return None

        # Search in all site-packages directories
        for site_pkg in site_packages:
            if site_pkg:  # site_pkg could be None
                lib_path = Path(site_pkg) / lib_subpath
                if lib_path.exists():
                    return lib_path

    return None


def get_usb_backend() -> Any | None:
    """Get the appropriate USB backend for the current platform.

    Tries paths in this order:
    1. VORTRAN_LIBUSB_PATH environment variable
    2. libusb package in site-packages
    3. Default relative paths

    Returns the libusb backend for Windows, None for other platforms
    to use the default backend.
    """
    if platform.system() == "Windows":
        # 1. Check for custom path first
        custom_path = os.getenv("VORTRAN_LIBUSB_PATH")
        if custom_path:
            lib_path = Path(custom_path)
            if not lib_path.exists():
                raise FileNotFoundError(f"Custom libusb library not found: {lib_path}")
            return usb.backend.libusb1.get_backend(find_library=lambda x: str(lib_path))

        # 2. Try libusb package in site-packages
        site_lib_path = _find_libusb_in_site_packages()
        if site_lib_path:
            return usb.backend.libusb1.get_backend(
                find_library=lambda x: str(site_lib_path)
            )

        # 3. Default paths with validation
        # libusb DLLs from: https://sourceforge.net/projects/libusb/
        arch = platform.architecture()
        if arch[0] == "32bit":
            default_path = Path("USB/libusb/x86/libusb-1.0.dll")
        elif arch[0] == "64bit":
            default_path = Path("USB/libusb/x64/libusb-1.0.dll")
        else:
            raise Exception(
                "Invalid platform. System must be a 32bit or 64bit architecture."
            )

        if not default_path.exists():
            raise FileNotFoundError(
                f"libusb library not found. Tried:\n"
                f"- Environment variable: VORTRAN_LIBUSB_PATH\n"
                f"- Site-packages: libusb package\n"
                f"- Default path: {default_path}\n"
                f"Install libusb package or set VORTRAN_LIBUSB_PATH environment variable."
            )

        return usb.backend.libusb1.get_backend(find_library=lambda x: str(default_path))
    return None


def get_usb_ports() -> dict[str, VortranDevice]:
    """Find all usb lasers."""

    # DEFINE IDS TO LOOK FOR
    LASER_VENDOR_ID = 0x201A
    LASER_PRODUCT_ID = 0x1001
    MANAGER_VENDOR_ID = 0x04D8
    MANAGER_PRODUCT_ID = 0x003F

    # DEFINE EMPTY DICTIONARY AND STARTING ID
    found_vortran_devices = dict()

    # DETERMINE BACKEND
    backend = get_usb_backend()

    # FIND MANAGERS
    found_info = usb.core.show_devices(
        idVendor=MANAGER_VENDOR_ID, idProduct=MANAGER_PRODUCT_ID
    )
    manager_lines = found_info.split("\n")

    # PARSE ALL LINES FOR BUS AND ADDRESS
    for line in manager_lines:
        # TRY TO FIND BUS AND ADDRESS
        bus, address = parse_bus_and_address(line)

        if bus and address:
            unique_name = (
                f"usb_{MANAGER_VENDOR_ID}_{MANAGER_PRODUCT_ID}_{bus}_{address}"
            )
            found_vortran_devices[unique_name] = VortranDevice(
                vendor_id=MANAGER_VENDOR_ID,
                product_id=MANAGER_PRODUCT_ID,
                bus=bus,
                address=address,
                is_manager=True,
            )

    # FIND LASERS
    found_info = usb.core.show_devices(
        idVendor=LASER_VENDOR_ID, idProduct=LASER_PRODUCT_ID
    )
    # print("Lasers Found:",found_info)
    laser_lines = found_info.split("\n")

    # PARSE ALL LINES FOR BUS AND ADDRESS
    for line in laser_lines:
        # TRY TO FIND BUS AND ADDRESS
        bus, address = parse_bus_and_address(line)
        emulation = False
        if bus and address:
            unique_name = f"usb_{LASER_VENDOR_ID}_{LASER_PRODUCT_ID}_{bus}_{address}"
            found_vortran_devices[unique_name] = VortranDevice(
                vendor_id=LASER_VENDOR_ID,
                product_id=LASER_PRODUCT_ID,
                bus=bus,
                address=address,
                is_manager=False,
            )

        # Optionally Create a fake laser so we can cook up the GUI - TODO AB
        if emulation:
            unique_name = "usb_EmuVendID_EmuProdID_NoBus_FakeAddy"
            found_vortran_devices[unique_name] = VortranDevice(
                vendor_id=LASER_VENDOR_ID,
                product_id=LASER_PRODUCT_ID,
                bus=bus,
                address=address,
                is_manager=False,
            )
    return found_vortran_devices


def parse_bus_and_address(text: str) -> tuple[int | None, int | None]:
    """Get the bus and address from the usb string."""

    # TRY TO FIND BUS AND ADDRESS
    tmp_match_bus = re.match(".*Bus (.*) Address.*", text)
    tmp_match_address = re.match(".*Address (.*), Spec.*", text)

    # TRY TO GET GROUPS
    bus = None
    address = None
    if tmp_match_bus:
        if len(tmp_match_bus.groups()) == 1:
            try:
                bus = int(tmp_match_bus.groups()[0])
            except ValueError:
                logger.warning("Failed to parse bus number from USB string: %s", text)

    if tmp_match_address:
        if len(tmp_match_address.groups()) == 1:
            try:
                address = int(tmp_match_address.groups()[0])
            except ValueError:
                logger.warning("Failed to parse address from USB string: %s", text)

    return bus, address
