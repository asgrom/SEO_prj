from .browser import Browser


class Google(Browser):
    xpath_search_field = '//input[@name="q"]'

    # xpath для поиска ссылок на странице выдачи
    xpath_for_links_on_search_page = '//div[@class="g"]//div[@class="r"]/a[1]'

    xpath_for_paginator_next = '//table[@id="nav"]//a[@class="pn" and *[contains(text(),"ледующая")]]'

    search_engine = 'https://google.ru'
