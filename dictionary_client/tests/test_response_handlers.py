import unittest

from response import (
    PreliminaryResponse,
    ServerPropertiesResponse,
    HandshakeResponse,
    DefineWordResponse,
)


class TestHandshakeResponse(unittest.TestCase):
    def test_parse_response_without_capabilities(self):
        dict_response = (
            b"220 dict.org dictd (version 0.9) <27831.860032493@dict.org>\r\n"
        )
        response = HandshakeResponse(dict_response)
        self.assertEqual("<27831.860032493@dict.org>", response.content["message_id"])

    def test_parse_response_with_capabilities(self):
        dict_response = (
            b"220 yonaguni.localdomain dictd 1.12.1/rf on Linux 5.6.7-arch1-1 "
            b"<auth.mime> <22.77854.1588081885@yonaguni.localdomain>\r\n"
        )
        response = HandshakeResponse(dict_response)
        self.assertEqual(
            "<22.77854.1588081885@yonaguni.localdomain>",
            response.content["message_id"],
        )
        self.assertEqual(
            ["auth", "mime"], response.content["capabilities"],
        )


class TestPreliminaryResponse(unittest.TestCase):
    def test_parse_response(self):
        fixtures = (
            (b"113 Help text follows", 113, {"text": "Help text follows"}),
            (b"250 Command complete", 250, {"text": "Command complete"}),
            (b"552 No match", 552, {"text": "No match"}),
            (
                b"150 1 definitions found: list follows",
                150,
                {"text": "1 definitions found: list follows"},
            ),
        )
        for response, code, content in fixtures:
            with self.subTest(response=response):
                handler = PreliminaryResponse(response)
                self.assertEqual(code, handler.status_code)
                self.assertEqual(content, handler.content)


class TestStrategyResponse(unittest.TestCase):
    def test_parse_content(self):
        dict_response = (
            b"111 5 strategies present: list follows\r\n"
            b'exact "Match words exactly"\r\n'
            b'prefix "Match word prefixes"\r\n'
            b'substring "Match substrings anywhere in word"\r\n'
            b".\r\n"
            b"250 Command complete\r\n"
        )
        response = ServerPropertiesResponse(dict_response)
        self.assertEqual(
            {
                "exact": "Match words exactly",
                "prefix": "Match word prefixes",
                "substring": "Match substrings anywhere in word",
            },
            response.content,
        )

    def test_handles_negative_response(self):
        dict_response = b"555 No strategies available"
        response = ServerPropertiesResponse(dict_response)
        self.assertEqual(None, response.content)
        self.assertEqual(555, response.status_code)


class TestShowDatabaseResponse(unittest.TestCase):
    def test_parse_content(self):
        dict_response = (
            b"110 3 databases present: list follows\r\n"
            b'wn "WordNet 1.5"\r\n'
            b'foldoc "Free On-Line Dictionary of Computing"\r\n'
            b'jargon "Hacker Jargon File"\r\n'
            b".\r\n"
            b"250 Command complete\r\n"
        )
        response = ServerPropertiesResponse(dict_response)
        self.assertEqual(
            {
                "wn": "WordNet 1.5",
                "foldoc": "Free On-Line Dictionary of Computing",
                "jargon": "Hacker Jargon File",
            },
            response.content,
        )

    def test_handles_negative_response(self):
        dict_response = b"554 No databases present"
        response = ServerPropertiesResponse(dict_response)
        self.assertEqual(None, response.content)
        self.assertEqual(554, response.status_code)


