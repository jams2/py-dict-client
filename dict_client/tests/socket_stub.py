class SocketStub(object):
    """ Mocks the socket.socket class providing responses matching the
    Dictionary Server protocol specification.
    """
    def __init__(self, *args, **kwargs):
        self.requests = []

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

    def sendall(self, request):
        self.requests.append(request.decode('utf-8'))
