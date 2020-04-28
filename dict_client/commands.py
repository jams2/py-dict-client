from abc import (
    ABCMeta,
    abstractmethod,
)

from constants import BUF_SIZE
from response import DictServerResponse
from status_codes import DictStatusCode


class DictClientCommand(metaclass=ABCMeta):
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


class ClientIdentCommand(DictClientCommand):
    def __init__(self, sock, client_id_info):
        self.client_id_info = client_id_info
        super().__init__(sock)

    def get_query(self):
        return self._encode_query(f'CLIENT {self.client_id_info}')


class DisconnectCommand(DictClientCommand):
    def get_query(self):
        return self._encode_query('QUIT')


class DefineWordCommand(DictClientCommand):
    def __init__(self, sock, word, database_name='*'):
        self.word = word
        self.database_name = database_name
        super().__init__(sock)

    def get_query(self):
        return self._encode_query(f'DEFINE {self.database_name} {self.word}')
