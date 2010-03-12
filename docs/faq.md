[TOC]

# Preguntas de Uso Frecuente

[beaker]: http://beaker.groovie.org/

## Cómo implementar sesiones

No se incluye soporte para sesiones porque no hay una manera *buena* de
hacerlo. Según requerimientos y entorno se podría usar el middleware [beaker][]
con un sustrato (*backend*) adecuado, o bien implementarlas uno mismo.

Por ejemplo, así podrían implementarse sessiones basadas en archivos con beaker.

    #!Python
    import bottle
    from beaker.middleware import SessionMiddleware

    app = bottle.default_app()
    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    }
    app = SessionMiddleware(app, session_opts)

    @bottle.route('/test')
    def test():
      s = bottle.request.environ.get('beaker.session')
      s['test'] = s.get('test',0) + 1
      s.save()
      return 'Test counter: %d' % s['test']

    bottle.run(app=app)



## Cómo usar un middleware de depuración

Bottle captura todas las excepciones lanzadas por el código de aplicación, de forma que el servidor WSGI no *se cuelgue*. Se puede cambiar este comportamiento si se necesita propagar las excepciones a un *middleware* de depuración.

    #!Python
    import bottle
    app = bottle.app() # o bottle.default_app() para versiones anteriores a 0.7
    app.catchall = False
    myapp = DebuggingMiddleware(app)
    bottle.run(app=myapp)

Ahora bottle capturará sólo sus propias excepciones (`HTTPError`, `HTTPResponse` y `BottleException`) y su *middleware* puede manejar el resto.




## Cómo llamar una aplicación WSGI desde bottle

Esta no es la manera recomendada de hacerlo, ya que se debería usar un *middleware* delanta de bottle para ello, pero se puede llamar a otras aplicaciones WSGI desde su aplicación bottle, permitiendo así a bottle funcionar como un *pseudo-middleware*. Véase un ejemplo:

    #!Python
    from bottle import request, response, route
    subproject = SomeWSGIApplication()

    @route('/subproject/:subpath#.*#', method='ALL')
    def call_wsgi(subpath):
        new_environ = request.environ.copy()
        new_environ['SCRIPT_NAME'] = new_environ.get('SCRIPT_NAME','') + '/subproject'
        new_environ['PATH_INFO'] = '/' + subpath
        def start_response(status, headerlist):
            response.status = int(status.split()[0])
            for key, value in headerlist:
                response.header.append(key, value) # or .add_header() with bottle < 0.7
      return app(new_environ, start_response)

De nuevo: esta **no es la manera recomendada** de implementar subproyectos. Ponemos este ejemplo aquí porque mucha gente preguntó por la manera de hacerlo, y también para mostrar cómo se enlaza bottle con WSGI.

## Cómo ignorar las barras inclinadas al final de la URL

Bottle no ignora  barras inclinadas ("/") al final de la URL por defecto. 
Para hacer que URLs como `/ejemplo` and `/ejemplo/` se traten igual, 
se puede poner dos decoradores `@route`

    #!Python
    @route('/test')
    @route('/test/')
    def test(): pass

o usar expresiones regulares en rutas dinámicas

    #!Python
    @route('/test/?')
    def test(): pass

o añadir un *middleware* WSGI que elimine las barras ('/') finales de las URLs

    #!Python
    class StripPathMiddleware(object):
      def __init__(self, app):
        self.app = app
      def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)
    
    app = bottle.app()
    app = StripPathMiddleware(app)
    bottle.run(app=app)






## mod_python y "Template Not Found"

Bottle busca plantillas en "./" y en "./views/". Cuando se usa mod_python el 
directorio de trabajo ('.') depende de la configuración de Apache. Se debería
añadir un camino absoluto al camino de búsqueda

    #!Python
    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/')

o bien cambiar el directorio de trabajo

    #!Python
    os.chdir(os.path.dirname(__file__))

de forma que bottle busque en los directorios correctos.

