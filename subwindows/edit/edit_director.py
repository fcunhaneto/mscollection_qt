import os
import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QWidget, \
    QTableWidgetItem, QVBoxLayout, QGridLayout, QLabel, QLineEdit, \
    QSpacerItem, QSizePolicy, QCheckBox

from sqlalchemy.orm.exc import ObjectDeletedError

import texts

from db.db_model import Director, Movie, MovieDirector
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, get_combobox_info, show_msg, db_get_id, db_select_all, \
    db_insert_obj
from lib.write_movie_html import write_movie_html


class EditDirector(QMdiSubWindow):
    def __init__(self, main):
        """
        Class for edit director.

        :param main: Reference for main windows.
        :param type: Type object, movie or series.
        """
        super(EditDirector, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.id = None
        self.movie_director = None

        title = texts.edit + texts.movie_s + texts.director_p
        self.setWindowTitle(title)
        width = int(0.4 * main.frameSize().width())
        height = int(0.6 * main.frameSize().height())
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
        movie = self.session.query(Movie).all()
        self.lb_select = QLabel(texts.movie_s)
        self.lb_select.setFont(font)
        self.lb_select.setFixedHeight(25)
        self.cb_select = cb_create('')
        self.cb_select.setFont(font)
        self.cb_select.setFixedHeight(30)
        populate_combobox(self.cb_select, movie)
        self.vbox_main.addWidget(self.lb_select)
        self.vbox_main.addWidget(self.cb_select)

        self.lb_director = QLabel(texts.director_p)
        self.lb_director.setFont(font)
        self.lb_director.setFixedHeight(25)
        self.pb_add_row = pb_create('+', 11, 25, 50)
        self.pb_add_row.setToolTip(texts.pb_add_row_tt)
        self.pb_add_row.setShortcut('Ctrl+T')
        self.pb_add_row.clicked.connect(self.table_add_rows)

        self.hbox_director = hbox_create([self.lb_director, self.pb_add_row])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_director.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_director)

        # Director Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setContentsMargins(20, 0, 0, 0)

        font = QFont()
        font.setPointSize(12)

        self.table.setHorizontalHeaderLabels([
            texts.director_s,
            texts.order,
            'Del'
        ])

        # table set column width
        self.table.setColumnWidth(0, int(0.60 * (width - 50)))
        self.table.setColumnWidth(1, int(0.20 * (width - 50)))
        self.table.setColumnWidth(2, int(0.20 * (width - 50)))

        # self.table.horizontalHeader().setFixedHeight(30)
        self.table.horizontalHeader().setFont(font)
        self.table.horizontalHeader().setStyleSheet(
            'background-color: rgb(230, 230, 230);')
        self.table.verticalHeader().setVisible(False)

        self.vbox_main.addWidget(self.table)

        self.rows = 0
        self.chbox_count = 0
        self.cb_director = []
        self.le = []
        self.chbox_del = []

        # Buttons Save Clear
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)

        self.pb_save = pb_create(texts.pb_save, height=40)
        self.pb_save.clicked.connect(self.save_movie_director)
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

        self.cb_select.currentIndexChanged.connect(self.selected_movie)

    # Selected Movie
    def selected_movie(self):
        """
        When movie is selected search director values in database.
        """
        self.cb_select.currentIndexChanged.disconnect()
        self.id, name = get_combobox_info(self.cb_select)

        self.movie_director = self.session.query(MovieDirector). \
                filter(MovieDirector.movie_id == self.id).all()

        for md in self.movie_director:
            self.set_table_values(md)

    # Save MovieDirector
    def save_movie_director(self):
        """
        Save the edit to the database.
        """
        for i in range(self.chbox_count):
            if self.chbox_del[i].isChecked():
                id = self.chbox_del[i].text()

                try:
                    result = self.session.query(MovieDirector).\
                        filter(MovieDirector.id == id).delete()
                except ObjectDeletedError:
                    continue

                if result == 1:
                    self.session.commit()

                continue

            self.movie_director[i].director_id = db_get_id(
                self.session, self.cb_director[i], Director())
            self.movie_director[i].order = self.le[i].text()

            db_insert_obj(self.session, self.movie_director[i])

        for i in range(self.chbox_count, self.rows):
            id, name = get_combobox_info(self.cb_director[i])
            order = self.le[i].text()

            if id != 0:
                movie_director = MovieDirector(
                    movie_id=self.id, director_id=id, order=order)
                self.session.add(movie_director)
            else:
                director = db_insert_obj(self.session, Director(name=name))
                movie_director = MovieDirector(
                    movie_id=self.id, director_id=director.id, order=order)
                self.session.add(movie_director)

        movie = self.session.query(Movie).get(self.id)
        self.session.commit()

        movie.view = write_movie_html(self.session, movie)
        self.session.commit()

        self.clear()

    # Set Table Values
    def set_table_values(self, md):
        """
        Set combobox in table with director values from database.

        :param md: Object deirector.
        """
        self.table_add_rows(md.id, md.order)
        row = self.rows - 1
        director = md.director.name
        index = self.cb_director[row]. \
            findText(director, Qt.MatchFixedString)
        self.cb_director[row].setCurrentIndex(index)

    # Table Add Rows
    def table_add_rows(self, id=None, order=None):
        """
        Add rows to table.

        :param id: The id of director.
        :param order: The order of director.
        """
        self.table.insertRow(self.rows)
        cb = cb_create('')
        director = self.session.query(Director).order_by(Director.name).all()
        populate_combobox(cb, director)
        self.cb_director.append(cb)
        self.table.setCellWidget(self.rows, 0, self.cb_director[self.rows])

        le = QLineEdit()
        le.setAlignment(Qt.AlignHCenter)
        le.setPlaceholderText('press enter to confirm')
        self.le.append(le)
        self.table.setCellWidget(self.rows, 1, self.le[self.rows])

        if order:
            self.le[self.rows].setText(str(order))

        ch_del = None
        if id:
            ch_del = QCheckBox(str(id))
            self.chbox_del.append(ch_del)
            hb_del = hbox_create([self.chbox_del[self.chbox_count]], 0)
            hb_del.setAlignment(Qt.AlignCenter)
            cell_del = QWidget()
            cell_del.setLayout(hb_del)
            self.table.setCellWidget(self.rows, 2, cell_del)
            self.chbox_count += 1
        else:
            self.table.setItem(self.rows, 1, QTableWidgetItem(' '))
            self.table.setItem(self.rows, 2, QTableWidgetItem(' '))

        if self.rows % 2 != 0:
            self.table.cellWidget(self.rows, 0).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table.cellWidget(self.rows, 1).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            le.setStyleSheet('background-color: #E6E6E6;')
            if ch_del:
                self.table.cellWidget(self.rows, 2).setStyleSheet(
                    'background-color: #E6E6E6;'
                    'color: #E6E6E6;'
                )
            else:
                self.table.item(self.rows, 2).setBackground(
                    QColor(230, 230, 230))
        else:
            if ch_del:
                self.table.cellWidget(self.rows, 2).setStyleSheet(
                    'color: #FFFFFF;'
                )

        self.table.setRowHeight(self.rows, 35)
        self.rows += 1

    # Clear
    def clear(self):
        """
        Clears all values in the fields and also in the table.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.rows = 0
        self.chbox_count = 0
        self.cb_director = []
        self.le = []
        self.chbox_del = []
        self.session.expire_all()
        self.cb_select.setCurrentIndex(0)
        self.cb_select.currentIndexChanged.connect(self.selected_movie)

    # Help
    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_edit_director_creator.html'
        self.main.views_help(url, texts.help_edit_cast)

    def closeEvent(self, event):
        self.session.close()
