import os
import time
from subprocess import Popen

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from seo import VISITED_LINKS_FILE, Chrome_history
from seo import YANDEX, GOOGLE, MAILRU
from seo.google_search import Google
from seo.mailru_search import MailRu
from seo.yandex_search import Yandex
from . import Signals, BlinkerSignals
from . import seo_urwid
from .browser import ErrorExcept, Options

VisitedLinks = list()

Driver = None

RequiredWebElement = None

signals = Signals()

data_for_request = dict(
    search_engine=None,
    phrase=None,
    website_url=None,
    timer=None,
    geo_location=None
)

selectors_for_links = dict(
    css_elems=None,
    xpath_elems=None,
    num_links_to_click=None
)


def close_chrome():
    try:
        os.remove(Chrome_history)
    except Exception:
        pass
    if Driver is not None:
        Driver.quit()


def find_website_link():
    """Поиск ссылки на сайт в поисковике"""

    global RequiredWebElement

    # устанавливаем местоположение если поисковик яндекс и если задан город местоположения
    if Driver.geo_location and Driver.search_engine == YANDEX:
        Driver.change_browser_location()

    # ссылка на искомый веб-сайт
    link = Driver.find_website_link()

    if not link:
        raise ErrorExcept('ССЫЛКИ НА ИСКОМЫЙ САЙТ НЕ НАЙДЕНО')

    RequiredWebElement = link
    VisitedLinks.append(f'URL поисковика\n{Driver.current_url}')
    write_visited_links(mode='a')

    return link


def continue_browsing():
    """Переход по найденной ссылке основного сайта

    Прокручивание страницы поиска наверх, переход к ссылке, клик. Переключение на открытую вкладку.
    """
    # VisitedLinks.append(f'Ссылка с поисковика:\n{RequiredWebElement.get_attribute("href")}')

    try:
        # прокрутка страницы на начало
        # Driver.execute_script('scrollTo(0,0);')
        RequiredWebElement.send_keys(Keys.HOME)
        time.sleep(.5)
        # перейти к искомому элементу
        actChains = ActionChains(Driver)
        actChains.move_to_element(RequiredWebElement).perform()
        actChains.click(RequiredWebElement).perform()

        # сделать новую вкладку активной
        Driver.switch_to.window(Driver.window_handles[-1])
        VisitedLinks.append(f'URL страницы, на которую перешли с поисковика\n{Driver.current_url}')
        write_visited_links(mode='a')

    except Exception as e:
        raise ErrorExcept(f'ОШИБКА ПЕРЕХОДА ПО ССЫЛКЕ С ПОИСКОВИКА\n{e}')


def browser_init(proxy, user_dir, incognito):
    """Инициализация браузера

    Если браузер открыт, происходит его закрытие и создается новый экземпляр.
    """
    global Driver
    try:
        if Driver:
            close_chrome()

        if data_for_request['search_engine'] == GOOGLE:
            Driver = Google(options=Options(proxy=proxy, user_dir=user_dir,
                                            incognito=incognito), **data_for_request)

        elif data_for_request['search_engine'] == YANDEX:
            Driver = Yandex(options=Options(proxy=proxy, user_dir=user_dir,
                                            incognito=incognito), **data_for_request)

        elif data_for_request['search_engine'] == MAILRU:
            Driver = MailRu(options=Options(proxy=proxy, user_dir=user_dir,
                                            incognito=incognito), **data_for_request)

        return Driver
    except (WebDriverException, Exception) as e:
        raise ErrorExcept(f'ОШИБКА В ИНИЦИАЛИЗАЦИИ ДРАЙВЕРА\n{e}')


def start_links_click():
    """Начинаем поиск и просмотр ссылок на странице

    Активируем последнюю вкладку.
    Посещенные линки добавляем в глобальный список.
    """
    global Driver
    if Driver is None:
        Driver = Google(options=Options())

    num_links = selectors_for_links['num_links_to_click']

    timer = data_for_request['timer']

    Driver.switch_to.window(Driver.window_handles[-1])

    VisitedLinks.append(Driver.current_url)

    if num_links > len(Driver.get_links_from_website(
            css_elems=selectors_for_links['css_elems'],
            xpath_elems=selectors_for_links['xpath_elems'])):
        raise ErrorExcept(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')

    try:
        for i in range(num_links):
            links = Driver.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                  xpath_elems=selectors_for_links['xpath_elems'])
            links[i].click()

            Driver.page_scrolling_with_urwid_progress_bar(timer=timer)
            Signals.clicked.send(start_links_click, done=num_links)

            VisitedLinks.append(Driver.current_url)
            Driver.back()
    except WebDriverException as e:
        raise ErrorExcept(f'ОШИБКА!!! ПРИ ПЕРЕХОДЕ ПО ЭЛЕМЕНТАМ НА СТРАНИЦЕ\n{e}')
    finally:
        Signals.end.send('loop-end')


def scroll_current_page(timer):
    """Прокрутка текущей страницы"""
    Driver.switch_to.window(Driver.window_handles[-1])
    VisitedLinks.append(Driver.current_url)
    Driver.qt_page_scrolling(timer=timer)
    write_visited_links(mode='a')


def start_links_click_qt():
    """Клики по ссылкам

    Метод для Qt версии"""

    num_links = selectors_for_links['num_links_to_click']

    timer = data_for_request['timer']

    Driver.switch_to.window(Driver.window_handles[-1])

    VisitedLinks.append(f'Адреса посещенных ссылок\n{Driver.current_url}')
    if num_links > len(Driver.get_links_from_website(
            css_elems=selectors_for_links['css_elems'],
            xpath_elems=selectors_for_links['xpath_elems'])):
        raise ErrorExcept(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')
    BlinkerSignals.num_links.send(value=num_links)

    try:
        for i in range(num_links):
            links = Driver.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                  xpath_elems=selectors_for_links['xpath_elems'])
            actChains = ActionChains(Driver)
            actChains.move_to_element(links[i]).perform()
            actChains.click(links[i]).perform()
            # links[i].click()

            BlinkerSignals.pages_counter.send(value=i + 1)
            Driver.qt_page_scrolling(timer=timer)
            VisitedLinks.append(Driver.current_url)
            Driver.back()
            time.sleep(2)
        BlinkerSignals.pages_counter.send(value=0)
    except WebDriverException as e:
        raise ErrorExcept(f'ОШИБКА!!! ПРИ ПЕРЕХОДЕ ПО ЭЛЕМЕНТАМ НА СТРАНИЦЕ\n{e}')


def print_visited_links():
    """Запускается gvim c файлом посещенных ссылок"""
    try:
        Popen(['gvim', VISITED_LINKS_FILE])
    except OSError as e:
        raise ErrorExcept(e)


def write_visited_links(mode='w'):
    """Добавляет запись или перезаписывает файла посещенных ссылок

    Режим открытия файла зависит от аргумента mode: w - запись, a - добавление в конец файла.
    """
    if not VisitedLinks:
        return
    try:
        with open(VISITED_LINKS_FILE, mode=mode) as f:
            print(time.strftime('%d-%m-%Y %H:%M:%S', time.localtime()), file=f)
            for i in VisitedLinks:
                f.write(f'{i}\n')
            print(file=f)
        VisitedLinks.clear()

    except Exception as e:
        raise ErrorExcept(e)


def main():
    seo_urwid.main()


if __name__ == '__main__':
    main()
