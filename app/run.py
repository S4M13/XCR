import os
import asyncio

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from tornado.httpserver import HTTPServer

from waitress import serve

import Settings
from main import app

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

container = WSGIContainer(app)


def HTTPS_server():
    http_server = HTTPServer(container,
                             ssl_options={
                                 'certfile': Settings.CERTFILE_LOCATION,
                                 'keyfile': Settings.KEYFILE_LOCATION
                             })
    print("[+]Starting secure server...")
    http_server.listen(443, address='0.0.0.0')
    IOLoop.instance().start()


def HTTP_server():
    http_server = HTTPServer(container)

    print("[+]Starting insecure server...")
    http_server.listen(80, address='0.0.0.0')
    IOLoop.instance().start()


def waitress_server():
    serve(app, host='0.0.0.0', port=80)



waitress_server()
