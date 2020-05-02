from enum import IntEnum


class DictStatusCode(IntEnum):
    @staticmethod
    def response_complete(status):
        return status >= 200 and status < 300

    @staticmethod
    def text_follows(status):
        return status >= 100 and status < 200

    DATABASES_PRESENT = 110
    STRATEGIES_AVAILABLE = 111
    DB_INFO_FOLLOWS = 112
    HELP_TEXT_FOLLOWS = 113
    SERVER_INFO_FOLLOWS = 114
    SASL_CHALLENGE_FOLLOWS = 130
    DEFINITIONS_FOLLOW = 150
    DEFINITION_BODY = 151
    MATCHES_FOUND = 152

    STATUS_FOLLOWS = 210
    CONNECTION_ACCEPTED = 220
    CLOSING_CONNECTION = 221
    AUTH_SUCCESSFUL = 230
    OK = 250

    SASL_SEND_RESPONSE = 330

    SERVER_TEMP_UNAVAILABLE = 420
    SERVER_SHUTDOWN = 421

    CMD_NOT_RECOGNIZED = 500
    ILLEGAL_PARAMS = 501
    CMD_NOT_IMPLEMENTED = 502
    PARAM_NOT_IMPLEMENTED = 503
    ACCESS_DENIED = 530
    AUTH_FAILED = 531
    UNKNOWN_MECHANISM = 532
    INVALID_DB = 550
    INVALID_STRATEGY = 551
    NO_MATCH = 552
    NO_DATABASES = 554
    NO_STRATEGIES = 555


PERMANENT_NEGATIVE_COMPLETION_CODES = {
    DictStatusCode.CMD_NOT_RECOGNIZED,
    DictStatusCode.ILLEGAL_PARAMS,
    DictStatusCode.CMD_NOT_IMPLEMENTED,
    DictStatusCode.PARAM_NOT_IMPLEMENTED,
    DictStatusCode.ACCESS_DENIED,
    DictStatusCode.AUTH_FAILED,
    DictStatusCode.UNKNOWN_MECHANISM,
    DictStatusCode.INVALID_DB,
    DictStatusCode.INVALID_STRATEGY,
    DictStatusCode.NO_MATCH,
    DictStatusCode.NO_DATABASES,
    DictStatusCode.NO_STRATEGIES,
}
