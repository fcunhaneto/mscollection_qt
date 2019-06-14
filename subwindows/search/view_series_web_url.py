import datetime

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, \
    QTableWidget, QTableWidgetItem, QLabel, QSpacerItem, QSizePolicy


import texts

from db.db_model import Series
from db.db_settings import Database as DB

from lib.function_lib import cb_create, populate_combobox, hbox_create, \
    pb_create, le_create, db_select_all, get_combobox_info


class ViewSeriesUrl(QMdiSubWindow):
    def __init__(self, main):
        """
        Search movie by title.

        :param main: Reference for main windows.
        """
        super(ViewSeriesUrl, self).__init__()

        self.session = DB.get_session()
        self.main = main
        self.row_select = -1

        text = texts.series_s + ' ' + texts.search_web_url
        self.setWindowTitle(text)
        self.width = int(0.8 * main.frameSize().width())
        self.height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, self.width, self.height)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)

        # Title
        self.lb_title = QLabel(texts.title_s)
        self.lb_title.setMaximumSize(QSize(100, 25))
        series = db_select_all(self.session, Series)
        self.cb_title = cb_create()
        populate_combobox(self.cb_title, series)

        # Words
        text = texts.or_s + ' ' + texts.with_the_p + ' ' + texts.term_p
        self.lb_term = QLabel(text)
        self.le_term = le_create(30, texts.with_term_tt)
        self.le_term.setPlaceholderText('pressione enter')
        self.le_term.editingFinished.connect(self.query_term)

        # HBoxSearch
        self.hbox_search = hbox_create([self.lb_title, self.cb_title,
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

        # Hbox_result
        self.hbox_result = hbox_create([self.lb_total, self.le_total,
                                        self.pb_clear, self.pb_leave])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox_result.addItem(spacer)

        self.vbox_main.addLayout(self.hbox_result)

        # Table
        self.table = QTableWidget()
        self.table.horizontalHeader().sectionClicked.connect(self.repaint_cells)
        self.rows = 0
        self.clear_table()
        query = self.session.query(Series).all()
        self.set_table(query)

        self.vbox_main.addWidget(self.table)

        self.cb_title.currentIndexChanged.connect(self.query_title)

    # Clear Table
    def clear_table(self):
        """
        Clear all tables values.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.rows = 0

        headers = [
            texts.title_s,
            texts.original_title_s,
            texts.url,
            texts.last_edit,
            'id'
        ]

        self.table.setHorizontalHeaderLabels(headers)

        col_width = self.width - 50
        self.table.setColumnWidth(0, 0.30 * col_width)
        self.table.setColumnWidth(1, 0.30 * col_width)
        self.table.setColumnWidth(2, 0.30 * col_width)
        self.table.setColumnWidth(3, 0.10 * col_width)
        self.table.setColumnWidth(4, 0)

        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet('background-color: #FFFFFF;')
        self.table.setSortingEnabled(True)

    # Repaint Cell
    def repaint_cells(self, event):
        """
        When the table is self-reclassified repaint it.
        """
        for r in range(self.rows):
            for i in range(5):
                if r % 2 == 0:
                    self.table.item(r, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(r, i).setBackground(
                        QColor(255, 230, 245))

    # View Series
    def view_obj(self, row, col):
        """
        When clicked a cell table who has title show the html view of series.

        :param row: The number of the row on which the cell was clicked.
        :param col: The number of the column on which the cell was clicked.
        """
        if self.row_select != row and col == 0:
            movie_id = self.table.item(row, 4).text()
            obj = self.session.query(Series).get(movie_id)

            self.main.view_html(obj.view_url, obj.name)

            self.row_select = row

    # Set Table
    def set_table(self, series):
        """
        Set table with all movies.

        :param query: The movies values.
        """
        self.clear_table()
        for s in series:
            self.table.insertRow(self.rows)

            self.table.setItem(self.rows, 0, QTableWidgetItem(s.name))
            font = QFont()
            font.setUnderline(True)
            self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
            self.table.item(self.rows, 0).setFont(font)

            if s.original_name:
                self.table.setItem(self.rows, 1,
                                   QTableWidgetItem(s.original_name))
            else:
                self.table.setItem(self.rows, 1, QTableWidgetItem(''))

            self.table.setItem(self.rows, 2, QTableWidgetItem(s.url))

            date = "{:%d/%m/%Y}".format(s.new_edit)
            self.table.setItem(self.rows, 3, QTableWidgetItem(date))

            self.table.setItem(self.rows, 4, QTableWidgetItem(str(s.id)))

            for i in range(5):
                if self.rows % 2 == 0:
                    self.table.item(self.rows, i).setBackground(
                        QColor(240, 250, 228))
                else:
                    self.table.item(self.rows, i).setBackground(
                        QColor(255, 230, 245))

                self.table.item(self.rows, i).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.table.cellClicked.connect(self.view_obj)

            self.rows += 1

        self.le_total.setText(str(self.rows))

    def set_query_title(self, series):
        """
        Set table with movies values search in database.

        :param series: The movies values from a database search.
        """
        self.clear_table()
        self.table.insertRow(self.rows)

        self.table.setItem(self.rows, 0, QTableWidgetItem(series.name))
        font = QFont()
        font.setUnderline(True)
        self.table.item(self.rows, 0).setForeground(QColor(55, 34, 243))
        self.table.item(self.rows, 0).setFont(font)

        if series.original_name:
            self.table.setItem(self.rows, 1,
                               QTableWidgetItem(series.original_name))
        else:
            self.table.setItem(self.rows, 1, QTableWidgetItem(''))

        self.table.setItem(self.rows, 2, QTableWidgetItem(series.url))
        date = "{:%d/%m/%Y}".format(series.new_edit)
        self.table.setItem(self.rows, 3, QTableWidgetItem(date))

        self.table.setItem(self.rows, 4, QTableWidgetItem(str(series.id)))

        for i in range(5):
            if self.rows % 2 == 0:
                self.table.item(self.rows, i).setBackground(
                    QColor(249, 250, 228))
            else:
                self.table.item(self.rows, i).setBackground(
                    QColor(226, 255, 228))
            self.table.item(self.rows, i).setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.table.cellClicked.connect(self.view_obj)

        self.rows += 1

        self.le_total.setText(str(self.rows))

    # Query
    def query_title(self):
        """
        Search series by selected title in QCombobox.
        """
        id, name = get_combobox_info(self.cb_title)
        series = self.session.query(Series).get(id)

        self.set_query_title(series)

    def query_term(self):
        """
        Search series by words in title.
        """
        words = self.le_term.text().split()
        queries = []
        for word in words:
            word = '%{0}%'.format(word)
            query = self.session.query(Series) \
                .filter(Series.name.ilike(word)).all()
            queries += query

        self.set_table(queries)

    def clear(self):
        """
        Clear all values in windows.
        """
        self.cb_title.currentIndexChanged.disconnect()
        self.cb_title.setCurrentIndex(0)
        self.clear_table()
        query = self.session.query(Series).all()
        self.set_table(query)
        self.cb_title.currentIndexChanged.connect(self.query_title)

    # Close Event
    def closeEvent(self, event):
        self.session.close()

