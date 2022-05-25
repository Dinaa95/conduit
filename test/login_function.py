import time
from login_data import registered


def login(self):
    main_login_btn = self.browser.find_element_by_xpath('//a[@href="#/login"]')
    main_login_btn.click()
    email_input = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
    password_input = self.browser.find_element_by_xpath('//input[@type="password"]')
    sign_in_btn = self.browser.find_element_by_xpath('//button[contains(text(), "Sign in")]')
    email_input.send_keys(registered['email'])
    password_input.send_keys(registered['password'])
    sign_in_btn.click()
    time.sleep(1)

