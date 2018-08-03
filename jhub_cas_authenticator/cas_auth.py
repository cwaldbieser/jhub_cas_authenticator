
import logging
import urllib.parse
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import (
    Authenticator,
    LocalAuthenticator,
)
from lxml import etree
from tornado import gen, web
from tornado.httpclient import (
    AsyncHTTPClient,
    HTTPError,
)
from traitlets import (
    Set,
    Unicode,
)


class CASLogoutHandler(BaseHandler):
    """
    Log a user out by clearing their login cookie and redirecting
    to the CAS logout URL.
    """

    @gen.coroutine
    def get(self):
        user = self.get_current_user()
        if user:
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()
            self.statsd.incr('logout')

        url = self.authenticator.cas_logout_url
        self.log.debug("Redirecting to CAS logout: {0}".format(url))
        self.redirect(url, permanent=False)


class CASLoginHandler(BaseHandler):
    """
    Authenticate users via the CAS protocol.
    """

    @gen.coroutine
    def get(self):
        app_log = logging.getLogger("tornado.application")
        ticket = self.get_argument("ticket", None)
        has_service_ticket = ticket is not None
        app_log.debug("Has service ticket? {0}".format(has_service_ticket))

        # Redirect to get ticket if not presenting one
        if not has_service_ticket:
            cas_service_url = self.make_service_url()
            qs_map = dict(service=cas_service_url)
            qs = urllib.parse.urlencode(qs_map)
            url = "{0}?{1}".format(self.authenticator.cas_login_url, qs)
            app_log.debug("Redirecting to CAS to get service ticket: {0}".format(url))
            self.redirect(url)
            return

        # Validate ticket
        app_log.debug("Validating service ticket {0}...".format(ticket[:10]))
        result = yield self.validate_service_ticket(ticket)
        is_valid, user, attributes = result
        if not is_valid:
            raise web.HTTPError(401)

        app_log.debug("Service ticket was valid.")
        app_log.debug("User is '{0}'.".format(user))
        for a, v in attributes:
            app_log.debug("Attribute {0}: {1}".format(a, v))

        # Check for required attributes
        required_attribs = self.authenticator.cas_required_attribs
        if not required_attribs.issubset(attributes):
            app_log.debug("Missing required attributes:")
            missing = required_attribs - attributes
            for a, v in missing:
                app_log.debug("Attribute {0}: {1}".format(a, v))
            raise web.HTTPError(401)

        # Check against whitelist
        whitelist = self.authenticator.whitelist
        if whitelist and user not in whitelist:
            app_log.debug("User not in whitelist: {0}".format(user))
            raise web.HTTPError(401)

        # Success!  Log user in.
        app_log.debug("CAS authentication successful for '{0}'.".format(user))
        avatar = self.user_from_username(user)
        self.set_login_cookie(avatar)
        next_url = self.get_next_url(avatar)
        app_log.debug("CAS redirecting to: {0}".format(next_url))
        self.redirect(next_url)

    def make_service_url(self):
        """
        Make the service URL CAS will use to redirect the browser back to this service.
        """
        cas_service_url = self.authenticator.cas_service_url
        if cas_service_url is None:
            cas_service_url = self.request.protocol + "://" + self.request.host + self.request.uri
        return cas_service_url

    @gen.coroutine
    def validate_service_ticket(self, ticket):
        """
        Validate a CAS service ticket.

        Returns (is_valid, user, attribs).
        `is_valid` - boolean
        `attribs` - set of attribute-value tuples.
        """
        http_client = AsyncHTTPClient()
        service = self.make_service_url()
        qs_dict = dict(service=service, ticket=ticket)
        qs = urllib.parse.urlencode(qs_dict)
        cas_validate_url = self.authenticator.cas_service_validate_url + "?" + qs
        response = None
        print("Validate URL: {0}".format(cas_validate_url))
        try:
            response = yield http_client.fetch(
                cas_validate_url,
                method="GET",
                ca_certs=self.authenticator.cas_client_ca_certs)
            print("Response was successful: {0}".format(response))
        except HTTPError as ex:
            return (False, None, None)
        parser = etree.XMLParser()
        root = etree.fromstring(response.body, parser=parser)
        auth_result_elm = root[0]
        is_success = (etree.QName(auth_result_elm).localname == 'authenticationSuccess')
        if not is_success:
            return (False, None, None)
        user_elm = find_child_element(auth_result_elm, "user")
        user = user_elm.text.lower()
        attrib_results = set([])
        attribs = find_child_element(auth_result_elm, "attributes")
        if attribs is None:
            attribs = []
        for attrib in attribs:
            name = etree.QName(attrib).localname
            value = attrib.text
            attrib_results.add((name, value))
        return (True, user, attrib_results)


class CASAuthenticator(Authenticator):
    """
    Validate a CAS service ticket and optionally check for the presence of an
    authorization attribute.
    """
    cas_login_url = Unicode(
        config=True,
        help="""The CAS URL to redirect unauthenticated users to.""")

    cas_logout_url = Unicode(
        config=True,
        help="""The CAS URL for logging out an authenticated user.""")

    cas_service_url = Unicode(
        allow_none=True,
        default_value=None,
        config=True,
        help="""The service URL the CAS server will redirect the browser back to on successful authentication.""")

    cas_client_ca_certs = Unicode(
        allow_none=True,
        default_value=None,
        config=True,
        help="""Path to CA certificates the CAS client will trust when validating a service ticket.""")

    cas_service_validate_url = Unicode(
        config=True,
        help="""The CAS endpoint for validating service tickets.""")

    cas_required_attribs = Set(
            help="A set of attribute name and value tuples a user must have to be allowed access."
        ).tag(config=True)

    def get_handlers(self, app):
        return [
            (r'/login', CASLoginHandler),
            (r'/logout', CASLogoutHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


class CASLocalAuthenticator(LocalAuthenticator):
    """
    Validate a CAS service ticket and optionally check for the presence of an
    authorization attribute.
    """
    cas_login_url = Unicode(
        config=True,
        help="""The CAS URL to redirect unauthenticated users to.""")

    cas_logout_url = Unicode(
        config=True,
        help="""The CAS URL for logging out an authenticated user.""")

    cas_service_url = Unicode(
        allow_none=True,
        default_value=None,
        config=True,
        help="""The service URL the CAS server will redirect the browser back to on successful authentication.""")

    cas_client_ca_certs = Unicode(
        allow_none=True,
        default_value=None,
        config=True,
        help="""Path to CA certificates the CAS client will trust when validating a service ticket.""")

    cas_service_validate_url = Unicode(
        config=True,
        help="""The CAS endpoint for validating service tickets.""")

    cas_required_attribs = Set(
            help="A set of attribute name and value tuples a user must have to be allowed access."
        ).tag(config=True)

    def get_handlers(self, app):
        return [
            (r'/login', CASLoginHandler),
            (r'/logout', CASLogoutHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


def find_child_element(elm, child_local_name):
    """
    Find an XML child element by local tag name.
    """
    for n in range(len(elm)):
        child_elm = elm[n]
        tag = etree.QName(child_elm)
        if tag.localname == child_local_name:
            return child_elm
    return None
