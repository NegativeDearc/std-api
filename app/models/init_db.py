from run import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Users, Tasks, Tree
import pandas as pd


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)


def create_all(_engine):
    Users.metadata.create_all(bind=_engine)
    Tasks.metadata.create_all(bind=_engine)
    Tree.metadata.create_all(bind=_engine)


def init_users():
    df = pd.read_csv('/Users/Dearc/Desktop/book1.csv')
    df.to_sql('std_users', engine, if_exists='append', index=False)


if __name__ == '__main__':
    init_users()
