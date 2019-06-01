from seo.browser import Browser


class MailRu(Browser):
    xpath_search_field = '//input[@id="q"]'
    search_engine = 'https://mail.ru'
    xpath_for_links_on_search_page = '//li[@class="result__li"]/h3/a'
    css_for_paginator_next = '#js-bottomBar > nav > div > ul > li:last-child > a > svg > g > g'
