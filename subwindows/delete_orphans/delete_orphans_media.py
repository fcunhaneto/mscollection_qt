import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QWidget, \
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QCheckBox

from sqlalchemy import and_

import texts
from db.db_model import Media, Movie, Series
from db.db_settings import Database as DB
from lib.function_lib import hbox_create, pb_create, delete_orphans


class DeleteOrphansMedia(QMdiSubWindow):
    def __init__(self, main):
        """
        Class for delete media who are orphan in database.

        :param main: Reference for main windows.
        """
        super(DeleteOrphansMedia, self).__init__()

        self.session = DB.get_session()
        self.type = type
        self.main = main

        window_title = texts.delete_orphans + ' ' + texts.movie_p

        self.setWindowTitle(window_title)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        font = QFont()
        font.setPointSize(12)

        # Vbox Main
        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)
        self.vbox_main.setSpacing(10)

        # Table Cast
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setContentsMargins(20, 0, 0, 0)

        self.table.setHorizontalHeaderLabels([
            texts.box,
            'Del'
        ])

        # table set column width
        w = int(0.5 * main.frameSize().width())
        col_1 = int(0.60 * (w - 50))
        col_2 = int(0.20 * (w - 50))
        col_width = col_1 + col_2 + 4

        self.table.setColumnWidth(0, col_1)
        self.table.setColumnWidth(1, col_2)
        self.table.rowHeight(30)
        self.table.setFixedWidth(col_width)

        self.table.horizontalHeader().setFont(font)
        self.table.horizontalHeader().setStyleSheet(
            'background-color: rgb(230, 230, 230);')
        self.table.verticalHeader().setVisible(False)

        self.rows = 0
        self.ch_del = []

        self.vbox_main.addWidget(self.table)

        # Buttons
        self.pb_delete = pb_create(texts.pb_delete, 12, 40)
        self.pb_delete.setMinimumHeight(40)
        self.pb_delete.setShortcut('Ctrl+D')
        self.pb_delete.clicked.connect(self.delete)

        self.pb_leave = pb_create(texts.pb_leave, 12, 40)
        self.pb_leave.setMinimumHeight(40)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        self.pb_help = pb_create(texts.pb_help, height=40)
        self.pb_help.setMinimumHeight(40)
        self.pb_help.clicked.connect(self.help)
        self.pb_help.setShortcut('Ctrl+H')

        self.pb_select_all = pb_create(texts.pb_select_all, 12, 40)
        self.pb_select_all.setMinimumHeight(40)
        self.pb_select_all.setShortcut('Ctrl+A')
        self.pb_select_all.clicked.connect(self.select_all)

        self.hb_pb = QHBoxLayout()
        self.hb_pb.setSpacing(10)
        self.hb_pb.addWidget(self.pb_delete)
        self.hb_pb.addWidget(self.pb_leave)
        self.hb_pb.addWidget(self.pb_help)
        self.hb_pb.addWidget(self.pb_select_all)

        self.vbox_main.addLayout(self.hb_pb)

        self.width = col_width + 44
        self.height_min = int(0.5 * main.frameSize().height())
        self.setGeometry(0, 0, self.width, self.height_min)

        self.create_table()

    def create_table(self):
        """
        Create a table for show all orphan medias info and with a QCheckBox
        that if is check the actor will be delete.
        """
        media_movie = self.session.query(Movie.media_id).filter(
            Movie.media_id.isnot(None))
        sub_media_movie = media_movie.distinct()

        media_series = self.session.query(Series.media_id).filter(
            Series.media_id.isnot(None))
        sub_media_series = media_series.distinct()

        media_result = self.session.query(Media).\
            filter(and_(Media.id.notin_(sub_media_movie),
                        Media.id.notin_(sub_media_series))).all()

        for media in media_result:
            self.table.insertRow(self.rows)
            self.table.setItem(self.rows, 0, QTableWidgetItem(media.name))

            ch_del = QCheckBox(str(media.id))
            self.ch_del.append(ch_del)
            hb_del = hbox_create([self.ch_del[self.rows]], 0)
            hb_del.setAlignment(Qt.AlignCenter)
            cell_del = QWidget()
            cell_del.setLayout(hb_del)
            self.table.setCellWidget(self.rows, 1, cell_del)

            if self.rows % 2 != 0:
                self.table.item(self.rows, 0).setBackground(
                    QColor(230, 230, 230)
                )
                self.table.cellWidget(self.rows, 1).setStyleSheet(
                    'background-color: #E6E6E6;'
                    'color: #E6E6E6;'
                )
            else:
                self.table.cellWidget(self.rows, 1).setStyleSheet(
                    'color: #FFFFFF;'
                )

            self.table.item(self.rows, 0).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled
            )

            self.rows += 1

        height = self.rows * 30 + 20
        self.table.setMinimumHeight(height)
        self.height = height + 130
        self.setGeometry(0, 0, self.width, self.height)

    def delete(self):
        """
        Delete media from database.
        """
        delete_orphans(self.session, self.ch_del, Media, texts.media_s)
        self.clear()
        self.create_table()

    def select_all(self):
        """
        Mark all delete QCheckBox.
        """
        for ch in self.ch_del:
            ch.setChecked(True)

    # Clear
    def clear(self):
        """
        Clear all values in windows.
        """
        for row in range(self.rows):
            self.table.removeRow(row)
        self.table.clear()
        self.table.setRowCount(0)
        self.rows = 0
        self.ch_del = []
        self.session.expire_all()

    # Help
    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_delete_orphans.html'
        self.main.views_help(url, texts.help_edit_movie)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
