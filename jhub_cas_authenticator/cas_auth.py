
import os
import urllib.parse
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
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


class CASLoginHandler(BaseHandler):
    """
    Authenticate users via the CAS protocol.
    """

    cas_login_url = Unicode(
        default_value=None,
        config=True,
        help="""The CAS URL to redirect unauthenticated users to.""")

    cas_service_url = Unicode(
        default_value=None,
        config=True,
        help="""The service URL the CAS server will redirect the browser back to on successful authentication.""")

    cas_client_ca_certs = Unicode(
        default_value=None,
        config=True,
        help="""Path to CA certificates the CAS client will trust when validating a service ticket.""")

    cas_p3_server_validate_url = Unicode(
        default_value=None,
        config=True,
        help="""The CAS protocol 3 endpoint for validating service tickets.""")

    cas_required_attribs = Set(
            help="A set of attribute name and value tuples a user must have to be allowed access."
        ).tag(config=True)

    def get(self):
        service = self.get_argument("service", None)
        ticket = self.get_argument("ticket", None)
        has_service_ticket = not (service is None or ticket is None)
        if not has_service_ticket: 
            cas_service_url = self.cas_service_url
            if cas_service_url is None:
                cas_service_url = self.request.protocol + "://" + self.request.host + self.request.uri
            qs_map = dict(service=cas_service_url)
            qs = urllib.parse.urlencode(qs_map)
            url = "{0}?{1}".format(self.cas_login_url, qs) 
            self.redirect(url)
        else:
            is_valid, user, attributes = self.validate_service_ticket(service, ticket)
            if is_valid:
                required_attribs = self.cas_required_attribs
                if not required_attribs.issubset(attributes):
                    web.HTTPError(401)
                self.set_login_cookie(user)
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
            else:
                raise web.HTTPError(401)

    @gen.coroutine
    def validate_service_ticket(self, service, ticket):
        """
        Validate a CAS service ticket.

        Returns (is_valid, user, attribs).
        `is_valid` - boolean
        `attribs` - set of attribute-value tuples.
        """
        http_client = AsyncHTTPClient()
        qs_dict = dict(service=service, ticket=ticket)
        qs = urllib.parse.urlencode(qs_dict)
        cas_validate_url = self.cas_p3_server_validate_url + "?" + qs
        try:
            response = yield http_client.fetch(
                cas_validate_url, 
                method="GET",
                ca_certs=self.cas_client_ca_certs)
        except HTTPError as ex:
            return (False, None, None)
        
        parser = etree.XMLParser()
        root = etree.fromstring(data, parser=parser)
        auth_result_elm = root[0]
        is_success == (etree.QName(auth_result_elm).localname == 'authenticationSuccess')
        if not is_success:
            return (False, None, None)
        user_elm = find_child_element(auth_result_elm, "user")
        user = user_elm.text.lower()
        attrib_results = set([])
        attribs = root[0][1]
        for attrib in attribs:
            name = etree.QName(attrib).localname
            value = attrib.text
            attrib_set.add(tuple(name, value))
        return tuple(True, user, attrib_set)
        

class CASAuthenticator(Authenticator):
    """
    Validate a CAS service ticket and optionally check for the presence of an
    authorization attribute.
    """
    def get_handlers(self, app):
        return [
            (r'/login', CASLoginHandler),
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
        
