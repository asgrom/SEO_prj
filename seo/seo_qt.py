import re
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from . import BlinkerSignals
from . import core
from .mainwidget import Ui_Form


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print('Error: ', text)
    QMessageBox.critical(None, 'Error', text)
    # quit()


sys.excepthook = log_uncaught_exceptions


class QtSignals(QObject):
    done = pyqtSignal()
    send_error = pyqtSignal(str)


Signals = QtSignals()


class ScrollCurrentPageThread(QThread):
    """
        Прокрутка текущей страницы

        Отдельный поток для прокрутки текущей страницы.
        По окончании испускается сигнал, который обрабатывается в основном потоке.
    """

    def __init__(self, parent=None):
        super(ScrollCurrentPageThread, self).__init__(parent)
        self.timer = None

    def run(self) -> None:
        try:
            core.scroll_current_page(self.timer)
            Signals.done.emit()
        except Exception as e:
            Signals.send_error.emit(str(e))


class ClickLinksThread(QThread):
    """
        Клики по ссылкам на странице

        Клики по ссылкам на странице и прокрутка открываемых страниц. Отдельный поток.
        По окончании посылается сигнал, который обрабатывается в основном потоке.
    """

    def __init__(self):
        super(ClickLinksThread, self).__init__()
        self.running = False

    def run(self):
        try:
            core.start_links_click()
            Signals.done.emit()
        except Exception as e:
            Signals.send_error.emit(str(e))


class SearchWebPage(QThread):
    """
        Поиск ссылки на страницу в поисковой системе
    """

    page_found = pyqtSignal()  # найдена ссылка на сайт

    def __init__(self, parent: QObject = None):
        super(SearchWebPage, self).__init__(parent)

    def run(self) -> None:
        self.find_website_link()

    @pyqtSlot()
    def find_website_link(self):
        try:
            core.find_website_link()
            self.page_found.emit()
        except Exception as e:
            Signals.send_error.emit(str(e))


