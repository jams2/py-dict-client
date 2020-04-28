import socket
import re
import getpass
from datetime import datetime
from enum import IntEnum
from abc import ABCMeta, abstractmethod


BUF_SIZE = 4096
DEFAULT_PORT = 2628


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
            handler_class=ConnectionResponseParser,
        )
        if connection_response.get_status() != DictStatusCode.CONNECTION_ACCEPTED:
            raise Exception(connection_response.get_status())
        self._send_client_ident(sock)
        return (sock, connection_response.content)

    def _send_client_ident(self, sock):
        request = ClientIdentRequest(sock, self.client_id_info)
        request.send()
        if request.get_status() != DictStatusCode.OK:
            raise Exception(request.get_status())

    def parse_server_info(self):
        pass

    def get_word_definitions(self, word, database_name='*'):
        response = DefineWordRequest(self.sock, word, database_name=database_name)
        return response

    def disconnect(self):
        response = DisconnectRequest(self.sock)
        if response.get_status() != DictStatusCode.CLOSING_CONNECTION:
            raise Exception(response.get_status())
        self.sock.close()


class DictClientRequest(metaclass=ABCMeta):
    def __init__(self, sock):
        self.sock = sock
        self.response_segments = []

    @abstractmethod
    def get_query(self, *args, **kwargs):
        pass

    def send(self):
        self._send()

    def _encode_query(self, query, encoding='utf-8'):
        return f'{query}\r\n'.encode(encoding)

    def get_status(self):
        return self.response_segments[0].get_status()

    def _last_response_status(self):
        return self.response_segments[-1].get_status()

    def _send(self, *args, **kwargs):
        self.sock.sendall(self.get_query())
        self._recv()
        if DictStatusCode.TEXT_FOLLOWS(self._last_response_status()):
            while not DictStatusCode.RESPONSE_COMPLETE(self._last_response_status()):
                self._recv()

    def _recv(self):
        self.response_segments.append(DictServerResponse(self.sock.recv(BUF_SIZE)))


class ClientIdentRequest(DictClientRequest):
    def __init__(self, sock, client_id_info):
        self.client_id_info = client_id_info
        super().__init__(sock)

    def get_query(self):
        return self._encode_query(f'CLIENT {self.client_id_info}')


class DisconnectRequest(DictClientRequest):
    def get_query(self):
        return self._encode_query('QUIT')


class DefineWordRequest(DictClientRequest):
    def __init__(self, sock, word, database_name='*'):
        self.word = word
        self.database_name = database_name
        super().__init__(sock)

    def get_query(self):
        return self._encode_query(f'DEFINE {self.database_name} {self.word}')


class DictServerResponse:
    def __init__(self, response_bytes, handler_class=None):
        self.response = response_bytes.decode('utf-8')
        if handler_class:
            response_handler = handler_class(self.response)
            self.content = response_handler.get_content()

    def get_status(self):
        return int(self.response[:3])


class ConnectionResponseParser:
    REGEXP = re.compile(
        r'<(?P<capabilities>[\w\d_]*(\.[\w\d_]+)*)>\s*(?P<msg_id><[\d\w@.]+>)'
    )

    def __init__(self, response_text):
        self.response_text = response_text
        self.parsed_content = None

    def get_content(self):
        if self.parsed_content is not None:
            return self.parsed_content
        match = self.REGEXP.search(self.response_text)
        if not match:
            raise ValueError(
                'Client got unexpected banner in connection response: '
                f'{self.response_text}'
            )
        self.parsed_content = {
            'capabilities': '.'.split(match.group('capabilities')),
            'message_id': match.group('capabilities'),
        }


class DictStatusCode(IntEnum):
    @staticmethod
    def RESPONSE_COMPLETE(status):
        return status >= 200 and status < 300

    @staticmethod
    def TEXT_FOLLOWS(status):
        return status >= 100 and status < 200

    DATABASES_PRESENT = 110
    STRATEGIES_AVAILABLE = 111
    DB_INFO_FOLLOWS = 112
    HELP_TEXT_FOLLOWS = 113
    SERVER_INFO_FOLLOWS = 114
    SASL_CHALLENGE_FOLLOWS = 130
    DEFINITIONS_FOLLOW = 150
    DEFINITION_BODY = 151
    MATCHES_FOUND = 152

    STATUS_FOLLOWS = 210
    CONNECTION_ACCEPTED = 220
    CLOSING_CONNECTION = 221
    AUTH_SUCCESSFUL = 230
    OK = 250

    SASL_SEND_RESPONSE = 330

    SERVER_TEMP_UNAVAILABLE = 420
    SERVER_SHUTDOWN = 421

    CMD_NOT_RECOGNIZED = 500
    ILLEGAL_PARAMS = 501
    CMD_NOT_IMPLEMENTED = 502
    PARAM_NOT_IMPLEMENTED = 503
    ACCESS_DENIED = 530
    AUTH_FAILED = 531
    UNKNOWN_MECHANISM = 532
    INVALID_DB = 550
    INVALID_STRATEGY = 551
    NO_MATCH = 552
    NO_DATABASES = 554
    NO_STRATEGIES = 555
