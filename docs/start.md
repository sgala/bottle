Bottle: Python Web Framework
====================

<div style="float: right; padding: 0px 0px 2em 2em"><img src="/bottle-logo.png" alt="Botle Logo" /></div>

Bottle es un framework web [WSGI][] sencillo y rápido escrito en [Python][py] y distribuido en un solo fichero sin dependencias externas.

### Características principales

  * **Rutas:** Relacionan URLs a código usando una sintaxis de patrones simple y elegante.
  * **Plantillas:** *Motor* de plantillas **rápido** incluido, y soporte para plantillas [mako][], [jinja2][] y [cheetah][].
  * **Servidor:** Servidor HTTP para desarrollo includio, y soporte para [paste][], [fapws3][], [flup][], [cherrypy][] o cualquier otro servidor compatible con [WSGI][].
  * **Sin dependencias:** Todo en un solo archivo y sin otra dependencia que la librería estándar de Python.

  [mako]: http://www.makotemplates.org/
  [cheetah]: http://www.cheetahtemplate.org/
  [jinja2]: http://jinja.pocoo.org/2/
  [paste]: http://pythonpaste.org/
  [fapws3]: http://github.com/william-os4y/fapws3
  [flup]: http://trac.saddi.com/flup
  [cherrypy]: http://www.cherrypy.org/
  [WSGI]: http://www.wsgi.org/wsgi/
  [py]: http://python.org/
  [bottle-dl]: http://github.com/defnull/bottle/raw/master/bottle.py


### Descarga / Instalación

Se puede instalar la última revisión estable usando `easy_install -U bottle` o simplemente descargando la última versión de [bottle.py][bottle-dl] y poniéndola en el directorio del proyecto. No hay otras dependencias (requeridas) que la librería estándar de Python. Bottle funciona con **Python 2.5+ y 3.x** (usando 2to3).


## Características y ejemplos

No hace falta instalación o configuración. Tampoco otra dependencia que la librería estándar de Python. Consiga una copia de [bottle.py][bottle-dl], póngala en el directorio del proyecto y empiece a programar.

    #!Python
    from bottle import route, run
    
    @route('/')
    def index():
        return 'Hello World!'
    
    run() #default is localhost-only and port 8080

