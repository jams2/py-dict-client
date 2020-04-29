from abc import (
    ABCMeta,
    abstractmethod,
)

from constants import BUF_SIZE
from status_codes import DictStatusCode


class DictionaryClientCommand(metaclass=ABCMeta):
    def __init__(self, sock):
        self.sock = sock
        self._response_segments = []
        self.response = None

    @abstractmethod
    def get_query(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_response_class(self):
        pass

    def send(self):
        self._send()
        return self.response

    def _encode_query(self, query, encoding='utf-8'):
        return f'{query}\r\n'.encode(encoding)

    def _last_response_status(self):
        return int(self._response_segments[-1][0:3])

    def _send(self, *args, **kwargs):
        self.sock.sendall(self.get_query())
        self._recv()
        if DictStatusCode.TEXT_FOLLOWS(self._last_response_status()):
            while not DictStatusCode.RESPONSE_COMPLETE(self._last_response_status()):
                self._recv()

    def _recv(self):
        self._response_segments.append(self.sock.recv(BUF_SIZE))


class ClientIdentCommand(DictionaryClientCommand):
    def __init__(self, sock, client_id_info):
        self.client_id_info = client_id_info
        super().__init__(sock)

    def get_response_class(self):
        pass

    def get_query(self):
        return self._encode_query(f'CLIENT {self.client_id_info}')


class DisconnectCommand(DictionaryClientCommand):
    def get_query(self):
        return self._encode_query('QUIT')


class DefineWordCommand(DictionaryClientCommand):
    def __init__(self, sock, word, database_name='*'):
        self.word = word
        self.database_name = database_name
        super().__init__(sock)

    def get_query(self):
        return self._encode_query(f'DEFINE {self.database_name} {self.word}')
