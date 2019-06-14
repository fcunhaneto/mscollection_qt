import sys
import os

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame, \
    QDesktopWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTextBrowser, \
    QLabel, QRadioButton, QPushButton, QLineEdit, QSizePolicy, QSpacerItem, \
    QMessageBox

from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils import database_exists, create_database
import shutil
import install.texts_install as texts


class InstallDB(QMainWindow):
    def __init__(self):
        super(InstallDB, self).__init__()

        self.db = None
        self.url = None

        self.setGeometry(0, 0, 610, 400)
        self.setWindowTitle(texts.window_principal_title)
        screen = QDesktopWidget().screenGeometry()
        self.x = (screen.width() / 2) - (self.frameSize().width() / 2)
        self.y = (screen.height() / 2) - (self.frameSize().height() / 2)
        self.move(self.x, self.y)
        self.setStyleSheet("background-color: rgb(239, 235, 231);")

        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 610, 400)

        # Install Part 1
        self.widget_1 = QWidget(self.centralwidget)
        self.widget_1.setGeometry(0, 0, 610, 400)
        self.widget_1.setHidden(False)

        self.vbox_main_1 = QWidget(self.widget_1)
        self.vbox_main_1.setGeometry(0, 0, 610, 400)

        self.vbox_part_1 = QVBoxLayout(self.vbox_main_1)
        self.vbox_part_1.setContentsMargins(20, 20, 20, 20)
        self.vbox_part_1.setSpacing(10)

        self.tb_1 = QTextBrowser()
        self.tb_1.setText(texts.install_text_1)
        self.vbox_part_1.addWidget(self.tb_1)

        self.line_1 = QFrame(self.vbox_main_1)
        self.line_1.setFrameShape(QFrame.HLine)
        self.line_1.setFrameShadow(QFrame.Sunken)
        self.vbox_part_1.addWidget(self.line_1)

        self.hbox_rbs = QHBoxLayout()

        self.label = QLabel(texts.lb_label)
        self.hbox_rbs.addWidget(self.label)

        self.rb_sqlite = QRadioButton('SQLite')
        icon = QIcon()
        icon.addPixmap(QPixmap("images/sqlite.ico"),
                       QIcon.Normal, QIcon.Off)
        self.rb_sqlite.setIcon(icon)
        self.rb_sqlite.setIconSize(QSize(24, 24))
        self.rb_sqlite.setChecked(True)
        self.hbox_rbs.addWidget(self.rb_sqlite)

        self.rb_postgres = QRadioButton('PostgreSQL')
        icon1 = QIcon()
        icon1.addPixmap(QPixmap("images/postgresql-24x24.png"),
                        QIcon.Normal, QIcon.Off)
        self.rb_postgres.setIcon(icon1)
        self.rb_postgres.setIconSize(QSize(24, 24))
        self.hbox_rbs.addWidget(self.rb_postgres)

        self.rb_mysql = QRadioButton('MySQL')
        icon2 = QIcon()
        icon2.addPixmap(QPixmap("images/mysql-24x24.png"),
                        QIcon.Normal, QIcon.Off)
        self.rb_mysql.setIcon(icon2)
        self.rb_mysql.setIconSize(QSize(24, 24))
        self.hbox_rbs.addWidget(self.rb_mysql)
        self.vbox_part_1.addLayout(self.hbox_rbs)

        self.line_2 = QFrame(self.vbox_main_1)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.vbox_part_1.addWidget(self.line_2)

        self.hbox_pb_next = QHBoxLayout()
        self.hbox_pb_next.setContentsMargins(150, 10, 200, -1)

        self.hbox_pb_next = QHBoxLayout()
        self.hbox_pb_next.setContentsMargins(150, 10, 200, -1)

        self.pb_next = QPushButton()
        self.pb_next.clicked.connect(self.pb_next_clicked)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pb_next.sizePolicy().hasHeightForWidth())
        self.pb_next.setSizePolicy(sizePolicy)
        self.pb_next.setMaximumSize(QSize(400, 40))
        icon3 = QIcon()
        icon3.addPixmap(QPixmap("images/bt-next-24x24.png"),
                        QIcon.Normal, QIcon.Off)
        self.pb_next.setIcon(icon3)
        self.pb_next.setIconSize(QSize(400, 40))
        self.pb_next.setStyleSheet("background-color: rgb(211, 215, 207);\n"
                                   "alternate-background-color: "
                                   "qradialgradient(spread:repeat, cx:0.5, "
                                   "cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
                                   "stop:0 rgba(184,184,184, 255), "
                                   "stop:.5 rgba(211,211,211, 255), "
                                   "stop:1 rgba(255, 255, 255, 255));")
        self.hbox_pb_next.addWidget(self.pb_next)
        self.vbox_part_1.addLayout(self.hbox_pb_next)

        # Install Part 2
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setGeometry(0, 0, 621, 521)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setHidden(True)

        self.vbox_main_2 = QWidget(self.widget_2)
        self.vbox_main_2.setGeometry(0, 0, 621, 521)
        self.vbox_main_2.setObjectName("verticalLayoutWidget_2")
        self.vbox_part_2 = QVBoxLayout(self.vbox_main_2)
        self.vbox_part_2.setContentsMargins(20, 20, 20, 20)
        self.vbox_part_2.setSpacing(10)

        self.tb_2 = QTextBrowser()

        self.vbox_part_2.addWidget(self.tb_2)

        self.line_3 = QFrame(self.vbox_main_2)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.vbox_part_2.addWidget(self.line_3)

        self.fm_part_2 = QFormLayout()
        self.fm_part_2.setSpacing(10)

        self.lb_bd_name = QLabel(texts.lb_db_name)
        self.le_bd_name = QLineEdit('ms_collection')
        self.fm_part_2.setWidget(0, QFormLayout.LabelRole, self.lb_bd_name)
        self.fm_part_2.setWidget(0, QFormLayout.FieldRole, self.le_bd_name)

        self.lb_host = QLabel(texts.lb_host)
        self.le_host = QLineEdit('localhost')
        self.fm_part_2.setWidget(1, QFormLayout.LabelRole, self.lb_host)
        self.fm_part_2.setWidget(1, QFormLayout.FieldRole, self.le_host)

        self.lb_port = QLabel(texts.lb_port)
        self.le_port = QLineEdit()
        self.fm_part_2.setWidget(2, QFormLayout.FieldRole, self.le_port)
        self.fm_part_2.setWidget(2, QFormLayout.LabelRole, self.lb_port)

        self.lb_user = QLabel(texts.lb_user)
        self.le_user = QLineEdit('root')
        self.fm_part_2.setWidget(3, QFormLayout.LabelRole, self.lb_user)
        self.fm_part_2.setWidget(3, QFormLayout.FieldRole, self.le_user)

        self.lb_pw = QLabel(texts.lb_pw)
        self.le_pw = QLineEdit()
        self.fm_part_2.setWidget(4, QFormLayout.LabelRole, self.lb_pw)
        self.fm_part_2.setWidget(4, QFormLayout.FieldRole, self.le_pw)

        self.vbox_part_2.addLayout(self.fm_part_2)

        self.hbox_pb_send = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding,
                             QSizePolicy.Minimum)
        self.hbox_pb_send.addItem(spacer)

        self.pb_ok = QPushButton()
        self.pb_ok.clicked.connect(self.pb_ok_clicked)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap("images/bt-ok-24x24.png"),
                        QIcon.Normal, QIcon.Off)
        self.pb_ok.setIcon(icon3)
        self.pb_ok.setIconSize(QSize(250, 40))
        self.pb_ok.setStyleSheet(
            "background-color: rgb(211, 215, 207); "
            "alternate-background-color: "
            "qradialgradient(spread:repeat, cx:0.5, "
            "cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
            "stop:0 rgba(184,184,184, 255), "
            "stop:.5 rgba(211,211,211, 255), "
            "stop:1 rgba(255, 255, 255, 255));"
        )
        self.hbox_pb_send.addWidget(self.pb_ok)

        self.hbox_pb_send.addItem(spacer)

        self.line_3 = QFrame(self.vbox_main_2)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.vbox_part_2.addWidget(self.line_3)
        self.vbox_part_2.addLayout(self.hbox_pb_send)

    def pb_next_clicked(self):
        if self.rb_sqlite.isChecked():
            self.db = 'sqlite'
            self.url = 'sqlite:///db//mscollection.sqlite3'
            self.create_database()
            self.create_tables()
            self.close()
        elif self.rb_postgres.isChecked():
            self.db = 'postgres'
            text = texts.install_db_select('PostgreSQL')
            self.tb_2.setText(text)
            self.le_user.setText('postgres')
            self.le_port.setText('5432')
            self.change_window()
        elif self.rb_mysql.isChecked():
            self.db = 'mysql'
            text = texts.install_db_select('MySQL')
            self.tb_2.setText(text)
            self.le_port.setText('3306')
            self.change_window()

    def pb_ok_clicked(self):
        db_name = self.le_bd_name.text()
        db_host = self.le_host.text()
        db_port = (self.le_port.text())
        db_user = self.le_user.text()
        db_pw = self.le_pw.text()

        name = 'name = \'' + db_name + '\'\n'
        host = 'host = \'' + db_host + '\'\n'
        port = 'port = ' + db_port + '\n'
        user = 'user = \'' + db_user + '\'\n'
        pw = 'pw = \'' + db_pw + '\'\n'

        with open('db/db_values.py', 'w') as f:
            f.writelines([name, host, port, user, pw])

        int_port = int(db_port)

        if self.db == 'postgres':
            self.url = '{0}://{1}:{2}@{3}:{4}/{5}'.format(
                self.db, db_user,
                db_pw, db_host,
                int_port, db_name
            )
        else:
            self.url = '{0}+pymysql://{1}:{2}@{3}:{4}/{5}'. \
                format(self.db, db_user, db_pw, db_host, int_port, db_name)

        self.create_database()
        self.create_tables()

    def set_file_settings(self):
        abs_path = os.getcwd()
        print(abs_path)
        new_file = abs_path + '/db/db_settings.py'
        print(new_file)
        old_file = abs_path + '/install/' + self.db + '_settings.py'
        print(old_file)
        try:
            shutil.copyfile(old_file, new_file)
            self.close()
        except EnvironmentError as error:
            text = texts.cant_copy(self.db)
            self.show_msg('Erro', text, QMessageBox.Critical, QMessageBox.Close)

    def create_database(self):
        # utf8mb4 in MySQl and not utf8 see:
        # [https://www.eversql.com/mysql-utf8-vs-utf8mb4-whats-the-difference-between-utf8-and-utf8mb4/]
        # [https://medium.com/@adamhooper/in-mysql-never-use-utf8-use-utf8mb4-11761243e434]
        try:
            exist = database_exists(self.url)
            if not exist:
                if self.db == 'sqlite':
                    create_database(self.url)
                if self.db == 'postgres':
                    create_database(self.url)
                    self.set_file_settings()
                elif self.db == 'mysql':
                    create_database(self.url, 'utf8mb4')
                    self.set_file_settings()
            else:
                text = texts.database_exist
                self.show_msg(texts.windows_error_database, text,
                              QMessageBox.Critical, QMessageBox.Close)
        except ProgrammingError as error:
            text = texts.connection_rejected
            self.show_msg(texts.windows_error_database, text,
                          QMessageBox.Critical, QMessageBox.Close, str(error))

        self.set_file_settings()

    def create_tables(self):
        import install.install_tables as ins
        ins.create_tables(self.url)

    def change_window(self):
        self.widget_1.setHidden(False)
        self.setGeometry(self.x, self.y, 621, 520)
        self.centralwidget.setGeometry(0, 0, 621, 520)
        self.widget_2.setGeometry(0, 0, 621, 520)
        self.widget_2.setHidden(False)

    # Messages Box
    def show_msg(self, title, text, icon, button, detail='', info='', ):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(info)
        msg.setWindowTitle(title)
        msg.setDetailedText(detail)
        msg.setStandardButtons(button)
        msg.exec_()


def main():
    app = QApplication(sys.argv)
    main_window = InstallDB()
    main_window.show()
    sys.exit(app.exec_())