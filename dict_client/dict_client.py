import socket
import getpass
from datetime import datetime

from parsers import HandshakeResponseParser
from status_codes import DictStatusCode
from constants import (
    BUF_SIZE,
    DEFAULT_PORT,
)
from commands import (
    ClientIdentCommand,
    DefineWordCommand,
    DisconnectCommand,
)


class DictClient:
    """Implements a client for communication with a server implementing
    the Dict Server Protocol (https://tools.ietf.org/html/rfc2229).
    """
    def __init__(self, host='localhost', port=DEFAULT_PORT, sock_class=socket.socket):
        self.client_name = f'{getpass.getuser()}@{socket.gethostname()}'
        self.client_id_info = f'{self.client_name} {datetime.now().isoformat()}'
        self.sock, self.server_info = self.setup_socket(sock_class, host, port)

    def setup_socket(self, sock_class, host, port):
        sock = sock_class(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        connection_response = DictServerResponse(
            sock.recv(BUF_SIZE),
            handler_class=HandshakeResponseParser,
        )
        if connection_response.get_status() != DictStatusCode.CONNECTION_ACCEPTED:
            raise Exception(connection_response.get_status())
        self._send_client_ident(sock)
        return (sock, connection_response.content)

    def _send_client_ident(self, sock):
        command = ClientIdentCommand(sock, self.client_id_info)
        command.send()
        if command.get_status() != DictStatusCode.OK:
            raise Exception(command.get_status())

    def parse_server_info(self):
        pass

    def get_word_definitions(self, word, database_name='*'):
        command = DefineWordCommand(self.sock, word, database_name=database_name)
        return command

    def disconnect(self):
        command = DisconnectCommand(self.sock)
        if command.get_status() != DictStatusCode.CLOSING_CONNECTION:
            raise Exception(command.get_status())
        self.sock.close()
