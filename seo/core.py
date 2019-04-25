from .browser import Browser, Options
from .google_search import Google

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


# todo: page_css_selector
#       сделать так, чтобы клик на страницу, на которой будем искать элементы ссылок,
#       происходил до того, как вводится селектор ссылок.
def main():
    drv = Google(options=Options(), url='http://testsite.alex.org',
                 search_engine=GOOGLE, phrase='mazafaka', website_url='wiki.prankru.net')
    links = drv.search_website_link()
    print(links)
    links.click()
    drv.window_count()
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
