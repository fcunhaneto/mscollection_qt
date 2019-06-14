from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, QVBoxLayout, \
    QLabel, QProgressBar

import texts

from db.db_model import Movie, Series
from db.db_settings import Database as DB

from lib.function_lib import pb_create
from lib.write_movie_html import write_movie_html
from lib.write_series_html import write_series_html


class RewriteHtml(QMdiSubWindow):
    def __init__(self, main):
        super(RewriteHtml, self).__init__()

        self.session = DB.get_session()
        self.cb_categories = []
        self.main = main

        self.setWindowTitle(texts.rewrite_html)
        width = int(0.4 * main.frameSize().width())
        height = int(0.2 * main.frameSize().height())
        self.setGeometry(0, 0, width, height)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        # Series Left Side
        self.fm = QFormLayout()
        self.fm.setSpacing(10)
        self.fm.setContentsMargins(0, 0, 5, 0)

        self.lb_movies = QLabel(texts.movie_s)
        self.p_bar_movies = QProgressBar()
        self.p_bar_movies.setValue(0)
        self.fm.setWidget(0, QFormLayout.LabelRole, self.lb_movies)
        self.fm.setWidget(0, QFormLayout.FieldRole, self.p_bar_movies)

        self.lb_series = QLabel(texts.series_p)
        self.p_bar_series = QProgressBar()
        self.p_bar_series.setValue(0)
        self.fm.setWidget(1, QFormLayout.LabelRole, self.lb_series)
        self.fm.setWidget(1, QFormLayout.FieldRole, self.p_bar_series)

        self.pb_rewrite = pb_create(texts.pb_rewrite_html)
        self.pb_rewrite.clicked.connect(self.rewrite_html)
        self.pb_rewrite.setShortcut('Ctrl+R')
        self.fm.setWidget(2, QFormLayout.FieldRole, self.pb_rewrite)

        self.vbox_main.addLayout(self.fm)

    def rewrite_html(self):
        session = DB.get_session()

        movies = session.query(Movie).all()

        total = len(movies)
        self.p_bar_movies.setMaximum(total)
        i = 1
        for m in movies:
            view = write_movie_html(session, m)
            m.view = view
            session.commit()

            self.p_bar_movies.setValue(i)
            i += 1

        series = session.query(Series).all()

        total = len(series)
        self.p_bar_series.setMaximum(total)
        i = 1
        for s in series:
            view = write_series_html(session, s)
            s.view = view
            session.commit()

            self.p_bar_series.setValue(i)
            i += 1
            
            
            






