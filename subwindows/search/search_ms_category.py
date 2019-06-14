from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont, QCursor
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

from sqlalchemy import or_

import texts

from db.db_model import Category, Movie, Series
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchMSCategory(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie or series by categories.

        :param main: Reference for main windows.
        :param type: String if is "movie" then search for movie if not search
        by "series".
        """
        super(SearchMSCategory, self).__init__()

        self.session = DB.get_session()
        self.type = type
        self.main = main
        self.row_select = -1

        if self.type == 'movie':
            self.obj = self.session.query(Movie).order_by(Movie.category_1_id)
            name = texts.movie_p
        else:
            self.obj = self.session.query(Series).order_by(Series.category_1_id)
            name = texts.series_p

        windows_title = texts.search + ' ' + name + ' ' + texts.for_ \
                        + ' ' + texts.category_p
        self.setWindowTitle(windows_title)
        self.width = int(0.9 * main.frameSize().width())
        self.height = int(0.9 * main.frameSize().height())
        self.setGeometry(0, 0, self.width, self.height)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        # Category
        self.lb_category = QLabel(texts.category_s)
        self.lb_category.setMaximumSize(QSize(100, 25))
        if self.type == 'movie':
            categories = self.session.query(Category). \
                filter(or_(Category.id == Movie.category_1_id,
                           Category.id == Movie.category_2_id)).\
                order_by(Category.name)
        else:
            categories = self.session.query(Category). \
                filter(or_(Category.id == Series.category_1_id,
                           Category.id == Series.category_2_id)).\
                order_by(Category.name)
        self.cb_category = cb_create()
        populate_combobox(self.cb_category, categories)

        # total
        self.lb_total = QLabel(texts.lb_total)
        self.lb_total.setMaximumSize(QSize(100, 25))
        self.le_total = le_create(255)

        # Buttons
        self.pb_clear = pb_create(texts.pb_clear, 11, 30)
        self.pb_clear.setShortcut('Ctrl+L')
        self.pb_clear.clicked.connect(self.clear)
        self.pb_leave = pb_create(texts.pb_leave, 11, 30)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Hbox
        self.hbox = hbox_create([
            self.lb_category, self.cb_category, self.lb_total, self.le_total,
            self.pb_clear, self.pb_leave
        ])
        self.hbox.addSpacerItem(spacer)
        self.vbox_main.addLayout(self.hbox)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName('table-search')
        self.rows = 0

        self.clear_table()
        self.set_table(self.obj)

        self.vbox_main.addWidget(self.table)

        self.cb_category.currentIndexChanged.connect(self.query_category)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character combobox in table cast if windows resize.

        :param event: Window.
        """
        self.width = event.size().width()
        col_width = self.width - 70

        self.table.setColumnWidth(0, 0.4 * col_width)
        self.table.setColumnWidth(1, 0.18 * col_width)
        self.table.setColumnWidth(2, 0.18 * col_width)
        self.table.setColumnWidth(3, 0.08 * col_width)
        self.table.setColumnWidth(4, 0.08 * col_width)
        self.table.setColumnWidth(5, 0.08 * col_width)
        self.table.setColumnWidth(6, 0)

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setColumnCount(7)
        self.table.setRowCount(0)

        self.rows = 0

        if self.type == 'movie':
            headers = [
                texts.title_s,
                texts.category_1,
                texts.category_2,
                texts.lb_time,
                texts.media_s,
                texts.year_s,
                'id'
            ]
        else:
            headers = [
                texts.title_s,
                texts.category_1,
                texts.category_2,
                texts.season_p,
                texts.media_s,
                texts.year_s,
                'id'
            ]

        self.table.setHorizontalHeaderLabels(headers)

        col_width = self.width - 70
        self.table.setColumnWidth(0, 0.4 * col_width)
        self.table.setColumnWidth(1, 0.18 * col_width)
        self.table.setColumnWidth(2, 0.18 * col_width)
        self.table.setColumnWidth(3, 0.08 * col_width)
        self.table.setColumnWidth(4, 0.08 * col_width)
        self.table.setColumnWidth(5, 0.08 * col_width)
        self.table.setColumnWidth(6, 0)

        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet('background-color: #FFFFFF;')
        self.table.setSortingEnabled(True)

    # View Movie
    def view_obj(self, row, col):
        """
        When clicked a cell table who has title show the html view of movie.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            obj_id = self.table.item(row, 6).text()
            if self.type == 'movie':
                obj = self.session.query(Movie).get(obj_id)
            else:
                obj = self.session.query(Series).get(obj_id)

            if obj.view:
                self.main.view_html(obj.view, obj.name)

            self.row_select = row

    # Set Table
    def set_table(self, objs):
        """
        Inserts all values in the table.
        """
        self.clear_table()
        for o in objs:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(o.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            if o.category_1_id:
                self.table.setItem(
                    self.rows, 1, QTableWidgetItem(o.category_1.name))
            else:
                self.table.setItem(
                    self.rows, 1, QTableWidgetItem(''))

            if o.category_2_id:
                self.table.setItem(
                    self.rows, 2, QTableWidgetItem(o.category_2.name))
            else:
                self.table.setItem(
                    self.rows, 2, QTableWidgetItem(''))

            if self.type == 'movie':
                self.table.setItem(self.rows, 3, QTableWidgetItem(o.time))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(o.seasons))

            if o.media_id:
                self.table.setItem(self.rows, 4, QTableWidgetItem(o.media.name))
            else:
                self.table.setItem(self.rows, 4, QTableWidgetItem(''))

            self.table.setItem(self.rows, 5, QTableWidgetItem(o.year))
            self.table.setItem(self.rows, 6, QTableWidgetItem(str(o.id)))

            for i in range(7):
                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellDoubleClicked.connect(self.view_obj)

            self.rows += 1

        self.le_total.setText(str(self.rows))

        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "alternate-background-color: #F0FAE4;; background-color: #FFFFFF;")

    # Query
    def query_category(self):
        """
        Search movie by selected title in QCombobox.
        """
        id, name = get_combobox_info(self.cb_category)
        if self.type == 'movie' and id != 0:
            query = self.session.query(Movie).\
                filter(or_(Movie.category_1_id == id, Movie.category_2_id == id)).\
                order_by(Movie.name).all()
        elif self.type == 'movie' and id == 0:
            query = self.session.query(Movie).\
                filter(Movie.category_1_id.is_(None),
                       Movie.category_2_id.is_(None)).\
                order_by(Movie.name).all()
        elif self.type == 'series' and id != 0:
            query = series = self.session.query(Series).\
            filter(or_(Series.category_1_id == id, Series.category_2_id == id)).\
            order_by(Series.name).all()
        else:
            query = self.session.query(Series). \
                filter(Series.category_1_id.is_(None),
                       Series.category_2_id.is_(None)). \
                order_by(Movie.name).all()
        self.set_table(query)

    # Clear
    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_category.currentIndexChanged.disconnect()
        self.cb_category.setCurrentIndex(0)
        self.clear_table()
        self.set_table(self.obj)
        self.cb_category.currentIndexChanged.connect(self.query_category)