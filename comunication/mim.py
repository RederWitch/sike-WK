import comunication.sike_nc as nc

def server_side(server_port):
    server = nc.Server(secure=True)
    try:
        server.start(port=server_port)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        server.socket.close()
        print('Connection closed.')

def client_side(destination, port):
    client = nc.Client(secure=True)
    try:
        client.connect(destination, port)
    except (Exception, KeyboardInterrupt) as e:
        client.socket.close()
        print('Connection closed.')
        raise


def try_connect(mode: str, key_file, port, address=None ):
    print(mode)
    nc.FILENAME = key_file
    if not port:
        port = 8888
    if mode == "server":
        server_side(int(port))
    elif mode == "client":
        if port and address:
            client_side(address, int(port))
        else:
            raise Exception()
    else:
        print("Error")
