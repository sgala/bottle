%title = globals().get('title', 'Página de origen')
%import bottle
%version = bottle.__version__
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>{{title}} - Bottle: Framework Web Python</title>
    <link type="text/css" rel="stylesheet" href="/main.css" />
    <link type="text/css" rel="stylesheet" href="/pygments.css" />
    <link rel="alternate" type="application/rss+xml"  href="/rss.xml" title="Cambios recientes">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" >
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js" type="text/javascript"></script>
  </head>
  <body>
    <div id="navigation">
      <h1>Navegación</h1>
      <ul>
        <li><a href="/">Origen</a></li>
        <li><a href="/blog">Entradas de Blog</a></li>
        <li><a href="/page/docs">Documentación</a></li>
        <li><a href="/page/tutorial">Tutorial</a></li>
        <li><a href="/page/faq">F.A.Q.</a></li>
        <li><a href="/page/contact">Contacto</a></li>
      </ul>
      <h1>Enlaces</h1>
      <ul>
        <li><a target="_blank" href="http://pypi.python.org/pypi/bottle">Descargar</a></li>
        <li><a target="_blank" href="http://github.com/defnull/bottle">Repositorio en GitHub</a></li>
        <li><a target="_blank" href="http://github.com/defnull/bottle/issues">Informes de Error</a></li>
        <li><a target="_blank" href="http://groups.google.de/group/bottlepy">Grupo en Google Groups</a></li>
        <li><a target="_blank" href="http://twitter.com/bottlepy">Twitter</a></li>
      </ul>
      <h1>Otros</h1>
      <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
        <input type="hidden" name="cmd" value="_s-xclick">
        <input type="hidden" name="hosted_button_id" value="10013866">
        <input type="image" src="https://www.paypal.com/en_US/i/btn/btn_donate_SM.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
        <img alt="" border="0" src="https://www.paypal.com/de_DE/i/scr/pixel.gif" width="1" height="1">
      </form>
    </div>

    %include

    <div id='footer'>
      <div>Sitio web construido con <a href="/"><img src="/bottle-sig.png" /></a> <small>(Version {{version}})</small></div>
      <div>Ver código fuente en <a href="http://github.com/defnull/bottle">GitHub</a></div>
    </div>
  </body>
</html>
