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

Use the `@route()` decorator to bind URLs to your handler functions. Named parameters may be used to produce nice looking URLs.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return 'Hello, %s' % name

### Templates

Bottle includes a simple and lightning fast template engine called *SimpleTemplate*. Just return a dictionary filled with template variables and pass a template name to the `@view` decorator.

    #!Python
    @route('/hello/template/:names')
    @view('hello')
    def template_hello(names):
       names = names.split(',')
       return dict(title='Hello World', names=names)

And here is the template in "./views/hello.tpl":

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

Bottle makes it easy to switch to other template engines. [mako][], [jinja2][] and [cheetah][] are supported.

    #!Python
    from bottle import mako_view as view

### Static Files, Redirects and HTTP Errors

Use these handy helpers for regular tasks.

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

### POST, GET, Header and Cookies

As easy as using a `dict()`

    #!Python
    from bottle import request, response
    
    @route('/hello/cookie')
    def cookie():
        name = request.COOKIES.get('name', 'Stranger')
        response.header['Content-Type'] = 'text/plain'
        return 'Hello, %s' % name

    @route('/hello/cookie', method='POST')
    def set_cookie():
        if 'name' in request.POST:
            name = request.POST['name']
            response.COOKIES['name'] = name
        return 'OK'


### HTTP Server

Bottle has a HTTP Server build in but also supports [cherrypy][], 
[flup][], [paste][] and [fapws3][] as alternatives.

    #!Python
    from bottle import PasteServer
    run(server=PasteServer)
    
    
   
### Non-Features and Known Bugs

Bottle does **not** include (yet):

  * Models and ORMs: Choose your own (SQLAlchemy, Elixir)
  * HTML-Helper, Session, Identification and Authentication: Do it yourself
  * Scaffolding: No, sorry


## Voices

[Kaelin](http://bitbucket.org/kaelin), 2009-10-22, [PyPi Comment](http://pypi.python.org/pypi/bottle):

> Bottle rocks! The fastest path I've found between idea and implementation for simple Web applications.

[Seth](http://blog.curiasolutions.com/about/) in his [blog](http://blog.curiasolutions.com/2009/09/the-great-web-development-shootout/) [posts](http://blog.curiasolutions.com/2009/10/the-great-web-technology-shootout-round-3-better-faster-and-shinier/) about common web framework performance:

> As you can see, there was practically no difference in speed between Bottle and pure WSGI in a basic “hello world” test. Even with the addition of Mako and SQLAlchemy, Bottle performed significantly faster than a bare Pylons or Django setup. On a side note, adding a sample template using Bottle’s default templating package didn’t seem to change these numbers at all.

## Projects using Bottle

  * [whatismyencoding.com](http://whatismyencoding.com/) guesses the encoding of an URL or string.
  * [nagios4iphone](http://damien.degois.info/projects/nagios4iphone/) A Nagios interface for iPhone without touching anything on your nagios servers.
  * [flugzeit-rechner.de](http://www.flugzeit-rechner.de/) runs on Bottle and Jinja2.
  * [Cuttlefish](http://bitbucket.org/kaelin/cuttlefish/) A browser-based search tool for quickly `grep`ing source code.
  * [Torque](http://github.com/jreid42/torque) A multiuser collaborative interface for torrenting.
  * [Message in a Bottle](http://github.com/kennyshen/MIAB) A simple community messaging app using Bottle and Cassandra.
  * [ResBottle](http://github.com/tnm/redweb) A [Redis](http://code.google.com/p/redis/) web interface.

## Thanks to

In chronological order of their last contribution (DESC).

  * [Jochen Schnelle](http://github.com/noisefloor) for his great [bottle tutorial](/page/tutorial)
  * [Damien Degois](http://github.com/babs) for his `If-Modified-Since` support in `send_file()` and his excellent bug reports
  * [Stefan Matthias Aust](http://github.com/sma) for his contribution to `SimpleTemplate` and `Jinja2Template`
  * [DauerBaustelle](http://github.com/dauerbaustelle) for his ideas
  * [smallfish](http://pynotes.appspot.com/) for his chinese translation of the bottle documentation
  * [Johannes Schönberger](http://www.python-forum.de/user-6026.html) for his auto reloading code
  * [clutchski](http://github.com/clutchski) for his `CGIAdapter` and CGI support
  * huanguan1978 for his windows `send_file()` bug report and patch
  * The [German Python Community](http://www.python-forum.de/topic-19451.html) for their support and motivation
  

## Licence (MIT)

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

