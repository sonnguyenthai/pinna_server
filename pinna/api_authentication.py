"""
Custom Rest Framework authentication policies.
"""
from __future__ import unicode_literals

from django.conf import settings

from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import BaseAuthentication
from rest_framework.views import exception_handler


def get_header(header_name, request):
    """
    Return request's `header_name` header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get("HTTP_%s" %header_name, b'')
    if type(auth) == type(''):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

def custom_exception_handler(exc):
    """
    Custom Django Rest Framework exception handler
    """
    response = exception_handler(exc)

    # Now add the HTTP status code to the response.
    if response is not None:
        data = {}
        data['code'] = 0
        data['msg_code'] = "failed"
        data['message'] = response.data['detail']
        response.data = data

    return response

class APIAuthentication(BaseAuthentication):
    """
    Authentication against application ID/KEY.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        """
        Authenticate API request
        """
        app_id = get_header(settings.PINNA_APP_ID_HEADER, request).strip()
        app_key = get_header(settings.PINNA_APP_KEY_HEADER, request).strip()
        if (not app_key) or (not app_id):
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)

        if not self.check_credentials(app_id, app_key):
            msg = "Invalid basic header. Invalid credentials"
            raise exceptions.AuthenticationFailed(msg)

        return (None,None)

    def check_credentials(self, app_id, app_key):
        """
        Check if credentials are valid
        """
        if (app_id == settings.PINNA_CLIENT_APP_ID) \
                and (app_key == settings.PINNA_CLIENT_APP_KEY):
            return True
        return False

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm

