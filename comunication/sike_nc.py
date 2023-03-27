import argparse
import logging
import socket
import sys
import threading
import hashlib

import comunication.sike as sike
from Crypto.Cipher import AES

BUFFER_SIZE = 1024
ENCODING = 'utf-16'

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
NEW_LINE = '\n'

PRE_TEXT = NEW_LINE + CURSOR_UP_ONE + ERASE_LINE

EXCHANGE_CONFIRMATION = b'***CONFIRMED_EXCHANGE****'

FILENAME = ""


def _print(raw_data):
    print(PRE_TEXT + '>' + raw_data)


def padding(s):
    return s + (((8 - len(s) % 8) - 1) * '~')


def remove_padding(s: str):
    return s.replace('~', '')


def load_auth_key():
    filename = FILENAME
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def save_auth_key(new_auth_key):
    filename = FILENAME
    f = open(filename, "wb")
    f.write(new_auth_key)
    f.close()
    print('Key saved')


class SendMessageBase:
    def _send_message(self, socket):
        if self.is_secure:
            aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])
        while True:
            raw_data = input()
            if raw_data:
                if self.is_secure:
                    data = padding(raw_data).encode(ENCODING)
                    encrypted_data = aes.encrypt(data)
                    logging.debug('Sending encrypted message: \n%s\n key: %s', encrypted_data,
                                  self.key)
                    socket.send(bytes(encrypted_data))
                else:
                    socket.send(bytes(raw_data, ENCODING))


class Server(SendMessageBase):
    def __init__(self,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True
                 ):
        self.socket = socket.socket(socket_family, socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = None
        self.key = 'Sixteen byte key'
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        print('Exchanging key...')
        logging.debug('Waiting for public key response...')
        public_key = self.connection.recv(BUFFER_SIZE)
        logging.debug('Reviced public key: %s', public_key.hex())
        print('Encapsulating key...')
        shared_secret, ciphertext = self.sike_api.encapsulate(public_key)
        print('Sending cypher text message...')
        self.connection.sendall(ciphertext)
        print('Waiting for confirmation...')
        confirmation = self.connection.recv(BUFFER_SIZE)
        if not confirmation == EXCHANGE_CONFIRMATION:
            self.socket.close()
        print('Key exchanged.')

        logging.debug('Shared secret key is: %s', shared_secret.hex())
        return shared_secret

    def start(self, port):
        self.socket.bind(('', port))
        print('Listening on port %d...', port)
        self.socket.listen()
        try:
            self.connection, addr = self.socket.accept()
        except KeyboardInterrupt:
            self.socket.close()
            print('Connection closed.')
            sys.exit(1)

        with self.connection:
            print('Connected by %s', addr[0])
            print("Authorization in progress...")
            server_auth_key = load_auth_key()
            logging.debug("Server key OK hash:")
            logging.debug(server_auth_key)
            client_auth_key = str(self.connection.recv(BUFFER_SIZE), ENCODING)
            logging.debug("Client key recived")
            if server_auth_key != client_auth_key:
                print('Authorization failed, closing connection')
                exit(-1)
            else:
                print('Authorization successful')
                self.connection.send(bytes('200', ENCODING))

            aes = None
            if self.is_secure:
                self.key = self.key_exchange()
                save_auth_key(self.key)
                aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])

            input_thread = threading.Thread(target=self._send_message, args=[self.connection])
            input_thread.daemon = True
            input_thread.start()
            try:
                while True:
                    raw_data = self.connection.recv(BUFFER_SIZE)
                    if self.is_secure:
                        logging.debug('Received encrypted message: %s', raw_data)
                        decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                        _print(decrypted_data)
                    else:
                        _print(raw_data)
                    if not raw_data:
                        break
            except KeyboardInterrupt:
                pass
        self.socket.close()
        print('Connection closed.')


class Client(SendMessageBase):

    def __init__(self,
                 socket_family=socket.AF_INET,
                 socket_type=socket.SOCK_STREAM,
                 secure=True,
                 ):
        self.socket = socket.socket(socket_family, socket_type)
        self.key = 'Sixteen byte key'
        self.is_secure = secure
        self.sike_api = sike.CtypeSikeApi()

    def key_exchange(self):
        print('Exchanging key...')
        logging.debug('Generating key pair...')
        public_key, secret_key = self.sike_api.generate_key()
        logging.debug('Generated public key: %s', public_key.hex())
        logging.debug('Generated secret key: %s', secret_key.hex())

        logging.debug('Sending public key...')
        self.socket.send(public_key)

        logging.debug('Waiting for cypher text response...')
        cyphertext_message = self.socket.recv(BUFFER_SIZE)
        logging.debug('Recived cypher text message: %s', cyphertext_message.hex())
        print('Decapsulating shared key...')
        shared_secret = self.sike_api.decapsulate(secret_key, cyphertext_message)
        self.socket.send(EXCHANGE_CONFIRMATION)
        print('Key exchanged.')
        logging.debug('Shared secret key is: %s', shared_secret.hex())
        return shared_secret

    def connect(self, destination, port):
        aes = None
        self.socket.connect((destination, port))
        print('Connected with server')
        print("Authorization in progress...")
        auth_key = load_auth_key()
        logging.debug("Client key OK hash:")
        logging.debug(auth_key)
        self.socket.send(bytes(auth_key, ENCODING))
        logging.debug("C key sent")
        if str(self.socket.recv(BUFFER_SIZE), ENCODING) != "200":
            print("Authorization filed, closing connection")
            exit(-1)
        else:
            print("Authorization successful")

        if self.is_secure:
            self.key = self.key_exchange()
            save_auth_key(self.key)
            aes = AES.new(self.key, AES.MODE_CBC, IV=self.key[:16])

        input_thread = threading.Thread(target=self._send_message, args=[self.socket])
        input_thread.daemon = True
        input_thread.start()
        try:
            while True:
                raw_data = self.socket.recv(BUFFER_SIZE)
                if not raw_data:
                    break
                if self.is_secure:
                    logging.debug('Received encrypted message: %s', raw_data.hex())
                    decrypted_data = remove_padding(str(aes.decrypt(raw_data), ENCODING))
                    _print(decrypted_data)
                else:
                    _print(raw_data)
        except KeyboardInterrupt:
            pass

        self.socket.close()
        print('Connection closed.')


