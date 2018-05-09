=======
History
=======

v0.5.0 (2018-05-09)
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
* In ``extract`` default url is now ``None`` to avoid wrong results with
  ``urljoin``


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
* Web service Python 3 compatiblity
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
