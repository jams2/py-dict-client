import socket
import getpass
from datetime import datetime

from commands import (
    ClientIdentCommand,
    DefineWordCommand,
    DisconnectCommand,
)
from constants import (
    BUF_SIZE,
    DEFAULT_PORT,
)
from response import (
    HandshakeResponse,
)
from status_codes import DictStatusCode


class DictionaryClient:
    """Implements a client for communication with a server implementing
    the DICT Server Protocol (https://tools.ietf.org/html/rfc2229).
    """
    def __init__(self, host='localhost', port=DEFAULT_PORT, sock_class=socket.socket):
        self.client_name = f'{getpass.getuser()}@{socket.gethostname()}'
        self.client_id_info = f'{self.client_name} {datetime.now().isoformat()}'
        self.sock, self.server_info = self._setup_socket(sock_class, host, port)

    def _setup_socket(self, sock_class, host, port):
        sock = sock_class(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        response = HandshakeResponse(sock.recv(BUF_SIZE))
        if response.status_code != DictStatusCode.CONNECTION_ACCEPTED:
            raise Exception(response.status_code)
        self._send_client_ident(sock)
        return (sock, response.content)

    def _send_client_ident(self, sock):
        command = ClientIdentCommand(sock, self.client_id_info)
        response = command.send()
        if response.status != DictStatusCode.OK:
            raise Exception(response.status)

    def get_word_definitions(self, word, database_name='*'):
        command = DefineWordCommand(self.sock, word, database_name=database_name)
        return command

    def disconnect(self):
        command = DisconnectCommand(self.sock)
        if command.get_status() != DictStatusCode.CLOSING_CONNECTION:
            raise Exception(command.get_status())
        self.sock.close()
