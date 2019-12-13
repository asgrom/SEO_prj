import re
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

from seo import BlinkerSignals
from seo import Chrome_dir
from . import GOOGLE, YANDEX, Signals, MAILRU

signals = Signals()


class ErrorExcept(Exception):
    pass


class Options(ChromeOptions):
    opt = [
        f'user-data-dir={Chrome_dir}',
        'disable-infobars',
        'disable-extensions'
    ]

    def __init__(self, proxy=None):
        super().__init__()

        self.arguments.extend(self.opt)
        self.add_experimental_option("excludeSwitches", ['enable-automation'])

        if proxy is not None:
            self.arguments.append(f'proxy-server={proxy}')


class Browser(Chrome):
    # атрибуты определяются в дочерних классах
    xpath_for_links_on_search_page = None
    xpath_for_paginator_next = None
    xpath_search_field = None
    search_engine = None

    # css селектор для кнопки следущей страницы в поисковике mail.ru
    css_for_paginator_next = None

    def __init__(self, options=None, **kwargs):
        super().__init__(options=options)

        self.phrase = kwargs.get('phrase', None)
        self.website_url = kwargs.get('website_url', None)
        self.geo_location = kwargs.get('geo_location', None)

        self.implicitly_wait(5)
        self.get(self.search_engine)

    def find_website_link(self):
        """Поиск ссылки на искомый сайт на странице выдачи поиска"""

        try:
            search_field = self.find_element_by_xpath(self.xpath_search_field)
        except WebDriverException as e:
            raise ErrorExcept(f'ОШИБКА ПОИСКА ССЫЛКИ НА САЙТ \n{e}')
        search_field.clear()
        search_field.send_keys(self.phrase)
        search_field.send_keys(Keys.RETURN)
        self.switch_to.window(self.window_handles[-1])
        return self.find_link_in_search_result()

    def page_scrolling_with_urwid_progress_bar(self, timer):
        """Прокрутка страницы"""

        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 40 * timer / height
        # t = 1 / (height / 40 / timer)
        for i in range(int(height / 40)):
            html.send_keys(Keys.DOWN)
            Signals.scroll.send('scroll', done=int(height / 40))
            sleep(t)
        signals.end.send(self)

    def page_scrolling(self, timer):
        """Прокрутка страницы"""

        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 1 / (height / 60 / timer)
        for i in tqdm(range(int(height / 60)), desc='Прокрутка страницы', unit='click'):
            html.send_keys(Keys.DOWN)
            sleep(t)

    def qt_page_scrolling(self, timer):
        """Прокрутка страницы для Qt"""
        height = self.execute_script('return document.body.scrollHeight;')
        html = self.find_element_by_tag_name('html')
        t = 1 / (height / 40 / timer)
        BlinkerSignals.max_scrolling.send(value=int(height / 40))
        for i in range(int(height / 40)):
            html.send_keys(Keys.DOWN)
            sleep(t)
            BlinkerSignals.progress.send(value=i + 1)
        BlinkerSignals.progress.send(value=0)

    def get_links_from_website(self, css_elems=None, xpath_elems=None):
        """Поиск элементов для кликов на странице сайта

        :return: список элементов, содержащих ссылку для клика
        """
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

        :return: ссылку на искомый сайт"""

        try:
            # поиск всех ссылок на странице выдачи
            found_links = self.find_elements_by_xpath(self.xpath_for_links_on_search_page)
        except WebDriverException:
            raise ErrorExcept('ОШИБКА ПОИСКА ССЫЛОК В ВЫДАЧЕ')

        for link in found_links:
            if self.search_engine == YANDEX:
                if re.search(self.website_url,
                             link.find_element_by_xpath('./b').text,
                             flags=re.IGNORECASE):
                    return link

            elif self.search_engine == GOOGLE:
                if re.search(self.website_url,
                             link.find_element_by_xpath('.//cite').text,
                             flags=re.IGNORECASE):
                    return link

            elif self.search_engine == MAILRU:
                if re.search(self.website_url,
                             link.find_element_by_xpath('../../div[@class="block-info-serp"]/span').text,
                             flags=re.IGNORECASE):
                    return link

        try:
            # поиск в пагинаторе кнопки "Следующая"
            if self.search_engine == MAILRU:
                paginator_next = self.find_element_by_css_selector(self.css_for_paginator_next)
                paginator_next.click()
            else:
                paginator_next = self.find_element_by_xpath(self.xpath_for_paginator_next)
                paginator_next.click()
        except WebDriverException as e:
            raise ErrorExcept(f'ДОСТИГЛИ КОНЦА ПОИСКА\n{e}')

        return self.find_link_in_search_result()


if __name__ == '__main__':
    pass
