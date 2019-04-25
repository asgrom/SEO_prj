from .browser import Options
from .yandex_search import Yandex
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

visited_links = list()


def get_string(msg, required=None):
    """Получение и валидация ввода запрошенной строки"""
    msg = msg + '\n  >>>  '
    while True:
        line = input(msg)
        if not line:
            if not required:
                return ''
            else:
                print('Обязательный параметр!')
        else:
            return line


def get_integer(msg, required=None):
    """Получение и валидация запрошенной цифровой строки"""
    msg += '\n  >>>  '
    while True:
        line = input(msg)
        if not line:
            if not required:
                return ''
            else:
                print('Обязательный параметр!')
        elif not line.isdigit():
            print('Ввести только цифры!')
        else:
            return int(line)


def set_selectors_for_website_links():
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


def search_website_and_go(drv):
    """Поиск сайта и переход на него

    Если ссылка на сайт найдена, переходим на него и делаем вкладку с ним активной.
    Прежде чем перейти на сайт, выводится сообщение и происходит задерка. Это надо для того,
    если по условию задания надо посетить другие сайто до найденого.
    """
    link = drv.search_website_link()
    if link is not None:
        # притормозим просмотр. вдруг по условиям надо просмотреть другие сайты
        input('ССЫЛКА НА САЙТ НАЙДЕНА\nПРОДОЛЖИТЬ? >>> ')
        # drv.execute_script(f"arguments[0].scrollIntoView(true);", link)

        # прокрутка страницы на начало
        # drv.execute_script('scrollTo(0,0);')
        link.send_keys(Keys.HOME)

        # перейти к искомому элементу
        ActionChains(drv).move_to_element(link).click(link).perform()

        # сделать новую вкладку активной
        drv.switch_to.window(drv.window_handles[-1])

    return


# todo: page_css_selector
#       сделать так, чтобы клик на страницу, на которой будем искать элементы ссылок,
#       происходил до того, как вводится селектор ссылок.
def main():
    drv = Yandex(options=Options(), url='http://testsite.alex.org',
                 search_engine=YANDEX, phrase='lamoda', website_url='lamoda.ru')

    search_website_and_go(drv)
    # print(links)
    # links.click()
    # drv.window_count()
    # drv.find_element_by_css_selector(
    #     get_string('CSS-селектор страницы на которой будем искать', required=True)).click()
    # selectors_for_elems = set_selectors_for_website_links()
    # elem_links = drv.get_links_from_website(
    #     css_elems=selectors_for_elems['css_elems'],
    #     xpath_elems=selectors_for_elems['xpath_elems']
    # )
    # drv.get_screenshot_as_file('screenshot')
    # print(elem_links)
    input()
    drv.close()


if __name__ == '__main__':
    main()
