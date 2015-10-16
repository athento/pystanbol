from models import EntityAnnotation, TextAnnotation

class Enhancer():

    OUTPUTFORMAT = {
        'jsonld':'application/json',
        'xml':'application/rdf+xml',
        'rdfjson':'application/rdf+json',
        'nt' :'text/rdf+nt',
        'turtle':'text/turtle',
    }

    STANBOL_ENHANCER_PATH = "enhancer"
    STANBOL_CHAIN_PATH = "chain"
    STANBOL_DEFAULT_CHAIN = "default"

    ENHANCER_CHAIN = "chain"
    ENHANCER_FORMAT = "format"
    ENHANCER_DEREFERENCING_FIELDS = "fields"
    ENHANCER_LDPATH_PREFIXES = "prefixes"
    ENHANCER_LDPATH_FIELDS = "ldpath"

    __ENHANCER_DEFAULT_FORMAT = 'turtle'

    __ENHANCER_PARAM_LDPATH = "enhancer.engines.dereference.ldpath"
    __ENHANCER_PARAM_DEREF_FIELDS = "enhancer.engines.dereference.fields"

    def __init__(self, rest_client):
        self.__rest_client = rest_client
        """:type : RestClient"""

    def enhance(self, content, parameters={}):
        import urllib
        import parser

        enhancer_endpoint = self.__rest_client.endpoint + self.STANBOL_ENHANCER_PATH

        if self.ENHANCER_CHAIN in parameters:
            enhancer_endpoint += "/" + self.STANBOL_CHAIN_PATH + "/" + parameters[self.ENHANCER_CHAIN]

        deref_fields = False
        if self.ENHANCER_DEREFERENCING_FIELDS in parameters:
            fields = parameters[self.ENHANCER_DEREFERENCING_FIELDS]
            if isinstance(fields, dict):
                fields = fields.values()
                if len(fields) > 0:
                    deref_fields = True
                    for i, field in enumerate(fields):
                        if i == 0:
                            enhancer_endpoint += "?"
                        else:
                            enhancer_endpoint += "&"
                        enhancer_endpoint += self.__ENHANCER_PARAM_DEREF_FIELDS + "=" + urllib.quote(field)

        if self.ENHANCER_LDPATH_FIELDS in parameters:
            ldpath = self.__build_ldpath(parameters.get(self.ENHANCER_LDPATH_PREFIXES),
                                         parameters[self.ENHANCER_LDPATH_FIELDS])
            if ldpath and len(ldpath) > 0:
                if deref_fields:
                    enhancer_endpoint += "&"
                else:
                    enhancer_endpoint += "?"
                enhancer_endpoint += self.__ENHANCER_PARAM_LDPATH + "=" + urllib.quote(ldpath)

        headers = {'Content-Type':'text/plain'}
        if self.ENHANCER_FORMAT in parameters:
            headers['Accept'] = self.OUTPUTFORMAT[parameters[self.ENHANCER_FORMAT]]
            format = parameters[self.ENHANCER_FORMAT]
        else:
            headers['Accept'] = self.OUTPUTFORMAT[self.__ENHANCER_DEFAULT_FORMAT]
            format = self.__ENHANCER_DEFAULT_FORMAT

        response = self.__rest_client.rest_post(enhancer_endpoint, content, headers)
        return parser.parseEnhancementStructure(response.body_string("UTF-8"), format)

    @staticmethod
    def __build_ldpath(prefixes, fields):
        ldpath = ""
        if isinstance(prefixes, dict):
            for key, value in prefixes.iteritems():
                ldpath += "@prefix " + key + ":<" + value + ">;"
        if isinstance(fields, dict):
            for key, value in fields.iteritems():
                ldpath += key + "=" + value + ";"
        return ldpath


class EnhancerResult:

    def __init__(self, graph, enhancements):
        self.__graph = graph
        self.__enhancements = enhancements

    @property
    def enhancements(self):
        return self.__enhancements

    @property
    def graph(self):
        return self.__graph

    @property
    def languages(self):
        return list(set([ta.language for ta in self.get_text_annotations()]))

    def get_text_annotations(self, confidence=0.0):
        return [e for e in self.enhancements if isinstance(e, TextAnnotation) and e.confidence > confidence]

    def get_entity_annotations(self, textannotation=None, confidence=0.0):
        if not textannotation:
            return [e for e in self.enhancements if isinstance(e, EntityAnnotation) and e.confidence > confidence]
        else:
            return [e for e in self.enhancements if isinstance(e, EntityAnnotation) and e.confidence > confidence and textannotation in e.relations]

    def get_entity_annotation(self, entity_uri):
        return next(e for e in self.enhancements if isinstance(e, EntityAnnotation) and e.entity.uri == entity_uri)


    def get_entities(self, confidence=0.0):
        return [e.entity for e in self.enhancements if isinstance(e, EntityAnnotation) and e.confidence >= confidence]

    def get_enhancement(self, uri):
        return next(e for e in self.enhancements if e.uri == uri), None

    def removeEnhancement(self, uri):
        self.graph.remove((uri, None, None))
        self.graph.remove((None, None, uri))
        self.enhancements.remove(uri)

    def getEntity(self, uri):
        return next(e.entity for e in self.enhancements if isinstance(e, EntityAnnotation) and e.entityReference == uri)

    def filterByConfidence(self, confidenceThreshold):
        toremove = [e.uri for e in self.enhancements if isinstance(e, EntityAnnotation) and e.confidence < confidenceThreshold]
        for uri in toremove:
            self.removeEnhancement(uri)

    def get_annotations_map(self):
        eas = self.get_entity_annotations()
        result = {}
        for ea in eas:
            for relation in ea.relations:
                if isinstance(relation, TextAnnotation):
                    result.setdefault(relation, []).append(ea)
        return result

    @property
    def get_best_annotations_map(self):
        from operator import attrgetter
        annotations_map = self.get_annotations_map()
        for ta in annotations_map:
            annotations_map[ta] = max(annotations_map[ta], key=attrgetter('confidence'))
        return annotations_map

    @property
    def get_best_annotations(self):
        return self.get_best_annotations_map.values()
