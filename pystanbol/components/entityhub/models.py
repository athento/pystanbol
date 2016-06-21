from rdflib.namespace import RDF, RDFS, DCTERMS
from rdflib.namespace import Namespace
from rdflib.namespace import split_uri

class Entity:

    def __init__(self, uri, site, triples):
        self.__uri = uri
        self.__site = site
        self.__triples = triples


    @property
    def site(self):
        return self.__site

    @property
    def uri(self):
        return self.__uri.toPython()

    def get_labels(self, language=None):
        if not language:
            return [o for s,p,o in self.__triples if p == RDFS.label]
        else:
            return [o.value for s,p,o in self.__triples if p == RDFS.label and o.language == language]

    def get_categories(self):
        return [o for s,p,o in self.__triples if p == DCTERMS.subject]

    def get_types(self, localName=False):
        if not localName:
            return [o for s,p,o in self.__triples if p == RDF.type]
        else:
            return [split_uri(o)[1] for s,p,o in self.__triples if p == RDF.type]

    def get_descriptions(self, language=None):
        if not language:
            return [o for s,p,o in self.__triples if p == RDFS.comment]
        else:
            return [o.value for s,p,o in self.__triples if p == RDFS.comment and o.language == language]

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
            result = [o for s,p,o in self.__triples if p == predicate and o.language == language]
        else:
            result = [o for s,p,o in self.__triples if p == predicate]

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

    def setProperty(self, namespace, property, value):
        if isinstance(namespace, Namespace):
            predicate = namespace.term(property)
        else:
            n = Namespace(namespace)
            predicate = n.term(property)

        from itertools import chain
        chain(self.__triples, [(self.uri, predicate, value)])


    @property
    def properties(self):
        return set([p for s,p,o in self.__triples])
