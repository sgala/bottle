[TOC]

  [sqlite_win]: http://www.sqlite.org/download.html
  [pysqlite]: http://pypi.python.org/pypi/pysqlite/
  [py_db_api]: http://www.python.org/dev/peps/pep-0249/
  [decorator]: http://docs.python.org/glossary.html#term-decorator
  [python]: http://www.python.org
  [sqlite]: http://www.sqlite.org
  [bottle]: http://bottle.paws.org
  [bottle_doc]: http://github.com/defnull/bottle/blob/master/docs/docs.md
  [wsgiref]: http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server
  [cherrypy]: http://www.cherrypy.org/
  [fapws3]: http://github.com/william-os4y/fapws3
  [flup]: http://trac.saddi.com/flup
  [paste]: http://pythonpaste.org/
  [apache]: http://www.apache.org
  [mod_wsgi]: http://code.google.com/p/modwsgi/
  [json]: http://www.json.org


# Tutorial
Este tutorial sirve de breve introducción a la herramienta WSGI [Bottle][bottle]. El objetivo principal es, tras leer este tutorial, ser capaces de crear un proyecto usando Bottle. Este documento no muestra todas las capacidades, pero sí las principales y más importantes, como las rutas, el uso de las plantillas de Bottle para dar formato a la salida y el manejo de parámetros GET / POST.

Para entender el contenido no es necesario un conocimiento básido de WSGI, ya que Bottle intenta que apartar WSGI del usuario. Se necesita algún conocimiento del lenguaje de programación [Python][python]. Además, los ejemplos que usaremos recupera y almacena datos de una base de datos SQL, así que una idea básica de SQL ayuda, pero no es estrictamente necesaria para entender los conceptos de Bottle. En este tutorial usaremos [SQLite][sqlite]. La salida que Bottle envía al navegador se formatea usando HTML en algunos ejemplos. Por tanto una idea básica de los elementos comunes de HTML también ayuda.

Mantenemos corto el código Python "que hay por medio", para mantener el tutorial centrado en los conceptos de Bottle. Asímismo, todo el código del tutorial funciona, pero no es necesariamente lo que debería hacerse para usarlo "en la selva", es decir, en un servidor web público. Para hacerlo habría que añadir mejor gestión de errores, seguridad, validar y escapar las entradas, etc.

## Objetivos
Al acabar este tutorial tendremos un listado de tareas pendientes (ToDo) simple. Cada entrada del listado contiene un texto (con un máximo de 100 caracteres) y un estatus (0 para tareas cerradas, 1 para tareas abiertas). Usando la interfaz de usuario deweb se pueden ver y editar los elementos abiertos, así como añadir nuevos.

Durante el desarrollo las páginas se harán disponibles sólo a *localhost*, pero al final mostramos cómo adaptar la aplicación a condiciones de servidores *reales*, incluyndo el uso de mod_wsgi, de Apache.

Bottle se hará cargo de las rutas y el formado de la salida, usando plantillas. Los elementos de la lista se almacenan en una base de datos SQLite. Usamos código de python para leer y escribir en la base de datos.

Acabaremos con una aplicación que tendrá las siguientes páginas y funcionalidad:

 * Página de inicio `http://localhost:8080/todo`
 * Añadir nuevos elementos a la lista: `http://localhost:8080/new`
 * Página para edición de elementos: `http://localhost:8080/edit/:no` 
 * Usaremos el decorador `@validate` para validar los datos que se pasand a las rutas dinámicas
 * Captura de errores

## Antes de empezar...

### Instalación de Bottle

Asumiendo que tenemos una instalación reciente de Python (versión 2.5 o superior), sólo hace falta añadir Bottle. Bottle no tiene otras dependencias que Python.

Se puede instalar manualmente Bottle, copiando bottle.py al directorio del proyecto, o usar el comando easy_install así: `easy_install bottle`

### Otras necesidates de software

Como usamos la base de datos SQLite3, hay que asegurarse de que está instalada. Python 2.5 y superior incluye sqlite3. En sistemas Linux, la mayor parte de las distribuciones tienen sqlite3 instalado por defecto. SQLite se puede encontrar también para [Windows and MacOS X][sqlite_win].

