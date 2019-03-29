from app import init_app
from app import socketio
from app.config import config


app = init_app(config['dev'])
print(app.config)


if __name__ == '__main__':
    if app.debug:
        socketio.run(app, port=7659)
    else:
        # gevent is supported in a number of different configurations.
        # The long-polling transport is fully supported with the gevent package,
        # but unlike eventlet, gevent does not have native WebSocket support.
        # To add support for WebSocket there are currently two options.
        # Installing the gevent-websocket package adds WebSocket support to gevent or one can use the uWSGI web server,
        # which comes with WebSocket functionality. The use of gevent is also a performant option,
        #  but slightly lower than eventlet.
        socketio.run(app, port=7659)
