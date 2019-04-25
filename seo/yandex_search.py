from .browser import Browser


class Yandex(Browser):
    xpath_search_field = '//input[@name="text"]'
    xpath_for_links_on_search_page = (
        '//li//div[contains(@class,"typo_type_greenurl") and not(div[contains(@class,"label")])]'
        '/div[contains(@class, "path")]/a[1]'
    )
    xpath_for_paginator_next = '//div[contains(@class, "pager")]/a[contains(text(),"дальше")]'
