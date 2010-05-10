[TOC]

# Práctica Final
**Laboratorio de Servicios Web**
**Versión 0.2**, **5/5/2010**

En este documento se presenta de manera detallada la práctica final para
la asignatura Laboratorio de Servicios Web. Este documento se actualizará
según vayan surgiendo dudas y se vayan aclarando.

La práctica final es una actividad de obligatorio cumplimiento (i.e., sin
las prácticas aprobadas, no se aprueba la asignatura), implementadas en el
lenguaje de programación Python y cuya temática está relacionada con un
servicio web.

Realizar de manera completa y correcta la parte básica de la práctica
final se evalúa con *hasta* **3** puntos, mientras que si se realiza
funcionalidad adicional, se puede conseguir *hasta* **2** puntos más. La
entrega de la práctica tendrá lugar **el día del examen** de la asignatura y
constará de una presentación presencial en los laboratorios docentes del
GSyC por parte del estudiante y en presencia del profesor. Los profesores
determinarán una puntuación adicional de hasta dos puntos según la calidad
de la práctica.

Los aprobados (todas aquellas prácticas que tengan **al menos** 3 puntos) se
guardarán para la convocatoria de septiembre, pero no de un curso para otro.

Durante la última semana de mayo habrá clases específicas de apoyo a la
práctica final en el laboratorio. Fuera de ese horario se contestarán a
preguntas, preferentemente **en el foro** de la asignatura. Y, por supuesto,
siempre existe la posibilidad de concertar una tutoría con los profesores
para aclarar cuestiones.

Este documento contiene, al final, notas con pistas, funcionalidad o respuestas
a preguntas comunes que se han planteado. Distintas versiones contendrán más
información, por lo que recomendamos consultarlo cada cierto tiempo.

# Objetivo

El objetivo de la práctica final es tener un sistema que permite subir y
comentar vídeos cortos, orientados a la formación, en una web de una institución local, por ejemplo un Centro de Cooperación para el Desarrollo.
Además, esta web nos da la posibilidad de ofrecer nuestros
vídeos a otras instituciones similares usando JSON, y de importar
JSON de otros portales similares para permitir el intercambio de vídeos.
Se supone que los vídeos tienen un uso práctico, por ejemplo:

-   técnicas de cultivo
-   aseo, cuidados, curas de emergencia
-   prácticas saludables con el agua o alimentos
-   construcción o mantenimiento de equipos
-   etc.

# Requisitos mínimos

Los requisitos mínimos que se especifican a continuación son los que la
práctica ha de cumplir para aprobar la parte básica.

*   Funcionalidad para subir un vídeo corto. Por cada vídeo se almacena:
    -    el título del vídeo,
    -    el vídeo en sí,
    -    el autor del vídeo,
    -    su temática, por ejemplo como un conjunto de palabras clave, y
    -    una breve descripción;
    -    además, se le puede añadir la fecha.
    
*   Funcionalidad para comentar los vídeos subidos.
    Por cada vídeo habrá comentarios, con la siguiente información:
    -    nombre del que realiza el comentario,
    -    fecha y hora, que resulta útil para ordenar los comentarios, y
    -    texto del comentario.
