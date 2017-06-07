=======
extruct
=======

.. image:: https://img.shields.io/travis/scrapinghub/extruct/master.svg
    :target: https://travis-ci.org/scrapinghub/extruct

.. image:: https://img.shields.io/codecov/c/github/scrapinghub/extruct/master.svg?maxAge=2592000
    :target: https://codecov.io/gh/scrapinghub/extruct


*extruct* is a library for extracting embedded metadata from HTML markup.

It also has a built-in HTTP server to test its output as JSON.

Currently, *extruct* supports:

- `W3C's HTML Microdata`_
- `embedded JSON-LD`_
- (experimental) `RDFa`_ via `rdflib`_

.. _W3C's HTML Microdata: http://www.w3.org/TR/microdata/
.. _embedded JSON-LD: http://www.w3.org/TR/json-ld/#embedding-json-ld-in-html-documents
.. _RDFa: https://www.w3.org/TR/html-rdfa/
.. _rdflib: https://pypi.python.org/pypi/rdflib/

The microdata algorithm is a revisit of `this Scrapinghub blog post`_ showing how to use EXSLT extensions.

.. _this Scrapinghub blog post: http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/

Roadmap
-------

- support for `Complex Object Properties`_ within `Open Graph protocol <ogp>`_)

.. _Complex Object Properties: https://developers.facebook.com/docs/sharing/opengraph/object-properties#complex
.. _ogp: http://ogp.me/#metadata


Installation
------------

::

    pip install extruct


Usage
-----

All-in-one extraction
+++++++++++++++++++++

The simplest example how to use extruct is to call ``extruct.extract(htmlstring, url)``
with some HTML string and a URL.

Let's try this on a page on eBay which uses microdata and RDFa (with `ogp`_).

First fetch the HTML using python-requests and then feed the response body to ``extruct``::

    >>> import requests
    >>> from pprint import pprint

    >>> r = requests.get('http://www.ebay.com/itm/HERBERT-TERRY-2-STEP-ANGLEPOISE-LAMP-MODEL1227-/282478964487')

    >>> import extruct
    >>> data = extruct.extract(r.text, r.url)

    >>> pprint(data)
    {'json-ld': [],
     'microdata': [{'properties': {'image': ['http://i.ebayimg.com/images/g/0M4AAOSwT-FZBeOQ/s-l300.jpg',
                                             'http://i.ebayimg.com/images/g/0M4AAOSwT-FZBeOQ/s-l300.jpg'],
                                   'name': 'Details about  \xa0HERBERT TERRY 2 '
                                           'STEP ANGLEPOISE LAMP MODEL1227',
                                   'offers': {'properties': {'areaServed': 'United '
                                                                           'Kingdom '
                                                                           'and '
                                                                           'many '
                                                                           'other '
                                                                           'countries \n'
                                                                           '\t\t\t\t\t\t'
                                                                           '|  See '
                                                                           'details',
                                                             'availability': 'http://schema.org/InStock',
                                                             'availableAtOrFrom': 'Stockport, '
                                                                                  'United '
                                                                                  'Kingdom',
                                                             'itemCondition': '--not '
                                                                              'specified',
                                                             'price': '150.0',
                                                             'priceCurrency': 'GBP'},
                                              'type': 'http://schema.org/Offer'}},
                    'type': 'http://schema.org/Product'},
                   {'properties': {'itemListElement': [{'properties': {'item': 'http://www.ebay.com/sch/Antiques-/20081/i.html',
                                                                       'name': 'Antiques',
                                                                       'position': '1'},
                                                        'type': 'http://schema.org/ListItem'},
                                                       (...)
                                                       {'properties': {'item': 'http://www.ebay.com/sch/20th-Century-/66861/i.html',
                                                                       'name': '20th '
                                                                               'Century',
                                                                       'position': '4'},
                                                        'type': 'http://schema.org/ListItem'}]},
                    'type': 'http://schema.org/BreadcrumbList'}],
     'rdfa': [{'@id': 'http://www.ebay.com/itm/HERBERT-TERRY-2-STEP-ANGLEPOISE-LAMP-MODEL1227-/282478964487#w1-31-_topHelpTxt',
               'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#button'}]},
              (...)
              {'@id': 'http://www.ebay.com/itm/HERBERT-TERRY-2-STEP-ANGLEPOISE-LAMP-MODEL1227-/282478964487',
               'http://opengraphprotocol.org/schema/description': [{'@value': 'On '
                                                                              'one '
                                                                              'side '
                                                                              'of '
                                                                              'the '
                                                                              'base '
                                                                              'is '
                                                                              'a '
                                                                              'metal '
                                                                              'label '
                                                                              'from '
                                                                              'UMIST, '
                                                                              'where '
                                                                              'it '
                                                                              'was '
                                                                              'in '
                                                                              'use. '
                                                                              '| '
                                                                              'eBay!'}],
               'http://opengraphprotocol.org/schema/image': [{'@value': 'http://i.ebayimg.com/images/i/282478964487-0-1/s-l1000.jpg'}],
               'http://opengraphprotocol.org/schema/site_name': [{'@value': 'eBay'}],
               'http://opengraphprotocol.org/schema/title': [{'@value': 'HERBERT '
                                                                        'TERRY 2 '
                                                                        'STEP '
                                                                        'ANGLEPOISE '
                                                                        'LAMP '
                                                                        'MODEL1227  '
                                                                        '| eBay'}],
               'http://opengraphprotocol.org/schema/type': [{'@value': 'ebay-objects:item'}],
               'http://opengraphprotocol.org/schema/url': [{'@value': 'http://www.ebay.com/itm/HERBERT-TERRY-2-STEP-ANGLEPOISE-LAMP-MODEL1227-/282478964487'}],
               'http://www.facebook.com/2008/fbmlapp_id': [{'@value': '102628213125203'}]},
              {'@id': '_:Na28391785e4e48bb92849fccbe758c6b',
               'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#button'}]},
              (...)
              {'@id': 'http://www.ebay.com/itm/HERBERT-TERRY-2-STEP-ANGLEPOISE-LAMP-MODEL1227-/282478964487#glbfooter',
               'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#contentinfo'}]}]}


