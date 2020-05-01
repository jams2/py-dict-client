import select
import socket
import getpass
from datetime import datetime

from commands import (
    client_ident_command,
    define_word_command,
    disconnect_command,
    show_strategies_command,
)
from constants import (
    BUF_SIZE,
)
from response import (
    HandshakeResponse,
    DefineWordResponse,
    PreliminaryResponse,
    StrategiesResponse,
)
from status_codes import DictStatusCode


class DictionaryClient:
    """Implements a client for communication with a server implementing
    the DICT Server Protocol (https://tools.ietf.org/html/rfc2229).
    """
    def __init__(self, host='localhost', port=2628, sock_class=socket.socket):
        self.client_name = f'{getpass.getuser()}@{socket.gethostname()}'
        self.client_id_info = f'{self.client_name} {datetime.now().isoformat()}'
        self.sock = sock_class(socket.AF_INET, socket.SOCK_STREAM)
        self.server_info = self._connect(host, port)
        self.strategies = self._get_strategies()

    def _recv_all(self):
        rlist, _, _ = select.select([self.sock], [], [], 5)
        if self.sock not in rlist:
            raise TimeoutError('Client timed out expecting server response.')
        bytes_received = self.sock.recv(BUF_SIZE)
        status_code = self._get_status(bytes_received)
        if DictStatusCode.response_complete(status_code):
            return bytes_received
        while not self._response_complete(bytes_received):
            rlist, _, _ = select.select([self.sock], [], [], 5)
            if self.sock not in rlist:
                raise TimeoutError(
                    'Client timed out following preliminary response with status '
                    f'{status_code}.'
                )
            bytes_received += self.sock.recv(BUF_SIZE)
        return bytes_received

    def _connect(self, host, port):
        self.sock.connect((host, port))
        response = HandshakeResponse(self._recv_all())
        if response.status_code != DictStatusCode.CONNECTION_ACCEPTED:
            raise Exception(response.status_code)
        self._send_client_ident()
        return response.content

    def _send_client_ident(self):
        self.sock.sendall(client_ident_command(self.client_id_info))
        response = PreliminaryResponse(self._recv_all())
        if response.status_code != DictStatusCode.OK:
            raise Exception(response.status_code)

    def _get_status(self, response_bytes):
        return int(response_bytes[:3])

    def _response_complete(self, response_bytes):
        return b'250' in response_bytes

    def _get_strategies(self):
        self.sock.sendall(show_strategies_command())
        response = StrategiesResponse(self._recv_all())
        return response.content

    def define_word(self, word, db='*'):
        self.sock.sendall(define_word_command(word, db))
        response = DefineWordResponse(self._recv_all())
        return response.content

    def disconnect(self):
        self.sock.sendall(disconnect_command())
        bytes_recieved = self._recv_all()
        if self._get_status(bytes_recieved) != DictStatusCode.CLOSING_CONNECTION:
            raise ConnectionError(
                'Client got unexpected response to QUIT command: '
                f'"{bytes_recieved.decode()}"'
            )
        self.sock.close()
