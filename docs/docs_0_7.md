[TOC]

  [apache]: http://www.apache.org/
  [cherrypy]: http://www.cherrypy.org/
  [decorator]: http://docs.python.org/glossary.html#term-decorator
  [fapws3]: http://github.com/william-os4y/fapws3
  [flup]: http://trac.saddi.com/flup
  [http_code]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
  [http_method]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
  [mako]: http://www.makotemplates.org/
  [mod_wsgi]: http://code.google.com/p/modwsgi/
  [paste]: http://pythonpaste.org/
  [wsgi]: http://www.wsgi.org/wsgi/

# Documentación de Bottle

__Este documento está sujeto a cambio permanente__ y trata de ser una guía de uso, una guía *cómo* y documentación de la api. Si tiene cuestiones sin respuesta en este documento, compruebe si están en las [P.U.F. (F.A.Q.)](/page/faq) o bien escriba un informe de error en el [sistema de errores](http://github.com/defnull/bottle/issues) de bottle.

Esta documentación describe las características de la **versión 0.7**. Puede consultar los [documentos de la versión 0.6.4](/page/docs) en inglés.


## "Hola, Mundo" en una botella

Comencemos por un ejemplo muy sencillo: el *clásico* **Hola, Mundo**

    #!Python
    from bottle import route, run
    @route('/hello')
    def hello():
        return "¡Hola, Mundo!"
    run() # This starts the HTTP server

Ejecute este *script* y luego visite <http://localhost:8080/hello> y verá "¡Hola, Mundo!" en su navegador. ¿Qué ha pasado al lanzarlo?

  1. Primero importamos algunos componentes de bottle. El decorador `route()` y la función `run()`. 
  2. El [decorador][decorator] `route()` se usa para conectar parte de nuestro código a una URL. En este  ejemplo queremos responder peticiones que se hagan a la URL `/hello`.
  3. Se llamará a esta función cada vez que alguien pida la URL `/hello` en el servidor. Se llama una __función controladora__ (*handler* o *callback*).
  4. El valor que devuelva una función controladora se envía de vuelta al navegador.
  5. Ahora podermos arrancar el servidor HTTP. Por defecto se arrancará un servidor de desarrollo que corre __sólo__ en *localhost*, en el puerto *8080*. Servirá peticiones hasta que pulsemos __Ctrl-C__.




# Rutas

Se usan rutas para conectar una URL a una función (*callback*) que genera el contenido de esa URL específica. Bottle tiene un decorador `route()` que hace eso. Se le puede añadir cualquier número de rutas a una función controladora.

    #!Python
    from bottle import route
    @route('/')
    @route('/index.html')
    def index():
        return "<a href='/hello'>Ir a la página 'Hola, Mundo'</a>"

    @route('/hello')
    def hello():
        return "¡Hola, Mundo!"

Como puede ver, las URLs y las rutas no tienen nada que ver con ficheros reales en el servidor web. Las rutas son nombres únicos para las funciones controladoras, nada más y nada menos. Las peticiones a URLs que no encajen con ninguna ruta se responden con una página de error HTTP 404. Las exceptions que ocurran dentro de una función controladora causarán una respuesta de error HTTP 500. 





## Métodos de petición HTTP

El decorador `route()` tiene un argumento opcional con nombre, llamado `method`, que toma como valor por defecto `method='GET'`; eso quiere decir que sólo se reponden peticiones de tipo GET por esa ruta.
Los valores posibles de ese argumento son `POST`, `PUT`, `DELETE`, `HEAD`, o cualquier otro [método de HTTP][http_method] que queramos responder. Se puede usar también `ANY` para crear una ruta que se usará para cualquier método que no tenga una específica. Como una alternativa al parámetro `method` se pueden usar los decoradores `@get()`, `@post()`, `@put()` y `@delete()`.

    #!Python
    from bottle import post, request
    @post('/form/submit')
    def form_submit():
        form_data = request.POST # (*)
        do_something_with(form_data)
        return "Done"

\* En este ejemplo usamos [request.POST](#working-with-http-requests) para acceder a  datos del formulario POST.

Nótese que las peticiones `HEAD` se responden con la ruta `GET` si no tienen una específica. Como ya dijimos, cualquier petición se procesará en la ruta `ANY` si no existe una ruta para el método de petición original.






## Rutas Dinámicas

Las rutas estáticas están bien, per las URLs pueden también incluir información. Vamos a añadirle una variable `:name` a nuestra ruta.

    #!Python
    from bottle import route
    @route('/hello/:name')
    def hello(name):
        return "¡Hola, %s!" % name

Esta ruta dinámica se aplica a `/hello/alice` y también a `/hello/bob`. De hecho, la parte `:name` *captura* cualquier cosa que no sea una barra inclindad (`/`), así que podemos usar cualquier nombre. `/hello/bob/and/alice` o `/hellobob` no funcionan. Cada parte de la URL que *encaja* en una variable le llega a la función controladora como argumento con nombre, usando el nombre tras los `:`.

Una variable normal captura cualquier cosa hasta la siguiente barra inclinada. Para cambiarlo, se puede añadir un patrón en forma de expresión regular:

    #!Python
    from bottle import route
    @route('/get_object/:id#[0-9]+#')
    def get(id):
        return "ID de Objeto: %d" % int(id)

Se puede ver que los parámetros de URL siguen siendo cadenas, incluso cuando hacemos que sólo los enteros *encajen*. Hay que convertirlos explícitamente al tipo que necesitemos.




## El decorador @validate()

Bottle ofrece también un decorador muy cómodo, llamado `validate()`, para comprobar y manipular parámetros de la URL. Acepta un *llamable* (funciones or clases) como argumentos con nombre, y filtra el parámetro de la URL de ese nombre a través del *llamable* antes de pasarlos al manejador de peticiones.

    #!Python
    from bottle import route, validate
    # /test/validate/1/2.3/4,5,6,7
    @route('/test/validate/:i/:f/:csv')
    @validate(i=int, f=float, csv=lambda x: map(int, x.split(',')))
    def validate_test(i, f, csv):
        return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))

