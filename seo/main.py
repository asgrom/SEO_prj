import os

from selenium.common.exceptions import WebDriverException

from seo.google_search import Google
from seo.yandex_search import Yandex
from .browser import ErrorExcept, Options
from selenium.webdriver.common.keys import Keys
from seo import YANDEX, GOOGLE
from selenium.webdriver.common.action_chains import ActionChains

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


def find_website_link():
    """Поиск сайта и переход на него

    Если ссылка на сайт найдена, переходим на него и делаем вкладку с ним активной.
    Прежде чем перейти на сайт, выводится сообщение и происходит задерка. Это надо для того,
    если по условию задания надо посетить другие сайто до найденого."""

    # устанавливаем местоположение если поисковик яндекс и если задан город местоположения
    if browser.geo_location and browser.search_engine == YANDEX:
        browser.change_browser_location()

    # ссылка на искомый веб-сайт
    link = browser.find_website_link()

    if not link:
        raise ErrorExcept('ССЫЛКИ НА ИСКОМЫЙ САЙТ НЕ НАЙДЕНО')

    return link


def continue_browsing():
    visited_links.append(f'Ссылка с поисковика:\n{required_web_site_element.get_attribute("href")}')

    try:
        # притормозим просмотр. вдруг по условиям надо просмотреть другие сайты
        input('ССЫЛКА НА САЙТ НАЙДЕНА\nПРОДОЛЖИТЬ? >>> ')
        # browser.execute_script(f"arguments[0].scrollIntoView(true);", link)

        # прокрутка страницы на начало
        # browser.execute_script('scrollTo(0,0);')
        required_web_site_element.send_keys(Keys.HOME)

        # перейти к искомому элементу
        ActionChains(browser).move_to_element(required_web_site_element).click(required_web_site_element).perform()

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


def start_links_click(browser, selectors_for_links):
    """Начинаем поиск и просмотр ссылок на странице

    Активируем последнюю вкладку.
    Посещенные линки добавляем в глобальный список.
    Селекторы линков добавляем в словарь data_for_request.
    Добавлена возможность переопределить таймер.
    """
    selectors_for_links.clear()
    selectors_for_links.update(set_selectors_for_website_links())
    num_links = selectors_for_links['num_links_to_click']

    if selectors_for_links['timer']:
        browser.timer = selectors_for_links['timer']
    elif browser.timer is None:
        browser.timer = get_integer('Необходимо установить таймер:', required=True)

    browser.switch_to.window(browser.window_handles[-1])

    visited_links.append(browser.current_url)

    if num_links > len(browser.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                     xpath_elems=selectors_for_links['xpath_elems'])):
        raise ErrorExcept(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')

    try:
        for i in range(num_links):
            links = browser.get_links_from_website(css_elems=selectors_for_links['css_elems'],
                                                  xpath_elems=selectors_for_links['xpath_elems'])
            links[i].click()
            browser.page_scrolling()
            visited_links.append(browser.current_url)
            browser.back()
    except WebDriverException as e:
        raise ErrorExcept(f'ОШИБКА!!! ПРИ ПЕРЕХОДЕ ПО ЭЛЕМЕНТАМ НА СТРАНИЦЕ\n{e}')


if __name__ == '__main__':
    browser_init()
