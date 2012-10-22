from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def main(**settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("respire.tests.todo.views")

    return config.make_wsgi_app()

if __name__ == "__main__":
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
