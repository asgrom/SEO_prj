import subprocess
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from . import BlinkerSignals
from . import VISITED_LINKS_FILE
from . import seo_urwid
from .mainwidget import Ui_Form


class QtSignals(QObject):
    done = pyqtSignal()
    send_error = pyqtSignal(str)


Signals = QtSignals()


class ScrollCurrentPageThread(QThread):
    """Прокрутка текущей страницы"""

    def __init__(self, parent=None):
        super(ScrollCurrentPageThread, self).__init__(parent)
        self.timer = None

    def run(self) -> None:
        try:
            seo_urwid.scroll_current_page(self.timer)
            Signals.done.emit()
        except Exception as e:
            Signals.send_error.emit(str(e))


class ClickLinksThread(QThread):
    """Запуск просмотра страниц в отдельном потоке"""

    def __init__(self):
        super(ClickLinksThread, self).__init__()
        self.running = False

    def run(self):
        try:
            seo_urwid.start_links_click_qt()
        except Exception as e:
            Signals.send_error.emit(str(e))
        finally:
            seo_urwid.write_visited_links(mode='a')
        Signals.done.emit()


class SearchWebPage(QThread):
    """Поток поиска ссылки на сайт в поисковой системе"""

    page_found = pyqtSignal()  # найдена ссылка на сайт

    def __init__(self, parent: QObject = None):
        super(SearchWebPage, self).__init__(parent)

    def run(self) -> None:
        self.find_website_link()

    @pyqtSlot()
    def find_website_link(self):
        try:
            seo_urwid.find_website_link()
            self.page_found.emit()
        except Exception as e:
            Signals.send_error.emit(str(e))


class MainWidget(QWidget):

    def __init__(self, proxy, user_dir, incognito, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        seo_urwid.data_for_request['search_engine'] = seo_urwid.YANDEX
        self.ui.notepad.setText('Чтобы проскроллить текущую страницу в поле XPATH введи "//body"\n')
        self.page_scrolling_thread = ClickLinksThread()
        self.search_web_page_thread = SearchWebPage()
        self.scroll_current_page_thread = ScrollCurrentPageThread()
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
        self.ui.scrollCurrentPageBtn.clicked.connect(self.scroll_current_page)

        BlinkerSignals.progress.connect(self.increase_progress_bar)
        BlinkerSignals.pages_counter.connect(self.increase_pages_counter)
        BlinkerSignals.num_links.connect(self.set_max_pages_counter)
        BlinkerSignals.max_scrolling.connect(self.set_max_scrolling)

        Signals.done.connect(self.done_msg_dlg)
        Signals.send_error.connect(self.print_error)
        self.search_web_page_thread.page_found.connect(self.page_link_found)

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

    @pyqtSlot()
    def scroll_current_page(self):
        """Прокрутка текущей страницы"""
        self.ui.log_text_browser.clear()
        self.scroll_current_page_thread.timer = self.ui.timer_sb.value()
        self.scroll_current_page_thread.start()

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
        seo_urwid.data_for_request['geo_location'] = self.ui.geolocation_le.text().strip()
        seo_urwid.data_for_request['phrase'] = self.ui.phrase_le.text().strip()
        seo_urwid.data_for_request['website_url'] = self.ui.url_site_le.text().strip()
        try:
            seo_urwid.browser_init(self.proxy, self.user_dir, self.incognito)
        except Exception as e:
            self.print_error(e)
            return
        self.enable_addons_dialog()
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
    def done_msg_dlg(self):
        QMessageBox.information(self, 'All done!', 'All done!',
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

    @pyqtSlot()
    def enable_addons_dialog(self):
        QMessageBox.information(self, 'Включить addons',
                                'Перед продолжением включить addons в браузере или задать '
                                'город в геолокации',
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)


def main(proxy, user_dir, incognito):
    app = QApplication(sys.argv)
    win = MainWidget(proxy=proxy, user_dir=user_dir, incognito=incognito)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    pass
