from .browser import Browser
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import re


class Google(Browser):
    xpath_for_links_on_search_page = '//div[@class="g"]//div[@class="r"]/a'
    xpath_for_paginator_next = '//table[@id="nav"]//a[@class="pn" and *[contains(text(),"ледующая")]]'

    def search_website_link(self):
        self.get(self.data_for_request['search_engine'])

        search_field = self.find_element_by_xpath('//input[@name="q"]')
        search_field.clear()
        search_field.send_keys(self.phrase)
        search_field.send_keys(Keys.ENTER)

        return self._find_link_in_search_result()

    def _find_link_in_search_result(self):

        try:
            # поиск всех ссылок на странице выдачи
            found_links = self.find_elements_by_xpath(
                self.xpath_for_links_on_search_page)
        except WebDriverException:
            print('ОШИБКА ПОИСКА ССЫЛОК В ВЫДАЧЕ')

        for link in found_links:
            if re.search(self.website_url, link.get_attribute('href')):
                return link

        try:
            # поиск в пагинаторе кнопки "Следующая"
            paginator_next = self.find_element_by_xpath(self.xpath_for_paginator_next)
            paginator_next.click()
        except WebDriverException:
            print('ДОСТИГЛИ КОНЦА ПОИСКА')
            return None

        return self._find_link_in_search_result()
