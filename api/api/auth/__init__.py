# coding:utf-8


import urllib2
from pyramid.security import Authenticated, Everyone
from tokenlib import TokenManager


class MozillaTokenLibForHeaderAuthenticationPolicy(object):

    def _clean_principal(self, princid):
        if princid in (Authenticated, Everyone):
            princid = None
        return princid

    def __init__(self,
                 secret="secret",
                 callback=None,
                 timeout=None,
                 hashmod=None,
                 header_name='API_KEY'):
        self.manager = TokenManager(secret=secret,
                                    timeout=timeout,
                                    hashmod=hashmod)
        self.callback = callback
        self.header_name = header_name

    def authenticated_userid(self, request):
        userid = self.unauthenticated_userid(request)

        if userid is None:
            return None
        if self._clean_principal(userid) is None:
            return None
        if self.callback is None:
            return None
        callback_ok = self.callback(userid, request)
        if callback_ok is not None:
            return userid
        else:
            return None

    def unauthenticated_userid(self, request):
        api_value = request.headers.get(self.header_name, '')
        if api_value:
            data = self.manager.parse_token(api_value)
            return data['username']
        return None

    def effective_principals(self, request):

        effective_principals = [Everyone]
        username = self.unauthenticated_userid(request)

        if username is None:
            return effective_principals
        if self._clean_principal(username) is None:
            return effective_principals
        if self.callback is None:
            groups = []
        else:
            groups = self.callback(username, request)

        if groups is None:
            return effective_principals

        effective_principals.append(Authenticated)
        effective_principals.append(username)
        effective_principals.extend(groups)

        return effective_principals

    def remember(self, request, principal, **kw):
        return self.manager.make_token({'username': principal})

    def forget(self, request):
        return {}