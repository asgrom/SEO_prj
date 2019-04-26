import time
import sys

from .browser import Options
from .yandex_search import Yandex
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .console_menu import main_menu, get_integer, get_string, search_engine_menu

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

visited_links = list()


def set_selectors_for_website_links(*kargs, **kwargs):
    """Задать селекторы для ссылок, которые нужно посетить на сайте"""
    page_css_selector = get_string('CSS-селектор страницы на которой будем искать')
    css_elems = get_string(msg='CSS-селектор элементов')
    xpath_elems = get_string(msg='XPATH элементов')
    num_links_to_click = get_integer('Количество ссылок', required=True)
    return dict(
        page_css_selector=page_css_selector,
        css_elems=css_elems,
        xpath_elems=xpath_elems,
        num_links_to_click=num_links_to_click
    )


def search_website_and_go(driver):
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

    return status


def exit_prog(driver):
    if driver is not None:
        driver.close()
    sys.exit()


def set_search_engine(*kargs, **kwargs):
    search_engine ={'1': YANDEX, '2': GOOGLE}
    search_engine_menu()
    choice = get_string('ПОИСКОВИК', required=True)
    kwargs['data_for_request']["search_engine"] = search_engine[choice]

# todo: page_css_selector
#       сделать так, чтобы клик на страницу, на которой будем искать элементы ссылок,
#       происходил до того, как вводится селектор ссылок.


def main():
    driver = None
    data_for_request = dict()
    menu_func = {
        'q': exit_prog,
        '6': search_website_and_go,
        '5': set_search_engine
    }
    valid = list('12345678q')
    while True:
        main_menu()
        choice = get_string('Пункт меню', required=True, valid=valid)
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
    driver.close()


if __name__ == '__main__':
    main()