Another example with a page from SongKick containing RDFa and JSON-LD metadata::

    >>> r = requests.get('http://www.songkick.com/artists/236156-elysian-fields')

    >>> data = extruct.extract(r.text, r.url)

    >>> pprint(data)
    {'json-ld': [{'@context': 'http://schema.org',
                  '@type': 'MusicEvent',
                  'location': {'@type': 'Place',
                               'address': {'@type': 'PostalAddress',
                                           'addressCountry': 'US',
                                           'addressLocality': 'Brooklyn',
                                           'addressRegion': 'NY',
                                           'postalCode': '11225',
                                           'streetAddress': '497 Rogers Ave'},
                               'geo': {'@type': 'GeoCoordinates',
                                       'latitude': 40.660109,
                                       'longitude': -73.953193},
                               'name': 'The Owl Music Parlor',
                               'sameAs': 'http://www.theowl.nyc'},
                  'name': 'Elysian Fields',
                  'performer': [{'@type': 'MusicGroup',
                                 'name': 'Elysian Fields',
                                 'sameAs': 'http://www.songkick.com/artists/236156-elysian-fields?utm_medium=organic&utm_source=microformat'}],
                  'startDate': '2017-06-10T19:30:00-0400',
                  'url': 'http://www.songkick.com/concerts/30173984-elysian-fields-at-owl-music-parlor?utm_medium=organic&utm_source=microformat'},
                 (...)
                 {'@context': 'http://schema.org',
                  '@type': 'MusicGroup',
                  'image': 'https://images.sk-static.com/images/media/profile_images/artists/236156/card_avatar',
                  'interactionCount': '5557 UserLikes',
                  'logo': 'https://images.sk-static.com/images/media/profile_images/artists/236156/card_avatar',
                  'name': 'Elysian Fields',
                  'url': 'http://www.songkick.com/artists/236156-elysian-fields?utm_medium=organic&utm_source=microformat'}],
     'microdata': [],
     'rdfa': [{'@id': 'http://www.songkick.com/artists/236156-elysian-fields',
               'al:ios:app_name': [{'@value': 'Songkick Concerts'}],
               'al:ios:app_store_id': [{'@value': '438690886'}],
               'al:ios:url': [{'@value': 'songkick://artists/236156-elysian-fields'}],
               'http://ogp.me/ns#description': [{'@value': 'Buy tickets for an '
                                                           'upcoming Elysian '
                                                           'Fields concert near '
                                                           'you. List of all '
                                                           'Elysian Fields tickets '
                                                           'and tour dates for '
                                                           '2017.'}],
               'http://ogp.me/ns#image': [{'@value': 'http://images.sk-static.com/images/media/img/col4/20100330-103600-169450.jpg'}],
               'http://ogp.me/ns#site_name': [{'@value': 'Songkick'}],
               'http://ogp.me/ns#title': [{'@value': 'Elysian Fields'}],
               'http://ogp.me/ns#type': [{'@value': 'songkick-concerts:artist'}],
               'http://ogp.me/ns#url': [{'@value': 'http://www.songkick.com/artists/236156-elysian-fields'}],
               'http://www.facebook.com/2008/fbmlapp_id': [{'@value': '308540029359'}]}]}


