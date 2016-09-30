# -*- coding: utf-8 -*-
import json
import unittest

from extruct.rdfa import RDFaExtractor
from tests import get_testdata





class TestRDFa(unittest.TestCase):

    maxDiff = None

    def assertItemsEqual(self, a, b):
        json_kwargs = dict(indent=2, separators=(',', ': '), sort_keys=True, ensure_ascii=True)
        sa = set(json.dumps(i, **json_kwargs) for i in a['items'])
        sb = set(json.dumps(i, **json_kwargs) for i in b['items'])
        self.assertEqual(sa, sb)

    def test_example(self):
        sample = '''
<body prefix="foaf: http://xmlns.com/foaf/0.1/
                  schema: http://schema.org/
                  dcterms: http://purl.org/dc/terms/">
   <div resource="http://example.org/bob#me" typeof="foaf:Person">
     <p>
       Bob knows <a property="foaf:knows" href="http://example.org/alice#me">Alice</a>
       and was born on the <time property="schema:birthDate" datatype="xsd:date">1990-07-04</time>.
     </p>
     <p>
       Bob is interested in <span property="foaf:topic_interest"
       resource="http://www.wikidata.org/entity/Q12418">the Mona Lisa</span>.
     </p>
   </div>
   <div resource="http://www.wikidata.org/entity/Q12418">
     <p>
       The <span property="dcterms:title">Mona Lisa</span> was painted by
       <a property="dcterms:creator" href="http://dbpedia.org/resource/Leonardo_da_Vinci">Leonardo da Vinci</a>
       and is the subject of the video
       <a href="http://data.europeana.eu/item/04802/243FA8618938F4117025F17A8B813C5F9AA4D619">'La Joconde &agrave; Washington'</a>.
     </p>
   </div>
   <div resource="http://data.europeana.eu/item/04802/243FA8618938F4117025F17A8B813C5F9AA4D619">
       <link property="dcterms:subject" href="http://www.wikidata.org/entity/Q12418"/>
   </div>
 </body>
'''
        from pprint import pprint
        rdfa = RDFaExtractor()
        data = rdfa.extract(sample)
        #pprint(data)
        expected = {
            'items': [{u'@id': u'http://www.wikidata.org/entity/Q12418',
                      u'http://purl.org/dc/terms/creator': [{u'@id': u'http://dbpedia.org/resource/Leonardo_da_Vinci'}],
                      u'http://purl.org/dc/terms/title': [{u'@value': u'Mona Lisa'}]},
                     {u'@id': u'http://data.europeana.eu/item/04802/243FA8618938F4117025F17A8B813C5F9AA4D619',
                      u'http://purl.org/dc/terms/subject': [{u'@id': u'http://www.wikidata.org/entity/Q12418'}]},
                     {u'@id': u'http://example.org/bob#me',
                      u'@type': [u'http://xmlns.com/foaf/0.1/Person'],
                      u'http://schema.org/birthDate': [{u'@type': u'http://www.w3.org/2001/XMLSchema#date',
                                                        u'@value': u'1990-07-04'}],
                      u'http://xmlns.com/foaf/0.1/knows': [{u'@id': u'http://example.org/alice#me'}],
                      u'http://xmlns.com/foaf/0.1/topic_interest': [{u'@id': u'http://www.wikidata.org/entity/Q12418'}]}]
        }
        self.assertItemsEqual(data, expected)

