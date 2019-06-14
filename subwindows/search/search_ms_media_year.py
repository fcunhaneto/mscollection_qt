from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

from sqlalchemy import desc

import texts

from db.db_model import Movie, Series, Media
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchMSMediaYear(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie by title.

        :param main: Reference for main windows.
        """
        super(SearchMSMediaYear, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.type = type
        self.row_select = -1

        if self.type == 'movie':
            self.obj = self.session.query(Movie).order_by(desc(Movie.year)).all()
            name = texts.movie_p
        else:
            self.obj = self.session.query(Series).order_by(desc(Series.year)).all()
            name = texts.series_p

        windows_title = texts.search + ' ' + name + ' ' + \
                        texts.for_ + ' ' + texts.media_s + '/' + texts.year_s

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

        # Media
        self.lb_media = QLabel(texts.media_s)
        self.lb_media.setMaximumSize(QSize(100, 25))
        if self.type == 'movie':
            media = self.session.query(Media).\
                filter(Media.id == Movie.media_id)
        else:
            media = self.session.query(Media). \
                filter(Media.id == Series.media_id)
        self.cb_media = cb_create()
        self.cb_media.setMaximumWidth(300)
        populate_combobox(self.cb_media, media)

        # Year
        self.lb_year = QLabel(texts.year_s)
        self.cb_year = QComboBox()
        self.cb_year.addItem('', 0)
        self.cb_year.setMinimumWidth(100)

        if self.type == 'movie':
            years = self.session.query(Movie.year).distinct().\
                order_by(desc(Movie.year)).all()
            years = [y[0] for y in years]
        else:
            years = self.session.query(Series.year).distinct().order_by(
                desc(Series.year)).all()
            years = [y[0] for y in years]

        self.cb_year.addItems(years)

        self.hbox_my = hbox_create([
            self.lb_media, self.cb_media, self.lb_year, self.cb_year])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox_my.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_my)

        # total
        self.lb_total = QLabel(texts.lb_total)
        self.le_total = le_create(255)
        self.le_total.setMaximumWidth(100)

        # Buttons
        self.pb_clear = pb_create(texts.pb_clear, 11, 30)
        self.pb_clear.setMaximumWidth(100)
        self.pb_clear.setShortcut('Ctrl+L')
        self.pb_clear.clicked.connect(self.clear)
        self.pb_leave = pb_create(texts.pb_leave, 11, 30)
        self.pb_leave.setMaximumWidth(100)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.clicked.connect(self.close)

        # Hbox result
        self.hbox_result = hbox_create([
            self.lb_total, self.le_total, self.pb_clear, self.pb_leave])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox_result.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_result)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName('table-search')
        if self.type == 'movie':
            self.num_col = 6
        else:
            self.num_col = 5
        self.rows = 0
        self.clear_table()

        self.set_table(self.obj)

        self.vbox_main.addWidget(self.table)

        self.cb_media.currentIndexChanged.connect(self.query_media)
        self.cb_year.currentIndexChanged.connect(self.query_year)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character combobox in table cast if windows resize.

        :param event: Window.
        """
        self.width = event.size().width()
        col_width = self.width - 50

        self.table.setColumnWidth(0, 0.3 * col_width)
        self.table.setColumnWidth(1, 0.3 * col_width)
        self.table.setColumnWidth(2, 0.15 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.15 * col_width)
        self.table.setColumnWidth(5, 0)

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(6)
        self.rows = 0
        col_width = self.width - 50
        if self.type == 'movie':
            headers = [
                texts.title_s,
                texts.original_title_s,
                texts.lb_time,
                texts.media_s,
                texts.year_s,
                'id'
            ]


        else:
            headers = [
                texts.title_s,
                texts.original_title_s,
                texts.season_p,
                texts.media_s,
                texts.year_s,
                'id'
            ]

        self.table.setHorizontalHeaderLabels(headers)

        self.table.setColumnWidth(0, 0.35 * col_width)
        self.table.setColumnWidth(1, 0.35 * col_width)
        self.table.setColumnWidth(2, 0.1 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.1 * col_width)
        self.table.setColumnWidth(5, 0)

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
            obj_id = self.table.item(row, 5).text()
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
        Set table with all movies.

        :param query: The movies values.
        """
        self.clear_table()
        for o in objs:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(o.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)
            self.table.setItem(self.rows, 1, QTableWidgetItem(o.original_name))

            if self.type == 'movie':
                self.table.setItem(self.rows, 2, QTableWidgetItem(o.time))
            else:
                self.table.setItem(self.rows, 2, QTableWidgetItem(o.seasons))

            if o.media_id:
                self.table.setItem(self.rows, 3,
                                   QTableWidgetItem(o.media.name))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(''))

            self.table.setItem(self.rows, 4, QTableWidgetItem(o.year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(o.id)))

            for i in range(6):
                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellDoubleClicked.connect(self.view_obj)

            self.rows += 1

        self.table.setAlternatingRowColors(True);
        self.table.setStyleSheet(
            "alternate-background-color: #F0FAE4;; background-color: #FFFFFF;")

        self.le_total.setText(str(self.rows))

    # Query Media
    def query_media(self):
        """
        Search movie by selected title in QCombobox.
        """
        id, name = get_combobox_info(self.cb_media)
        if self.type == 'movie' and id != 0:
            query = self.session.query(Movie). \
                filter(Movie.media_id == id).order_by(Movie.name).all()
        elif self.type == 'movie' and id == 0:
            query = self.session.query(Movie). \
                filter(Movie.media_id.is_(None)).order_by(Movie.name).all()
        elif self.type == 'series' and id != 0:
            query = self.session.query(Series). \
                filter(Series.media_id == id).order_by(Series.media_id).all()
        else:
            query = self.session.query(Series). \
                filter(Series.media_id.is_(None)).order_by(Series.media_id).all()

        self.set_table(query)

    # Query Year
    def query_year(self):
        """
        Search movie by selected title in QCombobox.
        """
        id, name = get_combobox_info(self.cb_year)
        if self.type == 'movie':
            query = self.session.query(Movie). \
                filter(Movie.year == name).order_by(Movie.year).all()
        else:
            query = self.session.query(Series). \
                filter(Series.year == name).order_by(Series.year).all()

        self.set_table(query)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_media.currentIndexChanged.disconnect()
        self.cb_year.currentIndexChanged.disconnect()
        self.cb_media.setCurrentIndex(0)
        self.cb_year.setCurrentIndex(0)
        self.clear_table()
        self.set_table(self.obj)
        self.cb_media.currentIndexChanged.connect(self.query_media)
        self.cb_year.currentIndexChanged.connect(self.query_year)

    # Close Event
    def closeEvent(self, event):
        self.session.close()