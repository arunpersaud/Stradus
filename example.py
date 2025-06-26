import vortran

if __name__ == "__main__":
    my_connection = []
    devices = vortran.get_usb_ports()
    lasers = list()
    if devices:
        for device in devices:
            if devices[device]["is_manager"]:
                manager = device
            else:
                lasers.append(device)
                print("Attaching Endpoint", device)

    my_timeout = 500
    my_retries = 0
    for laser in lasers:
        new_connection = vortran.USB_ReadWrite(
            devices[laser],
            my_timeout,
            my_retries,
            is_protocol_laser=True,
        )
        my_connection.append(new_connection)
        is_open = my_connection[-1].open_connection()
        print("IS CONNECTION OPEN: {is_open}")
        r = my_connection[-1].send_usb(
            cmd="LE=1",
            writeOnly=False,
        )
        print(r)