Se puede lanzar (`raise`) la excepción `ValueError` en los llamables que escribamos si un parámetro no valida correctamente.




# Generación de contenido

La [epecificación WSGI][wsgi] espera que la aplicación devuelva un iterable que produzca una secuencia de cadenas de bytes, y no sabe manejar ficheros, unicode, diccionarios or excepciones.

    #!Python
    @route('/wsgi')
    def wsgi():
        return ['WSGI','quiere una','lista de','cadenas']

Bottle intenta automáticamente convertir el resultado de nuestra manejadora a un tipo soportado por WSGI, de forma que nosotros no tengamos que hacerlo.
Los ejemplos siguientes funcionarán con Bottle, pero fallarán si usamos una herramienta de  desarrollo WSGI *pura*.

## Cadenas y Unicode

Devolver cadenas (de bytes) no es un problema. Si usamos unicode, en cambio, necesitamos codificarlo en una cadena de bytes antes de que el servidor web pueda enviarlo a los clientes. La codificación por defecto es __utf-8__. Si eso no supone un problema, se puede simplemente devolver cadenas unicode, o bien iterables que produzcan unicode, o cadenas unicode.

    #!Python
    @route('/string')
    def get_string():
        return 'Bottle convierte las cadenas en iterables'
    
    @route('/unicode')
    def get_unicode():
        return u'El unicode se codifica usando UTF-8 por defecto'

Se puede cambiar la codificación por defecto de Bottles cambiando el valor de `response.content_type` a un valor que contenga un parámetro `charset=...` o cambiando directamente `response.charset`.

    #!Python
    from bottle import response
    @route('/iso')
    def get_iso():
        response.charset = 'ISO-8859-15'
        return u'This will be sent with ISO-8859-15 encoding.'

    @route('/latin9')
    def get_latin():
        response.content_type = 'text/html; charset=latin9'
        return u'ISO-8859-15 is also known as latin9.'

En algunos casos raros los nombres de las codificaciones de Python difieren de los nombres soportados en la especificación HTTP. En ese caso hay que hacer ambas cosas: primero cambiar la cabecera `response.content_type`, que se envía al cliente sin cambiar, y también poner la opción `response.charset`, que se utiliza para decodificar unicode.