*   Página principal listando en uno de los bloques los vídeos contenidos en
el sitio.
*   Exportar los datos de los vídeos en JSON, accesibles mediante URL pública
*   Dar de alta la URL pública del servidor en un servidor de anuncio.
Este servidor de anuncio, proporcionado por los profesores, se encargará en
todo momento de anunciar las URLs donde se pueden acceder a los datos de los
vídeos en JSON.
*   Tomar los datos de una web que contenga URLs de otros sitios similares
al que estamos construyendo en JSON y mostrarlo en uno de los bloques de
la página principal.
*   Funcionalidad de búsqueda del vídeo (por su título, temática o autor)
*   Utilización de hojas de estilo (por ejemplo, alguna de [oswd.org](http://oswd.org). [Tutorial de HTML + CSS](http://www.w3.org/Style/Examples/011/firstcss.es.html).)

# Requisitos avanzados

Además de la parte básica, se pueden realizar requisitos avanzados. Todo
lo que sea funcionalidad adicional a la parte básica, será considerado
como tal. A continuación, se proponen algunos ejemplos:

* Autenticación sencilla para subir vídeos y poner comentarios, de manera
  que sólo los usuarios que estén dados de alta puedan poner vídeos, o comentar.
  Se proporcionará el esqueleto del código para hacerlo al final de este documento.
* Página conforme a los estándares HTML y CSS (validación con los
  formularios del w3c, [http://validator.w3.org/](http://validator.w3.org/))
* Permitir [markdown](http://daringfireball.net/projects/markdown/dingus) para
  mejor formato del texto de vídeos y de comentarios.
* valoración de vídeos o comentarios, click sobre una flecha arriba o abajo usa javascript + JSON para llamar al servidor e incrementar una valoración. Si se implementa, lógicamente, debería darse la opción de ordenar por valoración o por fecha...
* ...

# Calidad del código

El código Python de la práctica ha de ser limpio y claro. Esto quiere decir
que se valorará positivamente:

* Que los manejadores tengan código limpio y que no haya mucho *corta y pega*
  de código, separándose funciones auxiliares
* Estructurar el código para que no haya funciones demasiado grandes
* Estructurar el código para que la generación de HTML se haga mediante plantillas
* Utilizar estructuras de código sencillas y acordes con Python (por
ejemplo, en los bucles, etc.)
* Adecuada documentación del código (incluyendo manejadores, tablas de BD, y plantillas)
* Utilizar nombres razonables para las variables

# Notas

Las siguientes notas irán conteniendo distintos fragmentos de código, pistas
o ejemplos para facilitar el desarrollo de la funcionalidad opcional o bien
resolver dudas que se hayan planteado en clase o en los foros.

## Autenticación
TBD (**Pendiente**)

## Plantillas de bottle
TBD (**Pendiente**)

## Validación de HTML
TBD (**Pendiente**)

## Validación de CSS
TBD (**Pendiente**)

## Cómo subir archivos binarios usando bottle
En el manual de bottle hay una sección sobre [subida de ficheros](/docs/tutorial.html#file-uploads). La traduzco: Bottle maneja los ficheros que
se suben de la misma manera que datos de formulario POST. En lugar de 
cadenas nos llega un objeto similar a un fichero. Estos objetos tienen dos
atributos primarios: ``file`` es un fichero temporal que se puede usar para leerlo,
y ``value``, que lo leerá y lo devolverá como una cadena. Ejemplo de
controlador:

    #!python
    from bottle import route, request
    @route('/subida', method='POST')
    def sube_fichero():
        ficherodatos = request.POST.get('ficherodatos')
        return ficherodatos.file.read()

Ese ejemplo funcionará con un formulario HTML parecido al siguiente:

    #!html
    <form action="/subida" method="post" enctype="multipart/form-data">
      <input name="ficherodatos" type="file" />
    </form>

Es importante que el atributo ``action`` del formulario corresponda
con la ruta de bottle, el método sea ``post`` y el enctype ``multipart/form-data``
así como la correspondencia del nombre del campo, en este caso, ``ficherodatos``,
con el atributo del que hacemos ``.get()`` en el diccionario ``request.POST``.

## Código y formato para reproducir vídeo en HTML5
TBD (**Pendiente**)

## Uso de markdown para formato de textos y comentarios
Markdown es un lenguaje simple, parecido a texto, que se convierte en HTML.
Ver [chuleta de formato](http://daringfireball.net/projects/markdown/dingus).
Ejemplo para convertir markdown en HTML:

    #!pycon
    >>> import markdown
    >>> markdown.markdown(u"Hola. Esto está *muy* **bien**.")
    u'<p>Hola. Esto est\xe1 <em>muy</em> <strong>bien</strong>.</p>'

y se vería así: "Hola. Esto está *muy* **bien**". Markdown está instalado
en los ordenadores del laboratorio. En ubuntu se instala mediante
``sudo apt-get install python-markdown``. En windows siguiendo las
instrucciones en TBD(**Pendiente**).

## Servir archivos estáticos
Por ejemplo, en el subdirectorio *static* de la aplicación
podemos colocar las hojas de estilo o imágenes,
y servirlas con código así:

    #!python
    @route('/:filename#.+\.(css|js|ico|png|txt|html)#')
    def static(filename):
        return bottle.static_file(filename, root='./static/')

Este código está copiado de la aplicación que crea el *sitio web*
de bottle, en `homepage/app.py`. Lo que hace es servir cualquier recurso
que termine en las extensiones citadas desde el subdirectorio *static*
del directorio en que está la aplicación. Si quisiéramos servir cualquier
fichero del subdirectorio ``/static`` incluyendo subdirectorios se 
podría hacer, por ejemplo, así:

    #!python
    @route('/static/:filename#.*#')
    def static(filename):
        return bottle.static_file(filename, root='./static/')


