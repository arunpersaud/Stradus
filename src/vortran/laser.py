from enum import IntFlag

from .usb_connection import USB_ReadWrite


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
    def set_power_control_mode(self):
        self.send_usb("C=0")

    def set_current_control_mode(self):
        self.send_usb("C=1")

    @property
    def control_mode(self):
        self.send_usb("?C")
        return self.read_usb(timeout=1)

    def enable_delay(self):
        self.send_usb("DELAY=0")

    def disable_delay(self):
        self.send_usb("DELAY=1")

    @property
    def delay(self):
        self.send_usb("?DELAY")
        return self.read_usb(timeout=1)

    def enable_external_power_control(self):
        self.send_usb("EPC=1")

    def disable_external_power_control(self):
        self.send_usb("EPC=0")

    @property
    def external_power_control(self):
        self.send_usb("?EPC")
        return self.read_usb(timeout=1)

    @property
    def current(self):
        self.send_usb("?LC")
        return self.read_usb(timeout=1)

    @current.setter
    def current(self, value):
        self.send_usb("LC={value:05.1f}")

    def on(self):
        self.send_ubs("LE=1")

    def off(self):
        self.send_ubs("LE=0")

    @property
    def on_off(self):
        self.send_usb("?LE")
        return self.read_usb(timeout=1)

    @property
    def power(self):
        self.send_usb("?LP")
        return self.read_usb(timeout=1)

    @current.setter
    def power(self, value):
        self.send_usb("LP={value:05.1f}")

    @property
    def pulse_power(self):
        self.send_usb("?PP")
        return self.read_usb(timeout=1)

    @current.setter
    def pulse_power(self, value):
        self.send_usb("PP={value:05.1f}")

    def disable_pulsed_power(self):
        self.send_usb("PUL=0")

    def enable_pulsed_power(self):
        self.send_usb("PUL=1")

    @property
    def pulsed_power(self):
        self.send_usb("?PUL")
        return self.read_usb(timeout=1)

    @property
    def base_plate_temperature(self):
        self.send_usb("?BPT")
        return self.read_usb(timeout=1)

    @property
    def computer_control(self):
        self.send_usb("?CC")
        return self.read_usb(timeout=1)

    @property
    def fault_code(self):
        self.send_usb("?FC")
        fault = self.read_usb(timeout=1)
        fault = LaserStatus(fault)
        return fault

    @property
    def fault_text(self):
        self.send_usb("?FD")
        return self.read_usb(timeout=1)

    @property
    def firmware_protocal(self):
        self.send_usb("?FP")
        return self.read_usb(timeout=1)

    @property
    def firmware_version(self):
        self.send_usb("?FV")
        return self.read_usb(timeout=1)

    @property
    def interlock_status(self):
        self.send_usb("?IL")
        return self.read_usb(timeout=1)

    @property
    def laser_hours(self):
        self.send_usb("?LH")
        return self.read_usb(timeout=1)

    @property
    def laser_id(self):
        self.send_usb("?LI")
        return self.read_usb(timeout=1)

    @property
    def laser_power_setting(self):
        self.send_usb("?LPS")
        return self.read_usb(timeout=1)

    @property
    def laser_status(self):
        self.send_usb("?LS")
        return self.read_usb(timeout=1)

    @property
    def laser_wavelength(self):
        self.send_usb("?LW")
        return self.read_usb(timeout=1)

    @property
    def laser_max_power(self):
        self.send_usb("?MAXP")
        return self.read_usb(timeout=1)

    @property
    def optical_block_temperature(self):
        self.send_usb("?OBT")
        return self.read_usb(timeout=1)

    @property
    def rated_power(self):
        self.send_usb("?RP")
        return self.read_usb(timeout=1)
