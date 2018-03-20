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
- `microformat`_ via `mf2py`_
- `Facebook's opengraph`_
- (experimental) `RDFa`_ via `rdflib`_

.. _W3C's HTML Microdata: http://www.w3.org/TR/microdata/
.. _embedded JSON-LD: http://www.w3.org/TR/json-ld/#embedding-json-ld-in-html-documents
.. _RDFa: https://www.w3.org/TR/html-rdfa/
.. _rdflib: https://pypi.python.org/pypi/rdflib/
.. _microformat: http://microformats.org/wiki/Main_Page
.. _mf2py: https://github.com/microformats/mf2py
.. _Facebook's opengraph: http://ogp.me/

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

Let's try this on a webpage that uses all the syntaxes supported (RDFa with `ogp`_).

First fetch the HTML using python-requests and then feed the response body to ``extruct``::

    >>> import requests
    >>> from pprint import pprint

    >>> r = requests.get('https://www.optimizesmart.com/how-to-use-open-graph-protocol/')

    >>> import extruct
    >>> data = extruct.extract(r.text, r.url)

    >>> pprint(data)
    {'jsonld': [{'@context': 'https://schema.org',
             '@id': '#organization',
             '@type': 'Organization',
             'logo': 'https://www.optimizesmart.com/wp-content/uploads/2016/03/optimize-smart-Twitter-logo.jpg',
             'name': 'Optimize Smart',
             'sameAs': ['https://www.facebook.com/optimizesmart/',
                        'https://uk.linkedin.com/in/analyticsnerd',
                        'https://www.youtube.com/user/optimizesmart',
                        'https://twitter.com/analyticsnerd'],
             'url': 'https://www.optimizesmart.com/'}],
 'microdata': [{'properties': {'headline': ''},
                'type': 'http://schema.org/WPHeader'}],
 'microformat': [{'children': [{'properties': {'category': ['specialized-tracking'],
                                               'name': ['Open Graph Protocol '
                                                        'for Facebook '
                                                        'explained with '
                                                        'examples\n'
                                                        '\n'
                                                        'Specialized Tracking\n'
                                                        '\n'
                                                        '\n'
                                                        (...)
                                                        (...)
                                                        (...)
                                                        '!function(d,s,id){var '
                                                        "js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, "
                                                        "'script', "
                                                        "'twitter-wjs');"]},
                                'type': ['h-entry']}],
                  'properties': {'name': ['Open Graph Protocol for Facebook '
                                          'explained with examples\n'
                                          '\n'
                                          'Specialized Tracking\n'
                                          '\n'
                                          '\n'
                                          'What is Open Graph Protocol and why '
                                          (...)
                                          (...)
                                          (...)
                                          "js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, "
                                          "'script', 'twitter-wjs');"]},
                  'type': ['h-feed']}],
 'opengraph': [{'namespace': {'og': 'http://ogp.me/ns#'},
                'properties': [('og:locale', 'en_US'),
                               ('og:type', 'article'),
                               ('og:title',
                                'Open Graph Protocol for Facebook explained '
                                'with examples'),
                               ('og:description',
                                'What is Open Graph Protocol and why you need '
                                'it? Learn to implement Open Graph Protocol '
                                'for Facebook on your website. Open Graph '
                                'Protocol Meta Tags.'),
                               ('og:url',
                                'https://www.optimizesmart.com/how-to-use-open-graph-protocol/'),
                               ('og:site_name', 'Optimize Smart'),
                               ('og:updated_time', '2018-03-09T16:26:35+00:00'),
                               ('og:image',
                                'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg'),
                               ('og:image:secure_url',
                                'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg')]}],
 'rdfa': [{'@id': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/',
           'article:modified_time': [{'@value': '2018-03-09T16:26:35+00:00'}],
           'article:published_time': [{'@value': '2010-07-02T18:57:23+00:00'}],
           'article:publisher': [{'@value': 'https://www.facebook.com/optimizesmart/'}],
           'article:section': [{'@value': 'Specialized Tracking'}],
           'http://ogp.me/ns#description': [{'@value': 'What is Open Graph '
                                                       'Protocol and why you '
                                                       'need it? Learn to '
                                                       'implement Open Graph '
                                                       'Protocol for Facebook '
                                                       'on your website. Open '
                                                       'Graph Protocol Meta '
                                                       'Tags.'}],
           'http://ogp.me/ns#image': [{'@value': 'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg'}],
           'http://ogp.me/ns#image:secure_url': [{'@value': 'https://www.optimizesmart.com/wp-content/uploads/2010/07/open-graph-protocol.jpg'}],
           'http://ogp.me/ns#locale': [{'@value': 'en_US'}],
           'http://ogp.me/ns#site_name': [{'@value': 'Optimize Smart'}],
           'http://ogp.me/ns#title': [{'@value': 'Open Graph Protocol for '
                                                 'Facebook explained with '
                                                 'examples'}],
           'http://ogp.me/ns#type': [{'@value': 'article'}],
           'http://ogp.me/ns#updated_time': [{'@value': '2018-03-09T16:26:35+00:00'}],
           'http://ogp.me/ns#url': [{'@value': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/'}],
           'http://ogp.me/ns/fb#app_id': [{'@value': '1047458588599837'}],
           'https://api.w.org/': [{'@id': 'https://www.optimizesmart.com/wp-json/'}]},
          {'@id': 'https://www.optimizesmart.com/how-to-use-open-graph-protocol/#header',
           'http://www.w3.org/1999/xhtml/vocab#role': [{'@id': 'http://www.w3.org/1999/xhtml/vocab#banner'}]}]}


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

Downloads "http://example.com" and outputs the Microdata, JSON-LD and RDFa
metadata to `stdout`.

Supported Parameters
++++++++++++++++++++

By default, the command line tool will try to extract all the supported
metadata formats from the page (currently Microdata, JSON-LD and RDFa). If you
want to restrict the output to just one or a subset of those, you can use the
individual switches.

For example, this command extracts only Microdata and JSON-LD metadata from
"http://example.com"::

    extruct --microdata --jsonld "http://example.com"


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
