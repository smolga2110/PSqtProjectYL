import sys
import platform
from PySide2 import QtGui, QtWidgets
from PyQt5 import QtCore
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence,
                           QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
import os
import youtube_dl

from ui_splash_screen import Ui_SplashScreen

from ui_main import Ui_MainWindow

counter = 0


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    class downloader(QtCore.QThread):
        mysignal = QtCore.pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.url = None

        def run(self):
            self.mysignal.emit('Процесс скачивания запущен!')

            with youtube_dl.YoutubeDL({}) as ydl:
                ydl.download([self.url])

            self.mysignal.emit('Процесс скачивания завершен!')
            self.mysignal.emit('finish')

        def init_args(self, url):
            self.url = url

    class gui(QtWidgets.QMainWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            self.download_folder = None
            self.ui.pushButton.clicked.connect(self.get_folder)
            self.ui.pushButton_2.clicked.connect(self.start)
            self.mythread = downloader()
            self.mythread.mysignal.connect(self.handler)

        def start(self):
            if len(self.ui.lineEdit.text()) > 5:
                if self.download_folder != None:
                    link = self.ui.lineEdit.text()
                    self.mythread.init_args(link)
                    self.mythread.start()
                    self.locker(True)
                else:
                    QtWidgets.QMessageBox.warning(self, "Ошибка", "Вы не выбрали папку!")
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Ссылка на видео не указана!")

        def get_folder(self):
            self.download_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выбрать папку для сохранения')
            os.chdir(self.download_folder)

        def handler(self, value):
            if value == 'finish':
                self.locker(False)

            else:
                self.ui.plainTextEdit.appendPlainText(value)

        def locker(self, lock_value):
            base = [self.ui.pushButton, self.ui.pushButton_2]

            for item in base:
                item.setDisabled(lock_value)


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)


        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)


        self.ui.label_description.setText("<strong>ДОБРО</strong> ПОЖАЛОВАТЬ")

        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>ЗАГРУЗКА</strong> БАЗЫ ДАННЫХ"))
        QtCore.QTimer.singleShot(3000,
                                 lambda: self.ui.label_description.setText("<strong>ЗАГРУЗКА</strong> ИНТЕРФЕЙСА"))

        self.show()

    def progress(self):
        global counter

        self.ui.progressBar.setValue(counter)

        if counter > 100:
            self.timer.stop()

            self.main = MainWindow()
            self.main.show()

            self.close()

        counter += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SplashScreen()
    sys.exit(app.exec_())
