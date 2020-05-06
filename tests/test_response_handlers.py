import unittest

from dictionary_client.response import (
    PreliminaryResponse,
    ServerPropertiesResponse,
    HandshakeResponse,
    DefineWordResponse,
    MatchResponse,
    DatabaseInfoResponse,
    MultiLineResponse,
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
            (b"113 Help text follows\r\n", 113, "Help text follows"),
            (b"250 Command complete\r\n", 250, "Command complete"),
            (b"552 No match\r\n", 552, "No match"),
            (
                b"150 1 definitions found: list follows\r\n",
                150,
                "1 definitions found: list follows",
            ),
            (
                b"210 status [d/m/c = 0/0/0; 100.000r 0.000u 0.000s]\r\n",
                210,
                "status [d/m/c = 0/0/0; 100.000r 0.000u 0.000s]",
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
    def test_no_match(self):
        dict_response = b"552 No match\r\n"
        response = DefineWordResponse(dict_response)
        self.assertIsNone(response.content)
        self.assertEqual(552, response.status_code)

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


class TestMultiLineResponse(unittest.TestCase):
    def test_parses_content(self):
        """ The output format is not in the specification, so we will
        just return a string.
        """
        dict_response = (
            b"114 server information\r\ndictd 1.12.1/rf on Linux 5.6.8-arch1-1\r\n"
            b"On yonaguni.localdomain: up 1+02:11:17, 12 forks (0.5/hour)\r\n\r\n"
            b"Database      Headwords         Index          Data  Uncompressed\r\n"
            b"fra-eng       8511        131 kB        140 kB        381 kB\r\n"
            b"eng-fra       8805        128 kB        132 kB        334 kB\r\n"
            b"wn          147483       3005 kB       9272 kB         29 MB\r\n"
            b"foldoc       15197        299 kB       2249 kB       5522 kB\r\n"
            b"\r\n.\r\n250 ok\r\n"
        )
        response = MultiLineResponse(dict_response)
        expected = (
            "dictd 1.12.1/rf on Linux 5.6.8-arch1-1\n"
            "On yonaguni.localdomain: up 1+02:11:17, 12 forks (0.5/hour)\n\n"
            "Database      Headwords         Index          Data  Uncompressed\n"
            "fra-eng       8511        131 kB        140 kB        381 kB\n"
            "eng-fra       8805        128 kB        132 kB        334 kB\n"
            "wn          147483       3005 kB       9272 kB         29 MB\n"
            "foldoc       15197        299 kB       2249 kB       5522 kB\n"
        )
        self.assertEqual(expected, response.content)


class TestDatabaseInfoResponse(unittest.TestCase):
    def test_invalid_db_returns_none(self):
        response = DatabaseInfoResponse(
            b'550 Invalid database, use "SHOW DB" for list of databases'
        )
        self.assertIsNone(response.content)

    def test_valid_response_parsed(self):
        dict_response = (
            b"112 information for eng-fra\r\n============ eng-fra ============"
            b"\r\nEnglish-French FreeDict Dictionary\r\n\r\nMaintainer: "
            b"[up for grabs]\r\n.\r\n250 ok\r\n"
        )
        response = DatabaseInfoResponse(dict_response)
        expected = (
            "============ eng-fra ============"
            "\nEnglish-French FreeDict Dictionary\n\nMaintainer: "
            "[up for grabs]"
        )
        self.assertEqual(expected, response.content)


class TestMatchResponse(unittest.TestCase):
    def test_parse_content_one_db(self):
        dict_response = (
            b"152 7 matches found: list follows\r\n"
            b"foldoc Fast SCSI\r\n"
            b"foldoc SCSI\r\n"
            b"foldoc SCSI-1\r\n"
            b"foldoc SCSI-2\r\n"
            b"foldoc SCSI-3\r\n"
            b"foldoc Ultra-SCSI\r\n"
            b"foldoc Wide SCSI\r\n"
            b".\r\n"
            b"250 Command complete\r\n"
        )
        response = MatchResponse(dict_response)
        self.assertEqual(
            {
                "foldoc": [
                    "Fast SCSI",
                    "SCSI",
                    "SCSI-1",
                    "SCSI-2",
                    "SCSI-3",
                    "Ultra-SCSI",
                    "Wide SCSI",
                ]
            },
            response.content,
        )
        self.assertEqual(152, response.status_code)

    def test_parse_content_with_quote_marks(self):
        """ The spec shows no quote marks around matches, but on this
        user's machine (dictd on Arch Linux) the following is returned.
        Handle both cases.
        """
        dict_response = (
            b"152 5 matches found: list follows\r\n"
            b'wn "william sydney porter"\r\n'
            b'wn "written report"\r\n'
            b'foldoc "accelerated graphics port"\r\n'
            b'foldoc "ada programming support environment"\r\n'
            b'foldoc "application portability architecture"\r\n'
            b".\r\n"
            b"250 Command complete\r\n"
        )
        response = MatchResponse(dict_response)
        self.assertEqual(
            {
                "wn": ["william sydney porter", "written report"],
                "foldoc": [
                    "accelerated graphics port",
                    "ada programming support environment",
                    "application portability architecture",
                ],
            },
            response.content,
        )

    def test_no_match(self):
        dict_response = b"552 No match\r\n"
        response = MatchResponse(dict_response)
        self.assertIsNone(response.content)
        self.assertEqual(552, response.status_code)
