import unittest

import extruct
from extruct.uniform import _flatten, infer_context, flatten_dict, _uopengraph
from tests import get_testdata


class TestUniform(unittest.TestCase):

    maxDiff = None

    def test_uopengraph(self):
        expected = [{"@context": {
                        "og": "http://ogp.me/ns#",
                        "fb": "http://www.facebook.com/2008/fbml",
                        "concerts": "http://ogp.me/ns/fb/songkick-concerts#"
                    },
                    "fb:app_id": "308540029359",
                    "og:site_name": "Songkick",
                    "@type": "songkick-concerts:artist",
                    "og:title": "Elysian Fields",
                    "og:description": "Buy tickets for an upcoming Elysian Fields concert near you. List of all Elysian Fields tickets and tour dates for 2017.",
                    "og:url": "http://www.songkick.com/artists/236156-elysian-fields",
                    "og:image": "http://images.sk-static.com/images/media/img/col4/20100330-103600-169450.jpg",
                }]
        body = get_testdata('songkick', 'elysianfields.html')
        data = extruct.extract(body, syntaxes=['opengraph'], uniform=True)
        self.assertEqual(data['opengraph'], expected)

    def test_uopengraph_with_og_array(self):
        expected = [{"@context": {
                        "og": "http://ogp.me/ns#",
                        "fb": "http://www.facebook.com/2008/fbml",
                        "concerts": "http://ogp.me/ns/fb/songkick-concerts#"
                    },
                    "fb:app_id": "308540029359",
                    "og:site_name": "Songkick",
                    "@type": "songkick-concerts:artist",
                    "og:title": "Elysian Fields",
                    "og:description": "Buy tickets for an upcoming Elysian Fields concert near you. List of all Elysian Fields tickets and tour dates for 2017.",
                    "og:url": "http://www.songkick.com/artists/236156-elysian-fields",
                    "og:image": [ "http://images.sk-static.com/images/media/img/col4/20100330-103600-169450.jpg",
                                  "http://images.sk-static.com/SECONDARY_IMAGE.jpg"],
                }]
        body = get_testdata('songkick', 'elysianfields.html')
        data = extruct.extract(body, syntaxes=['opengraph'], uniform=True, with_og_array=True)
        self.assertEqual(data['opengraph'], expected)

    def test_uopengraph_duplicated_priorities(self):
        # Ensures that first seen property is kept when flattening
        data = _uopengraph([{'properties':
                                 [('prop_{}'.format(k), 'value_{}'.format(v))
                                  for k in range(5)
                                  for v in range(5)],
                             'namespace': 'namespace'}])
        for k in range(5):
            assert data[0]['prop_{}'.format(k)] == 'value_0'

        # Ensures that empty is not returned if a property contains any
        # non empty value
        data = _uopengraph([{'properties':
                                 [('prop_empty', ' '),

                                  ('prop_non_empty', ' '),
                                  ('prop_non_empty', 'value!'),

                                  ('prop_non_empty2', 'value!'),
                                  ('prop_non_empty2', ' '),

                                  ('prop_non_empty3', ' '),
                                  ('prop_non_empty3', 'value!'),
                                  ('prop_non_empty3', 'other value'),
                                  ],
                             'namespace': 'namespace'}])
        assert data[0]['prop_empty'] == ' '
        assert data[0]['prop_non_empty'] == 'value!'
        assert data[0]['prop_non_empty2'] == 'value!'
        assert data[0]['prop_non_empty3'] == 'value!'

    def test_uopengraph_duplicated_with_og_array(self):
        # Ensures that first seen property is kept when flattening
        data = _uopengraph([{'properties':
                                 [('prop_{}'.format(k), 'value_{}'.format(v))
                                  for k in range(5)
                                  for v in range(5)],
                             'namespace': 'namespace'}], with_og_array=True)
        for k in range(5):
            assert data[0]['prop_{}'.format(k)] == ['value_0', 'value_1', 'value_2', 'value_3', 'value_4']

        # Ensures that empty is not returned if a property contains any
        # non empty value
        data = _uopengraph([{'properties':
                                 [('prop_empty', ' '),

                                  ('prop_non_empty', ' '),
                                  ('prop_non_empty', 'value!'),

                                  ('prop_non_empty2', 'value!'),
                                  ('prop_non_empty2', ' '),

                                  ('prop_non_empty3', ' '),
                                  ('prop_non_empty3', 'value!'),
                                  ('prop_non_empty3', 'other value'),
                                  ],
                             'namespace': 'namespace'}], with_og_array=True)
        assert data[0]['prop_empty'] == ' '
        assert data[0]['prop_non_empty'] == 'value!'
        assert data[0]['prop_non_empty2'] == 'value!'
        assert data[0]['prop_non_empty3'] == ['value!', 'other value']

    def test_umicroformat(self):
        expected = [ { '@context': 'http://microformats.org/wiki/',
                     '@type': ['h-hidden-phone', 'h-hidden-tablet'],
                     'name': ['']},
                   { '@context': 'http://microformats.org/wiki/',
                     '@type': ['h-hidden-phone'],
                     'children': [ { '@type': [ 'h-hidden-phone',
                                                'h-hidden-tablet'],
                                     'name': ['']},
                                   { '@type': ['h-hidden-phone'],
                                     'name': [ 'aJ Styles FastLane 2018 15 x '
                                               '17 Framed Plaque w/ Ring '
                                               'Canvas'],
                                     'photo': [ '/on/demandware.static/-/Sites-main/default/dwa3227ee6/images/small/CN1148.jpg']}],
                   },
                   { '@context': 'http://microformats.org/wiki/',
                     '@type': ['h-entry'],
                     'author': [ { '@type': ['h-card'],
                                   'name': ['W. Developer'],
                                   'url': ['http://example.com'],
                                   'value': 'W. Developer'}],
                     'content': [ { 'html': '<p>Blah blah blah</p>',
                                    'value': 'Blah blah blah'}],
                     'name': ['Microformats are amazing'],
                     'published': ['2013-06-13 12:00:00'],
                     'summary': [ 'In which I extoll the virtues of using '
                                  'microformats.']}]
        body = get_testdata('misc', 'microformat_test.html')
        data = extruct.extract(body, syntaxes=['microformat'], uniform=True)
        self.assertEqual(data['microformat'], expected)

    def test_umicrodata(self):
        expected = [{ "@context": "http://schema.org",
                      "@type": "Product",
                      "brand": "ACME",
                      "name": "Executive Anvil",
                      "image": "anvil_executive.jpg",
                      "description": "Sleeker than ACME's Classic Anvil, the Executive Anvil is perfect for the business traveler looking for something to drop from a height.",
                      "mpn": "925872",
                      "aggregateRating": {
                          "@type": "AggregateRating",
                          "ratingValue": "4.4",
                          "reviewCount": "89"},
                      "offers": {
                          "@type": "Offer",
                          "priceCurrency": "USD",
                          "price": "119.99",
                          "priceValidUntil": "2020-11-05",
                          "seller": {"@type": "Organization",
                                     "name": "Executive Objects"},
                          "itemCondition": "http://schema.org/UsedCondition",
                          "availability": "http://schema.org/InStock"
                          }}]
        body = get_testdata('misc', 'product_microdata.html')
        data = extruct.extract(body, syntaxes=['microdata'], uniform=True)
        self.assertEqual(data['microdata'], expected)


    def test_infer_context(self):
        context = 'http://schema.org/UsedCondition'
        self.assertEqual(infer_context(context), ('http://schema.org', 'UsedCondition'))

        context = 'http://ogp.me/ns#description'
        self.assertEqual(infer_context(context), ('http://ogp.me/ns', 'description'))

        context = 'http://ogp.me/ns/fb#app_id'
        self.assertEqual(infer_context(context), ('http://ogp.me/ns/fb', 'app_id'))

    def test_flatten_dict(self):
        d = {"type": "SPANISH INQUISITION",
             "properties": { "chief_weapon": "surprise",
                             "extra_weapon": "fear",
                             "another_one": "ruthless efficiency"}}
        expected = {"@type": "SPANISH INQUISITION",
                    "@context": "http://schema.org",
                    "chief_weapon": "surprise",
                    "extra_weapon": "fear",
                    "another_one": "ruthless efficiency"}
        self.assertEqual(flatten_dict(d, schema_context='http://schema.org', add_context=True), expected)


    def test_flatten(self):
        d = { 'children': [ { 'properties': {'name': ['']},
                                             'type': [ 'h-hidden-tablet',
                                                       'h-hidden-phone']},
                            { 'properties': { 'name': [ 'aJ Styles '
                                                        'FastLane 2018 '
                                                        '15 x 17 Framed '
                                                        'Plaque w/ Ring '
                                                        'Canvas'],
                                              'photo': [ 'path.jpg']},
                              'type': ['h-hidden-phone']}],
              'properties': {'name': ['']},
              'type': ['h-hidden-phone']}
        expected = { 'children': [ { 'name': [''],
                                     '@type': [ 'h-hidden-tablet',
                                                'h-hidden-phone']},
                                   { 'name': [ 'aJ Styles '
                                               'FastLane 2018 '
                                               '15 x 17 Framed '
                                               'Plaque w/ Ring '
                                               'Canvas'],
                                    'photo': [ 'path.jpg'],
                                    '@type': ['h-hidden-phone']}],
                    'name': [''],
                    '@type': ['h-hidden-phone']}
        self.assertEqual(_flatten(d, schema_context='http://schema.org'), expected)
