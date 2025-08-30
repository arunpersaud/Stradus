# Votran Stradus Laser Example by Vortran Tehnologies @ 2024
# Example was developed using Python 3.11
# Please see Readme.txt

import platform
import usb.core
import usb.backend.libusb1
import array
import logging
import time

from .usb import VortranDevice, get_usb_backend

logger = logging.getLogger(__name__)


class USB_ReadWrite:
    SET_CMD_QUERY = bytes([0xA0])
    GET_RESPONSE_STATUS = bytes([0xA1])
    GET_RESPONSE = bytes([0xA2])
    SET_RESPONSE_RECEIVED = bytes([0xA3])

    def __init__(
        self,
        laser: VortranDevice,
        timeout: int,
        retries: int = 1,
        logger=None,
        is_protocol_laser: bool = True,
    ) -> None:
        self.vendor_id = laser.vendor_id
        self.product_id = laser.product_id
        self.bus = laser.bus
        self.address = laser.address
        self.read_timeout = 40
        self.write_timeout = 0
        self.retries = retries
        self.connection = None
        self.logger = logger
        self.run_continuously = True
        self.is_protocol_laser = is_protocol_laser
        self.is_paused = False

        # DEFINE EMPTY COMMANDS USED FOR GETTING STATUS AND READING RESPONSE
        self.prefix_1 = bytearray(self.SET_CMD_QUERY)
        prefix_2 = bytearray(self.GET_RESPONSE_STATUS)
        prefix_3 = bytearray(self.GET_RESPONSE)
        prefix_4 = bytearray(self.SET_RESPONSE_RECEIVED)
        padding_empty = bytearray([0xFF] * 63)
        full_data_2 = prefix_2 + padding_empty
        full_data_3 = prefix_3 + padding_empty
        full_data_4 = prefix_4 + padding_empty
        self.data_in_array_2 = array.array("B", full_data_2)
        self.data_in_array_3 = array.array("B", full_data_3)
        self.data_in_array_4 = array.array("B", full_data_4)

        # SETUP LOGGER TO CONSOLE
        log_format = "%(message)s"
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format))
        self.console_logger = logging.getLogger("console_logger")
        self.console_logger.setLevel(logging.INFO)
        self.console_logger.addHandler(handler)

    def open_connection(self) -> bool:
        is_connection_open = False
        num_attempts = 0

        while not is_connection_open and num_attempts <= self.retries:
            try:
                backend = get_usb_backend()

                if backend:
                    self.connection = usb.core.find(
                        backend=backend,
                        idVendor=self.vendor_id,
                        idProduct=self.product_id,
                        bus=self.bus,
                        address=self.address,
                    )
                else:
                    self.connection = usb.core.find(
                        idVendor=self.vendor_id,
                        idProduct=self.product_id,
                        bus=self.bus,
                        address=self.address,
                    )

                # Linux-specific kernel driver handling
                if platform.system() == "Linux" and self.connection:
                    if self.connection.is_kernel_driver_active(0):
                        self.connection.detach_kernel_driver(0)

                if self.connection is None:
                    raise ValueError
                else:
                    is_connection_open = True

                self.connection.reset()
                self.connection.set_configuration()
                usb.util.claim_interface(self.connection, 0)

                if is_connection_open:
                    msg_out = "Successfully connected to USB Vendor_ID: {self.vendor_id}, Product_ID:{self.product_id}, Bus:{self.bus}, Address:{self.address}"
                    if self.logger:
                        self.logger.log.info(msg_out)

            except Exception as e:
                logger.error("USB connection failed: %s", repr(e))
                if self.logger:
                    self.logger.log.error(repr(e))

                num_attempts += 1
                if num_attempts <= self.retries:
                    logger.warning(
                        "Retrying USB connection (Vendor=%04x, Product=%04x). Attempt %d of %d",
                        self.vendor_id,
                        self.product_id,
                        num_attempts,
                        self.retries,
                    )
                    if self.logger:
                        msg_out = f"Retrying connection to USB Vendor_ID={self.vendor_id}, Product_ID={self.product_id}. Attempt {num_attempts} of {self.retries}"
                        self.logger.log.warning(msg_out)
        return is_connection_open

    def read_usb(self, timeout: int, include_first_byte: bool = False) -> str | None:
        try:
            data = self.connection.read(0x81, 64, timeout)
        except usb.core.USBError as e:
            logger.error("USB read error (timeout=%s): %s", timeout, e.args)
            return None

        if include_first_byte:
            byte_str = "".join(chr(n) for n in data[0:])
        else:
            byte_str = "".join(chr(n) for n in data[1:])

        result_str = byte_str.replace("\x00", "")
        return result_str if result_str else None

    def send_usb(self, cmd: str, writeOnly: bool = False) -> str | None:
        response = None
        workflow_timeout = 0.05
        if not cmd.endswith("\r\n"):
            cmd = cmd + "\r\n"
        stripped_cmd = (
            cmd.replace("\r\n", "").lower()
        )  # This part doesn't make sense given how the example code calls commands.
        try:
            response = self.read_usb(timeout=30)
            if self.is_protocol_laser:
                data = bytearray(cmd, "ascii")
                padding = bytearray([0xFF] * (63 - len(cmd)))
                full_data = self.prefix_1 + data + padding
                data_in_array_1 = array.array("B", full_data)

                self.connection.ctrl_transfer(0x21, 0x09, 0x200, 0x00, data_in_array_1)
                cmd_sent_time = time.time()
                while time.time() - cmd_sent_time < workflow_timeout:
                    self.connection.ctrl_transfer(
                        0x21, 0x09, 0x200, 0x00, self.data_in_array_2
                    )
                    status_confirmed = self.read_usb(
                        self.read_timeout, include_first_byte=True
                    )
                    if status_confirmed and chr(0x01) + chr(0xFF) in status_confirmed:
                        if writeOnly:
                            return "OK"
                        if not writeOnly:
                            break
                    time.sleep(0.005)

                self.connection.ctrl_transfer(
                    0x21, 0x09, 0x200, 0x00, self.data_in_array_3
                )
                sent_time = time.time()
                response = ""
                while time.time() - sent_time < 1:
                    response = self.read_usb(self.read_timeout)
                    if response and (
                        "\n" in response or stripped_cmd in response.lower()
                    ):
                        self.connection.ctrl_transfer(
                            0x21, 0x09, 0x200, 0x00, self.data_in_array_4
                        )
                        break
                return response

        except usb.core.USBError as e:
            logger.error("USB communication error: %s", repr(e.args))