## Ficheros y flujos de bytes (*streams*)

Bottle pasa todo objeto que tenga un método `read()` (objetos de tipo `file`) al `wsgi.file_wrapper` que proporciona la implementación de servidor WSGI. Este *llamable* debería usar llamadas al sistema optimizadas (por ejemplo `sendfile` en UNIX) para transferir los contenidos del fichero.

    #!Python
    @route('/file')
    def get_file():
        return open('some/file.txt','r')

## JSON

También pueden devolverse diccionarios. Se convierten en [json](http://de.wikipedia.org/wiki/JavaScript_Object_Notation) y se devuelven con la cabecera `Content-Type` puesta a `application/json`. Para deshabilitar esta característica, y pasar, por ejemplo, diccionarios a algún *middleware*, se puede poner `bottle.app().autojson` a `False`.

    #!Python
    @route('/api/status')
    def api_status():
        return {'status':'online', 'servertime':time.time()}

## Ficheros estáticos

Ya hemos dicho que se puede devolver directamente ficheros (objetos de tipo `file`). Sin embargo la manera recomendada de servir ficheros estáticos es `static_file()`. Automáticamente adivina el tipo de media de internet (MIME), añade una cabecera `Last-Modified`, restringe las rutas a un directorio raiz (`root`) por razones de seguridad y genera las respuestas de error apropiadas: 401 para los errores de permisos, 404 si falta el fichero. Incluso soporta la cabecera `If-Modified-Since` y genera en caso necesario una respuesta `304 Not modified`. Se le puede pasar un `mimetype` para deshabilitar el intento de adivinarlo.

    #!Python
    from bottle import static_file

    @route('/images/:filename#.*\.png#')
    def send_image(filename):
        return static_file(filename, root='/path/to/image/files', mimetype='image/png')
    
    @route('/static/:filename')
    def send_file(filename):
        return static_file(filename, root='/path/to/static/files')

EL valor que devuelve `static_file()` se puede lanzar (`raise`) como excepción si es necesario. Bottle sabe manejar la excepción `HTTPResponse`. 

## HTTPError, HTTPResponse y redirecciones

La función `abort(code[, message])` se usa para generar [páginas de error HTTP][http_code].

    #!Python
    from bottle import route, redirect, abort
    @route('/restricted')
    def restricted():
        abort(401, "Lo siento, se le deniega el acceso.")

Para reenviar un cliente a una URL distinta, se puede enviar una respuesta `303 See Other` con la cabecera `Location` indicando la nueva URL. `redirect(url[, code])` hace exactamente eso. Se puede proporcionar otro código de estado HTTP como un segundo parámetro.

    #!Python
    from bottle import redirect
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")

Ambas funcionees terminan la ejecución del código manejador, ya que lanzan una excepción de tipo `HTTPError`.

Se puede también devolver excepciones `HTTPError` en vez de usar `raise`. Es más rápido que lanzar y capturar excepciones, y hace exactamente lo mismo.

    #!Python
    from bottle import HTTPError

    @route('/denied')
    def denied():
        return HTTPError(401, '¡Acceso denegado!')

## Excepciones

Cualquier excepción distinta de `HTTPResponse` o `HTTPError` resultará en una respuesta de tipo `500 Internal Server Error`, que bottle captura para que no aborte el servidor WSGI. Se puede eliminar este comportamiento, de manera que se puedan manejar excepciones en el middleware dándole a `bottle.app().catchall` el valor `False`.

# Manejo de peticiones HTTP

Bottle analiza los datos de la petición HTTP y los almacena en un objeto `request` seguro con respecto a hilos (*thread-safe*) y proporciona algunas herramientas y métodos útiles para acceder a esos datos. La mayor parte del análisis ocurre sólo se se piden resultados, de manera que no se gastan recursos si no se necesita el resultado. Un corto resumen:

  * `request[key]`: Atajo en lugar de escribir `request.environ[key]`
  * `request.environ`: El diccionario de entorno WSGI. Úsese cuidadosamente.
  * `request.app`: La instancia actual de Bottle (lo mismo que `bottle.app()`)
  * `request.method`: Método de petición HTTP (GET,POST,PUT,DELETE,...).
  * `request.query_string`: Cadena de petición HTTP (http://host/path?query_string)
  * `request.path`: Parte del camino que se emparejó en la ruta actual.
  * `request.fullpath`: Camino completo, incluyendo la parte `SCRIPT_NAME` (nombre del script).
  * `request.url`: La URL completa que pidió el cliente (incluye `http(s)://` y el nombre de host)
  * `request.input_length` La cabecera Content-Length (si está presente) como un entero.
  * `request.header`: Diccionario de cabeceras HTTP.
  * `request.GET`: El contenido de `request.query_string` analizado como un `dict`. Cada valor puede ser una cadena o una lista de cadenas.
  * `request.POST`: Un `dict` que contiene datos de formulario analizados. Soporta tanto  URL-encoded como multipart-encoded. Cada valor puede ser una cadena, un fichero o una lista de cadenas o ficheros.
  * `request.COOKIES`: Las *cookies* como un `dict`.
  * `request.params`: Un `dict` que contiene tanto los datos de `request.GET` como los de `request.POST`. Si un valor está en los dos, se usan los datos de **POST**.
  * `request.body`: El cuerpo HTTP de la petición como un objeto de tipo `buffer`.
  * `request.auth`: Los datos de autorización HTTP como una tupla con nombre (`collections.namedtuple`). (experimental)
  * `request.get_cookie(key[, default])`: Devuelve una cookie específica, y decodifica *cookies* seguras. (experimental)


## *Cookies* ("galletitas")

Bottle almacena las *cookies* que envía el cliente en un diccionario llamado `request.COOKIES`. Para crear nuevas *cookies* se usa el método `response.set_cookie(name, value[, **params])`. Acepta parámetros adicionales siempre que sean atributos válidos para la cooke, soportados por la librería [SimpleCookie](http://docs.python.org/library/cookie.html#morsel-objects).

    #!Python
    from bottle import response
    response.set_cookie('key','value', path='/', domain='example.com', secure=True, expires=+500, ...)

Para dar valor al atributo `max-age` utilice el nombre `max_age`.

TODO: Se puede almacenar objetos python y listas en las *cookies*. Cuando se hace así se producen *cookies* firmadas, que se codifican y decodifican, con `pickle`, automáticamente. 

## Valores GET y POST

La cadena de petición (*query string*) y/o los datos de formularios POST se analizan y se guardan en diccionarios, disponibles como `request.GET` y `request.POST` respectivamente. Pueden aparecer valores múltiples por cada clave, así que cada valor de esos diccionarios puede contener tanto una cadena como una lista de cadenas.

Se puede usar `.getone(key[, default])` para estar seguro de que devuelve un sólo valor.

    #!Python
    from bottle import route, request
    @route('/search', method='POST')
    def do_search():
        query = request.POST.getone('query', '').strip()
        if not query:
            return "No proporcionó una variable 'query' en la petición."
        else:
            return 'Buscó Vd. %s.' % query


## Subida de ficheros

Bottle maneja la subida de ficheros de forma similar a los datos de formularios POST. En lugar de una cadena, se encontrará un objeto parecido a un fichero. 

    #!Python
    from bottle import route, request
    @route('/upload', method='POST')
    def do_upload():
        datafile = request.POST.get('datafile')
        return datafile.read()

El siguiente formulario HTML se puede usar para subir ficheros en combinación con el manejador del ejemplo anterior:

    #!html
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input name="datafile" type="file" />
    </form>



# Plantillas

Bottle usa por defecto su propio pequeño *motor* de plantillas. Se puede usar una plantilla llamando `template(template_name, **template_arguments)` y devolviendo el resultado.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return template('hello_template', username=name)

El ejemplo anterior cargará la plantilla `hello_template.tpl` dándole a la variable `username` la parte `:name` de la URL, y devolverá el resultado como una cadena.

El fichero `hello_template.tpl` podría tener este aspecto:

    #!html
    <h1>Hola {{username}}</h1>
    <p>¿Cómo estás?</p>




## Camino de búsqueda de plantillas

La lista `bottle.TEMPLATE_PATH` se utiliza para mapear nombres de plantilla a nombres de fichero. Por defecto, esta lista contiene `['./%s.tpl', './views/%s.tpl']`.




## Caché de plantillas

La plantillas se salvan en memoria después de compilarlas. Las modificaciones que se le hagan al fichero de la plantilla no tendrán efecto hasta que se borre la caché de plantillas. Para hacerlo llame a `bottle.TEMPLATES.clear()`.




## Sintaxis de las plantillas

La sintaxis de las plantillas es una capa muy fina sobre el lenguaje Python. 
Su propósito principal es asegurar la indentación correcta de los bloques, de manera que se pueda dar formato a la plantilla sin tener que preocuparse por el sangrado. Véase la descripción completa de la sintaxis:

  * `%...` comienza una línea de código Python. No hay que preocuparse por el sangrado, Bottle lo maneja.
  * `%end` cierra un bloque de Python abierto usando `%if ...`, `%for ...` o bien otras sentencias de bloque. Se requiere cerrar los bloques explícitamente.
  * `{{...}}` imprime el resultado de la expresión python incluida.
  * `%include template_name argumentos_opcionales` permite incluir otras plantillas.
  * El resto de las líneas se devuelve como texto.

Ejemplo:

    #!html
    %header = 'Test Template'
    %items = [1,2,3,'fly']
    %include http_header title=header, use_js=['jquery.js', 'default.js']
    <h1>{{header.title()}}</h1>
    <ul>
    %for item in items:
      <li>
        %if isinstance(item, int):
          Zahl: {{item}}
        %else:
          %try:
            Other type: ({{type(item).__name__}}) {{repr(item)}}
          %except:
            Error: Item has no string representation.
          %end try-block (yes, you may add comments here)
        %end
        </li>
      %end
    </ul>
    %include http_footer




# Bases de Datos Clave/Valor

<div style="color:darkred">Advertencia: La base de datos clave/valor incluida está deprecada.</div>

Utilice por favor una [base de datos](http://code.google.com/p/redis/) [clave](http://couchdb.apache.org/)/[valor](http://www.mongodb.org/) [real](http://docs.python.org/library/anydbm.html).




# Uso de WSGI y *middleware*

Una llamada a `bottle.default_app()` devuelve la aplicación WSGI asociada con Bottle. Tras aplicar tantos módulos de *middleware* como se desee, se le puede decir a Bottle `bottle.run()` para lanzar la applicación *envuelta*, en lugar de la aplicación por defecto.

    #!Python
    from bottle import default_app, run
    app = default_app()
    newapp = YourMiddleware(app)
    run(app=newapp)




## Cómo funciona default_app()

Bottle crea una sóla instancia de `bottle.Bottle()` y la usa como valor por defecto para la mayoría de los decoradores definidos a nivel de módulo y la rutina `bottle.run()`. 
`bottle.default_app()` devuelte (o cambia) ese valor por defecto. Se puede también crear nuestras propias instancias de `bottle.Bottle()`.

    #!Python
    from bottle import Bottle, run
    mybottle = Bottle()
    @mybottle.route('/')
    def index():
      return 'default_app'
    run(app=mybottle)




# Desarrollo
Bottle tiene dos características que pueden ser útiles durante la fase de desarrollo de aplicaciones web.

## Modo de depuración

En modo de depuración bottle es mucho más locuaz, e intenta ayudar a encontrar errores. Nunca se debe usar el modo de depuración en un entorno de producción.

    #!Python
    import bottle
    bottle.debug(True)

El modo de depuración hace lo siguiente:

  * Las excepciones imprimirán una traza de la pila en la salida estándar
  * Las páginas de error contendrán esa traza
  * Las plantillas no se cachean, se recargan cada vez.




## Auto recarga

Durante el desarrollo es necesario rearrancar el servidor con frecuencia para probar los cambios recientes. El *autorecargador* (*autoreloader*) puede hacerlo por nosotros automáticamente. Cada vez que se edite un fichero de código, el recargadaor reinicia el proceso del servidor y carga la última versión del código. 

    #!Python
    from bottle import run
    run(reloader=True)

Veamos cómo funciona: El proceso principal no arranca un servidor, sino que lanza un proceso hijo con los mismos argumentos de línea de comandos que se usaron para arrancar el proceso principal. Al actuar así, hay que tener cuidado: ¡Todo el código en el nivel de módulo se ejecuta al menos dos veces!.

El proceso hijo tendrá definido `os.environ['BOTTLE_CHILD']` con el valor `true` 
y comenand start as a normal non-reloading app server. As soon as any of the 
loaded modules changes, the child process is terminated and respawned by 
the main process. Changes in template files will not trigger a reload. 
Please use debug mode to deactivate template caching.

The reloading depends on the ability to stop the child process. If you are
running on Windows or any other operating system not supporting 
`signal.SIGINT` (which raises `KeyboardInterrupt` in Python), 
`signal.SIGTERM` is used to kill the child. Note that exit handlers and 
finally clauses, etc., are not executed after a `SIGTERM`.




# Deployment

Bottle uses the build-in `wsgiref.SimpleServer` by default. This non-threading
HTTP server is perfectly fine for development and early production,
but may become a performance bottleneck when server load increases.

There are three ways to eliminate this bottleneck:

  * Use a multi-threaded server adapter
  * Spread the load between multiple bottle instances
  * Do both




## Multi-Threaded Server

The easiest way to increase performance is to install a multi-threaded and
WSGI-capable HTTP server like [Paste][paste], [flup][flup], [cherrypy][cherrypy]
or [fapws3][fapws3] and use the corresponding bottle server-adapter.

    #!Python
    from bottle import PasteServer, FlupServer, FapwsServer, CherryPyServer
    bottle.run(server=PasteServer) # Example
    
If bottle is missing an adapter for your favorite server or you want to tweak
the server settings, you may want to manually set up your HTTP server and use
`bottle.default_app()` to access your WSGI application.

    #!Python
    def run_custom_paste_server(self, host, port):
        myapp = bottle.default_app()
        from paste import httpserver
        httpserver.serve(myapp, host=host, port=port)




## Multiple Server Processes

A single Python process can only utilise one CPU at a time, even if 
there are more CPU cores available. The trick is to balance the load 
between multiple independent Python processes to utilise all of your 
CPU cores.

Instead of a single Bottle application server, you start one instances 
of your server for each CPU core available using different local port 
(localhost:8080, 8081, 8082, ...). Then a high performance load 
balancer acts as a reverse proxy and forwards each new requests to 
a random Bottle processes, spreading the load between all available 
backed server instances. This way you can use all of your CPU cores and 
even spread out the load between different physical servers.

But there are a few drawbacks:

  * You can't easily share data between multiple Python processes.
  * It takes a lot of memory to run several copies of Python and Bottle 
at the same time.

One of the fastest load balancer available is [pound](http://www.apsis.ch/pound/) but most common web servers have a proxy-module that can do the work just fine.

I'll add examples for [lighttpd](http://www.lighttpd.net/) and 
[Apache](http://www.apache.org/) web servers soon.




## Apache mod_wsgi

Instead of running your own HTTP server from within Bottle, you can 
attach Bottle applications to an [Apache server][apache] using 
[mod_wsgi][] and Bottles WSGI interface.

All you need is an `app.wsgi` file that provides an 
`application` object. This object is used by mod_wsgi to start your 
application and should be a WSGI conform Python callable.

    #!Python
    # File: /var/www/yourapp/app.wsgi
    
    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))
    
    import bottle
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with mod_wsgi
    application = bottle.default_app()

The Apache configuration may look like this:

    #!ApacheConf
    <VirtualHost *>
        ServerName example.com
        
        WSGIDaemonProcess yourapp user=www-data group=www-data processes=1 threads=5
        WSGIScriptAlias / /var/www/yourapp/app.wsgi
        
        <Directory /var/www/yourapp>
            WSGIProcessGroup yourapp
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>




## Google AppEngine

I didn't test this myself but several Bottle users reported that this 
works just fine.

    #!Python
    import bottle
    from google.appengine.ext.webapp import util 
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with AppEngine
    util.run_wsgi_app(bottle.default_app())




## Good old CGI

CGI is slow as hell, but it works.

    #!Python
    import bottle
    # ... add or import your bottle app code here ...
    bottle.run(server=bottle.CGIServer)


