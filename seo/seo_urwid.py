import os
import time
from subprocess import Popen

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from seo import YANDEX, GOOGLE
from seo import all_pages_clicked_signal, pages_amount_signal
from seo.google_search import Google
from seo.yandex_search import Yandex
from . import urwid_menu
from .browser import ErrorExcept, Options

visited_links = list()

VISITED_LINKS_FILE = os.path.join(os.environ['HOME'], 'Документы/seo_visited_links')

browser = None

required_web_site_element = None

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


def exit_prog():
    if browser is not None:
        browser.quit()


def find_website_link():
    """Поиск сайта и переход на него

    Если ссылка на сайт найдена, переходим на него и делаем вкладку с ним активной.
    Прежде чем перейти на сайт, выводится сообщение и происходит задерка. Это надо для того,
    если по условию задания надо посетить другие сайто до найденого."""

    global required_web_site_element

    # устанавливаем местоположение если поисковик яндекс и если задан город местоположения
    if browser.geo_location and browser.search_engine == YANDEX:
        browser.change_browser_location()

    # ссылка на искомый веб-сайт
    link = browser.find_website_link()

    if not link:
        raise ErrorExcept('ССЫЛКИ НА ИСКОМЫЙ САЙТ НЕ НАЙДЕНО')

    required_web_site_element = link

    return link


def continue_browsing():
    visited_links.append(f'Ссылка с поисковика:\n{required_web_site_element.get_attribute("href")}')

    try:
        # прокрутка страницы на начало
        # browser.execute_script('scrollTo(0,0);')
        required_web_site_element.send_keys(Keys.HOME)
        time.sleep(.5)
        # перейти к искомому элементу
        actChains = ActionChains(browser)
        actChains.move_to_element(required_web_site_element).perform()
        actChains.click(required_web_site_element).perform()

        # сделать новую вкладку активной
        browser.switch_to.window(browser.window_handles[-1])

    except Exception as e:
        raise ErrorExcept(f'ОШИБКА ПЕРЕХОДА ПО ССЫЛКЕ С ПОИСКОВИКА\n{e}')


def browser_init():
    global browser
    try:
        if browser:
            browser.quit()

        if data_for_request['search_engine'] == GOOGLE:
            browser = Google(options=Options(), **data_for_request)

        elif data_for_request['search_engine'] == YANDEX:
            browser = Yandex(options=Options(), **data_for_request)

    except (WebDriverException, Exception) as e:
        raise ErrorExcept(f'ОШИБКА В ИНИЦИАЛИЗАЦИИ ДРАЙВЕРА\n{e}')


def start_links_click():
    """Начинаем поиск и просмотр ссылок на странице

    Активируем последнюю вкладку.
    Посещенные линки добавляем в глобальный список.
    Селекторы линков добавляем в словарь data_for_request.
    Добавлена возможность переопределить таймер.
    """
    global browser
    if not browser:
        browser = Google(options=Options())

    num_links = selectors_for_links['num_links_to_click']

    browser.timer = data_for_request['timer']

    browser.switch_to.window(browser.window_handles[-1])

    visited_links.append(browser.current_url)

    if num_links > len(browser.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                      xpath_elems=selectors_for_links['xpath_elems'])):
        # print(browser.get_links_from_website(selectors_for_links['css_elems', selectors_for_links['xpath_elems']]))
        raise ErrorExcept(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')

    try:
        for i in range(num_links):
            links = browser.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                   xpath_elems=selectors_for_links['xpath_elems'])
            links[i].click()

            browser.page_scrolling_with_urwid_progress_bar()
            pages_amount_signal.send(start_links_click, done=num_links)

            visited_links.append(browser.current_url)
            browser.back()
        all_pages_clicked_signal.send(start_links_click)
    except WebDriverException as e:
        raise ErrorExcept(f'ОШИБКА!!! ПРИ ПЕРЕХОДЕ ПО ЭЛЕМЕНТАМ НА СТРАНИЦЕ\n{e}')


def print_visited_links():
    try:
        Popen(['gvim', VISITED_LINKS_FILE])
    except OSError as e:
        raise ErrorExcept(e)


def write_visited_links(mode='w'):
    try:
        with open(VISITED_LINKS_FILE, mode=mode) as f:
            for i in visited_links:
                f.write(f'{i}\n\n')
    except Exception as e:
        raise ErrorExcept(e)


def main():
    urwid_menu.main()


if __name__ == '__main__':
    main()