Si usamos python 2.5 también hace falta [Pysqlite][pysqlite], los módulos python para acceder base de datos SQLite. De nuevos, muchas distribuciones linux los tienen instalados (se suele llamar "python-sqlite3"). Si no es el caso es necesario instalarlo manualmente o vía `easy_install pysqlite`.

*Nota*: Sistemas viejos pueden tener SQLite2 pre-instalado. Los ejemplos funcionarán bien con esa versión. Pero hace falta importar el módulo python llamado "sqlite" en vez de "sqlite3" en los ejemplos.


### Creación de una base de datos SQL

En primer lugar necesitamos crear la base de datos que usaremos, que guardaremos en `todo.db`. Para hacerlo podemos lanzar SQLite con el comando `sqlite3 todo.db`. Así se crea una base de datos vacía con el nombre "todo.db" y veremos el *prompt* de SQLite, que será parecido a: `sqlite>`. Podemos ahora escribir los siguientes comandos:

    #!sql
    CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL);
    INSERT INTO todo (task,status) VALUES ('Read A-byte-of-python to get a good introduction into Python',0);
    INSERT INTO todo (task,status) VALUES ('Visit the Python website',1);
    INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1);
    INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0);

La primera línea genera una tabla llamada "todo" con las tres columnas "id", "task", y "status". "id" es un identificador único para cada fila, que usaremos más tarde para referenciar las filas. La columna "task" guarda el texto que describe la tareas, que puede ser de hasta 100 caracteres de largo. Finalmente, la columna "status" se usa para marcar si una tareas está pendiente (valor `1`) o cerrada (valor `0`).

Alternativamente se puede crear la base de datos usando directamente la versión de sqlite embebida en python desde la versión 2.5. Así no hay necesidad de instalar el paquete sqlite completo. Basta ejecutar `python` y escribir:

    #!pycon
    >>> import sqlite3
    >>> con=sqlite3.connect("todo.db")
    >>> sql = """
    ... CREATE TABLE todo (id integer PRIMARY KEY, task char(100) NOT NULL, status boolean NOT NULL);
    ... INSERT INTO "todo" VALUES(1,'Read A-byte-of-python to get a good introduction into  Python',0);
    ... INSERT INTO "todo" VALUES(2,'Visit the Python website',1);
    ... INSERT INTO "todo" VALUES(3,'Test various editors for and check the syntax highlighting',1);
    ... INSERT INTO "todo" VALUES(4,'Choose your favorite WSGI-Framework',0);
    ... """
    >>> con.executescript(sql)


## Uso de Bottle para una lista de tareas pendientes en web

Ahora es el momento de presentar cómo se puede usar Bottle para crear una aplicación web. Pero primero necesitamos ver un concepto básico de Bottle: rutas.

### Comprendiendo las rutas
Básicalmente cada página visible en el navegador se genera dinámicamente cuando se accede a la dirección de la página. En el uso normal de bottle, por tanto, no hay contenido estático.

En Bottle se le llama ruta a una dirección, o recurso, en el servidor. Por ejemplo, cuando se accede a la página `http://localhost:8080/todo` en el navegador, Bottle mira si hay alguna función (Python) asignada a la ruta "/todo". Si ese es el caso Bottle ejecutará el código Python corespondiente y devolverá el resultado que devuelva.

