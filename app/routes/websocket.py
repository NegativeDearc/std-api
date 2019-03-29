from flask_socketio import Namespace, emit


class ConnectionStatus(Namespace):
    def on_connect(self):
        emit('Sever Connected')

    def on_disconnect(self):
        emit('Server Lost')