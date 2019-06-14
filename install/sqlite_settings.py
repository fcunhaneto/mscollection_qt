from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.engine import Engine
from sqlalchemy import event
import texts
from lib.function_lib import show_msg


class Database:
    def __init__(self):
        self.engine = None
        self.connection = None

    def get_engine(self):
        if not self.engine:
            self.engine = create_engine('sqlite:///db//mscollection.sqlite3')
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

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


Base = declarative_base()
engine = Database().get_engine()

connection = Database().get_connection()

install = True
