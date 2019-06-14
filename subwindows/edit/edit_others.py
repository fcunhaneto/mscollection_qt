import os

from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, \
    QHBoxLayout, QLabel, QMessageBox, QSpacerItem, QSizePolicy

import texts

from db.db_model import Keyword, Media, Actor, Character, Category, Box
from db.db_settings import Database as DB

from lib.function_lib import cb_create, le_create, pb_create, db_insert_obj, \
    populate_combobox, get_combobox_info, show_msg, db_select_all, hbox_create


class EditOthers(QMdiSubWindow):
    def __init__(self, main, op):
        """
        Class for edit category, actor, character, box, media and keyword
        according given op.

        :param main: Reference for main windows.
        :param op: String representing the class to be edited.
        """
        super(EditOthers, self).__init__()

        self.main = main
        self.op = op
        self.session = DB.get_session()
        self.cls = None
        self.obj = None

        self.name = ''
        if self.op == 'category':
            self.cls = Category
            self.name = texts.category_s
        elif self.op == 'actor':
            self.cls = Actor
            self.name = texts.actor_s
        elif self.op == 'character':
            self.cls = Character
            self.name = texts.character_s
        elif self.op == 'box':
            self.cls = Box
            self.name = texts.box
        elif self.op == 'media':
            self.cls = Media
            self.name = texts.media_s
        elif self.op == 'keyword':
            self.cls = Keyword
            self.name = texts.keyword

        self.window_title = texts.edit + ' ' + self.name
        self.setWindowTitle(self.window_title)
        self.setGeometry(0, 0, 511, 205)

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        font = QFont()
        font.setPointSize(11)

        # Vbox Main
        self.vbox_main = QVBoxLayout(self.subwindow)
        self.vbox_main.setContentsMargins(20, 20, 20, 20)
        self.vbox_main.setSpacing(10)

        # Select Label and Combobox
        objs = db_select_all(self.session, self.cls)
        text = texts.select + ' ' + self.name
        self.lb_select = QLabel(text)
        self.lb_select.setFont(font)
        self.lb_select.setFixedHeight(25)
        self.cb_select = cb_create('')
        self.cb_select.setFont(font)
        self.cb_select.setFixedHeight(30)
        populate_combobox(self.cb_select, objs)
        self.cb_select.setEditable(False)
        self.vbox_main.addWidget(self.lb_select)
        self.vbox_main.addWidget(self.cb_select)

        # PB Select
        self.pb_select = pb_create(texts.pb_leave)
        self.pb_select.setFixedHeight(40)
        self.pb_select.setEnabled(True)
        self.pb_select.setHidden(False)
        self.pb_select.clicked.connect(self.close)

        self.pb_help_1 = pb_create(texts.pb_help)
        self.pb_help_1.setFixedHeight(40)
        self.pb_help_1.setEnabled(True)
        self.pb_help_1.setHidden(False)
        self.pb_help_1.clicked.connect(self.help)
        self.pb_help_1.setShortcut('Ctrl+H')

        self.hbox_select = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_select.addItem(spacer)
        self.hbox_select.addWidget(self.pb_select)
        self.hbox_select.addWidget(self.pb_help_1)
        self.hbox_select.addItem(spacer)
        self.vbox_main.addLayout(self.hbox_select)

        # Title
        text = texts.actual_value + ' ' + self.name
        self.lb = QLabel(text)
        self.lb.setFont(font)
        self.lb.setFixedHeight(25)
        self.le = le_create()
        self.le.setFont(font)
        self.lb.setEnabled(False)
        self.lb.setHidden(True)
        self.le.setEnabled(False)
        self.le.setHidden(True)
        self.vbox_main.addWidget(self.lb)
        self.vbox_main.addWidget(self.le)

        # Buttons
        self.pb_save = pb_create(texts.pb_save)
        self.pb_save.setShortcut('Ctrl+S')
        self.pb_save.clicked.connect(self.edit_object)
        self.pb_save.setMaximumHeight(40)

        self.pb_help_2 = pb_create(texts.pb_help)
        self.pb_help_2.clicked.connect(self.help)
        self.pb_help_2.setShortcut('Ctrl+H')
        self.pb_help_2.setMaximumHeight(40)

        self.pb_leave = pb_create(texts.pb_leave)
        self.pb_leave.clicked.connect(self.close)
        self.pb_leave.setShortcut('Ctrl+Q')
        self.pb_leave.setMaximumHeight(40)

        self.hb_pb = hbox_create([self.pb_save, self.pb_help_2, self.pb_leave])

        self.pb_save.setEnabled(False)
        self.pb_save.setHidden(True)
        self.pb_help_2.setEnabled(False)
        self.pb_help_2.setHidden(True)
        self.pb_leave.setEnabled(False)
        self.pb_leave.setHidden(True)

        self.vbox_main.addLayout(self.hb_pb)

        self.cb_select.currentIndexChanged.connect(self.obj_selected)

    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_edit_box_others.html'
        self.main.views_help(url, texts.help_insert_series)

    # OBJ Select
    def obj_selected(self):
        """
        When object is selected in combobox get it in database and start new
        windows to edit it.
        """
        id, name = get_combobox_info(self.cb_select)

        self.obj = self.session.query(self.cls).get(id)

        if self.obj and id != 0:
            self.lb_select.setEnabled(False)
            self.lb_select.setHidden(True)
            self.cb_select.setEnabled(False)
            self.cb_select.setHidden(True)
            self.pb_select.setEnabled(False)
            self.pb_select.setHidden(True)
            self.pb_help_1.setEnabled(False)
            self.pb_help_1.setHidden(True)
            self.hbox_select.setEnabled(False)

            self.vbox_main.setContentsMargins(20, 0, 20, 20)
            self.setGeometry(0, 0, 511, 205)

            self.lb.setEnabled(True)
            self.lb.setHidden(False)
            self.le.setEnabled(True)
            self.le.setHidden(False)
            self.pb_save.setEnabled(True)
            self.pb_save.setHidden(False)
            self.pb_help_2.setEnabled(True)
            self.pb_help_2.setHidden(False)
            self.pb_leave.setEnabled(True)
            self.pb_leave.setHidden(False)
            self.le.setText(self.obj.name)

            self.le.returnPressed.connect(self.edit_object)
            self.cb_select.currentIndexChanged.disconnect()

    def edit_object(self):
        """
        Save object in database.
        """
        self.obj.name = self.le.text()
        result = db_insert_obj(self.session, self.obj)

        if result:
            text = texts.msg_edit_ok(self.obj.name)
            show_msg(
                texts.edit_ok,
                text,
                QMessageBox.Information,
                QMessageBox.Close
            )
        else:
            text = texts.msg_edit_erro(self.obj.name)
            show_msg(
                texts.edit_error,
                text,
                QMessageBox.Critical,
                QMessageBox.Close
            )

        self.le.setText('')
        objs = db_select_all(self.session, self.cls)
        populate_combobox(self.cb_select, objs)

        self.lb.setEnabled(False)
        self.lb.setHidden(True)
        self.le.setEnabled(False)
        self.le.setHidden(True)
        self.pb_save.setEnabled(False)
        self.pb_save.setHidden(True)
        self.pb_help_2.setEnabled(False)
        self.pb_help_2.setHidden(True)
        self.pb_leave.setEnabled(False)
        self.pb_leave.setHidden(True)

        self.vbox_main.setContentsMargins(20, 0, 20, 40)
        self.setGeometry(0, 0, 511, 205)

        self.lb_select.setEnabled(True)
        self.lb_select.setHidden(False)
        self.cb_select.setEnabled(True)
        self.cb_select.setHidden(False)
        self.pb_select.setEnabled(True)
        self.pb_select.setHidden(False)
        self.pb_help_1.setEnabled(True)
        self.pb_help_1.setHidden(False)
        self.hbox_select.setEnabled(True)

        self.le.setText('')

        self.le.returnPressed.disconnect()
        self.cb_select.currentIndexChanged.connect(self.obj_selected)

    def help(self):
        """
        Call for help.

        :return: Show a help view.
        """
        # I have to perform help preview functions on the main because the bug
        # "stack_trace posix.cc (699)" does not let the page find its directory.
        dir = os.getcwd()
        url = 'file:///' + dir + '/views_help/help_edit_box_others.html'
        self.main.views_help(url, texts.help_insert_series)

    # Close Event
    def closeEvent(self, event):
        self.session.close()
