import subprocess
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from . import BlinkerSignals
from . import VISITED_LINKS_FILE
from . import seo_urwid
from .mainwidget import Ui_Form


class StartThread(QThread):
    """Запуск просмотра страниц в отдельном потоке"""

    send_error = pyqtSignal(str)

    def __init__(self):
        super(StartThread, self).__init__()
        self.running = False

    def run(self):
        try:
            seo_urwid.start_links_click_qt()
        except Exception as e:
            self.send_error.emit(str(e))
        finally:
            seo_urwid.write_visited_links(mode='a')


class SearchWebPage(QThread):
    """Поток поиска ссылки на сайт в поисковой системе"""

    thread_error = pyqtSignal(str)
    done = pyqtSignal()
    addon_dlg_signal = pyqtSignal()

    def __init__(self, parent: QObject = None):
        super(SearchWebPage, self).__init__(parent)
        self.proxy = None
        self.user_dir = True
        self.incognito = False
        self.parent().enable_addons_signal.connect(self.find_website_link)

    def run(self) -> None:
        try:
            seo_urwid.browser_init(self.proxy, user_dir=self.user_dir, incognito=self.incognito)
            self.addon_dlg_signal.emit()
        except Exception as e:
            self.thread_error.emit(str(e))

    @pyqtSlot()
    def find_website_link(self):
        try:
            seo_urwid.find_website_link()
            self.done.emit()
        except Exception as e:
            self.thread_error.emit(str(e))


class MainWidget(QWidget):
    enable_addons_signal = pyqtSignal()

    def __init__(self, proxy, user_dir, incognito, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        seo_urwid.data_for_request['search_engine'] = seo_urwid.YANDEX
        self.ui.notepad.setText('Чтобы проскроллить текущую страницу в поле XPATH введи "//body"\n')
        self.page_scrolling_thread = StartThread()
        self.search_web_page_thread = SearchWebPage(self)
        self.proxy = proxy
        self.user_dir = user_dir
        self.incognito = incognito
        self.connect_signals()

    def connect_signals(self):
        """Подключение сигналов"""
        self.ui.view_saved_links_btn.clicked.connect(lambda: self.view_saved_links(VISITED_LINKS_FILE))
        self.ui.close_chrome_btn.clicked.connect(self.close_chrome)
        self.ui.search_site_btn.clicked.connect(self.search_site_btn_clicked)
        self.ui.search_elems_btn.clicked.connect(self.search_links_on_active_page)
        self.ui.yandex_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.YANDEX))
        self.ui.google_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.GOOGLE))
        self.ui.mailr_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.MAILRU))
        BlinkerSignals.progress.connect(self.increase_progress_bar)
        BlinkerSignals.pages_counter.connect(self.increase_pages_counter)
        BlinkerSignals.num_links.connect(self.set_max_pages_counter)
        BlinkerSignals.max_scrolling.connect(self.set_max_scrolling)
        self.page_scrolling_thread.send_error.connect(self.print_error)
        self.search_web_page_thread.thread_error.connect(self.print_error)
        self.search_web_page_thread.done.connect(self.page_link_found)
        self.search_web_page_thread.addon_dlg_signal.connect(self.enable_addons_dialog)

    @pyqtSlot(str)
    def print_error(self, err):
        self.ui.log_text_browser.setText(err)

    def set_max_scrolling(self, _, value):
        """Устанавливает максимальное значение для прогрессбара скроллинга страницы"""
        self.ui.scrolling_prog_bar.setMaximum(value)

    def increase_progress_bar(self, _, value):
        """Увеличение прогрессбара прокрутки страницы"""
        self.ui.scrolling_prog_bar.setValue(value)

    def increase_pages_counter(self, _, value):
        """Увеличение прогрессбара просмотренных страниц"""
        self.ui.num_pages_prog_bar.setValue(value)

    def set_max_pages_counter(self, _, value):
        """Установка максимального значения прогрессбара просмотренных страниц"""
        self.ui.num_pages_prog_bar.setMaximum(value)

    @pyqtSlot()
    def rbt_status_changed(self, search_engine: str):
        """Установка поисковой системы"""
        seo_urwid.data_for_request['search_engine'] = search_engine

    @pyqtSlot()
    def search_links_on_active_page(self):
        """Поиск ссылок на активной странице

        Устанавливает последнюю открытую вкладку браузера активной
        и начинает поиск необходимых элементов"""
        self.ui.log_text_browser.clear()
        seo_urwid.data_for_request['timer'] = self.ui.timer_sb.value()
        seo_urwid.selectors_for_links['num_links_to_click'] = self.ui.number_elems_sb.value()
        seo_urwid.selectors_for_links['css_elems'] = self.ui.css_le.text()
        seo_urwid.selectors_for_links['xpath_elems'] = self.ui.xpaath_le.text()
        self.page_scrolling_thread.start()

    def search_page_link(self):
        """Поиск веб сайта в поисковаой системе"""
        seo_urwid.browser_init(self.proxy, self.user_dir, incognito=self.incognito)
        return seo_urwid.find_website_link()

    @pyqtSlot()
    def page_link_found(self):
        """Обработка сигнала когда найдена ссылка на сайт в поисковой системе"""
        QMessageBox.information(self, 'Ссылка найдена',
                                'Ссылка на сайт найдена',
                                buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)
        try:
            seo_urwid.continue_browsing()
        except Exception as e:
            self.ui.log_text_browser.setText(str(e))

    @pyqtSlot()
    def search_site_btn_clicked(self):
        """Нажата кнопка поиска сайта в поисковаой системе"""
        self.ui.log_text_browser.clear()
        seo_urwid.data_for_request['geo_location'] = self.ui.geolocation_le.text()
        seo_urwid.data_for_request['phrase'] = self.ui.phrase_le.text()
        seo_urwid.data_for_request['website_url'] = self.ui.url_site_le.text()
        self.search_web_page_thread.proxy = self.proxy
        self.search_web_page_thread.user_dir = self.user_dir
        self.search_web_page_thread.incognito = self.incognito
        self.search_web_page_thread.start()

    @pyqtSlot()
    def close_chrome(self):
        """Закрытие веб-движка

        Также очищает историю браузера"""
        seo_urwid.close_chrome()

    def view_saved_links(self, file=None):
        subprocess.Popen(['gvim', file])

    def closeEvent(self, event):
        """Перед закрытием будет очищать историю браузера и удалять объект браузера"""
        seo_urwid.close_chrome()
        super(MainWidget, self).closeEvent(event)

    @pyqtSlot()
    def enable_addons_dialog(self):
        QMessageBox.information(self, 'Включить addons',
                                'Перед продолжением включить addons в браузере или задать '
                                'город в геолокации',
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
        self.enable_addons_signal.emit()


def main(proxy, user_dir, incognito):
    app = QApplication(sys.argv)
    win = MainWidget(proxy=proxy, user_dir=user_dir, incognito=incognito)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    pass
