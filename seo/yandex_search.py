from selenium.webdriver.common.keys import Keys

from .browser import Browser


class Yandex(Browser):
    xpath_search_field = '//input[@name="text"]'

    # xpath для поиска ссылок на странице выдачи
    xpath_for_links_on_search_page = (
        '//li//div[contains(@class,"typo_type_greenurl") and not(div[contains(@class,"label")])]'
        '/div[contains(@class, "path")]/a[1]')

    xpath_for_paginator_next = '//div[contains(@class, "pager")]/a[contains(text(),"дальше")]'

    def change_browser_location(self):
        self.get(self.search_engine)
        geo_link = self.find_element_by_xpath('//a[contains(@class, "geolink")]')
        geo_link.click()
        geo_input = self.find_element_by_xpath('//input[@name="name"]')
        geo_input.click()
        geo_input.clear()
        geo_input.send_keys(self.geo_location)
        geo_input.send_keys(Keys.RETURN)
