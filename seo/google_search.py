from .browser import Browser
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import re


class Google(Browser):
    xpath_search_field = '//input[@name="q"]'
    xpath_for_links_on_search_page = '//div[@class="g"]//div[@class="r"]/a'
    xpath_for_paginator_next = '//table[@id="nav"]//a[@class="pn" and *[contains(text(),"ледующая")]]'
