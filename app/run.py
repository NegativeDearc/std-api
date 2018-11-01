from app import init_app
from app.config import config
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


app = init_app(config['dev'])


if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    print('Run Serve At Port.. http://localhost:7659')
    http_server.listen(7659)
    IOLoop.instance().start()
