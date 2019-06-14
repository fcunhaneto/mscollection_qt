from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import texts
from db import db_values as dbs
from lib.function_lib import show_msg


class Database:
    def __init__(self):
        self.engine = None
        self.connection = None

    def get_engine(self):
        if not self.engine:
            url = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
                dbs.user,
                dbs.pw,
                dbs.host,
                dbs.port,
                dbs.name
            )
            self.engine = create_engine(url)

        return self.engine

    @staticmethod
    def get_session():
        Session = sessionmaker(bind=engine)
        return Session()

    def get_connection(self):
        if not self.connection:
            try:
                engine = self.get_engine()
                self.connection = engine.connect()
            except OperationalError as error:
                show_msg(texts.db_error, texts.msg_db_conn,
                         QMessageBox.Critical, QMessageBox.Close, str(error))

        return self.connection


Base = declarative_base()
engine = Database().get_engine()

connection = Database().get_connection()

install = True
