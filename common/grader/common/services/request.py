from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from traitlets.config.configurable import LoggingConfigurable
from typing import Dict
from tornado.escape import json_decode
from traitlets.traitlets import Int, TraitError, Unicode, validate
import socket


class RequestService(LoggingConfigurable):
    scheme = Unicode('http', help="The http scheme to use. Either 'http' or 'https'").tag(config=True)
    host = Unicode('127.0.0.1', help="Host adress the service should make requests to").tag(config=True)
    port = Int(4010, help="Host port of service").tag(config=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.http_client = AsyncHTTPClient()

    async def request(self, method: str, endpoint: str, body: dict=None, header: Dict[str, str]=None) -> dict:
        response: HTTPResponse = await self.http_client.fetch(self.url+endpoint, method=method, headers=header, body=body)
        return json_decode(response.body)
    
    @validate("scheme")
    def _validate_scheme(self, proposal):
        if proposal["value"] not in {"http", "https"}:
            raise TraitError("Invalid scheme. Use either http or https")
        return proposal["value"]

    @validate("host")
    def _validate_host(self, proposal):
        try:
            socket.gethostbyname(proposal["value"])
            return proposal["value"]
        except socket.error:
            raise TraitError("Host adress has to resolve. Invalid hostname %s" % proposal["value"])
    
    @validate("port")
    def _validate_port(self, proposal):
        value = proposal["value"]
        if not 1 <= value <= 65535:
            raise TraitError("Port number has to be between 1 and 65535.")
        return value

    @property
    def url(self):
        return self.scheme + "://" + self.host + ":" + str(self.port)
    