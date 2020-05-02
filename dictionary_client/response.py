import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from status_codes import DictStatusCode, PERMANENT_NEGATIVE_COMPLETION_CODES


class BaseResponse(metaclass=ABCMeta):
    STATUS_REGEXP = re.compile(r"^\d{3}")
    CONTENT_DELIMITER = "."
    LINE_DELIMITER = "\r\n"

    def __init__(self, response_bytes):
        self.response_text = response_bytes.decode()
        self.status_code = self.parse_status_code()
        self.content = self.parse_content()

    def parse_status_code(self):
        match = self.STATUS_REGEXP.match(self.response_text)
        if not match:
            raise ValueError(
                f"Expected status response but received: {self.response_text}"
            )
        return int(match.group(0))

    @abstractmethod
    def parse_content(self):
        pass

    def is_content_line(self, line):
        return self.STATUS_REGEXP.match(line) is None


class ServerPropertiesResponse(BaseResponse):
    """ Responses to a SHOW DB or SHOW STRAT command
    """

    def parse_content(self):
        if self.status_code in PERMANENT_NEGATIVE_COMPLETION_CODES:
            return None
        response_lines = self.response_text.split(self.LINE_DELIMITER)
        content_lines = list(filter(self.is_content_line, response_lines))
        content_lines = content_lines[: content_lines.index(self.CONTENT_DELIMITER)]
        lines_split = (line.split(maxsplit=1) for line in content_lines)
        return {item: description.strip('"') for item, description in lines_split}


class PreliminaryResponse(BaseResponse):
    """ A generic one line response (status code followed by optional
    text).
    """

    def parse_content(self):
        return {"text": self.response_text.split(maxsplit=1)[1]}


class DefineWordResponse(BaseResponse):
    def parse_content(self):
        if self.status_code == DictStatusCode.NO_MATCH:
            return None
        definition_lines = list(
            filter(self.is_content_line, self.response_text.split(self.LINE_DELIMITER))
        )
        definitions = []
        while "." in definition_lines:
            delim_index = definition_lines.index(self.CONTENT_DELIMITER)
            new_def = definition_lines[:delim_index]
            definitions.append(
                {"db": new_def[0].split()[2], "definition": "\n".join(new_def[1:])}
            )
            definition_lines = definition_lines[delim_index + 1 :]
        return definitions

    def is_content_line(self, line):
        return not line.startswith("150") and not line.startswith("250")


class MatchResponse(BaseResponse):
    def parse_content(self):
        if self.status_code == DictStatusCode.NO_MATCH:
            return None
        match_lines = list(
            filter(self.is_content_line, self.response_text.split(self.LINE_DELIMITER))
        )
        match_lines = match_lines[: match_lines.index(".")]
        matches = defaultdict(list)
        for line in match_lines:
            db_name, match = line.split(maxsplit=1)
            matches[db_name].append(match.strip('"'))
        return matches


class HandshakeResponse(PreliminaryResponse):
    CAPABILITIES_RE = re.compile(r"<([\w\d_]*(\.[\w\d_]+)*)>")
    MSG_ID_RE = re.compile(r"(<[\d\w@.]+>)\r\n")

    def parse_content(self):
        capabilities_match = self.CAPABILITIES_RE.search(self.response_text)
        msg_id_match = self.MSG_ID_RE.search(self.response_text)
        if not msg_id_match:
            raise ValueError(
                "Client got unexpected banner in connection response: "
                f"{self.response_text}"
            )
        content = {"message_id": msg_id_match.group(1), "capabilities": None}
        if capabilities_match:
            content.update({"capabilities": capabilities_match.group(1).split(".")})
        return content
