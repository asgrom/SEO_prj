import os
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm


class Options(ChromeOptions):
    opt = [
        f'user-data-dir={os.path.join(os.environ["HOME"], ".local/share/seo", "chrome/profile")}',
        'disable-infobars',
        'disable-extensions'
    ]

    def __init__(self, proxy=None):
        super().__init__()

        self.arguments.extend(self.opt)

        if proxy is not None:
            self.arguments.append(f'proxy-server={proxy}')


class Browser(Chrome):
    timer = None
    url = None
    search_engine = None
    phrase = None
    website_url = None

    # todo:
    #       функцию для просмотра сайта рекламы.
    #       подумать может ее отдельно не делать, а совместить с функцией получения ссылок с сайта.
    #       все равно они делают похожую работу.
    #       а для кликов сделать отдельную функцию. что так и будет.

    def __init__(self, options=None, **kwargs):
        super().__init__(options=options)
        self.data_for_request = kwargs

        self.timer = kwargs.get('timer', None)
        self.search_engine = kwargs.get('search_engine', None)
        self.phrase = kwargs.get('phrase', None)
        self.website_url = kwargs.get('website_url', None)
        self.url = kwargs.get('url', None)

        self.visited_pages = list()
        self.implicitly_wait(5)
        # self.get(self.url)

    def page_scrolling(self):
        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 1 / (height / 60 / self.data_for_request['timer'])
        for _ in tqdm(range(int(height / 60)), desc='Прокрутка страницы', unit='click'):
            html.send_keys(Keys.DOWN)
            sleep(t)

    def get_links_from_website(self, css_elems=None, xpath_elems=None):
        """Поиск элементов для кликов"""
        elem_links = None
        try:
            if not css_elems:
                elem_links = self.find_elements_by_xpath(xpath_elems)
            else:
                elem_links = self.find_elements_by_css_selector(css_elems)
        except WebDriverException as e:
            print('ОШИБКА!!!\nПО ЗАДАННОМУ СЕЛЕКТОРУ НИЧЕГО НЕ НАЙДЕНО')
            print(f'CSS-SELECTOR: {css_elems}')
            print(f'XPATH: {xpath_elems}')
            print(e)
        return elem_links

    def window_count(self):
        windows = self.window_handles
        print(windows)
        sleep(10)
        print(self.window_handles)
        print(self.current_window_handle)


if __name__ == '__main__':
    pass
