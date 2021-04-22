from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from tornado.util import import_object
from traitlets.config.configurable import Configurable
from typing import Dict
import json
from tornado.escape import json_decode

from traitlets.traitlets import Int, Unicode


class RequestService(Configurable):
    scheme = Unicode('http', help="The http scheme to use. Either 'http' or 'https'").tag(config=True)
    host = Unicode('127.0.0.1', help="Host adress of the grader service").tag(config=True)
    port = Int(8880, help="Host port of the grader service").tag(config=True)

    async def request(self,method: str, endpoint: str, body: dict=None, header: Dict[str, str]=None) -> dict:
        http_client = AsyncHTTPClient()
        response: HTTPResponse = await http_client.fetch(self.url+endpoint, method=method, headers=header, body=body)
        return json_decode(response.body)
    
    @property
    def url(self):
        return self.scheme + "://" + self.host + ":" + str(self.port)