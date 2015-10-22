=======
extruct
=======

.. image:: https://img.shields.io/travis/scrapinghub/extruct.svg
    :target: https://travis-ci.org/scrapinghub/extruct

Extract structured information from web pages


Installation
------------

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
