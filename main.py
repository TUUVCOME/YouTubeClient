import sys
import os
import re
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QSettings, Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
extensions_dir = os.path.join(BASE_DIR, 'extensions')
cookies_file = os.path.join(BASE_DIR, 'cookies.txt')

def on_first_run(settings):
    print("Это первый запуск программы.")
    settings.setValue('firstRun', False)
    install_required_libraries()

def install_required_libraries():
    try:
        os.system("pip install PyQt5 PyQtWebEngine")
    except Exception as e:
        print(f"Ошибка при установке библиотек: {e}")

def check_first_run():
    settings = QSettings('YouTubeClient')
    if settings.value('firstRun', True, type=bool):
        on_first_run(settings)

class ColoredBackgroundWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setPalette(self.create_colored_palette())

    def create_colored_palette(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(15, 15, 15))
        return palette

class YouTubeClient(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.profile = QWebEngineProfile('custom_profile', self)
        self.cookie_store = self.profile.cookieStore()
        self.init_ui()
        self.load_cookies()

    def init_ui(self):
        self.setWindowTitle('YouTube Client')
        self.setGeometry(100, 100, 1280, 720)

        # Создаем виджеты
        self.central_widget = ColoredBackgroundWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        top_container = QtWidgets.QWidget()
        top_container.setFixedHeight(50)
        top_layout = QtWidgets.QHBoxLayout(top_container)
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText('https://www.youtube.com или введите поисковый запрос')
        self.url_input.setStyleSheet('border: 1px solid #444; border-radius: 5px; padding: 5px; color: #fff; background-color: #333;')
        top_layout.addWidget(self.url_input)

        self.show_button = QtWidgets.QPushButton('Открыть', self)
        self.show_button.setStyleSheet('background-color: #444; color: white; border-radius: 5px; padding: 8px;')
        top_layout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.load_video_or_search)

        self.layout.addWidget(top_container)

        self.browser = QWebEngineView(self)
        self.layout.addWidget(self.browser)
        self.browser.setUrl(QtCore.QUrl("https://www.youtube.com"))

        self.layout.setStretch(1, 1)
        self.browser.page().setBackgroundColor(QColor(15, 15, 15))

        self.browser.urlChanged.connect(self.update_url_input)
        self.url_input.returnPressed.connect(self.load_video_or_search)
        self.browser.page().fullScreenRequested.connect(self.on_full_screen_requested)

    def on_full_screen_requested(self, request):
        request.accept()
        if request.toggleOn():
            self.browser.showFullScreen()
        else:
            self.browser.showNormal()

    def load_video_or_search(self):
        query = self.url_input.text().strip()
        if not query:
            return
        if re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$', query):
            self.browser.setUrl(QtCore.QUrl(query))
        else:
            search_url = f"https://www.youtube.com/results?search_query={query}"
            self.browser.setUrl(QtCore.QUrl(search_url))

    def update_url_input(self, url):
        self.url_input.setText(url.toString())

    def load_cookies(self):
        def on_cookie_added(cookie):
            with open(cookies_file, 'a') as f:
                f.write(f"{cookie.toRawForm().data().decode()}\n")

        self.cookie_store.cookieAdded.connect(on_cookie_added)
        self.cookie_store.loadAllCookies()

    def save_cookies(self):
        pass

    def closeEvent(self, event):
        self.save_cookies()
        super().closeEvent(event)

def main():
    check_first_run()
    app = QtWidgets.QApplication(sys.argv)
    window = YouTubeClient()
    window.showMaximized()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    os.system(BASE_DIR + "x86_64/goodbyedpi.exe")
    main()
