import os
import datetime

from threading import Thread

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QFormLayout, QVBoxLayout, \
    QGridLayout, QPushButton, QTextEdit, QLabel, QCheckBox,  QMessageBox, \
    QSpacerItem, QTableWidget, QSizePolicy

from sqlalchemy.exc import IntegrityError, DBAPIError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

import texts

from db.db_model import Director, Box, Keyword, Movie, MovieDirector, MovieCast
from db.db_model import Media, Actor, Character, Category, Cast
from db.db_settings import Database as DB

from lib.function_lib import le_create, cb_create, populate_combobox, \
    hbox_create, pb_create, get_combobox_info, show_msg, db_insert_obj, \
    db_select_all, line_h_create, db_get_id, db_get_obj
from lib.imdb_scraping import ImdbScraping
from lib.adoro_cinema_scraping_movie import AdoroCinemaMovieScraping
from lib.write_movie_html import write_movie_html


class InsertMovie(QMdiSubWindow):

    def __init__(self, main):
        """
        Class to provide all methods to insert movie in database.

        :param main: Reference for main windows.
        """
        super(InsertMovie, self).__init__()

        self.session = DB.get_session()
        self.movie = None
        self.cb_categories = []
        self.main = main

        windows_title = texts.insert + ' ' + texts.movie_p
        self.setWindowTitle(windows_title)
        width = int(0.95 * main.frameSize().width())
        height = int(0.8 * main.frameSize().height())
        self.setGeometry(0, 0, width, height)
        self.tb_width = (0.5 * width) - 50

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.vbox_main = QVBoxLayout(self.subwindow)

        # Search in IMDB
        self.pb_search_confirm_imdb = pb_create(
            texts.pb_imdb_search_confirm, height=25, width=200)
        self.pb_search_confirm_imdb.setToolTip(texts.imdb_search_tt)
        self.pb_search_confirm_imdb.setShortcut('CTRL+Alt+I')
        self.pb_search_confirm_imdb.clicked.connect(self.search_confirmed_imdb)

        self.pb_search_confirm_ad = pb_create(
            texts.pb_ad_search_confirm, height=25, width=300)
        self.pb_search_confirm_ad.setToolTip(texts.ad_search_tt)
        self.pb_search_confirm_ad.setShortcut('CTRL+Alt+D')
        self.pb_search_confirm_ad.clicked.connect(self.search_confirmed_ad)

        self.lb_imdb_url = QLabel(texts.lb_search_imdb)
        self.lb_imdb_url.setEnabled(False)
        self.lb_imdb_url.setHidden(True)
        self.le_imdb_url = le_create(tooltip=texts.imdb_search_tt)
        self.le_imdb_url.setEnabled(False)
        self.le_imdb_url.setHidden(True)

        self.lb_ad_url = QLabel(texts.lb_search_ad)
        self.lb_ad_url.setEnabled(False)
        self.lb_ad_url.setHidden(True)
        self.le_ad_url = le_create(tooltip=texts.ad_search_tt)

        self.le_ad_url.setEnabled(False)
        self.le_ad_url.setHidden(True)

        self.pb_search_imdb = pb_create(
            texts.pb_imdb_ad_search, height=25, width=200)
        self.pb_search_imdb.clicked.\
            connect(lambda type: self.set_movie_scrapping('imdb'))
        self.pb_search_imdb.setShortcut('CTRL+Shift+I')
        self.pb_search_imdb.setEnabled(False)
        self.pb_search_imdb.setHidden(True)

        self.pb_search_ad = pb_create(
            texts.pb_imdb_ad_search, height=25, width=200)
        self.pb_search_ad.clicked.connect(lambda type: self.set_movie_scrapping('ad'))
        self.pb_search_ad.setShortcut('CTRL+Shift+A')
        self.pb_search_ad.setEnabled(False)
        self.pb_search_ad.setHidden(True)

        self.hbox_search = hbox_create([
            self.pb_search_confirm_imdb, self.lb_imdb_url, self.le_imdb_url,
            self.pb_search_confirm_ad, self.lb_ad_url, self.le_ad_url
        ])
        self.hbox_search.setContentsMargins(20, 10, 20, 0)

        self.hbox_pb_search = hbox_create([])
        self.hbox_pb_search.setContentsMargins(20, 0, 20, 0)

        self.line = line_h_create('2px', '#000000')

        self.vbox_main.addLayout(self.hbox_search)
        self.vbox_main.addLayout(self.hbox_pb_search)
        self.vbox_main.addWidget(self.line)

        # Form Layout 1
        self.fm_1 = QFormLayout()
        self.fm_1.setContentsMargins(20, 20, 20, 20)
        self.fm_1.setSpacing(10)

        # Title
        self.lb_title = QLabel(texts.title_s)
        self.le_title = le_create(255)
        self.fm_1.setWidget(0, QFormLayout.LabelRole, self.lb_title)
        self.fm_1.setWidget(0, QFormLayout.FieldRole, self.le_title)

        # Year
        self.lb_year = QLabel(texts.year_s)
        self.le_year = le_create(4)
        self.fm_1.setWidget(1, QFormLayout.LabelRole, self.lb_year)
        self.fm_1.setWidget(1, QFormLayout.FieldRole, self.le_year)

        # Media
        self.lb_media = QLabel(texts.media_s)
        media = db_select_all(self.session, Media)
        self.cb_media = cb_create()
        populate_combobox(self.cb_media, media)
        self.fm_1.setWidget(2, QFormLayout.LabelRole, self.lb_media)
        self.fm_1.setWidget(2, QFormLayout.FieldRole, self.cb_media)

        # Category 1
        category = db_select_all(self.session, Category)
        self.lb_category_1 = QLabel(texts.category_1)
        self.cb_category_1 = cb_create()
        populate_combobox(self.cb_category_1, category)
        self.fm_1.setWidget(3, QFormLayout.LabelRole, self.lb_category_1)
        self.fm_1.setWidget(3, QFormLayout.FieldRole, self.cb_category_1)

        # Box
        box = db_select_all(self.session, Box)
        self.lb_box = QLabel(texts.box)
        self.cb_box = cb_create()
        populate_combobox(self.cb_box, box)
        self.fm_1.setWidget(4, QFormLayout.LabelRole, self.lb_box)
        self.fm_1.setWidget(4, QFormLayout.FieldRole, self.cb_box)

        # Poster
        self.lb_poster = QLabel(texts.poster)
        self.le_poster = le_create(255)
        self.fm_1.setWidget(5, QFormLayout.LabelRole, self.lb_poster)
        self.fm_1.setWidget(5, QFormLayout.FieldRole, self.le_poster)

        # Form Layout 2
        self.fm_2 = QFormLayout()
        self.fm_2.setContentsMargins(20, 20, 20, 20)
        self.fm_2.setSpacing(10)

        # Original Title
        self.lb_original_title = QLabel(texts.original_title_s)
        self.le_original_title = le_create(255)
        self.fm_2.setWidget(0, QFormLayout.LabelRole, self.lb_original_title)
        self.fm_2.setWidget(0, QFormLayout.FieldRole, self.le_original_title)

        # Director
        director = db_select_all(self.session, Director)
        self.lb_director = QLabel(texts.director_s)
        self.cb_director = cb_create()
        populate_combobox(self.cb_director, director)
        self.fm_2.setWidget(1, QFormLayout.LabelRole, self.lb_director)
        self.fm_2.setWidget(1, QFormLayout.FieldRole, self.cb_director)

        self.lb_time = QLabel(texts.lb_time)
        self.le_time = le_create(10, texts.time_tt)
        self.fm_2.setWidget(2, QFormLayout.LabelRole, self.lb_time)
        self.fm_2.setWidget(2, QFormLayout.FieldRole, self.le_time)

        # Category 2
        category = db_select_all(self.session, Category)
        self.lb_category_2 = QLabel(texts.category_1)
        self.cb_category_2 = cb_create()
        populate_combobox(self.cb_category_2, category)
        self.fm_2.setWidget(3, QFormLayout.LabelRole, self.lb_category_2)
        self.fm_2.setWidget(3, QFormLayout.FieldRole, self.cb_category_2)

        # KeyWord
        keyword = db_select_all(self.session, Keyword)
        self.lb_keyword = QLabel(texts.keyword)
        self.cb_keyword = cb_create()
        populate_combobox(self.cb_keyword, keyword)
        self.fm_2.setWidget(4, QFormLayout.LabelRole, self.lb_keyword)
        self.fm_2.setWidget(4, QFormLayout.FieldRole, self.cb_keyword)

        # Web URL
        self.lb_web_url = QLabel(texts.lb_url)
        self.le_web_url = le_create(255)
        self.fm_2.setWidget(5, QFormLayout.LabelRole, self.lb_web_url)
        self.fm_2.setWidget(5, QFormLayout.FieldRole, self.le_web_url)

        # Horizontal Layout for Frame layout
        self.hbox_fms = hbox_create([])
        self.hbox_fms.addLayout(self.fm_1)
        self.hbox_fms.addLayout(self.fm_2)

        self.vbox_main.addLayout(self.hbox_fms)

        # Cast Summary
        self.hbox_summary_cast = hbox_create([])
        self.hbox_summary_cast.setContentsMargins(20, 0, 20, 0)
        self.vbox_summary = QVBoxLayout()

        # Summary
        self.lb_summary = QLabel(texts.summary_s)
        self.le_summary = QTextEdit()
        self.vbox_summary.addWidget(self.lb_summary)
        self.vbox_summary.addWidget(self.le_summary)
        self.vbox_summary.setSpacing(20)
        self.hbox_summary_cast.addLayout(self.vbox_summary)
        self.hbox_summary_cast.setSpacing(20)

        # Cast Label Button
        self.vbox_cast = QVBoxLayout()

        self.lb_cast = QLabel(texts.cast_s)
        self.pb_add_row = QPushButton('+')
        self.pb_add_row.setToolTip(texts.pb_add_row_tt)
        self.pb_add_row.clicked.connect(self.table_add_rows)
        self.pb_add_row.setShortcut('Ctrl+T')

        self.hbox_cast = hbox_create([self.lb_cast, self.pb_add_row])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_cast.addItem(spacer)

        self.vbox_cast.addLayout(self.hbox_cast)

        # Cast Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)

        self.headers = [
            texts.actor_s,
            texts.character_s,
            texts.order,
            texts.star.capitalize(),
        ]
        self.table.setHorizontalHeaderLabels(self.headers)

        self.table.setColumnWidth(0, 0.30 * self.tb_width)
        self.table.setColumnWidth(1, 0.40 * self.tb_width)
        self.table.setColumnWidth(2, 0.15 * self.tb_width)
        self.table.setColumnWidth(3, 0.15 * self.tb_width)

        self.rows = 0
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []
        self.table_add_rows()

        self.vbox_cast.addWidget(self.table)
        self.hbox_summary_cast.addLayout(self.vbox_cast)

        self.vbox_main.addLayout(self.hbox_summary_cast)

        # Buttons Save Clear
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)

        self.pb_save = pb_create(texts.pb_save, height=40)
        self.pb_save.clicked.connect(self.insert_movie)
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
        self.pb_leave.setShortcut('Ctrl+Q')
        self.grid_layout.addWidget(self.pb_leave, 0, 3, 1, 1)

        self.vbox_main.addLayout(self.grid_layout)

        # Tab Order
        self.le_title.setFocus()
        self.setTabOrder(self.le_title, self.le_original_title)
        self.setTabOrder(self.le_original_title, self.le_year)
        self.setTabOrder(self.le_year, self.cb_director)
        self.setTabOrder(self.cb_media, self.le_time)
        self.setTabOrder(self.le_time, self.cb_category_1)
        self.setTabOrder(self.cb_category_1, self.cb_category_2)
        self.setTabOrder(self.cb_category_2, self.cb_box)
        self.setTabOrder(self.cb_box, self.cb_keyword)
        self.setTabOrder(self.cb_keyword, self.le_poster)
        self.setTabOrder(self.le_poster, self.le_web_url)
        self.setTabOrder(self.le_web_url, self.le_summary)

    # Resize Event
    def resizeEvent(self, event):
        """
        Resize actors and character combobox in table cast if windows resize.

        :param event: Window.
        """
        width = event.size().width()
        self.tb_width = (0.5 * width) - 50
        self.table.setColumnWidth(0, 0.30 * self.tb_width)
        self.table.setColumnWidth(1, 0.40 * self.tb_width)
        self.table.setColumnWidth(2, 0.15 * self.tb_width)
        self.table.setColumnWidth(3, 0.15 * self.tb_width)

        for i in range(self.rows):
            self.cb_actor[i].setMaximumWidth(0.3 * self.tb_width)
            self.cb_character[i].setMaximumWidth(0.4 * self.tb_width)
            self.le_order[i].setMaximumWidth(0.15 * self.tb_width)
            self.chbox_star[i].setMaximumWidth(0.15 * self.tb_width)

        # Important don't delete it
        QMdiSubWindow.resizeEvent(self, event)

    # Insert Movie
    def insert_movie(self):
        """
        Insert movie in database.

        :return: The errors in dictionary containing the errors.
        """
        self.movie = Movie()

        if not self.le_title.text() or not self.le_year:
            show_msg(
                texts.insert_error, texts.no_title,
                QMessageBox.Warning,
                QMessageBox.Close
            )
        else:
            self.movie.name = self.le_title.text()
            self.movie.original_name = self.le_original_title.text()
            self.movie.year = self.le_year.text()
            self.movie.time = self.le_time.text()

            if self.le_imdb_url.isEnabled():
                self.movie.search_url = self.le_imdb_url.text()
            elif self.le_ad_url.isEnabled():
                self.movie.search_url = self.le_ad_url.text()

            if self.le_poster.text():
                self.movie.poster = self.le_poster.text()
            else:
                self.movie.poster = '../images/poster_placeholder.png'

            self.movie.web_url = self.le_web_url.text()
            self.movie.summary = self.le_summary.toPlainText()

            id, name = get_combobox_info(self.cb_media)
            if id:
                self.movie.media_id = id

            self.movie.box_id = db_get_id(self.session, self.cb_box, Box())

            self.movie.keyword_id = db_get_id(
                self.session, self.cb_keyword, Keyword())

            self.movie.category_1_id = db_get_id(
                self.session, self.cb_category_1, Category())

            self.movie.category_2_id = db_get_id(
                self.session, self.cb_category_2, Category())

            id, name = get_combobox_info(self.cb_director)
            director = db_get_obj(self.session, id, name, Director)
            if director:
                movie_director = MovieDirector(order=1, director=director)
                self.movie.directors.append(movie_director)

            i = 0
            old_order = 0
            for cb in self.cb_actor:
                actor_id = db_get_id(self.session, cb, Actor())

                character_id = db_get_id(
                    self.session, self.cb_character[i], Character()
                )

                if actor_id and character_id:
                    cast = Cast(actor_id=actor_id, character_id=character_id)
                    try:
                        self.session.add(cast)
                        self.session.commit()
                    # If except most probably is because cast exist so we try to get it
                    except IntegrityError:
                        self.session.rollback()
                        self.session.commit()
                        cast = self.session.query(Cast).filter(
                            Cast.actor_id == actor_id,
                            Cast.character_id == character_id).first()
                    except DBAPIError as error:
                        self.session.rollback()
                        self.session.commit()
                        _, actor = get_combobox_info(cb)
                        _, character = get_combobox_info(self.cb_character[i])
                        text = texts.cast_error + actor + ' ' + character + '.'
                        show_msg(
                            texts.db_error, text, QMessageBox.Critical,
                            QMessageBox.Close, str(error)
                        )
                        continue

                    if cast:
                        order = int(self.le_order[i].text())
                        if order == old_order:
                            order += 1
                            old_order = order
                        else:
                            old_order = order

                        movie_cast = MovieCast(
                            order=order,
                            star=self.chbox_star[i].isChecked(),
                            cast=cast
                        )
                        self.movie.movie_cast.append(movie_cast)

                i += 1

            hour_now = datetime.datetime.utcnow()
            self.movie.date_create = hour_now
            self.movie.date_edit = hour_now

            try:
                self.session.add(self.movie)
                self.session.commit()
                text = texts.msg_insert_ok(self.movie.name)
                show_msg(texts.insert_ok, text, QMessageBox.Information,
                         QMessageBox.Close)
            except IntegrityError as error:
                self.session.rollback()
                self.session.commit()
                show_msg(
                    texts.insert_error, texts.movie_exist,
                    QMessageBox.Critical, QMessageBox.Close, str(error)
                )
            except (DBAPIError, SQLAlchemyError) as error:
                self.session.rollback()
                self.session.commit()
                text = texts.msg_insert_erro(self.movie.name)
                show_msg(
                    texts.insert_error, text, QMessageBox.Critical,
                    QMessageBox.Close, str(error)
                )
            else:
                try:
                    self.movie.view = write_movie_html(self.session, self.movie)
                    self.session.add(self.movie)
                    self.session.commit()
                except SQLAlchemyError as error:
                    self.session.rollback()
                    self.session.commit()
                    show_msg(
                        texts.insert_error, texts.html_write,
                        QMessageBox.Critical, QMessageBox.Close, str(error)
                    )

    # Table Add Rows
    def table_add_rows(self):
        """
        Add rows in table cast.
        """
        cb = cb_create()
        cb.setMaximumWidth(0.3 * self.tb_width)
        actor = self.session.query(Actor).order_by(Actor.name).all()
        populate_combobox(cb, actor)
        self.cb_actor.append(cb)

        cb = cb_create()
        cb.setMaximumWidth(0.4 * self.tb_width)
        character = self.session.query(Character). \
            order_by(Character.name).all()
        populate_combobox(cb, character)
        self.cb_character.append(cb)

        le = le_create(5)
        le.setStyleSheet('padding: 10px;')
        self.le_order.append(le)
        self.le_order[self.rows].setText(str(self.rows+1))

        ch = QCheckBox(str(self.rows))
        icon = QIcon()
        icon.addPixmap(
            QPixmap('images/star_withe_16.png'), QIcon.Normal, QIcon.Off
        )
        ch.setIcon(icon)
        ch.setToolTip(texts.rb_star_tt)
        self.chbox_star.append(ch)
        i = self.rows
        self.chbox_star[i].stateChanged. \
            connect(lambda: self.chbox_star_changed(self.chbox_star[i]))

        i = self.rows
        hb = hbox_create([self.chbox_star[i]], 0)
        hb.setAlignment(Qt.AlignCenter)
        cell = QWidget()
        cell.setLayout(hb)

        self.table.insertRow(self.rows)
        self.table.setCellWidget(self.rows, 0, self.cb_actor[self.rows])
        self.table.setCellWidget(self.rows, 1, self.cb_character[self.rows])
        self.table.setCellWidget(self.rows, 2, self.le_order[self.rows])
        self.table.setCellWidget(self.rows, 3, cell)

        if self.rows % 2 != 0:
            self.table.cellWidget(self.rows, 0).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table.cellWidget(self.rows, 1).setStyleSheet(
                'background-color: #E6E6E6;'
            )
            self.table.cellWidget(self.rows, 2).setStyleSheet(
                'background-color: #E6E6E6; padding-left:10px;'
            )
            self.table.cellWidget(self.rows, 3).setStyleSheet(
                'background-color: #E6E6E6;'
                'color: #E6E6E6;'
            )
        else:
            self.table.cellWidget(self.rows, 3).setStyleSheet(
                'color: #FFFFFF;'
            )

        self.table.setRowHeight(self.rows, 35)

        self.rows += 1

    # Star Changed
    def chbox_star_changed(self, ch):
        """
        Change the icon on QCheckBox_stars on checkbox change.

        :param ch: QCheckBox from table who is in a list according rows.
        """
        ch_id = int(ch.text())

        icon = QIcon()
        if self.chbox_star[ch_id].isChecked():
            icon.addPixmap(
                QPixmap('images/star_yellow_16.png'), QIcon.Normal,
                QIcon.Off
            )
        else:
            icon.addPixmap(
                QPixmap('images/star_withe_16.png'), QIcon.Normal, QIcon.Off
            )

        self.chbox_star[ch_id].setIcon(icon)

    # Clear Table
    def clear_table(self):
        """
        Clear a table after saving movie in database or clear button is
        clicked.
        """
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(self.headers)
        self.rows = 0
        self.cb_actor = []
        self.cb_character = []
        self.le_order = []
        self.chbox_star = []

        self.table_add_rows()

    # Refresh Combobox
    def refresh_combobox(self):
        """
        Re-populate combobox after saving movie in database or clear button is
        clicked.
        """
        populate_combobox(self.cb_media, db_select_all(self.session, Media))
        populate_combobox(self.cb_box, db_select_all(self.session, Box))
        populate_combobox(self.cb_keyword, db_select_all(self.session, Keyword))
        category = db_select_all(self.session, Category)
        populate_combobox(self.cb_category_1, category)
        populate_combobox(self.cb_category_2, category)
        populate_combobox(self.cb_director, db_select_all(self.session, Director))
        self.clear_table()

    # Clear All
    def clear(self):
        """
        Clear all input values after saving movie in database or clear button is
        clicked.
        """
        self.le_imdb_url.setText('')
        self.le_ad_url.setText('')
        self.le_title.setText('')
        self.le_original_title.setText('')
        self.le_year.setText('')
        self.le_time.setText('')
        self.le_poster.setText('')
        self.le_web_url.setText('')
        self.le_summary.setText('')
        self.refresh_combobox()

        self.hbox_pb_search.removeWidget(self.pb_search_imdb)
        self.hbox_pb_search.removeWidget(self.pb_search_ad)
        self.pb_search_confirm_imdb.setEnabled(True)
        self.pb_search_confirm_imdb.setHidden(False)
        self.pb_search_confirm_ad.setEnabled(True)
        self.pb_search_confirm_ad.setHidden(False)
        self.lb_imdb_url.setEnabled(False)
        self.lb_imdb_url.setHidden(True)
        self.lb_ad_url.setEnabled(False)
        self.lb_ad_url.setHidden(True)
        self.le_imdb_url.setEnabled(False)
        self.le_imdb_url.setHidden(True)
        self.le_ad_url.setEnabled(False)
        self.le_ad_url.setHidden(True)
        self.pb_search_imdb.setEnabled(False)
        self.pb_search_imdb.setHidden(True)
        self.pb_search_ad.setEnabled(False)
        self.pb_search_ad.setHidden(True)

    # Search Confirmed IMDB
    def search_confirmed_imdb(self):
        """
        Start layout for search in IMDB after button pb_search_confirm is
        clicked
        """
        self.hbox_pb_search.removeWidget(self.pb_search_ad)
        self.hbox_pb_search.addWidget(self.pb_search_imdb)
        self.pb_search_confirm_imdb.setEnabled(False)
        self.pb_search_confirm_imdb.setHidden(True)
        self.pb_search_confirm_ad.setEnabled(False)
        self.pb_search_confirm_ad.setHidden(True)
        self.lb_imdb_url.setEnabled(True)
        self.lb_imdb_url.setHidden(False)
        self.lb_ad_url.setEnabled(False)
        self.lb_ad_url.setHidden(True)
        self.le_imdb_url.setEnabled(True)
        self.le_imdb_url.setHidden(False)
        self.le_imdb_url.returnPressed. \
            connect(lambda type='imdb': self.set_movie_scrapping(type))
        self.le_ad_url.setEnabled(False)
        self.le_ad_url.setHidden(True)
        self.pb_search_imdb.setEnabled(True)
        self.pb_search_imdb.setHidden(False)
        self.pb_search_ad.setEnabled(False)
        self.pb_search_ad.setHidden(True)

        self.pb_search_imdb.setFocusPolicy(Qt.NoFocus)
        self.le_imdb_url.setFocus()

    # Search Confirmed Adoro Cinema
    def search_confirmed_ad(self):
        """
        Start layout for search in IMDB after button pb_search_confirm is
        clicked.
        """
        self.hbox_pb_search.removeWidget(self.pb_search_imdb)
        self.hbox_pb_search.addWidget(self.pb_search_ad)
        self.pb_search_confirm_imdb.setEnabled(False)
        self.pb_search_confirm_imdb.setHidden(True)
        self.pb_search_confirm_ad.setEnabled(False)
        self.pb_search_confirm_ad.setHidden(True)
        self.lb_imdb_url.setEnabled(False)
        self.lb_imdb_url.setHidden(True)
        self.lb_ad_url.setEnabled(True)
        self.lb_ad_url.setHidden(False)
        self.le_imdb_url.setEnabled(False)
        self.le_imdb_url.setHidden(True)
        self.le_ad_url.setEnabled(True)
        self.le_ad_url.setHidden(False)
        self.le_ad_url.returnPressed. \
            connect(lambda type='ad': self.set_movie_scrapping(type))
        self.pb_search_imdb.setEnabled(False)
        self.pb_search_imdb.setHidden(True)
        self.pb_search_ad.setEnabled(True)
        self.pb_search_ad.setHidden(False)

        self.pb_search_ad.setFocusPolicy(Qt.NoFocus)
        self.le_ad_url.setFocus()

    # Scrapping
    def set_movie_scrapping(self, type):
        """
        Scrapping movie values in "IMDB" site or "Adoro Cinema" site according give
        type.
        :param type: If value is "imdb" scrapping from "IMDB" else if value is
        "ad" scrapping from "Adoro Cinema".
        """
        result = None

        if type == 'imdb':
            imdb_search = ImdbScraping(self.le_imdb_url.text(), 'movie')
            result = imdb_search.get_values()
        elif type == 'ad':
            ad_search = AdoroCinemaMovieScraping(self.le_ad_url.text())
            result = ad_search.get_values()

        if result['title']:
            self.le_title.setText(result['title'])

        if result['original_title']:
            self.le_original_title.setText(result['original_title'])

        if result['year']:
            self.le_year.setText(result['year'])

        if result['time']:
            self.le_time.setText(result['time'])

        if result['poster']:
            self.le_poster.setText(result['poster'])

        if result['summary']:
            self.le_summary.setText(result['summary'])

        if result['director']:
            self.set_combobox_value(self.cb_director, Director,
                                    result['director'])

        if result['category_1']:
            self.set_combobox_value(
                self.cb_category_1, Category, result['category_1'])

        if result['category_2']:
            self.set_combobox_value(
                self.cb_category_2, Category, result['category_2'])

        if result['cast']:
            self.set_cast_values(result['cast'])

    # Set Combobox
    def set_combobox_value(self, cb, obj, name):
        """
        Put the value corresponding to the movie found in the QComboBox.

        :param cb: The QComboBox who need set value.
        :param obj: The object that name needs to be set in the QComboBox.
        :param id: The id to find object in database.
        """
        try:
            result = self.session.query(obj).filter(obj.name == name).one()
            index = cb.findText(result.name, Qt.MatchFixedString)
            cb.setCurrentIndex(index)
        except NoResultFound:
            cb.setCurrentIndex(0)
            cb.setCurrentText(name)

    # Imdb Set Cast
    def set_cast_values(self, cast):
        """
        Look in a combobox in rows of table Cast for an existing value to appear
        in the combobox's first line.

        :param cast: Class Cast from file db/db_model.py who represent table
        cast in database.
        """
        total = len(cast) - 1
        i = 0
        for actor, character in cast:
            self.set_combobox_value(self.cb_actor[i], Actor, actor)
            self.set_combobox_value(self.cb_character[i], Character,
                                    character)
            self.table.setCellWidget(self.rows, 0, self.cb_actor[i])
            self.table.setCellWidget(self.rows, 1, self.cb_character[i])

            # Need the "if" for don't create empty row
            if i == total:
                break

            self.table_add_rows()
            i += 1

    # Help
    def help(self):
        """
        Call for help.
        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_insert_movie_series.html'

        self.main.views_help(url, texts.help_insert_movie)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
