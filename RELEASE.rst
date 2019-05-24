==================
Release Procedures
==================

* Edit version_label in :file:`setup.py`.
* Update file:`CHANGELOG.rst`
* Tag the git repo with the version.

.. code:: bash

    $ python3 setup.py sdist bdist_wheel
    $ twine upload dist/* 
