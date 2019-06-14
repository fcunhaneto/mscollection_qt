import os
import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QWidget, \
    QTableWidgetItem, QVBoxLayout, QGridLayout, QLabel, QMessageBox, \
    QSpacerItem, QSizePolicy, QCheckBox

import sqlalchemy.exc
from sqlalchemy import desc

import texts

from db.db_model import Actor, Character, Cast
from db.db_model import Movie, MovieCast, Series, SeriesCast
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, get_combobox_info, show_msg, db_get_id, db_select_all, \
    db_insert_obj, le_create
from lib.write_movie_html import write_movie_html
from lib.write_series_html import write_series_html


class EditCast(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Class for edit movie or series cast.

        :param main: Reference for main windows.
        :param type: Type object, movie or series.
        """
        super(EditCast, self).__init__()

        self.main = main
        self.type = type
        self.session = DB.get_session()
        self.id = None
        self.movie_series_cast = None
        self.actor = self.session.query(Actor).order_by(Actor.name).all()
        self.character = self.session.query(Character).order_by(
            Character.name).all()

        if self.type == 'movie':
            windows_title = texts.movie_p + ' ' + texts.cast_s
        else:
            windows_title = texts.series_p + ' ' + texts.cast_s

        self.setWindowTitle(windows_title)
        width = int(0.6 * main.frameSize().width())
        height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, width, height)

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

        # Select Label and Combobox
        if self.type == 'movie':
            select = db_select_all(self.session, Movie)
            text = texts.movie_s
        else:
            select = db_select_all(self.session, Series)
            text = texts.series_s
        self.lb_select = QLabel(text)
        self.lb_select.setFont(font)
        self.lb_select.setFixedHeight(25)
        self.cb_select = cb_create('')
        self.cb_select.setFont(font)
        self.cb_select.setFixedHeight(30)
        populate_combobox(self.cb_select, select)
        self.vbox_main.addWidget(self.lb_select)
        self.vbox_main.addWidget(self.cb_select)

        # Cast Table Add Row
        self.lb_cast = QLabel(texts.cast_s)
        self.lb_cast.setFont(font)
        self.lb_cast.setFixedHeight(25)
        self.pb_add_row = pb_create('+', 11, 25, 50)
        self.pb_add_row.setToolTip(texts.pb_add_row_tt)
        self.pb_add_row.setShortcut('Ctrl+T')
        self.pb_add_row.clicked.connect(self.table_add_rows)

        self.hbox_cast = hbox_create([self.lb_cast, self.pb_add_row])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_cast.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_cast)

        # Cast Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setContentsMargins(20, 0, 0, 0)

        font = QFont()
        font.setPointSize(12)

        self.headers = [
            texts.actor_s,
            texts.character_s,
            texts.order,
            texts.star.capitalize(),
            'Del'
        ]
        self.table.setHorizontalHeaderLabels(self.headers)

        # table set column width
        self.table.setColumnWidth(0, int(0.25 * (width - 50)))
        self.table.setColumnWidth(1, int(0.45 * (width - 50)))
        self.table.setColumnWidth(2, int(0.10 * (width - 50)))
        self.table.setColumnWidth(3, int(0.10 * (width - 50)))
        self.table.setColumnWidth(4, int(0.10 * (width - 45)))

        # self.table.horizontalHeader().setFixedHeight(30)
        self.table.horizontalHeader().setFont(font)
        self.table.horizontalHeader().setStyleSheet(
            'background-color: rgb(230, 230, 230);')
        self.table.verticalHeader().setVisible(False)

        self.vbox_main.addWidget(self.table)

        self.rows = 0
        self.cb_count = 0
        self.ch_del_count = 0
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []
        self.chbox_del = []

        # Buttons Save Clear
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)

        self.pb_save = pb_create(texts.pb_save, height=40)
        self.pb_save.clicked.connect(self.save_cast)
        self.pb_save.setShortcut('Ctrl+S')
        self.grid_layout.addWidget(self.pb_save, 0, 0, 1, 1)

        self.pb_clear = pb_create(texts.pb_clear, height=40)
        self.pb_clear.clicked.connect(self.clear)
        self.pb_clear.setShortcut('Ctrl+L')
        self.grid_layout.addWidget(self.pb_clear, 0, 1, 1, 1)

        self.pb_help = pb_create(texts.pb_help, height=40)
        self.pb_help.clicked.connect(self.help)
        self.pb_help.setShortcut('Ctrl+H')
        self.grid_layout.addWidget(self.pb_help, 0, 2, 1, 1)

        self.pb_leave = pb_create(texts.pb_leave, height=40)
        self.pb_leave.clicked.connect(self.close)
        self.pb_save.setShortcut('Ctrl+Q')
        self.grid_layout.addWidget(self.pb_leave, 0, 3, 1, 1)

        self.vbox_main.addLayout(self.grid_layout)

        self.cb_select.currentIndexChanged.connect(self.selected_movie_series)

    # Selected Movie Series
    def selected_movie_series(self):
        """
        Search MovieCast or SeriesCast values according object selected.
        """
        self.cb_select.currentIndexChanged.disconnect()
        self.id, name = get_combobox_info(self.cb_select)

        if self.type == 'movie':
            self.movie_series_cast = self.session.query(MovieCast). \
                filter(MovieCast.movie_id == self.id).\
                order_by(MovieCast.order, desc(MovieCast.star)).all()
        else:
            self.movie_series_cast = self.session.query(SeriesCast). \
                filter(SeriesCast.series_id == self.id).\
                order_by(SeriesCast.order, desc(SeriesCast.star)).all()

        for mc in self.movie_series_cast:
            actor = mc.cast.actors
            character = mc.cast.characters
            star = mc.star
            order = mc.order
            self.set_table_values(mc.id, actor, character, order, star)

    # Save Cast
    def save_cast(self):
        """
        Save values from cast table in database.
        """
        for i in range(self.ch_del_count):
            if self.chbox_del[i].isChecked():
                if self.type == 'movie':
                    result = self.session.query(MovieCast). \
                        filter(MovieCast.id == self.movie_series_cast[i].id). \
                        delete()
                else:
                    result = self.session.query(SeriesCast). \
                        filter(SeriesCast.id == self.movie_series_cast[i].id). \
                        delete()

                if result == 1:
                    self.session.commit()
                else:
                    self.session.rollback()

                continue

            self.movie_series_cast[i].cast.actor_id = db_get_id(
                self.session, self.cb_actor[i], Actor())

            self.movie_series_cast[i].cast.character_id = db_get_id(
                self.session, self.cb_character[i], Character())

            self.movie_series_cast[i].order = self.le_order[i].text()

            self.movie_series_cast[i].star = self.chbox_star[i].isChecked()

            db_insert_obj(self.session, self.movie_series_cast[i])

        for i in range(self.ch_del_count, self.rows):
            actor_id = db_get_id(self.session, self.cb_actor[i], Actor())

            character_id = db_get_id(
                self.session, self.cb_character[i], Character())

            if actor_id and character_id:
                cast = Cast(actor_id=actor_id, character_id=character_id)
                try:
                    self.session.add(cast)
                    self.session.commit()
                # If except most probably is because cast exist so we try to
                # get it
                except sqlalchemy.exc.IntegrityError:
                    self.session.rollback()
                    self.session.commit()
                    cast = self.session.query(Cast).filter(
                        Cast.actor_id == actor_id,
                        Cast.character_id == character_id).first()

                if cast:
                    if self.type == 'movie':
                        movie_series_cast = MovieCast(
                            movie_id=self.id,
                            cast_id=cast.id,
                            order=self.le_order[i].text(),
                            star=self.chbox_star[i].isChecked()
                        )
                    else:
                        movie_series_cast = SeriesCast(
                            series_id=self.id,
                            cast_id=cast.id,
                            order=self.le_order[i].text(),
                            star=self.chbox_star[i].isChecked()
                        )

                    db_insert_obj(self.session, movie_series_cast)

        movie_series = self.cb_select.currentText()
        name = movie_series + ' ' + texts.cast_s
        text = texts.msg_edit_ok(name)
        show_msg(
            texts.edit_ok, text, QMessageBox.Information, QMessageBox.Close)
        self.clear()

        ms = None
        if self.type == 'movie':
            ms = self.session.query(Movie).get(self.id)
        elif self.type == 'series':
            ms = self.session.query(Series).get(self.id)

        self.session.add(ms)
        self.session.commit()

        if self.type == 'movie':
            ms.view = write_movie_html(self.session, ms)
        elif self.type == 'series':
            ms.view = write_series_html(self.session, ms)

        self.session.add(ms)
        self.session.commit()

    # Set Table Values
    def set_table_values(self, mc, actor, character, order, star):
        """
        Get values for MovieCast or SeriesCast in Database.

        :param mc: MovieCast or SeriesCast value for id column
        :param actor: MovieCast or SeriesCast value for actor column
        :param character: MovieCast or SeriesCast value for character column
        :param order: MovieCast or SeriesCast value for order column
        :param star: MovieCast or SeriesCast value for star column
        """
        self.table_add_rows(order, star, mc)
        row = self.rows - 1
        index = self.cb_actor[row]. \
            findText(actor.name, Qt.MatchFixedString)
        self.cb_actor[row].setCurrentIndex(index)

        index = self.cb_character[row]. \
            findText(character.name, Qt.MatchFixedString)
        self.cb_character[row].setCurrentIndex(index)

    # CHBOX Star Changed
    def chbox_star_changed(self, ch):
        """
        Change icon on star checkbox.

        :param ch: QCheckBox.
        """
        icon = QIcon()
        if ch.isChecked():
            icon.addPixmap(QPixmap('images/star_yellow_16.png'), QIcon.Normal,
                           QIcon.Off)
        else:
            icon.addPixmap(QPixmap('images/star_withe_16.png'), QIcon.Normal,
                           QIcon.Off)

        ch.setIcon(icon)

    # Table Add Rows
    def table_add_rows(self, order, star=None, mc=None):
        """
        Add rows in table.

        :param order: MovieCast or SeriesCast value for order column
        :param star: MovieCast or SeriesCast value for star column
        :param mc: MovieCast or SeriesCast value for id column
        """
        self.table.insertRow(self.rows)

        cb = cb_create('')
        populate_combobox(cb, self.actor)
        self.cb_actor.append(cb)
        self.table.setCellWidget(self.rows, 0, self.cb_actor[self.cb_count])

        cb = cb_create('')
        populate_combobox(cb, self.character)
        self.cb_character.append(cb)
        self.table.setCellWidget(self.rows, 1, self.cb_character[self.cb_count])

        le = le_create(4)
        le.setStyleSheet('padding-left: 10px;')
        self.le_order.append(le)
        if order:
            self.le_order[self.cb_count].setText(str(order))
        else:
            self.le_order[self.cb_count].setText('')
        self.table.setCellWidget(self.rows, 2, self.le_order[self.cb_count])

        ch_star = QCheckBox()
        self.chbox_star.append(ch_star)
        if star:
            self.chbox_star[self.cb_count].setChecked(True)
            icon = QIcon()
            icon.addPixmap(QPixmap('images/star_yellow_16.png'), QIcon.Normal,
                           QIcon.Off)
        else:
            icon = QIcon()
            icon.addPixmap(QPixmap('images/star_withe_16.png'), QIcon.Normal,
                           QIcon.Off)

        i = self.cb_count
        self.chbox_star[i].stateChanged. \
            connect(lambda: self.chbox_star_changed(self.chbox_star[i]))
        self.chbox_star[i].setIcon(icon)

        hb_star = hbox_create([self.chbox_star[i]], 0)
        hb_star.setAlignment(Qt.AlignCenter)
        cell_star = QWidget()
        cell_star.setLayout(hb_star)

        self.table.setCellWidget(self.rows, 3, cell_star)

        ch_del = None
        if mc:
            ch_del = QCheckBox()
            self.chbox_del.append(ch_del)
            hb_del = hbox_create([self.chbox_del[self.ch_del_count]], 0)
            hb_del.setAlignment(Qt.AlignCenter)
            cell_del = QWidget()
            cell_del.setLayout(hb_del)
            self.table.setCellWidget(self.rows, 4, cell_del)
            self.ch_del_count += 1
        else:
            self.table.setItem(self.rows, 4, QTableWidgetItem(' '))

        if self.rows % 2 != 0:
            self.table.cellWidget(self.rows, 0).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table.cellWidget(self.rows, 1).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table.cellWidget(self.rows, 2).setStyleSheet(
                'background-color: #E6E6E6; padding-left: 10px;'
            )
            self.table.cellWidget(self.rows, 3).setStyleSheet(
                'background-color: #E6E6E6;'
                'color: #E6E6E6;'
            )
            if ch_del:
                self.table.cellWidget(self.rows, 4).setStyleSheet(
                    'background-color: #E6E6E6;'
                    'color: #E6E6E6;'
                )
            else:
                self.table.item(self.rows, 4).setBackground(
                    QColor(230, 230, 230))

        self.table.setRowHeight(self.rows, 35)

        self.cb_count += 1
        self.rows += 1

    # Set combobox values
    def set_combobox_value(self, cb, name):
        """
        Set correct value from database in combobox.

        :param cb: The QComboBox who need set value.
        :param name: The name that needs to be set in the QComboBox.
        """
        index = cb.findText(name, Qt.MatchFixedString)
        cb.setCurrentIndex(index)

    # Clear
    def clear(self):
        """
        Clear all values in windows.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.rows = 0
        self.cb_count = 0
        self.ch_del_count = 0
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []
        self.chbox_del = []
        self.session.expire_all()
        self.cb_select.setCurrentIndex(0)
        self.cb_select.currentIndexChanged.connect(self.selected_movie_series)
        self.actor = self.session.query(Actor).order_by(Actor.name).all()
        self.character = self.session.query(Character).order_by(
            Character.name).all()

    # Help
    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_edit_cast.html'
        self.main.views_help(url, texts.help_edit_cast)

    def closeEvent(self, event):
        self.session.close()
