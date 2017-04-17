__author__ = 'Rafa Haro <rh@athento.com>'

from restkit import Connection, request

from socketpool import ConnectionPool
import eventlet

class _RestClient(object):

    def __init__(self, endpoint, **kwargs):
        __pool = ConnectionPool(factory=Connection, backend="eventlet")
        self._epool = eventlet.GreenPool()
        self.endpoint = endpoint if endpoint.endswith("/") else endpoint + "/"
        self.__options = kwargs
        self.__options['pool'] = __pool

    def rest_get(self, url, headers={}):
        return request(url, 'GET', None, headers, **self.__options)

    def rest_post(self, url, body, headers={}):
        return request(url, 'POST', body, headers, **self.__options)

    def rest_delete(self, url, headers={}):
        return request(url, 'DELETE', None, headers, **self.__options)


class StanbolClient(object):
    """
    Apache Stanbol REST Client class. It jus initializes the proper resources for communicating with
    the Stanbol Server in a certain endpoint
    """

    def __init__(self, endpoint="http://localhost:8080", **kwargs):
        self.rest_client = _RestClient(endpoint, **kwargs)

    @property
    def enhancer(self):
        from components.enhancer.client import Enhancer
        return Enhancer(self.rest_client)

    @property
    def entityhub(self):
        from components.entityhub.client import EntityHub
        return EntityHub(self.rest_client)

