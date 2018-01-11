class EntityHub():
    """EntityHub REST API consumer"""

    STANBOL_ENTITYHUB_PATH = "entityhub"
    STANBOL_ENTITYHUB_SITE_PATH = "site"
    STANBOL_ENTITYHUB_SITEMANAGER_PATH = "sites"

    def __init__(self, rest_client):
        self.__rest_client = rest_client
        """:type : RestClient"""

    def get_sites(self):
        """Returns a list containing the IDs of all sites configured in Stanbol """
        import json
        endpoint = self.__rest_client.endpoint + \
                   self.STANBOL_ENTITYHUB_PATH + "/" + \
                   self.STANBOL_ENTITYHUB_SITEMANAGER_PATH + "/referenced"

        response = self.__rest_client.rest_get(endpoint)
        if response.status_int == 200:
            return json.loads((response.body_string("UTF-8")))
        else:
            return []

    def get_entity(self, uri, site=None):
        """
        Retrieve an entity from the specified site. If site is None, it will try to be retrieved from EntityHub cache
        :param uri: URI (ID) of the entity
        :param site: EntityHub site
        :return: Entity data as Entity Model
        """
        endpoint = self.__rest_client.endpoint + \
                   self.STANBOL_ENTITYHUB_PATH + "/"
        if site:
            endpoint += self.STANBOL_ENTITYHUB_SITE_PATH + "/" + site + "/"
        endpoint += "entity?id=" + uri

        headers = {
            'Accept': 'application/rdf+xml'
        }

        response = self.__rest_client.rest_get(endpoint, headers=headers)
        if response.status_int == 404:
            raise ValueError("Entity with URI %s not found at site %s" % (uri, site))
        elif response.status_int == 200:
            from pystanbol.parser import parse_entity_from_str
            return parse_entity_from_str(response.body_string("UTF-8"), 'xml', uri)
        else:
            return None

    def create_or_update_entity(self, entity, site=None):
        """
        Index an entity within a Site in the EntityHub. If site is None, it will be indexed into the global cache
        :param entity: Entity to be indexed. Can be passed as an Entity object or an String containing Entity
        data in a supported format
        :param site: EntityHub site where the entity will be indexed
        :return: 
        """
        from models import Entity
        endpoint = self.__rest_client.endpoint + \
                   self.STANBOL_ENTITYHUB_PATH + "/"
        if site:
            endpoint += self.STANBOL_ENTITYHUB_SITE_PATH + "/" + site + "/"
        endpoint += "entity?update=True"

        headers = {
            'Content-Type': 'application/rdf+xml'
        }
        if isinstance(entity, Entity):
            rdf_body = entity.graph.serialize(format='xml')
        else:
            rdf_body = entity

        response = self.__rest_client.rest_post(endpoint, rdf_body, headers)
        if response.status_int == 404:
            raise ValueError("Site %s not found" % site)
        elif response.status_int == 201:
            return response.body_string()
        else:
            raise ValueError("Error Creating entity: %s " % response.body_string())

    def delete_entity(self, uri, site=None):
        """
        Delete an entity from the specified site. If site is None, it will try to be deleted from EntityHub cache
        :param uri: URI (ID) of the entity
        :param site: EntityHub site
        :return: Entity data as Entity Model
        """
        endpoint = self.__rest_client.endpoint + \
                   self.STANBOL_ENTITYHUB_PATH + "/"
        if site:
            endpoint += self.STANBOL_ENTITYHUB_SITE_PATH + "/" + site + "/"
        endpoint += "entity?id=" + uri

        headers = {
            'Accept': 'application/rdf+xml'
        }

        response = self.__rest_client.rest_delete(endpoint, headers=headers)
        if response.status_int == 404:
            raise ValueError("Entity with URI %s not found at site %s" % (uri, site))
        elif response.status_int == 200:
            if uri != '*':
                from pystanbol.parser import parse_entity_from_str
                return parse_entity_from_str(response.body_string("UTF-8"), 'xml', uri)
            else:
                return response.body_string()
        else:
            return None

    def delete_all_entities(self, site=None):
        """
        Clear an EntityHub site
        :param site: the site where all entities will be deleted
        :return: 
        """
        return self.delete_entity('*', site)
