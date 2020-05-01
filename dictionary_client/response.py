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


class ServerPropertiesResponse(BaseResponse):
    """ Responses to a SHOW DB or SHOW STRAT command
    """
    def parse_content(self):
        if self.status_code > 500:
            return None
        response_lines = self.response_text.split('\r\n')
        content_lines = list(filter(lambda x: not x[:3].isnumeric(), response_lines))
        content_lines = content_lines[:content_lines.index('.')]
        lines_split = (line.split(maxsplit=1) for line in content_lines)
        return {l[0]: l[1].strip('"') for l in lines_split}


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
    CAPABILITIES_RE = re.compile(r'<([\w\d_]*(\.[\w\d_]+)*)>')
    MSG_ID_RE = re.compile(r'(<[\d\w@.]+>)\r\n')

    def parse_content(self):
        capabilities_match = self.CAPABILITIES_RE.search(self.response_text)
        msg_id_match = self.MSG_ID_RE.search(self.response_text)
        if not msg_id_match:
            raise ValueError(
                'Client got unexpected banner in connection response: '
                f'{self.response_text}'
            )
        content = {'message_id': msg_id_match.group(1), 'capabilities': None}
        if capabilities_match:
            content.update({'capabilities': capabilities_match.group(1).split('.')})
        return content
