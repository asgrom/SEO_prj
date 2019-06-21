import subprocess
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

from .mainwidget import Ui_Form
from . import seo_urwid
from . import BlinkerSignals
from . import VISITED_LINKS_FILE


class StartThread(QThread):
    """Запуск просмотра страниц в отдельном потоке"""

    def __init__(self, signal):
        self.signal = signal
        super(StartThread, self).__init__()

    def run(self):
        try:
            seo_urwid.start_links_click_qt()
        except Exception as e:
            self.signal.emit(str(e))
        finally:
            seo_urwid.write_visited_links(mode='a')


class MainWidget(QWidget):
    send_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.connect_signals()
        seo_urwid.data_for_request['search_engine'] = seo_urwid.YANDEX
        self.ui.notepad.setText('Чтобы проскроллить текущую страницу в поле XPATH введи "//body"\n')
        self.thread = StartThread(self.send_error)

    def connect_signals(self):
        """Подключение сигналов"""
        self.ui.view_saved_links_btn.clicked.connect(lambda: self.view_saved_links(VISITED_LINKS_FILE))
        self.ui.close_chrome_btn.clicked.connect(self.close_chrome)
        self.ui.search_site_btn.clicked.connect(self.search_web_site)
        self.ui.search_elems_btn.clicked.connect(self.search_links_on_active_page)
        self.ui.yandex_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.YANDEX))
        self.ui.google_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.GOOGLE))
        self.ui.mailr_rbtn.clicked.connect(lambda: self.rbt_status_changed(seo_urwid.MAILRU))
        BlinkerSignals.progress.connect(self.increase_progress_bar)
        BlinkerSignals.pages_counter.connect(self.increase_pages_counter)
        BlinkerSignals.num_links.connect(self.set_max_pages_counter)
        BlinkerSignals.max_scrolling.connect(self.set_max_scrolling)
        self.send_error.connect(self.print_error)

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
        self.thread.start()

    @pyqtSlot()
    def search_web_site(self):
        """Поиск веб сайта в поисковаой системе"""
        self.ui.log_text_browser.clear()
        seo_urwid.data_for_request['geo_location'] = self.ui.geolocation_le.text()
        seo_urwid.data_for_request['phrase'] = self.ui.phrase_le.text()
        seo_urwid.data_for_request['website_url'] = self.ui.url_site_le.text()
        try:
            self.setCursor(QtGui.QCursor(Qt.WaitCursor))
            seo_urwid.browser_init()
            self.unsetCursor()
            seo_urwid.find_website_link()
            msg = QMessageBox()
            msg.setText('Ссылка на сайт найдена')
            msg.exec()
            seo_urwid.continue_browsing()
        except Exception as e:
            self.ui.log_text_browser.setText(str(e))

    @pyqtSlot()
    def close_chrome(self):
        """Закрытие веб-движка

        Также очищает историю браузера"""
        seo_urwid.exit_prog()

    def view_saved_links(self, file=None):
        subprocess.Popen(['gvim', file])

    def closeEvent(self, event):
        """Перед закрытием будет очищать историю браузера и удалять объект браузера"""
        seo_urwid.exit_prog()
        super(MainWidget, self).closeEvent(event)


def main():
    app = QApplication(sys.argv)
    win = MainWidget()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
