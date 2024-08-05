import subprocess
import sys
import os
import re
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QColor, QPalette, QIcon, QPixmap
from PyQt6.QtCore import QSettings
import requests
import zipfile
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cookies_file = os.path.join(BASE_DIR, 'cookies.txt')
CURRENT_VERSION = "1.2"
ICON_URL = "https://cdn.discordapp.com/attachments/1110683992224694386/1270127179635884165/15zjnqt9i_link_yu-transformed.png?ex=66b2919d&is=66b1401d&hm=cf4d116a166fcd78be2d59f50c84a64dc8aa3ded329740a48299c36c7d938a3b&"

def load_icon_from_url(url, size=(32, 32)):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_data = response.content
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaled(size[0], size[1], QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        
        return QIcon(pixmap)
    except requests.RequestException as e:
        print(f"Ошибка при загрузке изображения: {e}")
        return QIcon()

def get_latest_release_info():
    url = "https://api.github.com/repos/TUUVCOME/YouTubeClient/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при получении информации о последнем релизе: {e}")
        return None

def download_and_extract_zip(url, extract_to='.'):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(extract_to)
    except requests.RequestException as e:
        print(f"Ошибка при загрузке и извлечении архива: {e}")
    except zipfile.BadZipFile:
        filename = os.path.join(extract_to, "YouTubeClient.exe")
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Файл сохранен как {filename}.")

def check_for_updates():
    release_info = get_latest_release_info()
    if release_info:
        latest_version = release_info['tag_name']
        if latest_version < CURRENT_VERSION:
            print("Что-то напутано с версиями! Скачиваю предыдущую.")
            asset = release_info['assets'][0]
            download_url = asset['browser_download_url']
            print("Загрузка обновления...")
            download_and_extract_zip(download_url, BASE_DIR)
            if latest_version != CURRENT_VERSION:
                print(f"Обнаружена новая версия: {latest_version}")
                asset = release_info['assets'][0]
                download_url = asset['browser_download_url']
                print("Загрузка обновления...")
                download_and_extract_zip(download_url, BASE_DIR)
                print("Обновление завершено. Перезапустите приложение.")
                return True
            print("У вас установлена последняя версия.")
    return False

def on_first_run(settings):
    print("Это первый запуск программы.")
    settings.setValue('firstRun', False)
    install_required_libraries()

def install_required_libraries():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "PyQtWebEngine", "requests"])
    except subprocess.CalledProcessError as e:
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
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 15))
        return palette
"""
def load_extensions(profile, extensions_dir):
    if os.path.exists(extensions_dir) and os.path.isdir(extensions_dir):
        for extension_name in os.listdir(extensions_dir):
            extension_path = os.path.join(extensions_dir, extension_name)
            if os.path.isdir(extension_path):
                manifest_path = os.path.join(extension_path, 'manifest.json')
                if os.path.isfile(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    print(f"Загружается расширение {manifest.get('name', extension_name)} из {extension_path}")

                    content_scripts = manifest.get('content_scripts', [])
                    for content_script in content_scripts:
                        matches = content_script.get('matches', [])
                        js_files = content_script.get('js', [])
                        for js_file in js_files:
                            js_path = os.path.join(extension_path, js_file)
                            if os.path.isfile(js_path):
                                with open(js_path, 'r', encoding='utf-8') as js_f:
                                    script_source = js_f.read()
                                for match in matches:
                                    view = QWebEngineView()
                                    view.setPage(QWebEnginePage(profile, view))
                                    view.load(QtCore.QUrl(match))
                else:
                    print(f"Не найден manifest.json в {extension_path}")
    else:
        print(f"Каталог с расширениями {extensions_dir} не найден.")
"""
class YouTubeClient(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.profile = QWebEngineProfile('custom_profile', self)
        self.cookie_store = self.profile.cookieStore()
        self.init_ui()
        #extensions_dir = os.path.join(BASE_DIR, 'extensions')
        #load_extensions(self.profile, extensions_dir)

    def init_ui(self):
        self.setWindowTitle('YouTube Client')
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowIcon(load_icon_from_url(ICON_URL, size=(64, 64)))

        self.central_widget = ColoredBackgroundWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.top_container = QtWidgets.QWidget()
        self.top_container.setFixedHeight(50)
        self.top_layout = QtWidgets.QHBoxLayout(self.top_container)
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText('https://www.youtube.com или введите поисковый запрос')
        self.url_input.setStyleSheet('border: 1px solid #444; border-radius: 10px; padding: 5px; color: #fff; background-color: #333;')
        self.top_layout.addWidget(self.url_input)

        self.layout.addWidget(self.top_container)

        self.browser = QWebEngineView(self)
        self.layout.addWidget(self.browser)

        self.browser.setUrl(QtCore.QUrl("https://www.youtube.com"))

        self.layout.setStretch(1, 1)
        self.browser.page().setBackgroundColor(QColor(15, 15, 15))

        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        self.browser.page().fullScreenRequested.connect(self.FullscreenRequest)

        self.url_input.returnPressed.connect(self.load_video_or_search)

    def FullscreenRequest(self, request):
        if request.toggleOn():
            self.showFullScreen()
            self.top_container.hide()
        else:
            self.showNormal()
            self.showMaximized()
            self.top_container.show()
        request.accept()

    def load_video_or_search(self):
        query = self.url_input.text().strip()
        if query:
            url = QtCore.QUrl(query) if re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$', query) else QtCore.QUrl(f"https://www.youtube.com/results?search_query={query}")
            self.browser.setUrl(url)

    def update_url_input(self, url):
        self.url_input.setText(url.toString())

    def load_cookies(self):
        def on_cookie_added(cookie):
            with open(cookies_file, 'a', encoding='utf-8') as f:
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

    if check_for_updates():
        print("Приложение было обновлено. Пожалуйста, перезапустите его.")
        sys.exit()

    window = YouTubeClient()
    window.showMaximized()
    try:
        sys.exit(app.exec())
    except (SystemExit, OSError, RuntimeError) as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == '__main__':
    main()
