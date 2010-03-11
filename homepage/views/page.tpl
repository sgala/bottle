%rebase basehtml title=page.title.encode('utf-8')
<div id='mdpage'>
{{!page.html.encode('utf-8')}}
</div>
<div style="text-align: left; color:grey;">Edite esta página en <a href="http://github.com/sgala/bottle/blob/laboratorio-servicios-web/docs/{{page.name}}.md">GitHub</a></div>
%if page.is_blogpost:
<div style="text-align: left; color:grey;">Publicado el {{page.blogtime.strftime('%A, %d %B %Y')}} por <a href="/page/contact">defnull</a>. Los comentarios no se han implementado.</div>
%end

