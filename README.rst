=======
extruct
=======

.. image:: https://img.shields.io/travis/scrapinghub/extruct/master.svg
    :target: https://travis-ci.org/scrapinghub/extruct
    :alt: Build Status

.. image:: https://img.shields.io/codecov/c/github/scrapinghub/extruct/master.svg?maxAge=2592000
    :target: https://codecov.io/gh/scrapinghub/extruct
    :alt: Coverage report

.. image:: https://img.shields.io/pypi/v/extruct.svg
   :target: https://pypi.python.org/pypi/extruct
   :alt: PyPI Version


*extruct* is a library for extracting embedded metadata from HTML markup.

Currently, *extruct* supports:

- `W3C's HTML Microdata`_
- `embedded JSON-LD`_
- `Microformat`_ via `mf2py`_
- `Facebook's Open Graph`_
- (experimental) `RDFa`_ via `rdflib`_

.. _W3C's HTML Microdata: http://www.w3.org/TR/microdata/
.. _embedded JSON-LD: http://www.w3.org/TR/json-ld/#embedding-json-ld-in-html-documents
.. _RDFa: https://www.w3.org/TR/html-rdfa/
.. _rdflib: https://pypi.python.org/pypi/rdflib/
.. _Microformat: http://microformats.org/wiki/Main_Page
.. _mf2py: https://github.com/microformats/mf2py
.. _Facebook's Open Graph: http://ogp.me/

The microdata algorithm is a revisit of `this Scrapinghub blog post`_ showing how to use EXSLT extensions.

.. _this Scrapinghub blog post: http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/


Installation
------------

::

    pip install extruct


Usage
-----

All-in-one extraction
+++++++++++++++++++++

The simplest example how to use extruct is to call
``extruct.extract(htmlstring, base_url=base_url)``
with some HTML string and an optional base URL.

Let's try this on a webpage that uses all the syntaxes supported (RDFa with `ogp`_).

