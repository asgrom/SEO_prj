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
from . import BlinkerSignals
from .browser import ErrorExcept, Options

VisitedLinks = list()

Driver = None

WebsiteLink = None

data_for_request = dict(
    search_engine=None,
    phrase=None,
    website_url=None,
    timer=0,
    geo_location=None
)

selectors_for_links = dict(
    css_elems=None,
    xpath_elems=None,
    num_links_to_click=0
)


def close_chrome():
    try:
        os.remove(Chrome_history)
    except OSError:
        pass
    if Driver is not None:
        Driver.quit()


def find_website_link():
    """Поиск ссылки на сайт в поисковике"""

    global WebsiteLink

    # устанавливаем местоположение если поисковик яндекс и если задан город местоположения
    if Driver.geo_location and Driver.search_engine == YANDEX:
        Driver.change_browser_location()

    # ссылка на искомый веб-сайт
    WebsiteLink = Driver.find_website_link()

    actChains = ActionChains(Driver)
    actChains.move_to_element(WebsiteLink).perform()

    VisitedLinks.append(f'URL поисковика\n{Driver.current_url}')
    write_visited_links(mode='a')

    return WebsiteLink


def goto_found_link():
    """Переход по найденной ссылке основного сайта

    Прокручивание страницы поиска наверх, переход к ссылке, клик. Переключение на открытую вкладку.
    """

    try:
        # прокрутка страницы на начало
        WebsiteLink.send_keys(Keys.HOME)
        time.sleep(.5)

        # перейти к искомому элементу
        actChains = ActionChains(Driver)
        actChains.move_to_element(WebsiteLink).perform()
        actChains.click(WebsiteLink).perform()

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


def scroll_current_page(timer):
    """Прокрутка текущей страницы"""
    Driver.switch_to.window(Driver.window_handles[-1])
    VisitedLinks.append(Driver.current_url)
    Driver.page_scrolling(timer=timer)
    write_visited_links(mode='a')


def start_links_click():
    """
        Клики по ссылкам
    """

    num_links = selectors_for_links['num_links_to_click']

    timer = data_for_request['timer']

    Driver.switch_to.window(Driver.window_handles[-1])

    VisitedLinks.append(f'Адреса посещенных ссылок\n{Driver.current_url}')
    if num_links > len(Driver.get_links_from_website(
            css_elems=selectors_for_links['css_elems'],
            xpath_elems=selectors_for_links['xpath_elems'])):
        raise ErrorExcept(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')
    BlinkerSignals.num_links.send(num_links)

    try:
        for i in range(num_links):
            links = Driver.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                  xpath_elems=selectors_for_links['xpath_elems'])
            actChains = ActionChains(Driver)
            actChains.move_to_element(links[i]).perform()
            actChains.click(links[i]).perform()

            BlinkerSignals.pages_counter.send(i + 1)
            Driver.page_scrolling(timer=timer)
            VisitedLinks.append(Driver.current_url)
            Driver.back()
            time.sleep(2)
        BlinkerSignals.pages_counter.send(0)
    except WebDriverException as e:
        raise ErrorExcept(f'ОШИБКА!!! ПРИ ПЕРЕХОДЕ ПО ЭЛЕМЕНТАМ НА СТРАНИЦЕ\n{e}')
    finally:
        if VisitedLinks:
            write_visited_links(mode='a')


def view_visited_links():
    """
        Запускается gvim c файлом посещенных ссылок
    """
    try:
        Popen(['gvim', VISITED_LINKS_FILE])
    except OSError as e:
        raise ErrorExcept(e)


def write_visited_links(mode='w'):
    """
        Добавляет запись или перезаписывает файла посещенных ссылок

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
    pass


if __name__ == '__main__':
    main()
