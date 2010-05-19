[TOC]

#Mini-Howto

##Cómo implementar autenticación en Bottle

Existen muchas posibles maneras de hacerlo. De hecho
se usan muchas formas de autenticación distintas, cada
una con sus ventajas e inconvenientes.

[authkit]: http://authkit.org/

En particular, hay muchas librerías que permiten implementar autenticación HTTP
usando middleware WSGI en python, por ejemplo [authkit][]. Para explotación
recomendamos o bien las facilidades del framework o librería que estemos usando o bien
una librería como authkit.

##Conceptos

Existen distintas maneras de autenticación en aplicaciones web. Comencemos 
por unos principios generales:

- Como HTTP es un protocolo cliente-servidor y el concepto de *sesión*
  es limitado, normalmente se debe autenticar cada petición por separado
- La autenticación especificada por el protocolo (RFC2617) se hace mediante
  una combinación de códigos de respuesta y cabeceras

###Autenticación HTTP

Cuando un servidor requiere autenticación para una petición de acceso
a un recurso, responde a la petición con el código ``401 Authentication Required``,
y además añade una cabecera indicando el método de autenticación que acepta,
``WWW-Authentication: Basic realm="Dominio"``, donde Basic indica el
**metodo** aceptado y el parámetro realm indica a qué dominio se refiere la autenticación. De esa manera un servidor puede tener distintos dominios de autenticación, y soportar diferentes métodos.

El navegador, al recibir esta respuesta, busca en su memoria la pareja servidor/método/dominio, y si tiene usuario y contraseña se repite la petición con la cabecera
``Authenticate: Basic <token>``, donde <token> es usuario:contraseña codificado 
usando Base64. Si no la tiene lanza una ventana emergente donde la pregunta al
usuario. Esa cabecera se mantendrá en todas las peticiones al mismo par
servidor/dominio hasta que se cierre el navegador.

El método básico es bastante débil si se puede ver el tráfico, por lo que
se suele usar en combinación con cifrado (https). Existen otros métodos de
autenticación, menos usados.

###Autenticación basada en formularios

La autenticación HTTP no resultó en su momento del agrado de los
responsables de sitios web, fundamentalmente porque la ventana emergente
del navegador no indicaba, aparte de los nombres de *servidor* y *dominio*, a dónde se estaba haciendo autenticación, y también por requerir dos "viajes" del cliente al servidor por cada acceso autenticado.

Se desarrolló un método alternativo, consistente en el uso de formularios HTML
combinados con cookies que contienen valores criptográficamente
difíciles de replicar (*tokens*).

Vamos a desarrollar un ejemplo particularmente simple de autenticación con bottle,
usando *cookies*.


Para autenticar peticiones HTTP usando cookies el servidor almacena
una cookie en el cliente como resultado de un proceso en el que el usuario
*demuestra* su identidad. A partir de ese momento, y hasta que se borre o expire
la cookie, el navegador permanece autenticado.

Imaginemos que tenemos una función que nos dice
cual es el usuario actual:

    #!Python
    def get_auth_data():
        try:
            user = request.get_cookie("user", secret) # Cookie segura
            if isinstance(user, dict):
                return user['name'], None # usuario, token
        except: # en get_cookie, no es diccionario o no tiene clave 'name'
            print "Problema en get_auth_data"
        return None

Entonces este código en todos nuestros manejadores *protegidos*
hará que las peticiones sin usuario vayan a una url de login:

    :::python
    ...
    login_url = '/auth/login'
    try:
        user, token = request.get_auth_data() #get auth data
        auth = check_auth(user, password)
        if not auth:
            redirect(login_url)
        request.environ['REMOTE_USER'] = user
        return result
    except:
        redirect(login_url)
    ... # devolver resultado

Eso sería todo lo necesario, pero no es conveniente tener que
copiar fragmentos de texto de unos controladores a otros, sin
olvidar lo que significa cambiar ese código cada vez.

Una función puede resumir ese código. Por ejemplo la siguiente,
donde `handler()` es nuestro controlador o *callback*:

    #!Python
    def check_auth(*a, **ka):
        try:
            user = get_auth_data() # ignoramos password
            request.environ['REMOTE_USER'] = user
        except:
            redirect(login_url)
        return handler(*a, **ka)


No es demasiado difícil *envolver* esa función en un decorador para
poder añadirlo a cada controlador. Veamos un ejemplo completo: el código
desde este punto hasta el final debería poder ejecutarse como una 
aplicación bottle muy simple.

    #!Python
    #!/usr/bin/python
    # coding: utf-8

    import functools, cgi
    from bottle import route, view, redirect, request, response, url, debug, app, run

    secret = "contraseña secreta"

    def get_auth_data():
        try:
            user = request.get_cookie("user", secret)
            if isinstance(user, dict):
                return user['name'], None # usuario, password
        except: # en get_cookie, no es diccionario o no tiene clave 'name'
            print "Problema en get_auth_data"
        return None

    def auth_required(check_auth, login_url="/auth/login"):
        def decorator(handler, *a, **ka):
            @functools.wraps(handler)
            def check_auth(*a, **ka):
                try:
                    user = get_auth_data()
                    request.environ['REMOTE_USER'] = user['name']
                except (KeyError, TypeError):
                    redirect(login_url + "?next="+cgi.escape(request.url))
                return handler(*a, **ka)
            return check_auth
        return decorator

`auth_required` es un decorador que, cuando se llama con una url de
login, por defecto `/auth/login`, devuelve una función (`decorator`)
que toma un argumento obligatorio (`handler`, nuestro manejador) y
devuelve la función `check_auth` con las variables `login_url` y `handler`
*ligadas* a los valores correspondientes; justo lo que necesitamos.

Se usaría en combinación con `get_auth_data()` y una ruta de login.
Por simplicidad se incluye la plantilla de formulario en una variable
(AUTH_TPL) en el código python:

    #!html+django
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
    
y con las rutas que se exponen a continuación. La ruta `GET`
sirve el formulario y la ruta `POST` procesa el nombre
de usuario (**sin contraseña, se trata de un ejemplo sencillo**) 

    #!Python
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

Un principal que funciona:

    #!Python
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

Como un ejemplo de a dónde se podría ir fácilmente desde este ejemplo,
la típica casilla de ``recuérdame en esta máquina`` se podría implementar
fácilmente añadiéndole a la set_cookie un ``expires=3600*24*30*3``, que
haría la autenticación válida durante 90 días. El código de este tutorial se
encuentra en ``samples/auth/auth.py`` en el repositorio, en la rama
``laboratorio-servicios-web``.
