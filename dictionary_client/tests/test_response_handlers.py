import unittest

from response import (
    PreliminaryResponse,
)


class TestPreliminaryResponse(unittest.TestCase):
    def test_parse_response(self):
        fixtures = (
            (b'113 Help text follows', 113, {'text': 'Help text follows'}),
            (b'250 Command complete', 250, {'text': 'Command complete'}),
            (b'552 No match', 552, {'text': 'No match'}),
            (b'150 1 definitions found: list follows', 150,
             {'text': '1 definitions found: list follows'}),
        )
        for response, code, content in fixtures:
            with self.subTest(response=response):
                handler = PreliminaryResponse(response)
                self.assertEqual(code, handler.status_code)
                self.assertEqual(content, handler.content)
