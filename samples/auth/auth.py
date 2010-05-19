#!/usr/bin/python
# coding: utf-8

import functools, cgi
from bottle import route, view, redirect, request, response, url, debug, app, run

secret = "contraseña secreta"


def get_auth_data():
    try:
        user = request.get_cookie("user", secret=secret)
        if isinstance(user, dict):
            return user['name'], None # usuario, password
    except: # en get_cookie, no es diccionario o no tiene clave 'name'
        print "Problema en get_auth_data"
    return None, None

def check_auth(user, password):
    return user is not None

def auth_required(check_auth=check_auth, login_url="/auth/login"):
    def decorator(handler, *a, **ka):
        @functools.wraps(handler)
        def wrapper(*a, **ka):
            try:
                user, token = get_auth_data()
                if check_auth(user, None):
                    request.environ['REMOTE_USER'] = user
                    return handler(*a, **ka)
                else:
                    redirect(login_url + "?next="+cgi.escape(request.url))
            except (KeyError, TypeError):
                print "excepción en auth_required, envío a login"
                redirect(login_url + "?next="+cgi.escape(request.url))
        return wrapper
    return decorator

AUTH_TPL="""
<html>
<body>
<div id="messages"><p>{{ msg }}
</p></div>
<form method='post' action="{{ url('login') }}">
Elija un usuario: <input name="user" type="text" value="{{user}}" />
<input name="next" type="hidden" value="{{next}}" />
<input name="login" type="submit" value="login" />
</form>
</body>
</html>
"""

@route("/auth/login", method='GET', name='login')
@view(AUTH_TPL, url=url)
def form():
    return dict(msg=request.params.get("msg",""),
                user=request.params.get("user",""),
                next=request.params.get("next",""))

@route("/auth/login", method='POST')
@view(AUTH_TPL, url=url)
def auth():
    user = request.params.get('user', '')
    if not user:
        redirect(url("login", request.params))
    response.set_cookie("user", dict(name=user), secret=secret, path="/")
    # Hacer proceso para nuevo usuario
    redirect(request.params.get('next','/'))

@route("/", name='principal')
@auth_required()
def main():
    return """%s está conectado.
        <a href="%s?msg=You+are+now+logged+out">Logout</a>
        """ % (request.environ['REMOTE_USER'], url('logout'))

@route("/auth/logout", name="logout")
@view(AUTH_TPL, url=url)
def logout():
    response.set_cookie("user", "", secret=secret, path="/", expires=-3600) # elimina la cookie
    query = '?msg=You+are+now+logged+out'
    return redirect(url("principal")+query)

debug(True)
run()

