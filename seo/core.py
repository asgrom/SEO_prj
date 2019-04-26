import time
import sys
import os
from pprint import pprint

from .browser import Options
from .yandex_search import Yandex
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from .console_menu import main_menu, get_integer, get_string, search_engine_menu

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

visited_links = list()
FILE_DATA_FOR_REQUEST = os.path.join(os.environ['HOME'], '.local/share/seo/data_for_request')
VISITED_LINKS_FILE = os.path.join(os.environ['HOME'], 'Документы/seo_visited_links')


def set_selectors_for_website_links():
    """Задать селекторы для ссылок, которые нужно посетить на сайте"""
    # page_css_selector = get_string('CSS-селектор страницы на которой будем искать')
    css_elems = get_string(msg='CSS-селектор элементов')
    xpath_elems = get_string(msg='XPATH элементов')
    num_links_to_click = get_integer('Количество ссылок', required=True)
    timer = get_integer('Переопределить таймер?')
    return (dict(
        # page_css_selector=page_css_selector,
        css_elems=css_elems,
        xpath_elems=xpath_elems,
        num_links_to_click=num_links_to_click,
        timer=timer
    ))


def search_website_and_go(driver, **kwargs):
    """Поиск сайта и переход на него

    Если ссылка на сайт найдена, переходим на него и делаем вкладку с ним активной.
    Прежде чем перейти на сайт, выводится сообщение и происходит задерка. Это надо для того,
    если по условию задания надо посетить другие сайто до найденого.

    :return: возвращает статус результата поиска сайта.
             Если веб-сайт найден и на него сделан переход, то возращается True, в противном случае None.
    """
    status = None

    link = driver.search_website_link()
    if link is None:
        return status

    try:
        # притормозим просмотр. вдруг по условиям надо просмотреть другие сайты
        input('ССЫЛКА НА САЙТ НАЙДЕНА\nПРОДОЛЖИТЬ? >>> ')
        # driver.execute_script(f"arguments[0].scrollIntoView(true);", link)

        # прокрутка страницы на начало
        # driver.execute_script('scrollTo(0,0);')
        link.send_keys(Keys.HOME)

        # перейти к искомому элементу
        ActionChains(driver).move_to_element(link).click(link).perform()

        # сделать новую вкладку активной
        driver.switch_to.window(driver.window_handles[-1])
        status = True
    except Exception as e:
        print(e)
        return status
    status = start_links_click(driver=driver, **kwargs)
    return status


def exit_prog(driver, **kwargs):
    if driver is not None:
        driver.quit()
    sys.exit()


def set_search_engine(**kwargs):
    search_engine = {'1': YANDEX, '2': GOOGLE}
    search_engine_menu()
    choice = get_string(required=True, valid=('1', '2'))
    kwargs['data_for_request']["search_engine"] = search_engine[choice]


# todo: page_css_selector
#       сделать так, чтобы клик на страницу, на которой будем искать элементы ссылок,
#       происходил до того, как вводится селектор ссылок.


def print_data_for_request(**kwargs):
    print('Данные для запроса:')
    pprint(kwargs['data_for_request'], indent=4)


def set_search_phrase(**kwargs):
    kwargs['data_for_request']['phrase'] = get_string('Поисковая фраза:', required=True)


def set_website_url(**kwargs):
    """Устанавливает URL веб-сайта

    Поддерживает регулярные выражения.
    """
    kwargs['data_for_request']['website_url'] = get_string('Website URL:', required=True)


def set_geo_location(**kwargs):
    kwargs['data_for_request']['geo_location'] = get_string('Местоположение:')


def set_timer(**kwargs):
    kwargs['data_for_request']['timer'] = get_integer('Timer:', required=True)


def print_visited_links(**kwargs):
    try:
        with open(VISITED_LINKS_FILE) as f:
            print(f.read())
    except OSError as e:
        print(e)


def start_links_click(**kwargs):
    """Начинаем поиск и просмотр ссылок на странице

    Активируем последнюю вкладку.
    Посещенные линки добавляем в глобальный список.
    Селекторы линков добавляем в словарь data_for_request.
    Добавлена возможность переопределить таймер.
    """
    driver = kwargs['driver']
    driver.switch_to.window(driver.window_handles[-1])
    selectors_links = set_selectors_for_website_links()
    kwargs['data_for_request'].update(selectors_links)
    num_links = selectors_links['num_links_to_click']
    if selectors_links['timer']:
        driver.timer = selectors_links['timer']

    visited_links.append(driver.current_url )

    if num_links > len(driver.get_links_from_website(
            css_elems=selectors_links['css_elems'],
            xpath_elems=selectors_links['xpath_elems'])):
        print(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')
        return False

    try:
        for i in range(num_links):
            links = driver.get_links_from_website(css_elems=selectors_links['css_elems'],
                                                  xpath_elems=selectors_links['xpath_elems'])
            links[i].click()
            driver.page_scrolling()
            visited_links.append(driver.current_url)
            driver.back()
    except WebDriverException as e:
        print(e)
        return False

    return True


def main():
    driver = None
    data_for_request = dict()

    menu_func = {
        'q': exit_prog,
        '6': search_website_and_go,
        '5': set_search_engine,
        '7': print_data_for_request,
        '1': set_search_phrase,
        '2': set_website_url,
        '3': set_geo_location,
        '4': set_timer,
        '8': print_visited_links
    }
    valid = list('12345678q')
    while True:
        main_menu()
        choice = get_string('Пункт меню:', required=True, valid=valid)
        menu_func[choice](driver=driver, data_for_request=data_for_request)

    driver = Yandex(options=Options(), url='http://testsite.alex.org',
                    search_engine=YANDEX, phrase='lamoda', website_url='lamoda.ru',
                    geo_location='киров', timer=3)

    driver.change_browser_location()

    search_website_and_go(driver)
    request_data = set_selectors_for_website_links()

    for i in range(request_data['num_links_to_click']):
        links = driver.get_links_from_website(xpath_elems=request_data['xpath_elems'])
        links[i].click()
        driver.page_scrolling()
        driver.back()

    input()
    driver.quit()


if __name__ == '__main__':
    driver = Yandex(options=Options(), url='http://testsite.alex.org',
                    search_engine=YANDEX, phrase='lamoda', website_url='lamoda.ru',
                    geo_location='киров', timer=5)
    input('as')
    # print(driver.current_window_handle)
    win = driver.window_handles
    print(win)
    start_links_click(driver=driver, data_for_request=dict())
    print(visited_links)
    driver.quit()
