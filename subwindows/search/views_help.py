from PyQt5.QtCore import QRect, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMdiSubWindow, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView


class ViewsHelp(QMdiSubWindow):
    def __init__(self, main, url, title):
        """
        Show html view help by given view url.

        :param main: Reference for main windows.
        :param url: The view url.
        :param title: The windows title.
        """
        super(ViewsHelp, self).__init__()

        geo = main.frameGeometry()
        width = int(0.6 * geo.width())
        height = int(0.8 * geo.height())
        self.setWindowTitle(title)
        self.setGeometry(QRect(0, 0, width, height))

        self.subwindow = QWidget()
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(p)
        self.setWidget(self.subwindow)

        self.web_view = QWebEngineView(self.subwindow)
        self.web_view.setGeometry(QRect(0, 0, width, height))
        self.web_view.load(QUrl(url))
        self.web_view.show()