class MainWidget(QWidget):

    def __init__(self, proxy, user_dir, incognito, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        core.data_for_request['search_engine'] = core.YANDEX
        self.ui.notepad.setText('Чтобы проскроллить текущую страницу в поле XPATH введи "//body"\n')
        self.page_scrolling_thread = ClickLinksThread()
        self.search_web_page_thread = SearchWebPage()
        self.scroll_current_page_thread = ScrollCurrentPageThread()
        self.proxy = proxy
        self.user_dir = user_dir
        self.incognito = incognito
        self.set_css()
        self.connect_signals()

    def set_css(self):
        self.setStyleSheet(
            """
            QProgressBar::chunk {
                background-color: #CD96CD;
                width: 10px;
                margin: 0.5px;
            }
            
            QProgressBar {
                text-align: center;
                border-radius: 5px;
                border: 1px solid grey;
                padding: 0.5px;
            }
            
            QLineEdit {
                border: 1px solid grey;
                border-radius: 5px;
                padding: 2px;
            }
            """
        )

    def connect_signals(self):
        """
            Подключение сигналов
        """
        self.ui.view_saved_links_btn.clicked.connect(core.view_visited_links)
        self.ui.close_chrome_btn.clicked.connect(self.close_chrome)
        self.ui.search_site_btn.clicked.connect(self.search_site_btn_clicked)
        self.ui.search_elems_btn.clicked.connect(self.search_links_on_active_page)
        self.ui.yandex_rbtn.clicked.connect(lambda: self.rbt_status_changed(core.YANDEX))
        self.ui.google_rbtn.clicked.connect(lambda: self.rbt_status_changed(core.GOOGLE))
        self.ui.mailr_rbtn.clicked.connect(lambda: self.rbt_status_changed(core.MAILRU))
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
        QMessageBox.warning(self, "Внимание!!!", err,
                            buttons=QMessageBox.Ok,
                            defaultButton=QMessageBox.Ok)

    def set_max_scrolling(self, value):
        """
            Устанавливает максимальное значение для прогрессбара скроллинга страницы
        """
        self.ui.scrolling_prog_bar.setMaximum(value)

    def increase_progress_bar(self, value):
        """
            Увеличение прогрессбара прокрутки страницы
        """
        if value == 0:
            self.ui.scrolling_prog_bar.reset()
            return
        self.ui.scrolling_prog_bar.setValue(value)

    def increase_pages_counter(self, value):
        """
            Увеличение прогрессбара просмотренных страниц
        """
        if value == 0:
            self.ui.num_pages_prog_bar.reset()
            return
        self.ui.num_pages_prog_bar.setValue(value)

    def set_max_pages_counter(self, value):
        """
            Установка максимального значения прогрессбара просмотренных страниц
        """
        self.ui.num_pages_prog_bar.setMaximum(value)

    @pyqtSlot()
    def rbt_status_changed(self, search_engine: str):
        """
            Установка поисковой системы
        """
        core.data_for_request['search_engine'] = search_engine

    @pyqtSlot()
    def search_links_on_active_page(self):
        """
            Поиск ссылок на активной странице

            Устанавливает последнюю открытую вкладку браузера активной
            и начинает поиск необходимых элементов
        """
        self.ui.log_text_browser.clear()
        core.data_for_request['timer'] = self.ui.timer_sb.value()
        core.selectors_for_links['num_links_to_click'] = self.ui.number_elems_sb.value()
        core.selectors_for_links['css_elems'] = self.ui.css_le.text()
        core.selectors_for_links['xpath_elems'] = self.ui.xpaath_le.text()
        self.page_scrolling_thread.start()

    @pyqtSlot()
    def scroll_current_page(self):
        """
            Прокрутка текущей страницы
        """
        self.ui.log_text_browser.clear()
        self.scroll_current_page_thread.timer = self.ui.timer_sb.value()
        self.scroll_current_page_thread.start()

    @pyqtSlot()
    def page_link_found(self):
        """
            Обработка сигнала когда найдена ссылка на сайт в поисковой системе
        """
        QMessageBox.information(self, 'Ссылка найдена',
                                'Ссылка на сайт найдена',
                                buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)
        try:
            core.goto_found_link()
        except Exception as e:
            self.print_error(str(e))

    @pyqtSlot()
    def search_site_btn_clicked(self):
        """
            Нажата кнопка поиска сайта в поисковаой системе
        """
        self.ui.log_text_browser.clear()
        core.data_for_request['geo_location'] = self.ui.geolocation_le.text().strip()
        url = self.ui.url_site_le.text().strip()
        url = re.sub(r'(\*)+|(\.){2,}', '.*', url)
        self.ui.url_site_le.setText(url)
        core.data_for_request['phrase'] = self.ui.phrase_le.text().strip()
        core.data_for_request['website_url'] = url
        try:
            core.browser_init(self.proxy, self.user_dir, self.incognito)
        except Exception as e:
            self.print_error(e)
            return
        self.enable_addons_dialog()
        self.search_web_page_thread.start()

    @pyqtSlot()
    def close_chrome(self):
        """
            Закрытие веб-движка

            Также очищает историю браузера
        """
        core.close_chrome()

    def closeEvent(self, event):
        """
            Перед закрытием будет очищать историю браузера и удалять объект браузера
        """
        core.close_chrome()
        super(MainWidget, self).closeEvent(event)

    @pyqtSlot()
    def done_msg_dlg(self):
        """
            Сообщение о выполнении задач
        """
        QMessageBox.information(self, 'All done!', 'All done!',
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)

    @pyqtSlot()
    def enable_addons_dialog(self):
        """
            Диалог показывается после инициализации браузера

            Перед продолжением работы активировать и настроить расширения браузера.
        """
        QMessageBox.information(self, 'Включить addons',
                                'Перед продолжением включить addons в браузере или задать '
                                'город в геолокации',
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)


def main(proxy, user_dir, incognito):
    app = QApplication(sys.argv)
    with open('/home/alexandr/PycharmProjects/SEO_prj/qss/stylesheet.qss') as f:
        app.setStyleSheet(f.read())
    win = MainWidget(proxy=proxy, user_dir=user_dir, incognito=incognito)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    pass
