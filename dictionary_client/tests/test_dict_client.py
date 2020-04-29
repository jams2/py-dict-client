import unittest

from socket_stub import SocketStub
from dictionary_client import DictionaryClient


class TestDictClient(unittest.TestCase):
    def test_parses_server_banner(self):
        client = DictionaryClient(sock_class=SocketStub)
        self.assertEqual(
            {
                'capabilities': ['auth', 'mime'],
                'message_id': '<22.77854.1588081885@yonaguni.localdomain>',
            },
            client.server_info,
        )
