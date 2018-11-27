from flask_restful import Resource, marshal_with, fields, reqparse
from app.models.database import Users, Tasks
from app import db
from flask import jsonify, request, make_response
from itertools import groupby
from operator import itemgetter
from sqlalchemy import desc, asc, or_, and_, func
from cron_descriptor import get_description, Options
from app.utils.next_run import next_run
from app.utils.rolling_days_from_now import rolling_days
from app.utils.pattern_search import is_central, is_management
import datetime


class Login(Resource):
    def post(self):
        user = db.session.query(Users).filter(Users.userId == request.form['userId']).first()
        db.session.close()
        if user and user.password == request.form['password']:
            response = jsonify({"userId": user.userId, "userName": user.userName, "userGroup": user.group})
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
        'isVisible': fields.Boolean,
        'remark': fields.String
    }

    @marshal_with(resource_fields)
    def get(self, task_id):
        task = db.session.query(Tasks).filter(Tasks.id == task_id, Tasks.isVisible == True).first()
        db.session.close()
        return task, 200

    def post(self, task_id):
        this_task = db.session.query(Tasks).filter(Tasks.id == task_id).first()
        update_form = request.json

        for k in list(update_form.keys()):
            if getattr(this_task, k) == update_form[k]:
                del update_form[k]

        if update_form:
            try:
                db.session.query(Tasks).filter(Tasks.id == task_id).update(update_form)
                if 'frequency' in update_form.keys():
                    this_task.nextLoopAt = next_run(update_form.get('frequency'), last_run_at=None)
                db.session.commit()
                return make_response(('updated', 200))
            except Exception as e:
                db.session.rollback()
                return make_response((str(e), 500))
        else:
            pass

    @marshal_with(resource_fields)
    def put(self, task_id):
        _is_done = request.form.get('isDone')

        if _is_done == 'true':
            is_done = True
        elif _is_done == 'false':
            is_done = False

        task = db.session.query(Tasks).filter(Tasks.id == task_id).first()

        if task.frequency is not None and \
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
        'isVisible': fields.Boolean,
        'remark': fields.String
    }

    @marshal_with(resource_fields)
    def get(self, user_id):
        # if need sort by multi-key
        # .order_by(asc(Tasks.isDone), asc(func.timestamp(Tasks.nextLoopAt, Tasks.remindAt))) \

        tasks = db.session.query(Tasks) \
            .filter(Tasks.createBy == user_id, Tasks.isVisible == True) \
            .order_by(asc(Tasks.isDone), asc(func.timestamp(Tasks.nextLoopAt, Tasks.remindAt))) \
            .all()
        db.session.close()

        return tasks, 200

    def post(self, user_id):
        print(request.json)

        task = Tasks(
            taskTitle=request.json.get("taskTitle"),
            taskDescription=request.json.get("taskDescription"),
            createBy=user_id,
            frequency=request.json.get("taskRepeatInterval"),
            freqDescription=request.json.get("taskFreqDescription", None),
            remindAt=request.json.get("taskRemindAt", None),
            taskTags=request.json.get("taskTags"),
            nextLoopAt=next_run(request.json.get("taskRepeatInterval"), last_run_at=None)
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
        on_time_finish = db.session.query(func.count(Tasks.id)) \
            .filter(
            Tasks.createBy == user_id,
            Tasks.isVisible == True,
            Tasks.punchTime <= Tasks.nextLoopAt
        ).one()

        in_progress = db.session.query(func.count(Tasks.id)) \
            .filter(
            Tasks.createBy == user_id,
            Tasks.isDone == False,
            Tasks.isVisible == True,
            Tasks.nextLoopAt >= datetime.datetime.now(),
        ).one()

        delay = db.session.query(func.count(Tasks.id)) \
            .filter(
            or_(
                and_(
                    Tasks.createBy == user_id,
                    Tasks.isDone == False,
                    Tasks.isVisible == True,
                    Tasks.nextLoopAt < datetime.datetime.now()),
                and_(
                    Tasks.createBy == user_id,
                    Tasks.isDone == True,
                    Tasks.isVisible == True,
                    Tasks.punchTime > Tasks.nextLoopAt)
            )
        ).one()

        return {'OTF': on_time_finish[0], 'IP': in_progress[0], 'D': delay[0]}, 200


class Punch(Resource):
    def get(self, user_id):
        user_group = db.session.query(Users.group).filter(Users.userId == user_id).one()
        user_group_suffix = user_group.group.split('OP/SCN-')[1]

        if len(user_group_suffix) > 2 and not is_central(user_group_suffix):
            group = user_group_suffix[:3]
        elif len(user_group_suffix) <= 2 and is_management(user_group_suffix):
            group = user_group_suffix
        elif is_central(user_group_suffix) is True:
            group = user_group_suffix[:2]
        else:
            pass

        rv = db.session.query(
            Tasks.id,
            Tasks.taskTitle,
            Tasks.taskDescription,
            Tasks.createBy,
            Tasks.nextLoopAt.label('needFinishBefore'),
            Tasks.punchTime,
            (Tasks.frequency != 0).label('isLoop'),
            (or_(
                and_(
                    Tasks.isDone == True,
                    Tasks.punchTime > Tasks.nextLoopAt),
                and_(
                    Tasks.isDone == False,
                    func.current_timestamp() > Tasks.nextLoopAt)
            )).label('isDelay'),
            Tasks.isDone,
            Users.group,
            Users.userName
        ) \
            .join(Users, Tasks.createBy == Users.userId) \
            .filter(Users.group.like('%%%s%%' % group),
                    and_(Tasks.nextLoopAt <= rolling_days()[1],
                         Tasks.nextLoopAt >= rolling_days()[0]),
                    Tasks.isVisible == True
                    ).order_by(Tasks.nextLoopAt).all()

        res = []

        for x in rv:
            res.append(x._asdict())

        res.sort(key=itemgetter('userName'))
        res_grouped = groupby(res, itemgetter('userName'))

        result = dict([(key, list(group)) for key, group in res_grouped])
        return jsonify(result)


class ResetPassword(Resource):
    def post(self, user_id):
        print(request.form)
        user = db.session.query(Users).filter(Users.userId == user_id).one()
        if user and user.password == request.form.get('original'):
            user.password = request.form.get('new')
            db.session.commit()
            return make_response(('Modified Success', 200))
        else:
            return make_response(('Error!', 401))


class CronExpression(Resource):
    options = Options()
    options.locale_code = 'zh_CN'

    def post(self):
        try:
            cron_expression = request.form.get('expression', None)
            if cron_expression:
                expression = get_description(cron_expression, options=self.options)
                return {'description': str(expression)}, 200
            else:
                return make_response(('', 200))
        except Exception as e:
            return {'err': 'not valid %s' % e}, 500


class PlantDash(Resource):
    def get(self, segment):
        finished = db.session.query(func.count(Tasks.id).label('count')) \
            .join(Users, Tasks.createBy == Users.userId) \
            .filter(Users.group.like('%%%s%%' % segment),
                    Tasks.isDone == True,
                    and_(Tasks.nextLoopAt <= rolling_days()[1],
                         Tasks.nextLoopAt >= rolling_days()[0]),
                    Tasks.isVisible == True).one()

        total = db.session.query(func.count(Tasks.id).label('count'))\
            .join(Users, Tasks.createBy == Users.userId) \
            .filter(Users.group.like('%%%s%%' % segment),
                    and_(Tasks.nextLoopAt <= rolling_days()[1],
                         Tasks.nextLoopAt >= rolling_days()[0]),
                    Tasks.isVisible == True).one()

        try:
            rate = '%.1f' % (finished.count/total.count * 100)
        except ZeroDivisionError:
            rate = None

        return jsonify({'finishRate': rate})


class PlantDashDetail(Resource):
    def get(self, segment):
        rv = db.session.query(
            Tasks.id,
            Tasks.taskTitle,
            Tasks.taskDescription,
            Tasks.createBy,
            Tasks.nextLoopAt.label('needFinishBefore'),
            Tasks.punchTime,
            (Tasks.frequency != 0).label('isLoop'),
            (or_(
                and_(
                    Tasks.isDone == True,
                    Tasks.punchTime > Tasks.nextLoopAt),
                and_(
                    Tasks.isDone == False,
                    func.current_timestamp() > Tasks.nextLoopAt)
            )).label('isDelay'),
            Tasks.isDone,
            Users.group,
            Users.userName
        ) \
            .join(Users, Tasks.createBy == Users.userId) \
            .filter(Users.group.like('%%%s%%' % segment),
                    and_(Tasks.nextLoopAt <= rolling_days()[1],
                         Tasks.nextLoopAt >= rolling_days()[0]),
                    Tasks.isVisible == True
                    ).order_by(Tasks.nextLoopAt).all()

        res = []

        for x in rv:
            res.append(x._asdict())

        res.sort(key=itemgetter('userName'))
        res_grouped = groupby(res, itemgetter('userName'))

        result = dict([(key, list(group)) for key, group in res_grouped])
        return jsonify(result)