from pystanbol.client import StanbolClient
from rdflib import Graph, Literal, Namespace, RDF, URIRef, RDFS
from rdflib.namespace import FOAF
from pystanbol.components.entityhub.models import Entity
import pytest

class TestEntityHub():

    __STANBOL_ENDPOINT = "http://localhost:8080"

    def test_entityhub(self):
        client = StanbolClient(self.__STANBOL_ENDPOINT)
        entityhub = client.entityhub

        # Entity with rdflib
        g = Graph()
        uri_ref = URIRef('http://apache.stanbol.org/resource/1')
        g.add((uri_ref, RDF.type, FOAF.Person))
        g.add((uri_ref, FOAF.nick, Literal("donna", lang="en")))
        g.add((uri_ref, RDFS.label, Literal("Mary", lang="en")))
        rdf_body = g.serialize(format='xml')
        entityhub.create_or_update_entity(rdf_body)

        # Get Entity
        entity = entityhub.get_entity('http://apache.stanbol.org/resource/1')
        properties = entity.get_properties()
        assert len(properties) == 4
        assert properties['label'][0] == 'Mary'
        assert entity.get_types()[0].toPython().lower() == FOAF.person.toPython().lower()
        assert entity.values(FOAF.nick)[0].value == 'donna'
        assert entity.values(FOAF.nick)[0].language == 'en'

        # Delete Entity
        entityhub.delete_entity('http://apache.stanbol.org/resource/1')
        with pytest.raises(ValueError):
            entityhub.get_entity('http://apache.stanbol.org/resource/1')

        # Entity from Entity Model
        entity = Entity.empty_entity('http://apache.stanbol.org/resource/1')
        entity.add_property(RDF.type, FOAF.Person)
        entity.add_property(RDFS.label, Literal("Mary", lang="en"))
        entity.add_property('nick', Literal("donna", lang="en"), namespace=FOAF)
        entityhub.create_or_update_entity(entity)
        entity = entityhub.get_entity('http://apache.stanbol.org/resource/1')
        properties = entity.get_properties()
        assert len(properties) == 4
        assert properties['label'][0] == 'Mary'
        assert entity.get_types()[0].toPython().lower() == FOAF.person.toPython().lower()
        assert entity.values(FOAF.nick)[0].value == 'donna'
        assert entity.values(FOAF.nick)[0].language == 'en'
        entityhub.delete_entity('http://apache.stanbol.org/resource/1')


