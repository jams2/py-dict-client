import unittest

from response import (
    GenericResponse,
    PreliminaryQueryResponse,
)


class TestGenericResponseHandler(unittest.TestCase):
    def test_parse_response(self):
        fixtures = (
            (b'113 Help text follows', 113, {'text': 'Help text follows'}),
            (b'250 Command complete', 250, {'text': 'Command complete'}),
            (b'552 No match', 552, {'text': 'No match'}),
        )
        for response, code, content in fixtures:
            with self.subTest(response=response):
                handler = GenericResponse(response)
                self.assertEqual(code, handler.status_code)
                self.assertEqual(content, handler.content)


class TestPreliminaryQueryResponse(unittest.TestCase):
    def test_parse_status_code(self):
        pass

    def test_parse_content(self):
        pass
