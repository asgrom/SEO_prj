import os
import sys
from pprint import pprint
from subprocess import Popen

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .browser import Options
from .console_menu import main_menu, get_integer, get_string, search_engine_menu
from .google_search import Google
from .yandex_search import Yandex

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

VISITED_LINKS = list()
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


def search_website_and_go(driver, selectors_for_links):
    """Поиск сайта и переход на него

    Если ссылка на сайт найдена, переходим на него и делаем вкладку с ним активной.
    Прежде чем перейти на сайт, выводится сообщение и происходит задерка. Это надо для того,
    если по условию задания надо посетить другие сайто до найденого.

    :return: возвращает статус результата поиска сайта.
             Если веб-сайт найден и на него сделан переход, то возращается True, в противном случае None.
    """
    status = None

    if driver.geo_location is not None:
        driver.change_browser_location()

    link = driver.search_website_link()
    if link is None:
        return status
    VISITED_LINKS.append(f'Ссылка с поисковика:\n{link.get_attribute("href")}')

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
    status = start_links_click(driver=driver, selectors_for_links=selectors_for_links)
    return status


def exit_prog(driver):
    if driver is not None:
        driver.quit()
    sys.exit()


def set_search_engine(data_for_request):
    search_engine = {'1': YANDEX, '2': GOOGLE}
    search_engine_menu()
    choice = get_string(required=True, valid=('1', '2'))
    data_for_request["search_engine"] = search_engine[choice]


def print_data_for_request(data_for_request, selectors_for_links):
    print('Данные для запроса:')
    pprint(data_for_request, indent=4)
    print('Селекторы для линков:')
    pprint(selectors_for_links, indent=4)


def set_search_phrase(data_for_request):
    data_for_request['phrase'] = get_string('Поисковая фраза:', required=True)


def set_website_url(data_for_request):
    """Устанавливает URL веб-сайта

    Поддерживает регулярные выражения.
    """
    data_for_request['website_url'] = get_string('Website URL:', required=True)


def set_geo_location(data_for_request):
    data_for_request['geo_location'] = get_string('Местоположение:')


def set_timer(data_for_request):
    data_for_request['timer'] = get_integer('Timer:', required=True)


def print_visited_links():
    try:
        Popen(['gvim', VISITED_LINKS_FILE])
        with open(VISITED_LINKS_FILE) as f:
            print(f.read())
    except OSError as e:
        print(e)


def start_links_click(driver, selectors_for_links):
    """Начинаем поиск и просмотр ссылок на странице

    Активируем последнюю вкладку.
    Посещенные линки добавляем в глобальный список.
    Селекторы линков добавляем в словарь data_for_request.
    Добавлена возможность переопределить таймер.
    """
    selectors_links = set_selectors_for_website_links()
    selectors_for_links.update(selectors_links)
    num_links = selectors_links['num_links_to_click']

    if selectors_links['timer']:
        driver.timer = selectors_links['timer']
    elif driver.timer is None:
        driver.timer = get_integer('Необходимо установить таймер:', required=True)

    driver.switch_to.window(driver.window_handles[-1])

    VISITED_LINKS.append(driver.current_url)

    try:
        if num_links > len(driver.get_links_from_website(
                css_elems=selectors_links['css_elems'],
                xpath_elems=selectors_links['xpath_elems'])):
            print(f'КОЛИЧЕСТВО НАЙДЕННЫХ ЭЛЕМЕНТОВ НА СТРАНИЦЕ МЕНЬШЕ ТРЕБУЕМОГО')
            return False
    except WebDriverException as e:
        print(e)
        return False

    try:
        for i in range(num_links):
            links = driver.get_links_from_website(css_elems=selectors_links['css_elems'],
                                                  xpath_elems=selectors_links['xpath_elems'])
            links[i].click()
            driver.page_scrolling()
            VISITED_LINKS.append(driver.current_url)
            driver.back()
    except WebDriverException as e:
        print(e)
        return False

    return True


def write_visited_links(mode='w'):
    with open(VISITED_LINKS_FILE, mode=mode) as f:
        for i in VISITED_LINKS:
            f.write(f'{i}\n\n')


def driver_init(driver, data_for_request):
    try:
        if not driver:
            if 'search_engine' not in data_for_request:
                set_search_engine(data_for_request)
            if data_for_request['search_engine'] == GOOGLE:
                driver = Google(options=Options(), **data_for_request)
            elif data_for_request['search_engine'] == YANDEX:
                driver = Yandex(options=Options(), **data_for_request)
        else:
            # если драйвер существует обновляем его атрибуты из словаря с данными для запросов
            for k, v in data_for_request.items():
                setattr(driver, k, v)

            driver.get(GOOGLE)
            driver.switch_to.window(driver.window_handles[-1])
    except WebDriverException as e:
        print(e)
    return driver


def main():
    """Основная функция пакета

    Включает в себя основной цикл взаимодействия с пользователем и вызывает необходимые
    функции. Меню находится в бесконечном цикле (если, конечно, не возникнет исключение,
    которое не перехватывается).
    """
    driver = None
    data_for_request = dict()
    selectors_for_links = dict()

    menu_func = {
        '5': set_search_engine,
        '1': set_search_phrase,
        '2': set_website_url,
        '3': set_geo_location,
        '4': set_timer,
    }
    valid = list('123456789q')
    while True:
        main_menu()
        choice = get_string('Пункт меню:', required=True, valid=valid)

        ##########################################################################
        # начать поиск сайта и просмотр его
        ##########################################################################
        if choice == '6':
            try:
                driver = driver_init(driver, data_for_request)
                search_website_and_go(driver=driver, selectors_for_links=selectors_for_links)
            except Exception as e:
                print(e)
            write_visited_links(mode='w')

        ##########################################################################
        # вывести данные для запроса
        ##########################################################################
        elif choice == '7':  # вывести данные для запроса
            try:
                print_data_for_request(data_for_request=data_for_request,
                                       selectors_for_links=selectors_for_links)
            except Exception as e:
                print(e)

        ##########################################################################
        # начать просмотр на последней вкладке. если driver'a нет создаем экземпляр
        ##########################################################################
        elif choice == '9':
            try:
                if driver is None:
                    driver = Google(options=Options(), search_engine=GOOGLE)
                start_links_click(driver=driver, selectors_for_links=selectors_for_links)
            except WebDriverException as e:
                print(e)

            write_visited_links(mode='a')

        ##########################################################################
        # выход из программы
        ##########################################################################
        elif choice == 'q':
            exit_prog(driver=driver)

        ##########################################################################
        # просмотр посещенных ссылок
        ##########################################################################
        elif choice == '8':
            try:
                print_visited_links()
            except Exception as e:
                print(e)

        else:
            try:
                menu_func[choice](data_for_request=data_for_request)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
