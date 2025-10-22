from enum import IntFlag
from typing import Any
import logging

from .usb_connection import USB_ReadWrite
from .usb import get_usb_ports, VortranDevice
from .parser import parse_output, verify_result

logger = logging.getLogger(__name__)


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

    def enable_power_control_mode(self) -> None:
        self.send_usb("C=0")

    def enable_current_control_mode(self) -> None:
        self.send_usb("C=1")

    @property
    def control_mode(self) -> bool | None:
        mode = parse_output(self.send_query("?C"))
        if mode:
            mode = bool(mode[0])
        return mode

    def enable_delay(self) -> None:
        self.send_usb("DELAY=1")

    def disable_delay(self) -> None:
        self.send_usb("DELAY=0")

    @property
    def delay(self) -> list[str] | None:
        return parse_output(self.send_query("?DELAY"))

    def enable_external_power_control(self) -> None:
        self.send_usb("EPC=1")

    def disable_external_power_control(self) -> None:
        self.send_usb("EPC=0")

    @property
    def external_power_control(self) -> list[str] | None:
        return parse_output(self.send_query("?EPC"))

    @property
    def current(self) -> float | None:
        curent = parse_output(self.send_query("?LC"))
        if current:
            current = float(current[0])
        return current

    @current.setter
    def current(self, value: float) -> None:
        self.send_usb(f"LC={value:05.1f}")

    def on(self) -> None:
        self.send_usb("LE=1")

    def off(self) -> None:
        self.send_usb("LE=0")

    @property
    def on_off(self) -> bool | None:
        on_off = parse_output(self.send_query("?LE"))
        if on_off:
            on_off = bool(on_off[0])
        return on_off

    @property
    def power(self) -> float | None:
        power = parse_output(self.send_query("?LP"))
        if power:
            power = float(power[0])
        return power

    @power.setter
    def power(self, value: float) -> None:
        self.send_usb(f"LP={value:05.1f}")

    @property
    def pulse_power(self) -> float | None:
        pulse_power = parse_output(self.send_query("?PP"))
        if pulse_power:
            pulse_power = float(pulse_power[0])
        return pulse_power

    @pulse_power.setter
    def pulse_power(self, value: float) -> None:
        self.send_usb(f"PP={value:05.1f}")

    def disable_pulsed_power(self) -> None:
        self.send_usb("PUL=0")

    def enable_pulsed_power(self) -> None:
        self.send_usb("PUL=1")

    @property
    def pulsed_power(self) -> float | None:
        pulsed_power = parse_output(self.send_query("?PUL"))
        if pulsed_power:
            pulsed_power = float(pulsed_power[0])
        return pulsed_power

    @property
    def base_plate_temperature(self) -> float | None:
        temp = parse_output(self.send_query("?BPT"))
        if temp:
            temp = float(temp[0])
        return temp

    @property
    def computer_control(self) -> list[str] | None:
        return parse_output(self.send_query("?CC"))

    @property
    def fault_code(self) -> list[LaserStatus] | None:
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
    def fault_text(self) -> list[str] | None:
        return parse_output(self.send_query("?FD"))

    @property
    def firmware_protocol(self) -> list[str] | None:
        return parse_output(self.send_query("?FP"))

    @property
    def firmware_version(self) -> list[str] | None:
        return parse_output(self.send_query("?FV"))

    @property
    def interlock_status(self) -> list[str] | None:
        return parse_output(self.send_query("?IL"))

    @property
    def laser_hours(self) -> float | None:
        hours = parse_output(self.send_query("?LH"))
        if hours:
            hours = float(hours[0])
        return hours

    @property
    def laser_id(self) -> list[str] | None:
        return parse_output(self.send_query("?LI"))

    @property
    def laser_power_setting(self) -> float | None:
        power = parse_output(self.send_query("?LPS"))
        if power:
            power = float(power[0])
        return power

    @property
    def laser_status(self) -> list[str] | None:
        return parse_output(
            self.send_query("?LS", alt_list=["?C", "?LPS", "?LCS", "?EPC", "?DELAY"])
        )

    @property
    def laser_wavelength(self) -> float | None:
        wavelength = parse_output(self.send_query("?LW"))
        if wavelength:
            wavelength = float(wavelength[0])
        return wavelength

    @property
    def laser_max_power(self) -> float | None:
        power = parse_output(self.send_query("?MAXP"))
        if power:
            power = float(power[0])
        return power

    @property
    def optical_block_temperature(self) -> list[str] | None:
        return parse_output(self.send_query("?OBT"))

    @property
    def rated_power(self) -> float | None:
        power = parse_output(self.send_query("?RP"))
        if power:
            power = float(power[0])
        return power

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

        if (result is not None) and verify_result(result, verify_list):
            data = result
        else:  # if result is None or not verified, ask again
            logger.debug("Query failed, trying second attempt for command: %s", command)
            second_try = self.send_usb(command)
            if (second_try is not None) and verify_result(second_try, verify_list):
                data = second_try
            else:
                data = None

        return data


def get_lasers() -> list[Laser]:
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
                logger.info("Found laser device: %s", device)

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
