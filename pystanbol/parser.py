from rdflib import Graph
from rdflib.resource import Resource
from rdflib.namespace import RDF, DCTERMS
from pystanbol.FISE import FISE, ENTITY_HUB
from pystanbol.components.enhancer.models import TextAnnotation, EntityAnnotation
from pystanbol.components.entityhub.models import Entity
from pystanbol.components.enhancer.client import EnhancerResult


def parse_enhancement_structure(strGraph, format):
    graph = Graph()
    graph.parse(data=strGraph, format=format)
    enhancements = {subject:parse_enhancement(graph, subject) for subject in graph.subjects(RDF.type, FISE.term('Enhancement'))}
    __process_relations(graph, enhancements)
    return EnhancerResult(graph, enhancements.values())


def __process_relations(graph, enhancements):
    for key in enhancements:
        relations = graph.objects(key, DCTERMS.relation)
        enhancement = enhancements[key]
        for relation in relations:
            enhancement._addRelation(enhancements[relation])


def parse_enhancement(graph, subject):
    types = graph.objects(subject, RDF.type)
    for type in types:
        if type == FISE.term("TextAnnotation"):
            return TextAnnotation(graph, subject)
        elif type == FISE.term("EntityAnnotation"):
            reference = graph.objects(subject, FISE.term('entity-reference')).next()
            return EntityAnnotation(graph, subject, parse_entity(graph, reference))

    return None


def parse_entity_from_str(str_rdf_entity, format, entity_uri=None):
    graph = Graph()
    graph.parse(data=str_rdf_entity, format=format)
    if not entity_uri:
        subjects = graph.subjects(None, None)
        subject = subjects[0]
    else:
        from rdflib import URIRef
        subject = URIRef(entity_uri)

    return parse_entity(graph, subject)


def parse_entity(graph, entity_reference):
    if entity_reference:
        triples = list(graph.triples((entity_reference, None, None)))
        try:
            site = graph.objects(entity_reference, ENTITY_HUB.site).next().value
        except StopIteration: # Some engines are not able to return site
            from rdflib import URIRef
            entity_uri = entity_reference.toPython()
            meta = entity_uri + ".meta"
            meta_ref = URIRef(meta)
            try:
                site = graph.objects(meta_ref, ENTITY_HUB.site).next().value
            except:
                site = None

        return Entity(Resource(graph, entity_reference), site, triples)
    return None
