from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from app.logs.log_setting import DebugFalseLog

cors = CORS()
socketio = SocketIO()
api = Api()
db = SQLAlchemy(use_native_unicode='utf8')


def init_app(cfg):
    from app.routes.routes import Login, Task, UserTask, UserTaskOnce, Search, Dash, Punch, \
        ResetPassword, CronExpression, PlantDash, PlantDashDetail

    app = Flask(__name__)
    app.config.from_object(cfg)

    api.add_resource(Task,            '/api/task/<string:task_id>')
    api.add_resource(UserTask,        '/api/task/user/<string:user_id>')
    api.add_resource(UserTaskOnce,        '/api/task/user/once/<string:user_id>')
    api.add_resource(Search,          '/api/task/search')
    api.add_resource(Login,           '/api/auth/login')
    api.add_resource(Dash,            '/api/dash/<string:user_id>')
    api.add_resource(PlantDash,       '/api/dash/plant/<string:segment>')
    api.add_resource(PlantDashDetail, '/api/dash/plant/detail/<string:segment>')
    api.add_resource(Punch,           '/api/punch/<string:user_id>')
    api.add_resource(ResetPassword,   '/api/reset_password/<string:user_id>')
    api.add_resource(CronExpression,  '/api/cron/expression')

    api.init_app(app)
    socketio.init_app(app)
    cors.init_app(app)
    db.init_app(app)
    db.app = app

    handler = DebugFalseLog().get_handler()
    app.logger.addHandler(handler)

    from app.routes.websocket import ConnectionStatus
    socketio.on_namespace(ConnectionStatus('/api/connection'))

    return app
