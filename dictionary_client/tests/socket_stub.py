class SocketStub(object):
    """ Mocks the socket.socket class providing responses matching the
    Dictionary Server protocol specification.
    """
    def __init__(self, *args, **kwargs):
        self.requests = []
        self.define_count = 0

    def connect(self, addr_info):
        pass

    def recv(self, *args, **kwargs):
        if not self.requests:
            # First call to recv() after connection, return the banner.
            return (
                b'220 yonaguni.localdomain dictd 1.12.1/rf on Linux 5.6.7-arch1-1 '
                b'<auth.mime> <22.77854.1588081885@yonaguni.localdomain>\r\n'
            )
        elif self.requests[-1].startswith('CLIENT'):
            return b'250 ok'
        elif self.requests[-1] == 'DEFINE fra-eng table\r\n':
            if self.define_count == 0:
                self.define_count += 1
                return b'150 1 definition retrieved'
            return (
                b'151 "table" fra-eng "French-English '
                b'FreeDict Dictionary ver. 0.4.1"\r\ntable /tabl/ <n, fem>\r\ntable\r\n'
                b'.\r\n250 ok [d/m/c = 1/0/12; 0.000r 0.000u 0.000s]\r\n'
            )
        elif self.requests[-1] == 'DEFINE * table\r\n':
            if self.define_count == 0:
                self.define_count += 1
                return b'150 3 definitions retrieved'
            return (
                b'151 "table" fra-eng "French-English '
                b'FreeDict Dictionary ver. 0.4.1"\r\ntable /tabl/ <n, fem>\r\ntable\r\n'
                b'.\r\n151 "table" eng-fra "English-French FreeDict Dictionary ver. '
                b'0.1.6"\r\ntable /teibl/\r\n1. liste, tableau\r\n2. table\r\n.\r\n151 '
                b'"table" wn "WordNet (r) 3.1 (2011)"\r\ntable\r\n    n 1: a set of '
                b'data arranged in rows and columns; "see table 1"\r\n         [syn: '
                b'{table}, {tabular array}]\r\n    2: a piece of furniture having a '
                b'smooth flat top that is usually\r\n       supported by one or more '
                b'vertical legs; "it was a sturdy\r\n       table"\r\n    3: a piece '
                b'of furniture with tableware for a meal laid out on\r\n       it; "I '
                b'reserved a table at my favorite restaurant"\r\n    4: flat tableland '
                b'with steep edges; "the tribe was relatively\r\n       safe on the '
                b'mesa but they had to descend into the valley for\r\n       water" '
                b'[syn: {mesa}, {table}]\r\n    5: a company of people assembled at a '
                b'table for a meal or game;\r\n       "he entertained the whole table '
                b'with his witty remarks"\r\n    6: food or meals in general; "she '
                b'sets a fine table"; "room and\r\n       board" [syn: {board}, '
                b'{table}]\r\n    v 1: hold back to a later time; "let\'s postpone the '
                b'exam" [syn:\r\n         {postpone}, {prorogue}, {hold over}, '
                b'{put over}, {table},\r\n         {shelve}, {set back}, {defer}, '
                b'{remit}, {put off}]\r\n    2: arrange or enter in tabular form '
                b'[syn: {table}, {tabularize},\r\n       {tabularise}, {tabulate}]\r\n.'
                b'\r\n250 ok [d/m/c = 3/0/40; 0.000r 0.000u 0.000s]\r\n'
            )

    def sendall(self, request):
        self.requests.append(request.decode('utf-8'))
