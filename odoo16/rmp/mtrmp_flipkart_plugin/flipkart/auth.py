# -*- coding: utf-8 -*-
import requests
from sanction import Client as SanctionClient


class Authentication(object):
    """
    A helper class to get access token with the different authentication
    workflows.

    Usage::

        from flipkart import Authentication
        auth = Authentication(app_id, app_secret)

    app_id and app_secret can be obtained from the Seller APIs - Developer
    Admin portal. `Read more
    <https://seller.flipkart.com/api-docs/FMSAPI.html#seller-registration>`_
    """
    def __init__(self, app_id, app_secret, sandbox=False):
        self.app_id = app_id
        self.app_secret = app_secret
        self.sandbox = sandbox

    @property
    def oauth_url(self):
        if self.sandbox:
            return 'https://sandbox-api.flipkart.net/oauth-service/'
        return 'https://api.flipkart.net/oauth-service/'

    @property
    def auth_endpoint(self):
        return self.oauth_url + 'oauth/authorize'

    @property
    def token_endpoint(self):
        return self.oauth_url + 'oauth/token'

    def get_client(self):
        return SanctionClient(
            auth_endpoint=self.auth_endpoint,
            token_endpoint=self.token_endpoint,
            client_id=self.app_id,
            client_secret=self.app_secret,
        )

    def get_token_from_client_credentials(self, scope=None):
        """
        Used when the application accesses API resources that it owns.

        :param scope: You can pass multiple scopes as comma separated values.

        .. note::

            Getting token using client credentials in basic auth does not seem
            to be Oauth2 standard. Impementing this outside of the auth client
        """
        return requests.get(
            self.token_endpoint,
            params={
                'grant_type': 'client_credentials',
                'scope': 'Seller_Api',
            },
            auth=(self.app_id, self.app_secret)
        ).json()


    def get_authorization_url(self, scope=None, redirect_uri=None, state=None):
        """
        Used to get a URL to redirect the user to a page where the user can
        authorize your application to use data in the user's account. Once the
        user grants (or denies) access, the user is redirected to the
        redirect_uri specified above.

        :param scope: You can pass multiple scopes as comma separated values.
        :param redirect_uri: The url to which the user has to be redirected
                             once access has been granted or denied to flipkart
        :param state: A random code to protect from CSRF.

        .. note::
            It is strongly encouraged that you use the state parameter to
            offer CSRF protection. It is also up to you to process the state
            parameter and handle redirection accordingly before calling
            request_token.
        """
        client = self.get_client()
        return client.auth_uri(
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
        )

    def get_token_from_authorization_code(self, code, state=None):
        """
        Once redirected back to your application with a short lived `code`,
        this method helps you exchange it for an access_token that can be used
        for making subsequent requests
        """
        return requests.get(
            self.token_endpoint,
            params={
                'grant_type': 'authorization_code',
                'code': code,
                'state': state,
            },
            auth=(self.app_id, self.app_secret)
        ).json()