You can also use each extractor individually. See below.

Microdata extraction
++++++++++++++++++++

::

    >>> from pprint import pprint
    >>>
    >>> from extruct.w3cmicrodata import MicrodataExtractor
    >>>
    >>> # example from http://www.w3.org/TR/microdata/#associating-names-with-items
    >>> html = """<!DOCTYPE HTML>
    ... <html>
    ...  <head>
    ...   <title>Photo gallery</title>
    ...  </head>
    ...  <body>
    ...   <h1>My photos</h1>
    ...   <figure itemscope itemtype="http://n.whatwg.org/work" itemref="licenses">
    ...    <img itemprop="work" src="images/house.jpeg" alt="A white house, boarded up, sits in a forest.">
    ...    <figcaption itemprop="title">The house I found.</figcaption>
    ...   </figure>
    ...   <figure itemscope itemtype="http://n.whatwg.org/work" itemref="licenses">
    ...    <img itemprop="work" src="images/mailbox.jpeg" alt="Outside the house is a mailbox. It has a leaflet inside.">
    ...    <figcaption itemprop="title">The mailbox.</figcaption>
    ...   </figure>
    ...   <footer>
    ...    <p id="licenses">All images licensed under the <a itemprop="license"
    ...    href="http://www.opensource.org/licenses/mit-license.php">MIT
    ...    license</a>.</p>
    ...   </footer>
    ...  </body>
    ... </html>"""
    >>>
    >>> mde = MicrodataExtractor()
    >>> data = mde.extract(html)
    >>> pprint(data)
    [{'properties': {'license': 'http://www.opensource.org/licenses/mit-license.php',
                     'title': 'The house I found.',
                     'work': 'http://www.example.com/images/house.jpeg'},
      'type': 'http://n.whatwg.org/work'},
     {'properties': {'license': 'http://www.opensource.org/licenses/mit-license.php',
                     'title': 'The mailbox.',
                     'work': 'http://www.example.com/images/mailbox.jpeg'},
      'type': 'http://n.whatwg.org/work'}]


JSON-LD extraction
++++++++++++++++++

::

    >>> from pprint import pprint
    >>>
    >>> from extruct.jsonld import JsonLdExtractor
    >>>
    >>> html = """<!DOCTYPE HTML>
    ... <html>
    ...  <head>
    ...   <title>Some Person Page</title>
    ...  </head>
    ...  <body>
    ...   <h1>This guys</h1>
    ...     <script type="application/ld+json">
    ...     {
    ...       "@context": "http://schema.org",
    ...       "@type": "Person",
    ...       "name": "John Doe",
    ...       "jobTitle": "Graduate research assistant",
    ...       "affiliation": "University of Dreams",
    ...       "additionalName": "Johnny",
    ...       "url": "http://www.example.com",
    ...       "address": {
    ...         "@type": "PostalAddress",
    ...         "streetAddress": "1234 Peach Drive",
    ...         "addressLocality": "Wonderland",
    ...         "addressRegion": "Georgia"
    ...       }
    ...     }
    ...     </script>
    ...  </body>
    ... </html>"""
    >>>
    >>> jslde = JsonLdExtractor()
    >>>
    >>> data = jslde.extract(html)
    >>> pprint(data)
    [{'@context': 'http://schema.org',
      '@type': 'Person',
      'additionalName': 'Johnny',
      'address': {'@type': 'PostalAddress',
                  'addressLocality': 'Wonderland',
                  'addressRegion': 'Georgia',
                  'streetAddress': '1234 Peach Drive'},
      'affiliation': 'University of Dreams',
      'jobTitle': 'Graduate research assistant',
      'name': 'John Doe',
      'url': 'http://www.example.com'}]


RDFa extraction (experimental)
++++++++++++++++++++++++++++++

