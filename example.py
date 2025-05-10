import votran

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
    for x in range(len(lasers)):
        new_connection = vortran.ConnectionUsbReadWrite(
            devices[lasers[x]]["vendor_id"],
            devices[lasers[x]]["product_id"],
            devices[lasers[x]]["bus"],
            devices[lasers[x]]["address"],
            my_timeout,
            my_retries,
            is_protocol_laser=True,
        )
        my_connection.append(new_connection)
        is_open = my_connection[x].open_connection()
        print("IS CONNECTION OPEN: {is_open}")
        r = my_connection[x].send_my_command(
            cmd="LE=1\r\n",
            is_log_cmd=False,
            is_initialization_cmd=False,
            writeOnly=False,
        )
        print(r)