First fetch the HTML using python-requests and then feed the response body to ``extruct``::

  >>> import extruct
  >>> import requests
  >>> import pprint
  >>> from w3lib.html import get_base_url
  >>>
  >>> pp = pprint.PrettyPrinter(indent=2)
  >>> r = requests.get('https://www.optimizesmart.com/how-to-use-open-graph-protocol/')
  >>> base_url = get_base_url(r.text, r.url)
  >>> data = extruct.extract(r.text, base_url=base_url)
  >>>
  >>> pp.pprint(data)
  { 'json-ld': [ { '@context': 'https://schema.org',
                   '@graph': [...]},
                 { '@context': 'http://schema.org',
                   '@id': '',
                   '@type': 'ProfessionalService',
                   'address': { '@type': 'PostalAddress',...},
                   'image': 'https://www.optimizesmart.com/wp-content/themes/Sept17OptimizeSmartDEV/images/logo-small.png',
                   'name': 'Optimize Smart',
                   'openingHoursSpecification': { '@type': 'OpeningHoursSpecification',...},
                   'sameAs': [...],
                   'telephone': '',
                   'url': 'https://www.optimizesmart.com'}],
    'microdata': [ { 'properties': {'headline': ''},
                     'type': 'http://schema.org/WPHeader'}],
    'microformat': [ { 'children': [ { 'properties': { 'category': [ 'facebook-tracking']},
                                       'type': ['h-entry']}],
                       'properties': {},
                       'type': ['h-feed']}],
    'opengraph': [ { 'namespace': { 'article': 'http://ogp.me/ns/article#',
                                    'og': 'http://ogp.me/ns#'},
                     'properties': [ ('og:locale', 'en_US'),
                                     ('og:type', 'article'),
                                     ( 'og:title',
                                       'Open Graph Protocol for Facebook '
                                       'explained with examples'),
                                     ( 'og:description',
                                       'What is Open Graph Protocol and why you '
                                       'need it? Learn to implement Open Graph '
                                       'Protocol for Facebook on your website. '
                                       'Open Graph Protocol Meta Tags.'),
                                     ( 'og:url',
                                       'https://www.optimizesmart.com/how-to-use-open-graph-protocol/'),...]}],
    'rdfa': [ { '@id': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/#header',
                'http://www.w3.org/1999/xhtml/vocab#role': [ { '@id': 'http://www.w3.org/1999/xhtml/vocab#banner'}]},
              { '@id': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/',
                'article:modified_time': [ { '@value': '...'}],
                'article:published_time': [ { '@value': '...'}],
                'article:publisher': [ { '@value': 'https://www.facebook.com/optimizesmart/'}],
                'article:section': [{'@value': 'Facebook Tracking'}],
                'http://ogp.me/ns#description': [ { '@value':...}],
                'http://ogp.me/ns#image': [ { '@value': 'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg'}],
                'http://ogp.me/ns#image:height': [{'@value': '309'}],
                'http://ogp.me/ns#image:secure_url': [ { '@value': 'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg'}],
                'http://ogp.me/ns#image:width': [{'@value': '711'}],
                'http://ogp.me/ns#locale': [{'@value': 'en_US'}],
                'http://ogp.me/ns#site_name': [{'@value': 'Optimize Smart'}],
                'http://ogp.me/ns#title': [ { '@value':...}],
                'http://ogp.me/ns#type': [{'@value': 'article'}],
                'http://ogp.me/ns#url': [ { '@value': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/'}],
                'https://api.w.org/': [ { '@id': 'https://www.optimizesmart.com/wp-json/'}]}]}

Select syntaxes
+++++++++++++++
It is possible to select which syntaxes to extract by passing a list with the desired ones to extract. Valid values: 'microdata', 'json-ld', 'opengraph', 'microformat', 'rdfa'. If no list is passed all syntaxes will be extracted and returned::

  >>> r = requests.get('http://www.songkick.com/artists/236156-elysian-fields')
  >>> base_url = get_base_url(r.text, r.url)
  >>> data = extruct.extract(r.text, base_url, syntaxes=['microdata', 'opengraph', 'rdfa'])
  >>>
  >>> pp.pprint(data)
  { 'microdata': [ { 'properties': { 'author': 'rainerkromarek',...},
                     'type': 'http://schema.org/Review'}],
    'opengraph': [ { 'namespace': { 'concerts': 'http://ogp.me/ns/fb/songkick-concerts#',
                                    'fb': 'http://www.facebook.com/2008/fbml',
                                    'og': 'http://ogp.me/ns#'},
                     'properties': [...]}],
    'rdfa': [ { '@id': 'https://www.songkick.com/artists/236156-elysian-fields',
                'al:ios:app_name': [{'@value': 'Songkick Concerts'}],
                'al:ios:app_store_id': [{'@value': '438690886'}],
                'al:ios:url': [ { '@value': 'songkick://artists/236156-elysian-fields'}],
                ...}]}


Uniform
+++++++
Another option is to uniform the output of microformat, opengraph, microdata and json-ld syntaxes to the following structure: ::

    {'@context': 'http://example.com', 
                 '@type': 'example_type',
                 /* All other the properties in keys here */
                 }

To do so set ``uniform=True`` when calling ``extract``, it's false by default for backward compatibility. Here the same example as before but with uniform set to True: ::

  >>> r = requests.get('http://www.songkick.com/artists/236156-elysian-fields')
  >>> base_url = get_base_url(r.text, r.url)
  >>> data = extruct.extract(r.text, base_url, syntaxes=['microdata', 'opengraph', 'rdfa'], uniform=True)
  >>>
  >>> pp.pprint(data)
  { 'microdata': [ { '@context': 'http://schema.org',
                     '@type': 'Review',
                     'author': 'rainerkromarek',
                     'itemReviewed': 'Elysian Fields',
                     ...}],
    'opengraph': [ { '@context': { 'concerts': 'http://ogp.me/ns/fb/songkick-concerts#',
                                   'fb': 'http://www.facebook.com/2008/fbml',
                                   'og': 'http://ogp.me/ns#'},
                     '@type': 'songkick-concerts:artist',
                     'fb:app_id': '308540029359',
                     ...}],
    'rdfa': [ { '@id': 'https://www.songkick.com/artists/236156-elysian-fields',
                'al:ios:app_name': [{'@value': 'Songkick Concerts'}],
                'al:ios:app_store_id': [{'@value': '438690886'}],
                'al:ios:url': [ { '@value': 'songkick://artists/236156-elysian-fields'}],
                ...}]}

NB rdfa structure is not uniformed yet

Returning HTML node
+++++++++++++++++++

It is also possible to get references to HTML node for every extracted metadata item.
The feature is supported only by microdata syntax.

To use that, just set the ``return_html_node`` option of ``extract`` method to ``True``.
As the result, an additional key "nodeHtml" will be included in the result for every
item. Each node is of ``lxml.etree.Element`` type: ::

  >>> r = requests.get('http://www.rugpadcorner.com/shop/no-muv/')
  >>> base_url = get_base_url(r.text, r.url)
  >>> data = extruct.extract(r.text, base_url, syntaxes=['microdata'], return_html_node=True)
  >>>
  >>> pp.pprint(data)
  { 'microdata': [ { 'htmlNode': <Element div at 0x7f10f8e6d3b8>,
                     'properties': { ...
                                     'offers': [ { 'htmlNode': <Element div at 0x7f10f8e6d138>,
                                                   'properties': { 'availability': 'http://schema.org/InStock',
                                                                   'price': 'Price:  '
                                                                            '$45'},
                                                   'type': 'http://schema.org/Offer'},
                                                 { 'htmlNode': <Element div at 0x7f10f8e60f48>,
                                                   'properties': { 'availability': 'http://schema.org/InStock',
                                                                   'price': '(Select '
                                                                            'Size/Shape '
                                                                            'for '
                                                                            'Pricing)'},
                                                   'type': 'http://schema.org/Offer'}],
                                     ...},
                     'type': 'http://schema.org/Product'}]}

Single extractors
-----------------

You can also use each extractor individually. See below.

Microdata extraction
++++++++++++++++++++
::

  >>> import pprint
  >>> pp = pprint.PrettyPrinter(indent=2)
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
  >>> pp.pprint(data)
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

  >>> import pprint
  >>> pp = pprint.PrettyPrinter(indent=2)
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
  >>> pp.pprint(data)
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

  >>> import pprint
  >>> pp = pprint.PrettyPrinter(indent=2)
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
  >>> pp.pprint(rdfae.extract(html, base_url='http://www.example.com/index.html'))
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


Open Graph extraction
++++++++++++++++++++++++++++++

::

  >>> import pprint
  >>> pp = pprint.PrettyPrinter(indent=2)
  >>>
  >>> from extruct.opengraph import OpenGraphExtractor
  >>>
  >>> html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  ... <html xmlns="https://www.w3.org/1999/xhtml" xmlns:og="https://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
  ...  <head>
  ...   <title>Himanshu's Open Graph Protocol</title>
  ...   <meta http-equiv="Content-Type" content="text/html;charset=WINDOWS-1252" />
  ...   <meta http-equiv="Content-Language" content="en-us" />
  ...   <link rel="stylesheet" type="text/css" href="event-education.css" />
  ...   <meta name="verify-v1" content="so4y/3aLT7/7bUUB9f6iVXN0tv8upRwaccek7JKB1gs=" >
  ...   <meta property="og:title" content="Himanshu's Open Graph Protocol"/>
  ...   <meta property="og:type" content="article"/>
  ...   <meta property="og:url" content="https://www.eventeducation.com/test.php"/>
  ...   <meta property="og:image" content="https://www.eventeducation.com/images/982336_wedding_dayandouan_th.jpg"/>
  ...   <meta property="fb:admins" content="himanshu160"/>
  ...   <meta property="og:site_name" content="Event Education"/>
  ...   <meta property="og:description" content="Event Education provides free courses on event planning and management to event professionals worldwide."/>
  ...  </head>
  ...  <body>
  ...   <div id="fb-root"></div>
  ...   <script>(function(d, s, id) {
  ...               var js, fjs = d.getElementsByTagName(s)[0];
  ...               if (d.getElementById(id)) return;
  ...                  js = d.createElement(s); js.id = id;
  ...                  js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=501839739845103";
  ...                  fjs.parentNode.insertBefore(js, fjs);
  ...                  }(document, 'script', 'facebook-jssdk'));</script>
  ...  </body>
  ... </html>"""
  >>>
  >>> opengraphe = OpenGraphExtractor()
  >>> pp.pprint(opengraphe.extract(html))
  [{"namespace": {
        "og": "http://ogp.me/ns#"
    },
    "properties": [
        [
            "og:title",
            "Himanshu's Open Graph Protocol"
        ],
        [
            "og:type",
            "article"
        ],
        [
            "og:url",
            "https://www.eventeducation.com/test.php"
        ],
        [
            "og:image",
            "https://www.eventeducation.com/images/982336_wedding_dayandouan_th.jpg"
        ],
        [
            "og:site_name",
            "Event Education"
        ],
        [
            "og:description",
            "Event Education provides free courses on event planning and management to event professionals worldwide."
        ]
      ]
   }]


Microformat extraction
++++++++++++++++++++++++++++++

::

  >>> import pprint
  >>> pp = pprint.PrettyPrinter(indent=2)
  >>>
  >>> from extruct.microformat import MicroformatExtractor
  >>>
  >>> html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  ... <html xmlns="https://www.w3.org/1999/xhtml" xmlns:og="https://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
  ...  <head>
  ...   <title>Himanshu's Open Graph Protocol</title>
  ...   <meta http-equiv="Content-Type" content="text/html;charset=WINDOWS-1252" />
  ...   <meta http-equiv="Content-Language" content="en-us" />
  ...   <link rel="stylesheet" type="text/css" href="event-education.css" />
  ...   <meta name="verify-v1" content="so4y/3aLT7/7bUUB9f6iVXN0tv8upRwaccek7JKB1gs=" >
  ...   <meta property="og:title" content="Himanshu's Open Graph Protocol"/>
  ...   <article class="h-entry">
  ...    <h1 class="p-name">Microformats are amazing</h1>
  ...    <p>Published by <a class="p-author h-card" href="http://example.com">W. Developer</a>
  ...       on <time class="dt-published" datetime="2013-06-13 12:00:00">13<sup>th</sup> June 2013</time></p>
  ...    <p class="p-summary">In which I extoll the virtues of using microformats.</p>
  ...    <div class="e-content">
  ...     <p>Blah blah blah</p>
  ...    </div>
  ...   </article>
  ...  </head>
  ...  <body></body>
  ... </html>"""
  >>>
  >>> microformate = MicroformatExtractor()
  >>> data = microformate.extract(html)
  >>> pp.pprint(data)
  [{"type": [
        "h-entry"
    ],
    "properties": {
        "name": [
            "Microformats are amazing"
        ],
        "author": [
            {
                "type": [
                    "h-card"
                ],
                "properties": {
                    "name": [
                        "W. Developer"
                    ],
                    "url": [
                        "http://example.com"
                    ]
                },
                "value": "W. Developer"
            }
        ],
        "published": [
            "2013-06-13 12:00:00"
        ],
        "summary": [
            "In which I extoll the virtues of using microformats."
        ],
        "content": [
            {
                "html": "\n<p>Blah blah blah</p>\n",
                "value": "\nBlah blah blah\n"
            }
        ]
      }
   }]

Command Line Tool
-----------------

*extruct* provides a command line tool that allows you to fetch a page and
extract the metadata from it directly from the command line.

Dependencies
++++++++++++

The command line tool depends on requests_, which is not installed by default
when you install **extruct**. In order to use the command line tool, you can
install **extruct** with the `cli` extra requirements::

    pip install extruct[cli]


Usage
+++++

::

    extruct "http://example.com"

Downloads "http://example.com" and outputs the Microdata, JSON-LD and RDFa, Open Graph
and Microformat metadata to `stdout`.

Supported Parameters
++++++++++++++++++++

By default, the command line tool will try to extract all the supported
metadata formats from the page (currently Microdata, JSON-LD, RDFa, Open Graph
and Microformat). If you want to restrict the output to just one or a subset of
those, you can pass their individual names collected in a list through 'syntaxes' argument.

For example, this command extracts only Microdata and JSON-LD metadata from
"http://example.com"::

    extruct "http://example.com" --syntaxes microdata json-ld 

NB syntaxes names passed must correspond to these: microdata, json-ld, rdfa, opengraph, microformat

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
