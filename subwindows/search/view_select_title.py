from os import getcwd
from PyQt5.QtCore import QRect, QUrl
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView


class ViewSelectTitle(QMdiSubWindow):
    def __init__(self, main, view, title):
        """
        Show html view movie or series by given view url.
        :param view: The view url.
        :param title: The windows title.
        """
        super(ViewSelectTitle, self).__init__()

        self.setWindowTitle(title)
        self.setGeometry(QRect(0, 0, 950, 620))
        path = getcwd()

        view = 'file://' + path + view

        self.webView = QWebEngineView()
        self.setWidget(self.webView)
        self.webView.setUrl(QUrl(view))
        self.webView.show()