### Primer paso: Mostrar todos los elementos abiertos
Tras entender el concepto de rutas creeos una. El objetivo es ver todos los elementos abiertos en la lista de tareas pendientes:

    #!Python
    import sqlite3
    from bottle import route, run
    
    @route('/todo')
    def todo_list():
        with sqlite3.connect('todo.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id, task FROM todo WHERE status LIKE 1")
            result = c.fetchall()
            return str(result)
        
    run()
    
Salve el código a "todo.py", preferiblemente en el mismo directorio que el archivo "todo.db". En caso contrario necesitará añadir el camino a "todo.db" en el argumento a  `sqlite3.connect()`.

Vamos a ver qué hicimos: hemos importado el módulo "sqlite3", necesario para acceder a una base de datos SQLite, y desde Bottle importamos "route" y "run". La llamada a `run()` arranca el servidor web incluido en Bottle. Por defecto el servidor web sirve páginas para localhost en el puerto 8080. También importamos "route", que es la función responsable de las rutas de Bottle. Como se puede ver hemos definido una función, `todo_list()`, con unas líneas de código que leen de la base de datos. La parte importante es la [sentencia decoradora][decorator] `@route('/todo')` justo antes de la línea `def todo_list()`. Haciendo eso enlazamos esa función a la ruta `/todo`, para que cada vez que un navegador accede a `http://localhost:8080/todo`, Bottle devuelva el resultado de la función `todo_list()`. Así funcionan las rutas de bottle.

De hecho se puede enlazar más de una ruta a una función. Así que el código siguiente

    #!Python
    ...
    @route('/todo')
    @route('/my_todo_list')
    def todo_list():
        ...
        
también funciona bien. Lo que no funciona es enlazar una ruta a más de una función.

El navegador muestra lo que devolvamos, por tanto el valor de la sentencia `return`. En este ejemplo necesitamos convertir `result` en una cadena usando `str()`, ya que Bottle espera que se devuelva una cadena o una lista de cadenas. Pero el resultado de la petición a la base de datos es una lista de tuplas, que es el estándar que define la [API de Base de Datoa de python][py_db_api].

Ahora que comprendemos el pequeño *script* de arriba es el momento de ejecutarlo y ver nosotros mismos el resultado.. En los sistemas operativos basados en Linux/Unix el archivo `todo.py` necesita hacerse ejecutable o, si no, ejecutar `python todo.py`. Luego podremos cargar la página `http://localhost:8080/todo` en el navegador. Si no cometimos ningún error en el script, la salida será parecida a:

    #!Python
    [(2, u'Visit the Python website'), (3, u'Test various editors for and check the syntax highlighting')]
    
Si es así ¡felicidades! Ya es usted un usuario de Bottle. Si no funcionó y necesite cambiar algunas cosas en el script, recuerde detener el servidor de Bottle que sirve la página, en caso contrario no cargará la nueva versión.

De hecho la salida no es demasiado interesante, ni agradable de leer. Es el resultado de la petición SQL, exactamente como llegó.

Nuestro siguiente paso será darle un formato mejor a la salida. Pero antes de hacerlo vamos a hacernos la vida un poco más fácil.

### Depuración y auto-recarga
Quizá ya haya experimentado que Bottle envía un mensaje de error corto al navegador en caso de que algo vaya mal en el *script*, por ejemplo si la conexión a la base de datos tiene algún problema. Para depuración ayuda mucho tener más detalles. Se puede conseguir fácilmente añadiendo al *script* la siguiente sentencia:

    #!Python
    from bottle import run, route, debug
    ...
    #añada esto al final:
    debug(True)
    run()

Llamando a la función `debug` se consigue que bottle imprima una traza de la pila del intérprete de python, que normalmente contiene información útil para encontrar errores. Además, así bottle recargará las plantillas (ver más abajo) en cada petición, de manera que podremos ver los cambios en las plantillas sin tener que detener el servidor.

**Nota**: `debug(True)` se debe usar sólo para desarrollo, **nunca** debe usarse en entornos de producción.

Otra característica interesante es la auto-recarga, que se habilita modificando la sentencia `run()` así

    #!Python
    run(reloader=True)
    
De esta manera se detectan automáticamente los cambios del *script* y se recarga la versión nueva sin necesidad de parar y arrancar el servidor.

Lo mismo que las trazas, esta característica está pensada para usarse durante el desarrollo, no en sistemas en producción.

### Plantillas de Bottle para dar formato a la salida
Vamos ahora a considerar maneras de darle un formato adecuado a la salida que produce el *script*.

Bottle espera recibir una cadena o una lista de cadenas de caracteres de los manejadores, y los devuelve al navegador con ayuda del servidor incluido. A bottle no le importa el contenido de la cadena, que puede ser texto formateado con marcado HTML.

Bottle proporciona su propio *motor* de plantillas. Las plantillas se almacenan como ficheros con una extensión `.tpl`. Se puede llamar a las plantillas desde cualquier función. Pueden contener cualquier tipo de texto, que será muy probablemente marcado HTML o similar mezclado con sentencias de python. Las plantillas pueden recibir argumentos, por ejemplo el resultado de una petición a la base de datos, a los que se podrá dar formato.

Right here, we are going to cast the result of our query showing the open ToDo items into a simple table with two columns: the first column will contain the ID of the item, the second column the text. The result set is, as seen above, a list of tuples, each tuple contains one set of results.

To include the template into our example, just add the following lines:

    #!Python
    from bottle import from bottle import route, run, debug, template
    ...
    result = c.fetchall()
    c.close()
    output = template('make_table', rows=result)
    return output
    ...
    
So we do here two things: First, we import "template" from Bottle in order to be able to use templates. Second, we assign the output of the template "make_table" to the variable "output", which is then returned. In addition to calling the template, we assign "result", which we received from the database query, to the variable "rows", which is later on used within the template. If necessary, you can assign more than one variable / value to a template.

Templates always return a list of strings, thus there is no need to convert anything. Of course, we can save one line of code by writing `return template('make_table', rows=result)`, which gives exactly the same result as above.

Now it is time to write the corresponding template, which looks like this:

    #!html
    %#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
    <p>The open items are as follows:</p>
    <table border="1">
    %for row in rows:
      <tr>
      %for r in row:
        <td>{{r}}</td>
      %end
      </tr>
    %end
    </table>

Save the code as "make_table.tpl" in the same directory where "todo.py" is stored.

Let's have a look at the code: Every line starting with % is interpreted as Python code. Please note that, of course, only valid Python statements are allowed, otherwise the template will raise an exception, just as any other Python code. The other lines are plain HTML-markup.

As you can see, we use Python's "for"-statement two times, in order to go through "rows". As seen above, "rows" is a variable which holds the result of the database query, so it is a list of tuples. The first "for"-statement accesses the tuples within the list, the second one the items within the tuple, which are put each into a cell of the table. Important is the fact that you need additionally close all "for", "if", "while" etc. statements with `%end`, otherwise the output may not be what you expect.

If you need to access a variable within a non-Python code line inside the template, you need to put it into double curly braces. This tells the template to insert the actual value of the variable right in place.

Run the script again and look at the output. Still not really nice, but at least better readable than the list of tuples. Of course, you can spice-up the very simple HTML-markup above, e.g. by using in-line styles to get a better looking output.

### Using GET And POST values
As we can review all open items properly, we move to the next step, which is adding new items to the ToDo list. The new item should be received from a regular HTML-based form, which sends its data by the GET-method.

To do so, we first add a new route to our script and tell the route that it should get GET-data:

    #!Python
    from bottle import route, run, debug, template, request
    ...
    return template('make_table', rows=result)
    ...
    
    @route('/new', method='GET')
    def new_item():
    
        new = request.GET.get('task', '').strip()
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        
        query = "INSERT INTO todo (task,status) VALUES (?,1)"
        c.execute(query, (new,))
        new_id = c.lastrowid
        conn.commit()
        c.close()
        
        return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
       
To access GET (or POST) data, we need to import "request" from Bottle. To assign the actual data to a variable, we use the statement `request.GET.get('task','').strip()` statement, where "task" is the name of the GET-data we want to access. That's all. If your GET-data has more than one variable, multiple `request.GET.get()` statements can be used and assigned to other variables.

The rest of this piece of code is just processing of the gained data: writing to the database, retrieve the corresponding id from the database and generate the output.

But where do we get the GET-data from? Well, we can use a static HTML page holding the form. Or, what we do right now, is to use a template which is output when the route "/new" is called without GET-data.

The code need to be extended to:

    #!Python 
    ...
    @route('/new', method='GET')
    def new_item():

    if request.GET.get('save','').strip():
        
        new = request.GET.get('task', '').strip()
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        
        query = "INSERT INTO todo (task,status) VALUES (?,1)"
        c.execute(query, (new,))
        new_id = c.lastrowid
        conn.commit()
        c.close()
  
        return '<p>The new task was inserted into the database, the ID is %s</p>' %new_id
    
    else:
        return template('new_task.tpl')
    ...

"new_task.tpl" looks like this:

    #!html
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="GET">
    <input type="text" size="100" maxlength="100" name="task">
    <input type="submit" name="save" value="save">
    </form>
    
That's all. As you can see, the template is plain HTML this time.

Now we are able to extend our to do list.

By the way, if you prefer to use POST-data: This works exactly the same why, just use `request.POST.get()` instead.

### Editing Existing Items
The last point to do is to enable editing of existing items.

By using the routes we know so far only it is possible, but may be quite tricky. But Bottle knows something called "dynamic routes", which makes this task quite easy.

The basic statement for a dynamic route looks like this:

    #!Python
    @route('/myroute/:something')
    
The key point here is the colon. This tells Bottle to accept for ":something" any string up to the next slash. Furthermore, the value of "something" will be passed to the function assigned to that route, so the data can be processed within the function.

For our ToDo list, we will create a route `@route('/edit/:no)`, where "no" is the id of the item to edit.

The code looks like this:

    #!Python
    @route('/edit/:no', method='GET')
    def edit_item(no):

        if request.GET.get('save','').strip():
            edit = request.GET.get('task','').strip()
            status = request.GET.get('status','').strip()
            
            if status == 'open':
                status = 1
            else:
                status = 0
                
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            query = "UPDATE todo SET task = ?, status = ? WHERE id LIKE ?"
            c.execute(query, (edit,status,no))
            conn.commit()
            
            return '<p>The item number %s was successfully updated</p>' %no
            
        else:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            query = "SELECT task, status FROM todo WHERE id LIKE ?"
            c.execute(query, (no,))
            cur_data = c.fetchone()
            
            return template('edit_task', old = cur_data, no = no)

It is basically pretty much the same what we already did above when adding new items, like using "GET"-data etc. The main addition here is using the dynamic route ":no", which here passes the number to the corresponding function. As you can see, "no" is used within the function to access the right row of data within the database.

The template "edit_task.tpl" called within the function looks like this:

    #!html
    %#template for editing a task
    %#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item
    <p>Edit the task with ID = {{no}}</p>
    <form action="/edit/{{no}}" method="get">
    <input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
    <select name="status">
    <option>open</option>
    <option>closed</option>
    </select>
    <br/>
    <input type="submit" name="save" value="save">
    </form>

Again, this template is a mix of Python statements and HTML, as already explained above.

A last word on dynamic routes: you can even use a regular expression for a dynamic route. But this topic is not discussed further here.

### Validating dynamic routes
Using dynamic routes is fine, but for many cases it makes sense to validate the dynamic part of the route. For example, we expect a integer number in our route for editing above. But if a float, characters or so are received, the Python interpreter throws an exception, which is not what we want.

For those cases, Bottle offers the `@validate` decorator, which validates the "input" prior to passing it to the function. In order to apply the validator, extend the code as follows:

    #!Python
    from bottle import route, run, debug, template, request, validate
    
    ...
    
    @route('/edit/:no', method='GET')
    @validate(no=int)
    def edit_item(no):
    
    ...
    
At first, we imported "validate" from the Bottle framework, than we apply the @validate-decorator. Right here, we validate if "no" is an integer. Basically, the validation works with all types of data like floats, lists etc.

Save the code and call the page again using a "403 forbidden" value for ":no", e.g. a float. You will receive not an exception, but a "403 - Forbidden" error, saying that a integer was expected.

### Caching Errors
The next step may is to catch the error with Bottle itself, to keep away any type of error message from the user of your application. To do that, Bottle has an "error-route", which can be a assigned to a HTML-error.

In our case, we want to catch a 403 error. The code is as follows:

    #!Python
    from bottle import route, run, debug, template, request, validate, error
    
    ...
    
    @error(403)
    def mistake(code):
        return 'The parameter you passed has the wrong format!'
        
So, at first we need to import "error" from Bottle and define a route by `error(403)`, which catches all "403 forbidden" errors. The function "mistake" is assigned to that. Please note that `error()` always passed the error-code to the function - even if you do not need it. Thus, the function always needs to accept one argument, otherwise it will not work.

Again, you can assign more than one error-route to a function, or catch various errors with one function each. So this code:

    #!Python
    @error(404)
    @error(403)
    def mistake(code):
        return 'There is something wrong!'
        
works fine, the following one as well:

    #!Python
    @error(403)
    def mistake403(code):
        return 'The parameter you passed has the wrong format!'
        
    @error(404)
    def mistake404(code):
        return 'Sorry, this page does not exist!'

### Summary
After going through all the sections above, you should have a brief understanding how the Bottle WSGI framework works. Furthermore you have all the knowledge necessary to use Bottle for you applications.

The following chapter give a short introduction how to adapt Bottle for larger projects. Furthermore, we will show how to operate Bottle with web servers which performs better on a higher load / more web traffic than the one we used so far.

## Server Setup
So far, we used the standard server used by Bottle, which is the [WSGI reference Server][wsgiref] shipped along with Python. Although this server is perfectly suitable for development purposes, it is not really suitable for larger applications. But before we have a look at the alternatives, let's have a look how to tweak the setting of the standard server first

### Running Bottle on a different port and IP
As a standard, Bottle does serve the pages on the IP-adress 127.0.0.1, also known as "localhost", and on port "8080". To modify there setting is pretty simple, as additional parameters can be passed to Bottle's `run()` function to change the port and the address.

To change the port, just add `port=portnumber` to the run command. So, for example

    #!Python
    run(port=80)
    
would make Bottle listen to port 80.

To change the IP-address where Bottle is listing / serving can be change by

    #!Python
    run(host='123.45.67.89')
    
Of course, both parameters can be combined, like:

    #!Python
    run(port=80, host='123.45.67.89')
    
The `port` and `host` parameter can also be applied when Bottle is running with a different server, as shown in the following section

### Running Bottle with a different server
As said above, the standard server is perfectly suitable for development, personal use or a small group of people only using your application based on Bottle. For larger task, the standard server may become a Bottle neck, as it is single-threaded, thus it can only serve on request at a time.

But Bottle has already various adapters to multi-threaded server on board, which perform better on higher load. Bottle supports [cherryPy][cherrypy], [fapws3][fapws3], [flup][flup] and [Paste][paste].

If you want to run for example Bottle with the Paste server, use the following code:

    #!Python
    from bottle import PasteServer
    ...
    run(server=PasterServer)
    
This works exactly the same way with `FlupServer`, `CherryPyServer` and `FapwsServer`.

### Running Bottle on Apache with mod_wsgi
Maybe you already have an [Apache web server][apache] or you want to run a Bottle-based application large scale - than it is time to think about Apache with [mod_wsgi][mod_wsgi].

We assume that your Apache server is up and running and mod_wsgi is working fine as well. On a lot of Linux distributions, mod_wsgi can be installed via the package management easily.

Bottle brings a adapter for mod_wsgi with it, so serving your application is an easy task.

In the following example, we assume that you want to make your application "ToDO list" accessible through "http://www.mypage.com/todo" and your code, templates and SQLite database is stored in the path "var/www/todo".

At first, we need to import "defautl_app" from Bottle in our little script:

    #!Python
    from bottle import route, run, debug, template, request, validate, error, default_app
    
When you run your application via mod_wsgi, it is imperative to remove the `run()` statement from you code, otherwise it won't work here.

After that, create a file called "adapter.wsgi" with the following content:

    #!Python
    import sys
    sys.path = ['/var/www/todo/'] + sys.path

    import todo
    import os

    os.chdir(os.path.dirname(__file__))

    application = default_app()

and save it in the same path, "/var/www/todo". Actually the name of the file can be anything, as long as the extensions is ".wsgi". The name is only used to reference the file from your virtual host.

Finally, we need to add a virtual host to the Apache configuration, which looks like this:

    #!ApacheConf
        <VirtualHost *>
            ServerName mypage.com
            
            WSGIDaemonProcess todo user=www-data group=www-data processes=1 threads=5
            WSGIScriptAlias / /var/www/todo/adapter.wsgi
            
            <Directory /var/www/todo>
                WSGIProcessGroup todo
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
            </Directory>
        </VirtualHost>
        
After restarting the server, your the ToDo list should be accessible at "http://www.mypage.com/todo"

## Final words
Now we are at the end of this introduction and tutorial to Bottle. We learned about the basic concepts of Bottle and wrote a first application using the Bottle framework. In addition to that, we saw how to adapt Bottle for large task and server Bottle through a Apache web server with mod_wsgi.

As said in the introduction, this tutorial is not showing all shades and possibilities of Bottle. What we skipped here is e.g. using regular expressions on dynamic routes, returning [JSON data][json], how to serve static files and receive File Objects and Streams. Furthermore, we did not show how templates can be called from within another template. For an introduction into those points, please refer to the full [Bottle documentation][bottle_doc].

## Complete example listing
As above the ToDo list example was developed piece by piece, here is the complete listing:

Main code for the application `todo.py`:

    #!Python
    import os, sqlite3
    from bottle import route, run, debug, template, request, validate, error

    # only needed when you run Bottle on mod_wsgi
    from bottle import default_app
        
    @route('/todo')
    def todo_list():
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, task FROM todo WHERE status LIKE '1';")
        result = c.fetchall()
        c.close()
            
        output = template('make_table', rows=result)
        return output

    @route('/new', method='GET')
    def new_item():

        if request.GET.get('save','').strip():
            
            new = request.GET.get('task', '').strip()
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            
            query = "INSERT INTO todo (task,status) VALUES (?,1)"
            c.execute(query, (new,))
            new_id = c.lastrowid
            conn.commit()
            c.close()
      
            return '<p>The new task was inserted into the database, the ID is %s</p>' %new_id
        
        else:
            return template('new_task.tpl')
            
    @route('/edit/:no', method='GET')
    @validate(no=int)
    def edit_item(no):

        if request.GET.get('save','').strip():
            edit = request.GET.get('task','').strip()
            status = request.GET.get('status','').strip()
            
            if status == 'open':
                status = 1
            else:
                status = 0
                
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            query = "UPDATE todo SET task = ?, status = ? WHERE id LIKE ?"
            c.execute(query, (edit,status,no))
            conn.commit()
            
            return '<p>The item number %s was successfully updated</p>' %no
            
        else:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            query = "SELECT task FROM todo WHERE id LIKE ?"
            c.execute(query, (no,))
            cur_data = c.fetchone()
            print cur_data
            
            return template('edit_task', old = cur_data, no = no)


    @error(403)
    def mistake403(code):
        return 'There is a mistake in your url!'

    @error(404)
    def mistake404(code):
        return 'Sorry, this page does not exist!'


    debug(True)

    def main():
        run(reloader=True)

    if __name__ == "__main__":
        # Interactive mode
        main()
    else:
        # Mod WSGI launch
        os.chdir(os.path.dirname(__file__))
        application = default_app()

    #remember to remove reloader=True and debug(True) when you move your application from development to a productive environment.

Template `edit_task.tpl`:

    #!html
    %#template for editing a task
    %#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item
    <p>Edit the task with ID = {{no}}</p>
    <form action="/edit/{{no}}" method="get">
    <input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
    <select name="status">
    <option>open</option>
    <option>closed</option>
    </select>
    <br/>
    <input type="submit" name="save" value="save">
    </form>
    
Template `new_task.tpl`:

    #!html
    %#template for the form for a new task
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="GET">
    <input type="text" size="100" maxlenght="100" name="task">
    <input type="submit" name="save" value="save">
    </form>


