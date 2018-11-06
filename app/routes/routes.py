from flask_restful import Resource, marshal_with, fields, reqparse
from app.models.database import Users, Tasks
from app import db
from flask import jsonify, request, make_response
from sqlalchemy import desc, asc, or_, and_, func
from app.utils.next_run import next_run
import datetime


class Login(Resource):
    def post(self):
        user = db.session.query(Users).filter(Users.userId == request.form['userId']).first()
        db.session.close()
        if user and user.password == request.form['password']:
            response = jsonify({"userId": user.userId})
            response.status_code = 200
            return response
        else:
            return make_response(('Invalid User', 401))


class Task(Resource):
    resource_fields = {
        'id': fields.Integer,
        'uid': fields.String,
        'taskTitle': fields.String,
        'taskDescription': fields.String,
        'createBy': fields.Integer,
        'frequency': fields.String,
        'nextLoopAt': fields.String,
        'punchTime': fields.String,
        'remindAt': fields.String,
        'dueDate': fields.String,
        'isDone': fields.Boolean,
        'isLoop': fields.Boolean,
        'taskTags': fields.String,
        'isVisible': fields.Boolean
    }

    @marshal_with(resource_fields)
    def get(self, task_id):
        task = db.session.query(Tasks).filter(Tasks.id == task_id, Tasks.isVisible == True).first()
        db.session.close()
        return task, 200

    def post(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('taskTitle', type=str)
        parser.add_argument('taskDescription', type=str)
        parser.add_argument('dueDate', type=str)
        parser.add_argument('frequency', type=str)
        parser.add_argument('remindAt', type=str)
        parser.add_argument('taskTags', type=str)

        args = parser.parse_args()

        form = {}

        for k, v in args.items():
            if v is not None:
                form.update({k: v})

        db.session.query(Tasks).filter(Tasks.id == task_id) \
            .update(form)
        db.session.commit()

        return make_response(('UPDATED', 200))

    @marshal_with(resource_fields)
    def put(self, task_id):
        _is_done = request.form.get('isDone')

        if _is_done == 'true':
            is_done = True
        elif _is_done == 'false':
            is_done = False

        task = db.session.query(Tasks).filter(Tasks.id == task_id).first()

        if task.frequency != '' and \
                task.isDone is False and \
                (task.isLoop is False or task.isLoop is None):
            new_task = Tasks(
                taskTitle=task.taskTitle,
                uid=task.uid,
                taskDescription=task.taskDescription,
                createBy=task.createBy,
                frequency=task.frequency,
                remindAt=task.remindAt,
                dueDate=task.dueDate,
                taskTags=task.taskTags,
                nextLoopAt=next_run(task.frequency, task.nextLoopAt),
                isVisible=True
            )
            db.session.add(new_task)

        db.session.query(Tasks).filter(Tasks.id == task_id) \
            .update({
            'isDone': is_done,
            'punchTime': datetime.datetime.now() if is_done else None,
            'isLoop': True
        })

        try:
            db.session.commit()
            return task, 200
        except Exception as e:
            return e, 500

    def delete(self, task_id):
        db.session.query(Tasks).filter(Tasks.id == task_id). \
            update({'isVisible': False})

        db.session.commit()

        return make_response(('deleted', 200))


class UserTask(Resource):
    resource_fields = {
        'id': fields.Integer,
        'uid': fields.String,
        'taskTitle': fields.String,
        'taskDescription': fields.String,
        'createBy': fields.Integer,
        'frequency': fields.String,
        'nextLoopAt': fields.String,
        'punchTime': fields.String,
        'remindAt': fields.String,
        'dueDate': fields.String,
        'isDone': fields.Boolean,
        'isLoop': fields.Boolean,
        'taskTags': fields.String,
        'isVisible': fields.Boolean
    }

    @marshal_with(resource_fields)
    def get(self, user_id):
        tasks = db.session.query(Tasks) \
            .filter(Tasks.createBy == user_id, Tasks.isVisible == True) \
            .order_by(asc(Tasks.isDone), desc(Tasks.nextLoopAt)) \
            .all()
        db.session.close()

        return tasks, 200

    def post(self, user_id):
        task = Tasks(
            taskTitle=request.form.get("taskName"),
            taskDescription=request.form.get("taskDescription"),
            createBy=user_id,
            frequency=request.form.get("taskRepeatInterval"),
            remindAt=request.form.get("taskTimeSlot"),
            dueDate=request.form.get("taskDueDateParsed"),
            taskTags=request.form.get("taskTags"),
            nextLoopAt=next_run(request.form.get("taskRepeatInterval"), last_run_at=None)
        )

        db.session.add(task)
        try:
            db.session.commit()
            return make_response(('created', 201))
        except Exception as e:
            db.session.rollback()
            return make_response((str(e), 500))

    def put(self, task_id):
        pass

    def delete(self, task_id):
        db.session.query(Tasks).filter(Tasks.id == task_id) \
            .update({'isVisible': False})
        db.session.commit()

        return make_response(('OK', 200))


class Search(Resource):
    def get(self):
        pass


class Dash(Resource):
    def get(self, user_id):
        on_time_finish = db.session.query(func.count(Tasks.id))\
            .filter(
            Tasks.createBy == user_id,
            Tasks.isVisible == True,
            Tasks.punchTime <= func.timestamp(Tasks.nextLoopAt, Tasks.remindAt)
        ).one()

        in_progress = db.session.query(func.count(Tasks.id))\
            .filter(
            Tasks.createBy == user_id,
            Tasks.isDone == False,
            Tasks.isVisible == True,
            func.timestamp(Tasks.nextLoopAt, Tasks.remindAt) >= datetime.datetime.now(),
        ).one()

        delay = db.session.query(func.count(Tasks.id))\
            .filter(
                and_(
                    Tasks.createBy == user_id,
                    Tasks.isDone == False,
                    Tasks.isVisible == True,
                    func.timestamp(Tasks.nextLoopAt, Tasks.remindAt) < datetime.datetime.now()),
                and_(
                    Tasks.createBy == user_id,
                    Tasks.isDone == True,
                    Tasks.isVisible == True,
                    Tasks.punchTime > func.timestamp(Tasks.nextLoopAt, Tasks.remindAt))
        ).one()

        return {'OTF': on_time_finish[0], 'IP': in_progress[0], 'D': delay[0]}, 200


class Punch(Resource):
    # ref: https://github.com/flask-restful/flask-restful/issues/469
    # for marshal issue all null problem
    resource_fields = {
        'needFinishBefore': fields.DateTime(dt_format='iso8601'),
        'punchTime': fields.DateTime(dt_format='iso8601'),
        'isDelay': fields.Boolean,
        'isDone': fields.Boolean,
        'isLoop': fields.Boolean
    }

    @marshal_with(resource_fields)
    def get(self, user_id):
        rv = db.session.query(
            Tasks.id,
            func.timestamp(Tasks.nextLoopAt, Tasks.remindAt).label('needFinishBefore'),
            Tasks.punchTime,
            (Tasks.frequency != 0).label('isLoop'),
            (or_(Tasks.punchTime > func.timestamp(Tasks.nextLoopAt, Tasks.remindAt),
                 Tasks.nextLoopAt < func.current_timestamp())).label('isDelay'),
            Tasks.isDone
        ).filter(Tasks.createBy == user_id).order_by(func.timestamp(Tasks.nextLoopAt, Tasks.remindAt)).all()

        res = []

        for x in rv:
            res.append(x._asdict())

        return res
