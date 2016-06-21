from rdflib.namespace import ClosedNamespace, Namespace
from rdflib import URIRef

FISE = ClosedNamespace(
    uri=URIRef("http://fise.iks-project.eu/ontology/"),
    terms=[
        "Enhancement", "EntityAnnotation", "TextAnnotation", "UserAnnotation",
        "extracted-from", "confidence", "entity-label", "entity-reference",
        "entity-type", "selected-text", "selection-context", "start", "end"
    ]
)

ENTITY_HUB = Namespace("http://stanbol.apache.org/ontology/entityhub/entityhub#")
