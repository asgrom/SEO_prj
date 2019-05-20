import os
import re
from time import sleep

from blinker import signal
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm


class ErrorExcept(Exception):
    pass


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
    xpath_for_links_on_search_page = None
    xpath_for_paginator_next = None
    xpath_search_field = None
    search_engine = None

    scroll_signal = signal('scroll')
    scroll_end = signal('scroll-end')

    def __init__(self, options=None, **kwargs):
        super().__init__(options=options)

        self.timer = kwargs.get('timer', None)
        self.phrase = kwargs.get('phrase', None)
        self.website_url = kwargs.get('website_url', None)
        self.geo_location = kwargs.get('geo_location', None)

        self.implicitly_wait(5)
        self.get(self.search_engine)

    def find_website_link(self):
        """Поиск ссылки на искомый сайт на странице выдачи поиска

        :return: ссылка на искомый сайт
        """
        search_field = self.find_element_by_xpath(self.xpath_search_field)
        search_field.clear()
        search_field.send_keys(self.phrase)
        search_field.send_keys(Keys.RETURN)

        found_website_link = self.find_link_in_search_result()

        return found_website_link

    def page_scrolling_with_urwid_progress_bar(self, timer):
        """Прокрутка страницы"""
        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 1 / (height / 60 / timer)
        for _ in range(int(height / 60)):
            html.send_keys(Keys.DOWN)
            self.scroll_signal.send('scroll', done=int(height / 60))
            sleep(t)
        self.scroll_end.send(self)

    def page_scrolling(self, timer):
        """Прокрутка страницы"""
        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 1 / (height / 60 / timer)
        for _ in tqdm(range(int(height / 60)), desc='Прокрутка страницы', unit='click'):
            html.send_keys(Keys.DOWN)
            sleep(t)

    def get_links_from_website(self, css_elems=None, xpath_elems=None):
        """Поиск элементов для кликов на странице сайта

        :return: список элементов, содержащих ссылку для клика
        """
        elem_links = None
        try:
            if not css_elems:
                elem_links = self.find_elements_by_xpath(xpath_elems)
            else:
                elem_links = self.find_elements_by_css_selector(css_elems)
            return elem_links
        except WebDriverException as e:
            raise ErrorExcept('ОШИБКА!!!\nПО ЗАДАННОМУ СЕЛЕКТОРУ НИЧЕГО НЕ НАЙДЕНО')

    def find_link_in_search_result(self):
        """
        Рекурсивный поиск ссылки на искомый сайт на странице выдачи

        :return: ссылку на искомый сайт
        """

        try:
            # поиск всех ссылок на странице выдачи
            found_links = self.find_elements_by_xpath(self.xpath_for_links_on_search_page)
        except WebDriverException:
            raise ErrorExcept('ОШИБКА ПОИСКА ССЫЛОК В ВЫДАЧЕ')

        for link in found_links:
            # if re.search(self.website_url, link.get_attribute('href')):
            if re.search(self.website_url, link.find_element_by_xpath('./b').text, flags=re.IGNORECASE):
                return link

        try:
            # поиск в пагинаторе кнопки "Следующая"
            paginator_next = self.find_element_by_xpath(self.xpath_for_paginator_next)
            paginator_next.click()
        except WebDriverException:
            # raise ErrorExcept('ДОСТИГЛИ КОНЦА ПОИСКА')
            return None

        return self.find_link_in_search_result()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


if __name__ == '__main__':
    pass
