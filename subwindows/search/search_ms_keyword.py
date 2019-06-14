from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy

import texts

from db.db_model import Movie, Series, Keyword
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, le_create, db_select_all, get_combobox_info


class SearchMSKeyword(QMdiSubWindow):
    def __init__(self, main, type):
        """
        Search movie by title.

        :param main: Reference for main windows.
        """
        super(SearchMSKeyword, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.type = type
        self.row_select = -1

        if self.type == 'movie':
            self.obj = self.session.query(Movie).\
                filter(Movie.keyword_id.isnot(None),).\
                order_by(Movie.keyword_id)
            name = texts.movie_p
        else:
            self.obj = self.session.query(Series). \
                filter(Series.keyword_id.isnot(None)). \
                order_by(Series.keyword_id)
            name = texts.series_p

        windows_title = texts.search + ' ' + name + ' ' + \
                        texts.for_ + ' ' + texts.keyword

        self.setWindowTitle(windows_title)
        self.width = int(0.9 * main.frameSize().width())
        self.height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, self.width, self.height)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        # Keyword
        self.lb_keyword = QLabel(texts.keyword)
        self.lb_keyword.setMaximumSize(QSize(100, 25))

        if self.type == 'movie':
            keyword = self.session.query(Keyword).\
                filter(Keyword.id == Movie.keyword_id)
        else:
            keyword = self.session.query(Keyword). \
                filter(Keyword.id == Series.keyword_id)
        self.cb_keyword = cb_create()
        populate_combobox(self.cb_keyword, keyword)

        # Words
        text = texts.or_s + ' ' + texts.with_the_p + ' ' + texts.term_p
        self.lb_term = QLabel(text)
        self.le_term = le_create(30, texts.with_term_tt)
        self.le_term.setPlaceholderText('pressione enter')
        self.le_term.editingFinished.connect(self.query_term)

        # HBoxSearch
        self.hbox_search = hbox_create([self.lb_keyword, self.cb_keyword,
                                        self.lb_term, self.le_term])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox_search.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_search)

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
        self.rows = 0
        self.clear_table()

        self.set_table(self.obj)

        self.vbox_main.addWidget(self.table)

        self.cb_keyword.currentIndexChanged.connect(self.query_keyword)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character combobox in table cast if windows resize.

        :param event: Window.
        """
        self.width = event.size().width()
        col_width = self.width - 60

        self.table.setColumnWidth(0, 0.5 * col_width)
        self.table.setColumnWidth(1, 0.2 * col_width)
        self.table.setColumnWidth(2, 0.1 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.1 * col_width)
        self.table.setColumnWidth(5, 0)

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setColumnCount(6)
        self.table.setRowCount(0)
        self.rows = 0

        if self.type == 'movie':
            headers = [
                texts.title_s,
                texts.keyword,
                texts.lb_time,
                texts.media_s,
                texts.year_s,
                'id'
            ]

        else:
            headers = [
                texts.title_s,
                texts.keyword,
                texts.season_p,
                texts.media_s,
                texts.year_s,
                'id'
            ]

        col_width = self.width - 60
        self.table.setColumnWidth(0, 0.5 * col_width)
        self.table.setColumnWidth(1, 0.2 * col_width)
        self.table.setColumnWidth(2, 0.1 * col_width)
        self.table.setColumnWidth(3, 0.1 * col_width)
        self.table.setColumnWidth(4, 0.1 * col_width)
        self.table.setColumnWidth(5, 0)

        self.table.setHorizontalHeaderLabels(headers)

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

            if o.keyword_id:
                self.table.setItem(self.rows, 1, QTableWidgetItem(o.keyword.name))
            else:
                self.table.setItem(self.rows, 1, QTableWidgetItem(''))

            if self.type == 'movie':
                self.table.setItem(self.rows, 2, QTableWidgetItem(o.time))
            else:
                self.table.setItem(self.rows, 2, QTableWidgetItem(o.seasons))

            if o.media_id:
                self.table.setItem(self.rows, 3, QTableWidgetItem(o.media.name))
            else:
                self.table.setItem(self.rows, 3, QTableWidgetItem(''))

            self.table.setItem(self.rows, 4, QTableWidgetItem(o.year))
            self.table.setItem(self.rows, 5, QTableWidgetItem(str(o.id)))

            for i in range(6):
                if self.table.item(self.rows, i):
                    self.table.item(self.rows, i).setFlags(
                        Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellDoubleClicked.connect(self.view_obj)

            self.rows += 1

        self.table.setAlternatingRowColors(True);
        self.table.setStyleSheet(
            "alternate-background-color: #F0FAE4;; background-color: #FFFFFF;")

        self.le_total.setText(str(self.rows))

    # Query
    def query_keyword(self):
        """
        Search movie by selected title in QCombobox.
        """
        id, name = get_combobox_info(self.cb_keyword)
        if self.type == 'movie' and id != 0:
            query = self.session.query(Movie).\
                filter(Movie.keyword_id == id).order_by(Movie.name).all()
        elif self.type == 'movie' and id == 0:
            query = self.session.query(Movie).\
                filter(Movie.keyword_id.is_(None)).order_by(Movie.name).all()
        elif self.type == 'series' and id != 0:
            query = self.session.query(Series).\
                filter(Series.keyword_id == id).order_by(Series.name).all()
        else:
            query = self.session.query(Series). \
                filter(Series.keyword_id.is_(None)).order_by(Series.name).all()

        self.set_table(query)

    def query_term(self):
        """
        Search movie by words in title.
        """
        words = self.le_term.text().split()
        lib = []
        for word in words:
            word = '%{0}%'.format(word)
            keyword = self.session.query(Keyword).\
                filter(Keyword.name.ilike(word)).all()
            lib += keyword

        lid = []
        queries = []
        for b in lib:
            lid.append(b.id)
            if self.type == 'movie':
                query = self.session.query(Movie). \
                    filter(Movie.keyword_id.in_(lid)).all()
            else:
                query = self.session.query(Series). \
                    filter(Series.keyword_id.in_(lid)).all()

            queries += query

        self.set_table(queries)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_keyword.currentIndexChanged.disconnect()
        self.cb_keyword.setCurrentIndex(0)
        self.clear_table()
        self.set_table(self.obj)
        self.cb_keyword.currentIndexChanged.connect(self.query_keyword)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
