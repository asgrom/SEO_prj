from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
from .browser import Browser


class Yandex(Browser):
    xpath_search_field = '//input[@name="text"]'

    # xpath для поиска ссылок на странице выдачи
    # xpath_for_links_on_search_page = (
    #     '//li//div[contains(@class,"typo_type_greenurl") and not(div[contains(@class,"label")])]'
    #     '/div[contains(@class, "path")]/a[1]')
    # xpath_for_links_on_search_page = "//li[count(@*)<=5]//div[contains(@class, 'organic ')]"
    # xpath_for_links_on_search_page = "//li[count(@*)<=4]/div/div[1]/div[1]/a[1]"
    xpath_for_links_on_search_page = "//li[count(@*)<=5]/div[contains(@class, 'organic')]"

    xpath_for_paginator_next = '//div[contains(@class, "pager")]/a[contains(text(),"дальше")]'

    search_engine = 'https://yandex.ru'

    def change_browser_location(self):
        """
        Если в чекбоксе 'Автоматическое местоположение' невозможно сменить город.
        """
        # self.get(self.search_engine)
        geo = self.find_element_by_xpath("//div[contains(@class,'dropdown2')]//a[@role='button']")
        actChains = ActionChains(self)
        actChains.move_to_element(geo)
        actChains.click(geo)
        actChains.perform()
        time.sleep(1)
        button = self.find_element_by_xpath("//a[span[text()='Изменить город']]")
        # button.click()
        actChains = ActionChains(self)
        actChains.move_to_element(button)
        actChains.click(button)
        actChains.perform()

        # geo_link = self.find_element_by_xpath('//a[contains(@class, "geolink")]')
        # geo_link.click()

        # снятие выбора в чекбоксе автоматического определения местоположения
        chkbox = self.find_element_by_xpath('//input[@class="checkbox__control"]')
        if chkbox.is_selected():
            chkbox.click()

        time.sleep(1)

        geo_input = self.find_element_by_xpath('//input[@name="name"]')
        geo_input.click()
        geo_input.clear()
        geo_input.send_keys(self.geo_location)
        time.sleep(1)
        geo_input.send_keys(Keys.RETURN)
        geo_input.send_keys(Keys.RETURN)
