from rdflib.namespace import RDF, RDFS, DCTERMS
from rdflib.namespace import Namespace
from rdflib.namespace import split_uri


class Entity:

    def __init__(self, reference, site, graph):
        self.__reference = reference
        self.__site = site
        self.__graph = graph

    @classmethod
    def empty_entity(cls, uri):
        from rdflib import Graph, URIRef
        from rdflib.resource import Resource
        ref = URIRef(uri)
        g = Graph()
        reference = Resource(g, ref)
        return cls(reference, None, g)

    @property
    def site(self):
        return self.__site

    @property
    def uri(self):
        return self.__reference.identifier.toPython()

    @property
    def graph(self):
        return self.__graph

    def get_labels(self, language=None):
        if not language:
            return [o for s,p,o in self.__graph if p == RDFS.label]
        else:
            return [o.value for s,p,o in self.__graph if p == RDFS.label and o.language == language]

    def get_categories(self):
        return [o for s,p,o in self.__graph if p == DCTERMS.subject]

    def get_types(self, localName=False):
        if not localName:
            return [o for s,p,o in self.__graph if p == RDF.type]
        else:
            return [split_uri(o)[1] for s,p,o in self.__graph if p == RDF.type]

    def get_descriptions(self, language=None):
        if not language:
            return [o for s,p,o in self.__graph if p == RDFS.comment]
        else:
            return [o.value for s,p,o in self.__graph if p == RDFS.comment and o.language == language]

    def values(self, property, namespace=None, language=None, localName=False):
        from rdflib import URIRef
        if not isinstance(property, URIRef):
            if namespace:
                n = Namespace(namespace)
                predicate = n.term(property)
            else:
                predicate = URIRef(property)
        else:
            predicate = property

        if language:
            result = [o for s,p,o in self.__graph if p == predicate and o.language == language]
        else:
            result = [o for s,p,o in self.__graph if p == predicate]

        if localName:
            from rdflib import Literal
            aux = []
            for x in result:
                if isinstance(x, Literal):
                    aux.append(x.value)
                else:
                    aux.append(split_uri(x)[1])
            result = aux

        return result

    def get_properties(self, local_name=True):
        result = {}
        from rdflib import Literal
        for s,p,o in self.__graph:
            if local_name:
                key = split_uri(p)[1]
            else:
                key = p
            if not key in result:
                result[key] = []

            if isinstance(o, Literal):
                result[key].append(o.value)
            else:
                if local_name:
                    try:
                        result[key].append(split_uri(o)[1])
                    except:
                        result[key].append(o.toPython())
                else:
                    result[key].append(o.toPython())

        return result

    def add_property(self, property, value, namespace=None):
        from rdflib import URIRef, Literal
        if isinstance(value, str) or isinstance(value, unicode):
            value = Literal(value)
        if isinstance(property, URIRef):
            self.__graph.add((self.__reference.identifier, property, value))
        elif isinstance(property, str):
            if isinstance(namespace, Namespace):
                predicate = namespace.term(property)
            else:
                n = Namespace(namespace)
                predicate = n.term(property)

            self.__graph.add((self.__reference.identifier, predicate, value))

    @property
    def properties(self):
        return set([p for s,p,o in self.__graph])
