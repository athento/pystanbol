from pystanbol.client import StanbolClient
from pystanbol.components.enhancer.parser import parseEnhancementStructure
import mock
import os

class TestEnhancer():

    __STANBOL_ENDPOINT = "http://fake.stanbol.com"
    __TEST_SENTENCE = "Paris is the capital of France"

    def test_enhancer_basic(self):
        client = StanbolClient(self.__STANBOL_ENDPOINT)
        enhancer = client.enhancer
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test1.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        enhancerResult = enhancer.enhance(self.__TEST_SENTENCE)
        assert len(enhancerResult.enhancements) == 9
        eas = enhancerResult.get_entity_annotations()
        assert len(eas) == 6
        enhancerResult.filterByConfidence(0.2)
        assert len(enhancerResult.get_entity_annotations()) == 5
        assert eas[0].site == "dbpedia"

        labels = [ea.entityLabel for ea in eas]
        assert "Paris" in labels
        assert "France" in labels

        enhancerResult.filterByConfidence(0.6)
        tas = enhancerResult.get_text_annotations()
        for ta in tas:
            eas = enhancerResult.get_entity_annotations(textannotation=ta)
            if len(eas) > 0:
                assert len(eas) == 1

        languages = enhancerResult.languages
        assert len(languages) == 1
        assert next(iter(languages)) == 'en'

    def test_enhancer_advanced(self):
        client = StanbolClient(self.__STANBOL_ENDPOINT)
        enhancer = client.enhancer
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test2.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        enhancerResult = enhancer.enhance(self.__TEST_SENTENCE, {})
        assert len(enhancerResult.get_text_annotations()) == 3
        bests = enhancerResult.get_best_annotations_map
        tas = bests.keys()
        paris = next(ta for ta in tas if ta.selectedText=='Paris')
        assert paris is not None
        assert paris.start == 0
        assert paris.end == 5

        ea = bests[paris]
        assert ea is not None
        from pystanbol.components.enhancer.models import EntityAnnotation
        assert isinstance(ea, EntityAnnotation)
        assert ea.entityReference == 'http://dbpedia.org/resource/Paris'

        assert enhancerResult.graph is not None

        eas = enhancerResult.get_entity_annotations(textannotation=paris)
        assert len(eas) == 3
        assert all(x in [ea.entityReference for ea in eas]
                            for x in ['http://dbpedia.org/resource/Paris',
                                      'http://dbpedia.org/resource/Paris_Commune'])

        assert len(enhancerResult.get_entities()) == 6
        parisEa = enhancerResult.get_entity_annotation('http://dbpedia.org/resource/Paris')
        assert parisEa.site == 'dbpedia'
        paris = enhancerResult.getEntity('http://dbpedia.org/resource/Paris')
        assert parisEa.site == paris.site
        assert parisEa.entityReference == paris.uri
        properties = paris.properties
        assert len(properties) != 0
        from rdflib.namespace import RDFS, RDF, FOAF
        assert all(x in properties for x in [RDFS.comment, RDF.type, FOAF.depiction])
        labels = paris.get_labels()
        assert len(labels) != 0
        assert len(paris.values(RDFS.label)) == len(labels)
        assert len(paris.values('http://www.w3.org/2000/01/rdf-schema#label')) == len(labels)
        assert len(paris.values('label', 'http://www.w3.org/2000/01/rdf-schema#')) == len(labels)
        assert paris.values(RDFS.label, language='es', localName=True)[0] == u'Par\xeds'
        assert next((x for x in labels if x.language == 'it' and x.value == 'Parigi'), None) is not None

        assert 'Paris' in paris.get_labels('en')

        types = paris.values(RDF.type, localName=True)
        assert 'Place' in types
        types = paris.get_types(True)
        assert 'Place' in types
        from rdflib import URIRef
        assert URIRef("http://dbpedia.org/ontology/Place") in paris.get_types()
        assert len(paris.get_categories()) == 0
        assert float(paris.values('http://www.w3.org/2003/01/geo/wgs84_pos#lat', localName=True)[0]) == 48.8567

        bests = enhancerResult.get_best_annotations
        assert len(bests) == 2

    def test_dereferencing(self):
        client = StanbolClient(self.__STANBOL_ENDPOINT)
        enhancer = client.enhancer
        fields = ["geo:long", "geo:lat", "foaf:depiction"]
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test3.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        enhancer_result_deref = enhancer.enhance(self.__TEST_SENTENCE, dereferencing_fields=fields)
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test4.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        enhancer_result = enhancer.enhance(self.__TEST_SENTENCE)
        bests = enhancer_result_deref.get_best_annotations
        paris_deref = next(ea for ea in bests if ea.entityReference=='http://dbpedia.org/resource/Paris')
        assert paris_deref is not None
        paris_deref = paris_deref.entity
        assert len(paris_deref.get_labels()) == 0
        bests2 = enhancer_result.get_best_annotations
        paris = next(ea for ea in bests2 if ea.entityReference=='http://dbpedia.org/resource/Paris')
        paris = paris.entity
        assert len(paris.get_labels()) != 0
        france = enhancer_result_deref.getEntity("http://dbpedia.org/resource/France")
        from rdflib.namespace import FOAF
        depictions = france.values(FOAF.depiction)
        assert len(depictions) == 2
        from rdflib import URIRef
        assert URIRef("http://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg") in depictions
        lats = france.values("lat", namespace="http://www.w3.org/2003/01/geo/wgs84_pos#", localName=True)
        assert 47.0 in lats
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test5.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        fields = ["http://www.w3.org/2003/01/geo/wgs84_pos#long",
                  "http://www.w3.org/2003/01/geo/wgs84_pos#lat",
                  "foaf:depiction"]
        enhancer_result_deref = enhancer.enhance(self.__TEST_SENTENCE, dereferencing_fields=fields)
        france = enhancer_result_deref.getEntity("http://dbpedia.org/resource/France")
        lats = france.values("lat", namespace="http://www.w3.org/2003/01/geo/wgs84_pos#", localName=True)
        assert 47.0 in lats
        # Helpers
        from pystanbol import helpers
        fields_by_entities = helpers.get_fields_by_entity(bests, fields)
        france_fields = fields_by_entities["http://dbpedia.org/resource/France"]
        assert 47.0 in lats


    def test_ldpath(self):
        client = StanbolClient(self.__STANBOL_ENDPOINT)
        enhancer = client.enhancer
        prefixes = {'geo':'http://www.w3.org/2003/01/geo/wgs84_pos#',
                    'custom':'http://ldpath/custom#'}
        fields = {'foaf:depiction': 'foaf:depiction :: xsd:string',
                  'custom:location':'fn:concat("[",geo:lat,",",geo:long,"]") :: xsd:string'}
        ldpath = {enhancer.ENHANCER_LDPATH_PREFIXES:prefixes,
                  enhancer.ENHANCER_LDPATH_FIELDS:fields}
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test6.rdf")
        f = open(file_path)
        txt = f.read()
        f.close()
        enhancer.enhance = mock.MagicMock(return_value=parseEnhancementStructure(txt, 'turtle'))
        result = enhancer.enhance(self.__TEST_SENTENCE, ldpath=ldpath)
        france = result.getEntity("http://dbpedia.org/resource/France")
        location = france.values("location", namespace="http://ldpath/custom#", localName=True)[0]
        assert location == "[48.85666747.0,2.35083342.0]"
        from rdflib.namespace import FOAF
        depics = france.values("depiction", namespace=FOAF)
        assert len(depics) == 4
        # Helpers
        from pystanbol import helpers
        ldpath_by_entities = helpers.get_ldpath_fields_by_entity(result.get_best_annotations, prefixes, fields)
        france_fields = ldpath_by_entities["http://dbpedia.org/resource/France"]
        assert "[48.85666747.0,2.35083342.0]" in france_fields
