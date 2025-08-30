from enum import IntFlag
from types import NoneType

from .usb_connection import USB_ReadWrite
from .usb import get_usb_ports
from .parser import parse_output, verify_result


class LaserStatus(IntFlag):
    EMISSION_ACTIVE = 0
    STANDBY = 1
    WARMUP = 2
    OUT_OF_RANGE = 4
    INVALID_COMMAND = 8
    INTERLOCK_OPEN = 16
    TEC_OFF = 32
    DIODE_OVER_CURRENT = 64
    DIODE_TEMPERATURE_FAULT = 128
    BASE_PLATE_TEMPERATURE_FAULT = 256
    BUFFER_OVERFLOW = 512
    EEPROM_ERROR = 1024
    WATCH_DOG_ERROR = 8192
    FATAL_ERROR = 16384
    DIODE_END_OF_LIFE = 32768


class Laser(USB_ReadWrite):
    """Class representing laser connections. Its properties are
    wrappers around different commands. To see the possible values of
    each function result, please consult the manual.

    """

    def enable_power_control_mode(self):
        self.send_usb("C=0")

    def enable_current_control_mode(self):
        self.send_usb("C=1")

    @property
    def control_mode(self):
        # self.send_usb("?C")
        return parse_output(self.send_query("?C"))

    def enable_delay(self):
        self.send_usb("DELAY=0")

    def disable_delay(self):
        self.send_usb("DELAY=1")

    @property
    def delay(self):
        # self.send_usb("?DELAY")
        return parse_output(self.send_query("?DELAY"))

    def enable_external_power_control(self):
        self.send_usb("EPC=1")

    def disable_external_power_control(self):
        self.send_usb("EPC=0")

    @property
    def external_power_control(self):
        # self.send_usb("?EPC")
        return parse_output(self.send_query("?EPC"))

    @property
    def current(self):
        # self.send_usb("?LC")
        return parse_output(self.send_query("?LC"))

    @current.setter
    def current(self, value):
        self.send_usb(f"LC={value:05.1f}")

    def on(self):
        self.send_usb("LE=1")

    def off(self):
        self.send_usb("LE=0")

    @property
    def on_off(self):
        self.send_usb("?LE")
        return parse_output(self.send_query("?LE"))

    @property
    def power(self):
        # self.send_usb("?LP")
        return parse_output(self.send_query("?C"))

    @power.setter
    def power(self, value):
        self.send_usb("LP={value:05.1f}")

    @property
    def pulse_power(self):
        # self.send_usb("?PP")
        return parse_output(self.send_query("?PP"))

    @pulse_power.setter
    def pulse_power(self, value):
        self.send_usb("PP={value:05.1f}")

    def disable_pulsed_power(self):
        self.send_usb("PUL=0")

    def enable_pulsed_power(self):
        self.send_usb("PUL=1")

    @property
    def pulsed_power(self):
        # self.send_usb("?PUL")
        return parse_output(self.send_query("?PUL"))

    @property
    def base_plate_temperature(self):
        # self.send_usb("?BPT")
        return parse_output(self.send_query("?BPT"))

    @property
    def computer_control(self):
        # self.send_usb("?CC")
        return parse_output(self.send_query("?CC"))

    @property
    def fault_code(self):
        self.send_query("?FC")
        fault = self.read_usb(timeout=1)
        if (
            fault is not None
            and verify_result(fault, ["?FC"]) == True
            and parse_output(fault) is not None
        ):
            result = parse_output(fault)[0]  # type: ignore
            fault = LaserStatus(
                result
            )  # returns an error, might require parsing to get single value
            return list(fault)
        else:
            return None

    @property
    def fault_text(self):
        # self.send_usb("?FD")
        return parse_output(self.send_query("?FD"))

    @property
    def firmware_protocal(self):
        # self.send_usb("?FP")
        return parse_output(self.send_query("?FP"))

    @property
    def firmware_version(self):
        # self.send_usb("?FV")
        return parse_output(self.send_query("?FV"))

    @property
    def interlock_status(self):
        # self.send_usb("?IL")
        return parse_output(self.send_query("?IL"))

    @property
    def laser_hours(self):
        # self.send_usb("?LH")
        return parse_output(self.send_query("?LH"))

    @property
    def laser_id(self):
        # self.send_usb("?LI")
        return parse_output(self.send_query("?LI"))

    @property
    def laser_power_setting(self):
        # self.send_usb("?LPS")
        return parse_output(self.send_query("?LPS"))

    @property
    def laser_status(self):
        # self.send_usb("?LS")
        return parse_output(
            self.send_query("?LS", alt_list=["?C", "?LPS", "?LCS", "?EPC", "?DELAY"])
        )

    @property
    def laser_wavelength(self):
        # self.send_usb("?LW")
        return parse_output(self.send_query("?LW"))

    @property
    def laser_max_power(self):
        # self.send_usb("?MAXP")
        return parse_output(self.send_query("?MAXP"))

    @property
    def optical_block_temperature(self):
        # self.send_usb("?OBT")
        return parse_output(self.send_query("?OBT"))

    @property
    def rated_power(self):
        # self.send_usb("?RP")
        return parse_output(self.send_query("?RP"))

    def send_query(self, command: str, alt_list: list[str] = []) -> str | None:
        """Sends a query command to the laser and returns the
        result. If the result is None or empty, it tries again before
        returning None.

        """
        result = self.send_usb(command)
        if not alt_list:
            verify_list = [command]
        else:
            verify_list = alt_list

        # print(result)
        # print(alt_list)
        if (result is not None) and (verify_result(result, verify_list) == True):
            data = result
        else:  # if result is None or not verified, ask again
            print("trying second query")
            second_try = self.send_usb(command)
            if (result is not None) and (
                verify_result(second_try, verify_list) == True
            ):
                data = result
            else:
                data = None

        return data


def get_lasers():
    """Returns a list containing possible connections to
    lasers. First laser is index 0 of the return value.

    """

    connections = []

    devices = get_usb_ports()
    lasers = []
    if devices:
        for device in devices:
            if devices[device].is_manager:
                manager = device
            else:
                lasers.append(device)
                print("Attaching Endpoint", device)

    my_timeout = 500
    my_retries = 0
    for laser in lasers:
        new_connection = Laser(
            devices[laser],
            my_timeout,
            my_retries,
            is_protocol_laser=True,
        )
        connections.append(new_connection)
    return connections
