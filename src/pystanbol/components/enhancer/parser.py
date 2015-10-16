from rdflib import Graph
from rdflib.namespace import RDF, DCTERMS
from pystanbol.FISE import FISE, ENTITY_HUB
from models import TextAnnotation, EntityAnnotation
from pystanbol.components.entityhub.models import Entity
from pystanbol.components.enhancer.client import EnhancerResult

def parseEnhancementStructure(strGraph, format):
    graph = Graph()
    graph.parse(data=strGraph, format=format)
    enhancements = {subject:parseEnhancement(graph, subject) for subject in graph.subjects(RDF.type, FISE.term('Enhancement'))}
    __processRelations(graph, enhancements)
    return EnhancerResult(graph, enhancements.values())

def __processRelations(graph, enhancements):
    for key in enhancements:
        relations = graph.objects(key, DCTERMS.relation)
        enhancement = enhancements[key]
        for relation in relations:
            enhancement._addRelation(enhancements[relation])


def parseEnhancement(graph, subject):
    types = graph.objects(subject, RDF.type)
    for type in types:
        if type == FISE.term("TextAnnotation"):
            return TextAnnotation(graph, subject)
        elif type == FISE.term("EntityAnnotation"):
            return EntityAnnotation(graph, subject, parseEntity(graph, subject))

    return None

def parseEntity(graph, subject):
    reference = graph.objects(subject, FISE.term('entity-reference')).next()
    if reference:
        triples = list(graph.triples((reference, None, None)))
        try:
            site = graph.objects(subject, ENTITY_HUB.site).next().value
        except StopIteration: # Some engines are not able to return site
            site = None

        return Entity(reference, site, triples)
    return None
