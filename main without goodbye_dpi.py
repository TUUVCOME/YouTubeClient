import sys
import re
import os
from PyQt5 import QtCore, QtWidgets, QtNetwork
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import QSettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
        self.init_ui()
        self.profile = QWebEngineProfile.defaultProfile()
        self.cookie_store = self.profile.cookieStore()
        self.load_cookies()

    def init_ui(self):
        self.setWindowTitle('YouTube Client')
        self.setGeometry(100, 100, 1280, 720)

        self.central_widget = ColoredBackgroundWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        top_container = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top_container)
        
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText('https://www.youtube.com или введите поисковый запрос')
        self.url_input.setStyleSheet('border: 1px solid #444; border-radius: 5px; padding: 5px; color: #fff; background-color: #333;')
        top_layout.addWidget(self.url_input)
        
        self.show_button = QtWidgets.QPushButton('Show', self)
        self.show_button.setStyleSheet('background-color: #444; color: white; border-radius: 5px; padding: 8px;')
        top_layout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.load_video_or_search)
        
        self.layout.addWidget(top_container)
        
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)
        
        self.layout.setStretch(1, 1)
        self.browser.page().setBackgroundColor(QColor(15, 15, 15))

        self.browser.urlChanged.connect(self.update_url_input)
        self.url_input.returnPressed.connect(self.load_video_or_search)

    def load_cookies(self):
        if os.path.exists(cookies_file):
            with open(cookies_file, 'r') as f:
                cookies = f.read().splitlines()
                for cookie in cookies:
                    if cookie:
                        try:
                            cookie = QtNetwork.QNetworkCookie.fromRawForm(cookie.encode())
                            self.cookie_store.setCookie(cookie)
                        except Exception as e:
                            print(f"Error loading cookie: {e}")

    def save_cookies(self):
        def on_cookies_loaded(cookies):
            with open(cookies_file, 'w') as f:
                f.writelines(f"{cookie.toRawForm().decode()}\n" for cookie in cookies)
        
        def fetch_cookies():
            try:
                all_cookies = self.cookie_store.allCookies()
                all_cookies_finished = QtCore.QEventLoop()
                self.cookie_store.allCookiesFinished.connect(all_cookies_finished.quit)
                all_cookies_finished.exec_()
                on_cookies_loaded(all_cookies)
            except Exception as e:
                print(f"Error saving cookies: {e}")
        
        fetch_cookies()

    def load_video_or_search(self):
        query = self.url_input.text().strip()
        if not query:
            return
        try:
            if re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$', query):
                self.browser.setUrl(QtCore.QUrl(query))
            else:
                search_url = f"https://www.youtube.com/results?search_query={query}"
                self.browser.setUrl(QtCore.QUrl(search_url))
        except Exception as e:
            print(f"Unexpected error: {e}")

    def update_url_input(self, url):
        self.url_input.setText(url.toString())

    def closeEvent(self, event):
        try:
            self.save_cookies()
            super().closeEvent(event)
        except Exception as e:
            print(f"Unexpected error: {e}")

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
    main()