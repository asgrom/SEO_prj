from .browser import Options, Browser
from selenium.webdriver.common.keys import Keys


class Google(Browser):

    def search_website(self):
        self.get(self.requests['search_engine'])

        search_field = self.find_element_by_xpath('//input[@name="q"]')
        search_field.send_keys(self.requests['phrase'])
        search_field.send_keys(Keys.ENTER)
