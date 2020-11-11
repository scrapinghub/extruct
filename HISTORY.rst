=======
History
=======

v0.10.0 (2020-09-01)
--------------------

* support open graph arrays via ``with_og_array=True`` (PR #138)
* support "expanded" Open Graph metadata based on og:type (PR #140)
* parse JSON with JS comments for json-ld (PR #137)
* preserve order for duplicated properties for RDFa (PR #139)
* improve microdata parser performance with large number of items (PR #148)
* spelling fixes (PR #145)

v0.9.0 (2020-04-20)
-------------------

* REST API ``extruct.service`` removed
* ``rdflib`` dependency restrited to <5.0.0, as parsers used by extruct
  were removed in 5.0.0

v0.8.0 (2019-10-07)
-------------------
* Python 3.4 support is dropped;
* in case of duplicate OpenGraph definitions (e.g. multiple ``og:image``),
  empty results are de-prioritized now, to do the same as Facebook;
* text content of microdata attributes is now extracted using html-text
  library, which fixes badly extracted text in some cases
  (words glued together, etc.)

v0.7.3 (2019-06-10)
-------------------

* In case of duplicate OpenGraph definitions (e.g. multiple ``og:image``),
  extruct now keeps the first one, not the last one,
  to do the same as Facebook.

v0.7.2 (2019-02-14)
-------------------

* Cover all possible exception cases dealt by ``extruct()`` ``errors``
  attribute for values ``strict``, ``log`` and ``ignore``
* avoid including ``itemprop`` from child ``itemscope`` when using
  ``itemref`` for microdata
* proper processing order for ``itemref`` for microdata

v0.7.1 (2018-11-02)
-------------------

* json-ld parsing issue is fixed;
* deprecation warning for ``url`` argument points to caller code;
* better Python 3.7 support (fixed warnings, setup running 3.7 tests on CI).

v0.7.0 (2018-08-23)
-------------------

In this release OpenGraph parsing is improved:

* known OpenGraph namespaces (og, music, video,
  article, book, profile) work without an explicitly defined prefix;
* prefix is extracted both from ``<head>`` and ``<html>`` element attributes,
  not only from ``<head>``;
* prefix parsing is more permissive.

Other changes:

* pypi version badge is added to the README;
* html parsing code is cleaned up.

v0.6.0 (2018-08-09)
-------------------

* JSON-LD parsing is less strict now: control characters are allowed.

v0.5.0 (2018-06-08)
-------------------

* Add OpenGraph and Microformat extractors.
* Add argument ``syntaxes`` to ``extract`` and command line function, it allows to
  select which syntaxes to extract.
* Add argument ``uniform`` to ``extract`` and command line function, if True it maps
  the output of Microdata, OpenGraph, Microformat and Json-ld to the same template.
* Add argument ``errors``  to ``extract`` and command line function, it allows to
  define if errors should be raised, logged or ignored.
* Fix RDFa memory leak, now RDfaExtractor resets ``_lookups`` after each
  extraction.
* Fixed regex pattern in ``JsonLdExtractor`` to avoid removing comments from
  within valid JSON.
* In ``w3microdata`` strip whitespaces, newlines, etc from urls extracted from
  html nodes.
* ``base_url`` substitutes ``url`` in ``MicroformatExtractor``, ``JsonLdExtractor``,
  ``OpenGraphExtractor``, ``RDFaExtractor``  and ``MicrodataExtractor``
* individual extractors accept ``base_url`` instead of ``url``, unused keyword
  arguments are removed.
* In ``w3microdata.extract_items`` ``items_seen`` and ``url`` are no longer 
  class variables but are passed as arguments.
* In ``w3microdata`` the following functions are now private:
  ``extract_item``, ``extract_property_value``, ``extract_textContent``,
  ``_extract_property``, ``_extract_properties``, ``_extract_property_refs``
  and ``_extract_textContent``.
* In ``w3microdata`` ``_extract_properties``, ``_extract_property_refs``, 
  ``_extract_property``, ``_extract_property_value`` and ``_extract_item``
  now need ``items_seen`` and ``url`` to be passed as arguments.
* Add argument ``return_html_node`` to ``extract``, it allows to return HTML
  node with the result of metadata extraction. It is supported only by
  microdata syntax.

Warning: backward-incompatible change:

* ``base_url`` is used instead of ``url`` in ``extruct.extract``, ``url`` is 
  still supported by deprecated.
* In ``extruct.extract`` default ``base_url`` is now ``None`` to avoid wrong 
  results with ``urljoin``.




v0.4.0 (2017-06-20)
-------------------

* New ``extruct`` command line tool to fetch a page and extract its metadata.
  Works either via ``extruct`` directly or ``python -m extruct``.
* Accept leading HTML comment in JSON-LD payload.
* rdflib log messages were silenced to avoid the noise when importing extruct.


v0.3.1 (2017-06-07)
-------------------

* Fix dependencies and support RDFa by default (hence depend on rdflib by default).
* Update README with all-in-one extractor examples.

v0.3.0 (2017-06-07)
-------------------

* All extractors have an ``.extract_items()`` method, taking an lxml-parsed
  document as input, if you want to reuse one you already have.
* Add generic extraction: use ``extruct.extract()`` to call all extractors
  at once.

v0.3.0a2 (2017-02-01)
---------------------

Warning: backward-incompatible change:

* ``.extract()`` methods now return a list of Python dicts (the items)
  instead of a dict with an "items" key having this list as value.

v0.3.0a1 (2016-12-15)
---------------------

* Use rdflib's pyRdfa directly instead of pyRdfa3 code copy.


v0.3.0a0 (2016-12-02)
---------------------

* (Very) Experimental support for RDFa extraction using rdflib+lxml


v0.2.0 (2016-09-26)
-------------------

* Web service response content-type set to 'application/json'
* Web service Python 3 compatibility
* Code coverage reports
* Fix extraction of ``<object>`` "data" URL with microdata
* Handle textContent mixed with ``<script>`` and ``<style>`` tags
* Add JSON-LD extraction example to README
* Tests added for non-nested microdata output
* Tests added for text content option
* Tests added for "meter" and "data" attributes


v0.1.0 (2015-10-26)
-------------------

* First release on PyPI.
