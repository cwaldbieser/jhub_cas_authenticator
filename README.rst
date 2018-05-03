============================
Jupyterhub CAS Authenticator
============================

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

You will also need to add settings specific to the CAS authentication configuration::

    # The CAS URL to redirect unauthenticated users to.
    c.CASAuthenticator.cas_login_url = 'https://cas.example.net/cas/login'

    # The service URL the CAS server will redirect the browser back to on successful authentication.
    # If not set, this is set to the same URL the request comes in on.  This will work fine for
    # simple deployments, but deployments behind a proxy or load banalncer will likely need to
    # be adjusted so the CAS service redirects back to the *real* login URL for your Jupyterhub.
    c.CASAuthenticator.cas_service_url = 'https://your-jupyterhub.tld/login'

    # Path to CA certificates the CAS client will trust when validating a service ticket.
    c.CASAuthenticator.cas_client_ca_certs = '/path/to/ca_certs.pem'

    # The CAS endpoint for validating service tickets.
    c.CASAuthenticator.cas_service_validate_url = 'https://cas.example.net/cas/p3/serviceValidate'

    # A set of attribute name and value tuples a user must have to be allowed access.
    c.CASAuthenticator.cas_required_attribs = {('memberOf', 'jupyterhub_users')}

-----------------------------
Just-in-Time Account Creation
-----------------------------

If your Jupyterhub spawner relies on local users to exist for the authenticated
user, it can be useful to use `CASLocalAuthenticator` instead of
`CASAuthenticator`.  The former inherits from `LocalAuthenticator` and has the
property `create_system_users`.  You can use it like this:

.. code:: python

    c.JupyterHub.authenticator_class = 'jhub_cas_authenticator.cas_auth.CASLocalAuthenticator'
    # The CAS URL to redirect unauthenticated users to.
    c.CASLocalAuthenticator.cas_login_url = 'https://cas.example.net/cas/login'
    # The CAS URL for logging out an authenticated user.
    c.CASLocalAuthenticator.cas_logout_url = 'https://cas.example.net/cas/logout'
    # The service URL the CAS server will redirect the browser back to on successful authentication.
    # If not set, this is set to the same URL the request comes in on.  This will work fine for
    # simple deployments, but deployments behind a proxy or load banalncer will likely need to
    # be adjusted so the CAS service redirects back to the *real* login URL for your Jupyterhub.
    c.CASLocalAuthenticator.cas_service_url = 'https://jupyterhub.example.net/login'
    # Path to CA certificates the CAS client will trust when validating a service ticket.
    c.CASLocalAuthenticator.cas_client_ca_certs = '/path/to/ca_certs.pem'
    # The CAS endpoint for validating service tickets.
    c.CASLocalAuthenticator.cas_service_validate_url = 'https://cas.example.net/cas/p3/serviceValidate'
    # A set of attribute name and value tuples a user must have to be allowed access.
    c.CASLocalAuthenticator.cas_required_attribs = {('memberOf', 'jupyterhub_users')}
    # Allowed logins.
    c.CASLocalAuthenticator.whitelist = {'waldbiec', 'carl', 'logan'}
    # Create system users just-in-time.
    c.CASLocalAuthenticator.create_system_users = True