class TestDefineWordResponse(unittest.TestCase):
    def test_word_definition_single_db(self):
        dict_response = (
            b"150 1 definition retrieved\r\n"
            b'151 "table" fra-eng "French-English '
            b'FreeDict Dictionary ver. 0.4.1"\r\ntable /tabl/ <n, fem>\r\ntable\r\n'
            b".\r\n250 ok [d/m/c = 1/0/12; 0.000r 0.000u 0.000s]\r\n"
        )
        response = DefineWordResponse(dict_response)
        self.assertEqual(
            [{"db": "fra-eng", "definition": "table /tabl/ <n, fem>\ntable"}],
            response.content,
        )

    def test_word_definition_wild_db(self):
        dict_response = (
            b"150 3 definitions retrieved\r\n"
            b'151 "table" fra-eng "French-English '
            b'FreeDict Dictionary ver. 0.4.1"\r\ntable /tabl/ <n, fem>\r\ntable\r\n'
            b'.\r\n151 "table" eng-fra "English-French FreeDict Dictionary ver. '
            b'0.1.6"\r\ntable /teibl/\r\n1. liste, tableau\r\n2. table\r\n.\r\n151 '
            b'"table" wn "WordNet (r) 3.1 (2011)"\r\ntable\r\n    n 1: a set of '
            b'data arranged in rows and columns; "see table 1"\r\n         [syn: '
            b"{table}, {tabular array}]\r\n    2: a piece of furniture having a "
            b"smooth flat top that is usually\r\n       supported by one or more "
            b'vertical legs; "it was a sturdy\r\n       table"\r\n    3: a piece '
            b'of furniture with tableware for a meal laid out on\r\n       it; "I '
            b'reserved a table at my favorite restaurant"\r\n    4: flat tableland '
            b'with steep edges; "the tribe was relatively\r\n       safe on the '
            b'mesa but they had to descend into the valley for\r\n       water" '
            b"[syn: {mesa}, {table}]\r\n    5: a company of people assembled at a "
            b'table for a meal or game;\r\n       "he entertained the whole table '
            b'with his witty remarks"\r\n    6: food or meals in general; "she '
            b'sets a fine table"; "room and\r\n       board" [syn: {board}, '
            b"{table}]\r\n    v 1: hold back to a later time; \"let's postpone the "
            b'exam" [syn:\r\n         {postpone}, {prorogue}, {hold over}, '
            b"{put over}, {table},\r\n         {shelve}, {set back}, {defer}, "
            b"{remit}, {put off}]\r\n    2: arrange or enter in tabular form "
            b"[syn: {table}, {tabularize},\r\n       {tabularise}, {tabulate}]\r\n."
            b"\r\n250 ok [d/m/c = 3/0/40; 0.000r 0.000u 0.000s]\r\n"
        )
        response = DefineWordResponse(dict_response)
        self.assertEqual(
            [
                {"db": "fra-eng", "definition": "table /tabl/ <n, fem>\ntable"},
                {
                    "db": "eng-fra",
                    "definition": ("table /teibl/\n1. liste, tableau\n2. table"),
                },
                {
                    "db": "wn",
                    "definition": (
                        "table\n    n 1: a set of "
                        'data arranged in rows and columns; "see table 1"\n         [syn: '
                        "{table}, {tabular array}]\n    2: a piece of furniture having a "
                        "smooth flat top that is usually\n       supported by one or more "
                        'vertical legs; "it was a sturdy\n       table"\n    3: a piece '
                        'of furniture with tableware for a meal laid out on\n       it; "I '
                        'reserved a table at my favorite restaurant"\n    4: flat tableland '
                        'with steep edges; "the tribe was relatively\n       safe on the '
                        'mesa but they had to descend into the valley for\n       water" '
                        "[syn: {mesa}, {table}]\n    5: a company of people assembled at a "
                        'table for a meal or game;\n       "he entertained the whole table '
                        'with his witty remarks"\n    6: food or meals in general; "she '
                        'sets a fine table"; "room and\n       board" [syn: {board}, '
                        "{table}]\n    v 1: hold back to a later time; \"let's postpone the "
                        'exam" [syn:\n         {postpone}, {prorogue}, {hold over}, '
                        "{put over}, {table},\n         {shelve}, {set back}, {defer}, "
                        "{remit}, {put off}]\n    2: arrange or enter in tabular form "
                        "[syn: {table}, {tabularize},\n       {tabularise}, {tabulate}]"
                    ),
                },
            ],
            response.content,
        )
