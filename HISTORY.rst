=======
History
=======

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
