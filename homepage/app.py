#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

from SocketServer import TCPServer
import socket
TCPServer.address_family = socket.AF_INET6
import BaseHTTPServer
BaseHTTPServer.BaseHTTPRequestHandler.protocol_version = "HTTP/1.1"


from bottle import route, view, response
import bottle
import markdown
import os.path
import sys
import re
import codecs
import glob
import datetime
import cgi

class Page(object):
    pagedir  = '../docs'
    cachedir = './cache'
    options = ['codehilite(force_linenos=True)', 'toc']

    def __init__(self, name):
        self.name = name
        self.filename  = os.path.join(self.pagedir,  self.name+'.md')
        self.cachename = os.path.join(self.cachedir, self.name+'.html')

    @property
    def exists(self):
        return os.path.exists(self.filename)

    @property
    def rawfile(self):
        #if not self.exists:
        #    open(self.filename, 'w').close()
        return codecs.open(self.filename, encoding='utf8')

    @property
    def raw(self):
        return self.rawfile.read()

    @property
    def cachefile(self):
        if not os.path.exists(self.cachename) \
        or os.path.getmtime(self.filename) > os.path.getmtime(self.cachename):
           with self.rawfile as f:
               html = markdown.markdown(f.read(), self.options)
           with open(self.cachename, 'w') as f:
               f.write(html.encode('utf-8'))
        return codecs.open(self.cachename, encoding='utf8')

    @property
    def html(self):
        return self.cachefile.read()

    @property
    def title(self):
        ''' The first h1 element '''
        for m in re.finditer(r'<h1[^>]*>(.+?)</h1>', self.html):
            return m.group(1).strip()
        return self.name.replace('_',' ').title()

    @property
    def preview(self):
        for m in re.finditer(r'<p[^>]*>(.+?)</p>', self.html, re.DOTALL):
            return m.group(1).strip()
        return '<i>No preview available</i>'

    @property
    def blogtime(self):
        try:
            date, name = self.name.split('_', 1)
            year, month, day = map(int, date.split('-'))
            return datetime.date(year, month, day)
        except ValueError:
            raise AttributeError("This page is not a blogpost")

    @property
    def is_blogpost(self):
        try:
            self.blogtime
            return True
        except AttributeError:
            return False

def iter_blogposts():
    for post in glob.glob(os.path.join(Page.pagedir, '*.md')):
        name = os.path.basename(post)[:-3]
        if re.match(r'20[0-9]{2}-[0-9]{2}-[0-9]{2}_', name):
            yield Page(name)




# API docs

@route('/docs/:filename#.*#')
def static(filename):
    if not filename:
        filename = 'index.html'
    return bottle.static_file(filename, root='../apidoc/html/')

# Static files

@route('/:filename#.+\.(css|js|ico|png|txt|html|ogv|mp4)#')
def static(filename):
    return bottle.static_file(filename, root='./static/')

# Bottle Pages

@route('/')
@route('/page/:name')
@view('page')
def page(name='start'):
    p = Page(name) #replace('/','_')? Routes don't match '/' so this is save
    if p.exists:
        return dict(page=p)
    else:
        raise bottle.HTTPError(404, 'Page not found') # raise to escape the view...


@route('/rss.xml')
@view('rss')
def blogrss():
    response.content_type = 'application/xml+rss'
    posts = [post for post in iter_blogposts() if post.exists and post.is_blogpost]
    posts.sort(key=lambda x: x.blogtime, reverse=True)
    return dict(posts=posts)


@route('/blog')
@view('blogposts')
def bloglist():
    posts = [post for post in iter_blogposts() if post.exists and post.is_blogpost]
    posts.sort(key=lambda x: x.blogtime, reverse=True)
    return dict(posts=posts)

# Start server

app = bottle.app()
#from paste.gzipper import make_gzip_middleware
import gzip
from StringIO import StringIO
def make_gzip_middleware(app, level=6):
    def gzipper(environ, start_response):
        def send_headers(size):
            status, headers, exc_info = environ['gzipper']['start']
            # Keep dummy content-lenght to trick Paste to keep conn open
            # a MUST NOT (rfc2616). Server MUST ignore it, though
            headers = list((k,v) for k,v in headers if k != 'Content-Length')
            headers += [('Transfer-Encoding', 'chunked'),
                        ('Content-Encoding' , 'gzip')]
            start_response(status, headers, exc_info)
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', '') \
              or environ.get('SERVER_PROTOCOL','HTTP/1.0')[5:] < '1.1': 
            for i in app(environ, start_response):
                yield i  # noop
            return
        buf = StringIO()
        f = gzip.GzipFile(mode='wb', compresslevel=level, fileobj=buf)
        environ['gzipper'] = dict(compressible=False)
        def my_start_response(status, headers, exc_info=None):
            environ['gzipper']['start'] = (status, headers, exc_info)
            for h,v in headers:
                if h == 'Content-Encoding':
                    return start_response(status, headers, exc_info)
            for h,v in headers:
                if h == 'Content-Type':
                    if v and (v.startswith('text/') or v.startswith('application/')) \
                                and 'zip' not in v:
                        environ['gzipper']['compressible'] = True
                        return buf.write # a writer for legacy apps (noop)
            return start_response(status, headers, exc_info)
        result = app(environ, my_start_response)
        compressible = environ['gzipper']['compressible']
        if not compressible:
                for i in result:
                    yield i
                return
        sent_headers = False
        chunked = 0
        for i in result:
            f.write(i)
            if buf.tell()>chunked:
                if not sent_headers:
                    sent_headers = True
                    send_headers(buf.tell())
                #send a chunk
                #f.flush()
                yield '%x\r\n%s\r\n' % (buf.tell()-chunked, buf.getvalue()[chunked:buf.tell()])
                chunked = buf.tell()
        #TODO close result if hasattr close
        f.flush()
        f.close()
        if not sent_headers:
            sent_headers = True
            send_headers(buf.tell())
        # send chunk after flush (if there was content only)
        if f.tell()>0 and buf.tell()>chunked:
            yield '%x\r\n%s\r\n' % (buf.tell()-chunked, buf.getvalue()[chunked:buf.tell()])
        # send last zero sized chunk
        yield '0\r\n\r\n'
        return
    return gzipper

app = make_gzip_middleware(app)

bottle.debug(True)
bottle.run(host='::', port=int(sys.argv[1] if len(sys.argv) > 1 else 8080), server=bottle.PasteServer, reloader=True, app=app, protocol_version='HTTP/1.1')
