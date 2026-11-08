"""Serial local HTTP service with a bounded burst queue and header/body read timeout."""
from http.server import HTTPServer


class LocalEvidenceServer(HTTPServer):
    request_queue_size = 32
    request_read_timeout = 5

    def get_request(self):
        connection,address=super().get_request()
        connection.settimeout(self.request_read_timeout)
        return connection,address
