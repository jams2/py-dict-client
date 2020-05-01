import re
from abc import ABCMeta, abstractmethod


class BaseResponse(metaclass=ABCMeta):
    STATUS_REGEXP = re.compile(r'^\d{3}')

    def __init__(self, response_bytes):
        self.response_text = response_bytes.decode()
        self.status_code = self.parse_status_code()
        self.content = self.parse_content()

    def parse_status_code(self):
        match = self.STATUS_REGEXP.match(self.response_text)
        if not match:
            raise ValueError(
                f'Expected status response but received: {self.response_text}'
            )
        return int(match.group(0))

    @abstractmethod
    def parse_content(self):
        pass


class StrategiesResponse(BaseResponse):
    def parse_content(self):
        response_lines = self.response_text.split('\r\n')
        content_lines = list(filter(lambda x: not x[:3].isnumeric(), response_lines))
        content_lines = content_lines[:content_lines.index('.')]
        return set(line.split()[0] for line in content_lines)


class PreliminaryResponse(BaseResponse):
    """ A generic one line response (status code followed by optional
    text).
    """
    CONTENT_REGEXP = re.compile(r'^\d{3}\s((?:[\d:a-zA-Z]+\s?)+)$')

    def parse_content(self):
        match = self.CONTENT_REGEXP.search(self.response_text)
        if not match:
            raise ValueError(
                f'Expected response content but received: {self.response_text}'
            )
        return {'text': match.group(1)}


class DefineWordResponse(BaseResponse):
    DEFINITION_DELIMITER = '.'

    def parse_content(self):
        definitions = []
        lines = self.response_text.split('\r\n')
        definition_lines = list(
            filter(
                lambda x: not x.startswith('150') and not x.startswith('250'),
                lines,
            )
        )
        while '.' in definition_lines:
            delim_index = definition_lines.index(self.DEFINITION_DELIMITER)
            new_def = definition_lines[:delim_index]
            definitions.append({
                'db': new_def[0].split()[2],
                'definition': '\n'.join(new_def[1:])
            })
            definition_lines = definition_lines[delim_index+1:]
        return definitions

    def parse_status_code(self):
        pass


class HandshakeResponse(PreliminaryResponse):
    CONTENT_REGEXP = re.compile(
        r'<(?P<capabilities>[\w\d_]*(\.[\w\d_]+)*)>\s*(?P<msg_id><[\d\w@.]+>)'
    )

    def parse_content(self):
        match = self.CONTENT_REGEXP.search(self.response_text)
        if not match:
            raise ValueError(
                'Client got unexpected banner in connection response: '
                f'{self.response_text}'
            )
        return {
            'capabilities': match.group('capabilities').split('.'),
            'message_id': match.group('msg_id'),
        }