::

    >>> from pprint import pprint
    >>> from extruct.rdfa import RDFaExtractor  # you can ignore the warning about html5lib not being available
    INFO:rdflib:RDFLib Version: 4.2.1
    /home/paul/.virtualenvs/extruct.wheel.test/lib/python3.5/site-packages/rdflib/plugins/parsers/structureddata.py:30: UserWarning: html5lib not found! RDFa and Microdata parsers will not be available.
      'parsers will not be available.')
    >>>
    >>> html = """<html>
    ...  <head>
    ...    ...
    ...  </head>
    ...  <body prefix="dc: http://purl.org/dc/terms/ schema: http://schema.org/">
    ...    <div resource="/alice/posts/trouble_with_bob" typeof="schema:BlogPosting">
    ...       <h2 property="dc:title">The trouble with Bob</h2>
    ...       ...
    ...       <h3 property="dc:creator schema:creator" resource="#me">Alice</h3>
    ...       <div property="schema:articleBody">
    ...         <p>The trouble with Bob is that he takes much better photos than I do:</p>
    ...       </div>
    ...      ...
    ...    </div>
    ...  </body>
    ... </html>
    ... """
    >>>
    >>> rdfae = RDFaExtractor()
    >>> pprint(
    ...     rdfae.extract(html, url='http://www.example.com/index.html')
    ... )
    [{'@id': 'http://www.example.com/alice/posts/trouble_with_bob',
      '@type': ['http://schema.org/BlogPosting'],
      'http://purl.org/dc/terms/creator': [{'@id': 'http://www.example.com/index.html#me'}],
      'http://purl.org/dc/terms/title': [{'@value': 'The trouble with Bob'}],
      'http://schema.org/articleBody': [{'@value': '\n'
                                                   '        The trouble with Bob '
                                                   'is that he takes much better '
                                                   'photos than I do:\n'
                                                   '      '}],
      'http://schema.org/creator': [{'@id': 'http://www.example.com/index.html#me'}]}]

You'll get a list of expanded JSON-LD nodes.


REST API service
----------------

*extruct* also ships with a REST API service to test its output from URLs.

Dependencies
++++++++++++

* bottle_ (Web framework)
* gevent_ (Aysnc framework)
* requests_

.. _bottle: https://pypi.python.org/pypi/bottle
.. _gevent: http://www.gevent.org/
.. _requests: http://docs.python-requests.org/

Usage
+++++

::

    python -m extruct.service

launches an HTTP server listening on port 10005.

Methods supported
+++++++++++++++++

::

    /extruct/<URL>
    method = GET


    /extruct/batch
    method = POST
    params:
        urls - a list of URLs separted by newlines
        urlsfile - a file with one URL per line

E.g. http://localhost:10005/extruct/http://www.sarenza.com/i-love-shoes-susket-s767163-p0000119412

will output something like this:

::

    {
       "url":"http://www.sarenza.com/i-love-shoes-susket-s767163-p0000119412",
       "status":"ok",
       "microdata":[
             {
                "type":"http://schema.org/Product",
                "properties":{
                   "name":"Susket",
                   "color":[
                      "http://www.sarenza.com/i-love-shoes-susket-s767163-p0000119412",
                      "http://www.sarenza.com/i-love-shoes-susket-s767163-p0000119412"
                   ],
                   "brand":"http://www.sarenza.com/i-love-shoes",
                   "aggregateRating":{
                      "type":"http://schema.org/AggregateRating",
                      "properties":{
                         "description":"Soyez le premier \u00e0 donner votre avis"
                      }
                   },
                   "offers":{
                      "type":"http://schema.org/AggregateOffer",
                      "properties":{
                         "lowPrice":"59,00 \u20ac",
                         "price":"A partir de\r\n                  59,00 \u20ac",
                         "priceCurrency":"EUR",
                         "highPrice":"59,00 \u20ac",
                         "availability":"http://schema.org/InStock"
                      }
                   },
                   "size":[
                      "36 - Epuis\u00e9 - \u00catre alert\u00e9",
                      "37 - Epuis\u00e9 - \u00catre alert\u00e9",
                      "38 - Epuis\u00e9 - \u00catre alert\u00e9",
                      "39 - Derni\u00e8re paire !",
                      "40",
                      "41",
                      "42 - Derni\u00e8re paire !"
                   ],
                   "image":[
                      "http://cdn2.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_09.jpg?201509221045",
                      "http://cdn1.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_03.jpg?201509221045",
                      "http://cdn3.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_04.jpg?201509221045",
                      "http://cdn2.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_05.jpg?201509221045",
                      "http://cdn1.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_06.jpg?201509221045",
                      "http://cdn1.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_07.jpg?201509221045",
                      "http://cdn1.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_08.jpg?201509221045",
                      "http://cdn2.sarenza.net/static/_img/productsV4/0000119412/MD_0000119412_223992_02.jpg?201509291747"
                   ],
                   "description":""
                }
             }
       ]
    }


Development version
-------------------

::

    mkvirtualenv extruct
    pip install -r requirements-dev.txt


Tests
-----

Run tests in current environment::

    py.test tests


Use tox_ to run tests with different Python versions::

    tox


.. _tox: https://testrun.org/tox/latest/


Versioning
----------

Use bumpversion_ to conveniently change project version::

    bumpversion patch  # 0.0.0 -> 0.0.1
    bumpversion minor  # 0.0.1 -> 0.1.0
    bumpversion major  # 0.1.0 -> 1.0.0

.. _bumpversion: https://pypi.python.org/pypi/bumpversion
