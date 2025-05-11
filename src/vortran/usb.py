from dataclasses import dataclass
import usb.core
import usb.backend.libusb1
import re
import platform


@dataclass
class VortranDevice:
    """Specify all USB values needed to talk to a Vortran laser."""

    vendor_id: int
    product_id: int
    bus: int
    address: int
    is_manager: bool = False


def get_usb_ports():
    """Find all usb lasers."""

    # DEFINE IDS TO LOOK FOR
    LASER_VENDOR_ID = 0x201A
    LASER_PRODUCT_ID = 0x1001
    MANAGER_VENDOR_ID = 0x04D8
    MANAGER_PRODUCT_ID = 0x003F

    # DEFINE EMPTY DICTIONARY AND STARTING ID
    found_vortran_devices = dict()

    # DETERMINE BACKEND
    if platform.system() == "Windows":
        # libusb DLLs from: https://sourcefore.net/projects/libusb/
        arch = platform.architecture()
        if arch[0] == "32bit":
            usb.backend.libusb1.get_backend(
                find_library=lambda x: "USB/libusb/x86/libusb-1.0.dll"
            )  # 32-bit DLL, pick right one based on Python installation
        elif arch[0] == "64bit":
            usb.backend.libusb1.get_backend(
                find_library=lambda x: "USB/libusb/x64/libusb-1.0.dll"
            )  # 64-bit DLL
        else:
            raise Exception(
                "Invalid platform. System must be a 32bit or 64bit architecture."
            )

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


def parse_bus_and_address(text: str) -> (int, int):
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
                print("Unable to get a bus in utility get_usb_ports")

    if tmp_match_address:
        if len(tmp_match_address.groups()) == 1:
            try:
                address = int(tmp_match_address.groups()[0])
            except ValueError:
                print("Unable to get a bus in utility get_usb_ports")
    return bus, address
