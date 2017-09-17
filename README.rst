====================================
Jupyterhub REMOTE_USER Authenticator
====================================

Authenticate to Jupyterhub using the CAS 3.0 protocol
(https://apereo.github.io/cas/5.1.x/protocol/CAS-Protocol-Specification.html)

------------
Installation
------------

This package can be installed with `pip` either from a local git repository or from PyPi.

Installation from local git repository::

    cd jhub_cas_authenticator
    pip install .

Installation from PyPi::

    pip install jhub_cas_authenticator

Alternately, you can add the local project folder must be on your PYTHONPATH.

-------------
Configuration
-------------

You should edit your :file:`jupyterhub_config.py` to set the authenticator 
class::

    c.JupyterHub.authenticator_class = 'jhub_cas_authenticator.cas_auth.CASAuthenticator'

TODO: Explain configuration and usage.

