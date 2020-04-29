import re
from abc import ABCMeta, abstractmethod


class BaseResponse(metaclass=ABCMeta):
    STATUS_REGEXP = re.compile(r'^\d{3}')

    def __init__(self, response_bytes):
        self.response_text = response_bytes.decode()
        self.status_code = self._parse_status_code()
        self.content = self._parse_content()

    def _parse_status_code(self):
        match = self.STATUS_REGEXP.match(self.response_text)
        if not match:
            raise ValueError(
                f'Expected status response but received: {self.response_text}'
            )
        return int(match.group(0))

    @abstractmethod
    def _parse_content(self):
        pass


class GenericResponse(BaseResponse):
    """ A generic one part response (status code followed by optional
    text).
    """
    CONTENT_REGEXP = re.compile(r'(?:[a-zA-Z]+\s?)*$')

    def _parse_content(self):
        match = self.CONTENT_REGEXP.search(self.response_text)
        if not match:
            raise ValueError(
                f'Expected response content but received: {self.response_text}'
            )
        return {'text': match.group(0)}


class DefineWordResponse(BaseResponse):
    def _parse_content(self):
        pass

    def _parse_status_code(self):
        pass


class HandshakeResponse(GenericResponse):
    CONTENT_REGEXP = re.compile(
        r'<(?P<capabilities>[\w\d_]*(\.[\w\d_]+)*)>\s*(?P<msg_id><[\d\w@.]+>)'
    )

    def _parse_content(self):
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
