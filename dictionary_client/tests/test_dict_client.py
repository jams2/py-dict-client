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

    def test_word_definition_single_db(self):
        client = DictionaryClient(sock_class=SocketStub)
        result = client.define_word('table', db='fra-eng')
        self.assertEqual(
            [{'db': 'fra-eng', 'definition': 'table /tabl/ <n, fem>\ntable'}],
            result,
        )

    def test_word_definition_wild_db(self):
        client = DictionaryClient(sock_class=SocketStub)
        result = client.define_word('table')
        self.assertEqual(
            [{'db': 'fra-eng', 'definition': 'table /tabl/ <n, fem>\ntable'},
             {'db': 'eng-fra',
              'definition': (
                  'table /teibl/\n1. liste, tableau\n2. table'
              )},
             {'db': 'wn',
              'definition': (
                  'table\n    n 1: a set of '
                  'data arranged in rows and columns; "see table 1"\n         [syn: '
                  '{table}, {tabular array}]\n    2: a piece of furniture having a '
                  'smooth flat top that is usually\n       supported by one or more '
                  'vertical legs; "it was a sturdy\n       table"\n    3: a piece '
                  'of furniture with tableware for a meal laid out on\n       it; "I '
                  'reserved a table at my favorite restaurant"\n    4: flat tableland '
                  'with steep edges; "the tribe was relatively\n       safe on the '
                  'mesa but they had to descend into the valley for\n       water" '
                  '[syn: {mesa}, {table}]\n    5: a company of people assembled at a '
                  'table for a meal or game;\n       "he entertained the whole table '
                  'with his witty remarks"\n    6: food or meals in general; "she '
                  'sets a fine table"; "room and\n       board" [syn: {board}, '
                  '{table}]\n    v 1: hold back to a later time; "let\'s postpone the '
                  'exam" [syn:\n         {postpone}, {prorogue}, {hold over}, '
                  '{put over}, {table},\n         {shelve}, {set back}, {defer}, '
                  '{remit}, {put off}]\n    2: arrange or enter in tabular form '
                  '[syn: {table}, {tabularize},\n       {tabularise}, {tabulate}]'
              )}
            ],
            result,
        )
