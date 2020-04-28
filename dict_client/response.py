import re


class DictServerResponse:
    def __init__(self, response_bytes, handler_class=None):
        self.response = response_bytes.decode('utf-8')
        if handler_class:
            response_handler = handler_class(self.response)
            self.content = response_handler.get_content()

    def get_status(self):
        return int(self.response[:3])


class HandshakeResponseParser:
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
