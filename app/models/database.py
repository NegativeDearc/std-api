from sqlalchemy import Column, String, Integer, BOOLEAN, DATE, TIMESTAMP
from uuid import uuid4
from app import db
from sqlalchemy.dialects.mysql import TIME


def generate_uid():
    return uuid4().__str__()


class Users(db.Model):
    __tablename__ = 'std_users'

    id          = Column(Integer, autoincrement=True, primary_key=True)
    userId      = Column(Integer, nullable=False, unique=True)
    userName    = Column(String(50), nullable=False)
    password    = Column(String(100), nullable=False, default='123456')
    mailAddress = Column(String(100))
    isActivated = Column(BOOLEAN)
    segmentCode = Column(String(20))
    group       = Column(String(20))


class Tasks(db.Model):
    __tablename__ = 'std_tasks'

    id              = Column(Integer, autoincrement=True, primary_key=True)
    uid             = Column(String(50), default=generate_uid)
    taskTitle       = Column(String(200), nullable=False)
    taskDescription = Column(String(300))
    createBy        = Column(Integer, nullable=False)
    category        = Column(String(20))
    frequency       = Column(String(50))
    nextLoopAt      = Column(TIMESTAMP)
    punchTime       = Column(TIMESTAMP)
    remindAt        = Column(TIME, nullable=False)
    dueDate         = Column(DATE)
    isDone          = Column(BOOLEAN, default=False)
    isLoop          = Column(BOOLEAN, default=False)
    isVisible       = Column(BOOLEAN, default=True)
    taskTags        = Column(String(100))
    remark          = Column(String(200))


class Tree(db.Model):
    __tablename__ = 'std_tree'

    id   = Column(Integer, autoincrement=True, primary_key=True)
    tree = Column(String(20), nullable=False)
    node = Column(String(100))