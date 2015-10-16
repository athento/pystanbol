from rdflib.namespace import DCTERMS
from pystanbol.FISE import FISE, ENTITY_HUB

class Enhancement:

    def __init__(self, graph, subject):
        """
        :type graph: Graph
        """
        self.__uri = subject
        self.__relations = []
        self.__created = graph.objects(subject, DCTERMS.created).next().value
        self.__creator = graph.objects(subject, DCTERMS.creator).next().value

    def __eq__(self, other):
        if isinstance(other, Enhancement):
            return self.__uri == other.uri
        else:
            return self.__uri == other

    def __hash__(self):
        return hash(self.__uri)

    def _addRelation(self, enhancement):
        self.__relations.append(enhancement)

    @property
    def relations(self):
        return self.__relations

    @relations.setter
    def relations(self, relations):
        self.__relations = relations

    @property
    def uri(self):
        return self.__uri

    @property
    def created(self):
        return self.__created

    @property
    def creator(self):
        return self.__creator

class Annotation(Enhancement):

    def __init__(self, graph, subject):
        Enhancement.__init__(self, graph, subject)
        self.__extractedFrom = graph.objects(subject, FISE.term("extracted-from")).next().toPython()
        self.__confidence = float(graph.objects(subject, FISE.term("confidence")).next().value)

    @property
    def extractedFrom(self):
        return self.__extractedFrom

    @property
    def confidence(self):
        return self.__confidence


class TextAnnotation(Annotation):

    def __init__(self, graph, subject):
        Annotation.__init__(self, graph, subject)
        try:
            self.__type = graph.objects(subject, DCTERMS.type).next().toPython()
        except StopIteration:
            self.__type = None
        try:
            self.__selectedText = graph.objects(subject, FISE.term('selected-text')).next().value
        except StopIteration:
            self.__selectedText = None
        try:
            self.__selectionContext = graph.objects(subject, FISE.term('selection-context')).next().value
        except StopIteration:
            self.__selectionContext = None
        try:
            self.__start = graph.objects(subject, FISE.term('start')).next().value
        except StopIteration:
            self.__start = None
        try:
            self.__end = graph.objects(subject, FISE.term('end')).next().value
        except StopIteration:
            self.__end = None
        try:
            self.__language = graph.objects(subject, DCTERMS.language).next().value
        except StopIteration:
            if self.__selectionContext:
                self.__language = graph.objects(subject, FISE.term('selection-context')).next().language
            else:
                self.__language = None


    @property
    def type(self):
        return self.__type

    @property
    def selectedText(self):
        return self.__selectedText

    @property
    def selectionContext(self):
        return self.__selectionContext

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def language(self):
        return self.__language


class EntityAnnotation(Annotation):

    def __init__(self, graph, subject, entity):
        Annotation.__init__(self, graph, subject)
        self.__entityLabel = graph.objects(subject, FISE.term('entity-label')).next().value
        self.__entityReference = graph.objects(subject, FISE.term('entity-reference')).next().toPython()
        try:
            self.__site = graph.objects(subject, ENTITY_HUB.site).next().value
        except StopIteration:
            self.__site = None
        types = graph.objects(subject, FISE.term('entity-type'))
        self.__entityTypes = [t.toPython() for t in types]
        self.__entity = entity

    @property
    def entityLabel(self):
        return self.__entityLabel

    @property
    def entityReference(self):
        return self.__entityReference

    @property
    def site(self):
        return self.__site

    @property
    def entityTypes(self):
        return self.__entityTypes

    @property
    def entity(self):
        return self.__entity