Eso es todo. Ejecute el código y visite [http://localhost:8080/](/localhost.png) con el navegador.

### Rutas

Se puede usar el decorador `@route()` para conectar URLs a las funciones manejadoras. El uso de parámetros con nombre permite producir URLs elegantes.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return 'Hello, %s' % name

### Plantillas

Bottle incluye un *motor* de plantillas sencillo y muy rápido llamado *SimpleTemplate*. Basta con devolver un diccionario con variables de la plantilla y pasarle el nombre de la plantilla al decorador `@view`. Por ejemplo, este sería el código:

    #!Python
    @route('/hello/template/:names')
    @view('hello')
    def template_hello(names):
       names = names.split(',')
       return dict(title='Hello World', names=names)

y esta la plantilla que se guarda en "./views/hello.tpl":

    #!html
    <html>
     <head>
      <title>{{title}}</title>
     </head>
     <body>
      %for name in names:
        <p>Hello, <strong>{{name}}</strong></p>
      %end
     </body>
    </html>

Bottle hace fácil cambiar a otros *motores* de plantilla. Se soportan [mako][], [jinja2][] y [cheetah][].

    #!Python
    from bottle import mako_view as view

### Ficheros estáticos, redirecciones y errores HTTP

Se pueden usar funciones auxiliares para facilitar tareas habituales:

    #!Python
    from bottle import send_file, redirect, abort
    
    @route('/static/:filename')
    def static_file(filename):
        send_file(filename, root='/path/to/static/files') # send static file

    @route('/wrong/url')
    def wrong():
        redirect("/right/url") # redirect to given URL

    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.") # give error 401

### POST, GET, Cabeceras y *Cookies*

Tan fácil manejarlos como usar un  diccionario (`dict()`)

    #!Python
    from bottle import request, response
    
    @route('/hello/cookie')
    def cookie():
        name = request.COOKIES.get('name', 'Stranger') # retrieve cookie
        response.header['Content-Type'] = 'text/plain' # set header
        return 'Hello, %s' % name

    @route('/hello/cookie', method='POST')
    def set_cookie():
        if 'name' in request.POST: # variable in POST body
            name = request.POST['name']
            response.COOKIES['name'] = name # set cookie with value
        return 'OK'


### Servidor HTTP

Bottle incluye un servidor HTTP, pero soporta también otros como [cherrypy][], 
[flup][], [paste][] y [fapws3][].

    #!Python
    from bottle import PasteServer
    run(server=PasteServer)
    
    
   
### Bugs conocidos y *rarezas*

Bottle **no** incluye (todavía):

  * Modelos and Gestores Objeto-Relacional (ORMs): Elege uno: SQLAlchemy, Elixir
  * HTML-Helper, Sesiones, Identificación y Autenticación: Hágalo usted mismo
  * Scaffolding: No tenemos de eso, lo siento


## Otras voces

[Kaelin](http://bitbucket.org/kaelin), 2009-10-22, [Comentario en PyPi](http://pypi.python.org/pypi/bottle):

> ¡Bottle mola! Es el camino más rápido que he encontrado entre idea e implementación para aplicaciones Web simples.

[Seth](http://blog.curiasolutions.com/about/) en sus [entradas](http://blog.curiasolutions.com/2009/09/the-great-web-development-shootout/) de [blog](http://blog.curiasolutions.com/2009/10/the-great-web-technology-shootout-round-3-better-faster-and-shinier/) sobre prestaciones de frameworks para web:

> Como puede verse no hay prácticamente diferencia de velocidad entre Bottle y WSGI *puro* en un test “hello world” básico. Incluso añadiendo Mako y SQLAlchemy, Bottle tuvo unas prestaciones significativamente más rápidas que un montaje simple con Pylons o Django. Por cierto, añadir una plantilla de ejemplo usando el paquete de plantillas por defecto de Bottle no pareció cambiar en absoluto esos números.

## Proyectos que usan Bottle

  * [whatismyencoding.com](http://whatismyencoding.com/) calcula la codificación de una cadena o del contenido de una URL.
  * [nagios4iphone](http://damien.degois.info/projects/nagios4iphone/) Una interfaz Nagios para iPhone sin modificar nada en los servidores Nagios.
  * [flugzeit-rechner.de](http://www.flugzeit-rechner.de/) corre con Bottle y Jinja2.
  * [Cuttlefish](http://bitbucket.org/kaelin/cuttlefish/) Una herramienta de búsqueda basada en navegador para hacer `grep` de código fuente rápidamente.
  * [Torque](http://github.com/jreid42/torque) Una interfaz multiusuario colaborativa para torrentes.
  * [Message in a Bottle](http://github.com/kennyshen/MIAB) Una aplicación simple de mensajería comunitaria que usa Bottle y Cassandra.
  * [ResBottle](http://github.com/tnm/redweb) Una interfaz web para  [Redis](http://code.google.com/p/redis/).

## Gracias a...

En orden cronológico descendente de su última contribución contribution.

  * [Jochen Schnelle](http://github.com/noisefloor) por su gran [tutorial de bottle](/page/tutorial)
  * [Damien Degois](http://github.com/babs) por el soporte a `If-Modified-Since` en `send_file()` y sus excelentes informes de errores
  * [Stefan Matthias Aust](http://github.com/sma) por su contribución a `SimpleTemplate` y `Jinja2Template`
  * [DauerBaustelle](http://github.com/dauerbaustelle) por sus ideas
  * [smallfish](http://pynotes.appspot.com/) por su traducción al chino de la documentación de bottle
  * [Johannes Schönberger](http://www.python-forum.de/user-6026.html) por su código de autorecarga
  * [clutchski](http://github.com/clutchski) por su `CGIAdapter` y el soporte a CGI
  * huanguan1978 por su informe de error sobre `send_file()` para windows y su parche
  * La [comunidad Python de Alemania](http://www.python-forum.de/topic-19451.html) por su soporte y motivación
  

## Licencia (MIT)

   Copyright (c) 2009, Marcel Hellkamp.

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

