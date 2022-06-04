import time
from login_data import registered


def registration(self):
    main_register_btn = self.browser.find_element_by_xpath('//a[@href="#/register"]')
    main_register_btn.click()
    username_input = self.browser.find_element_by_xpath('//input[@placeholder="Username"]')
    email_input = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
    password_input = self.browser.find_element_by_xpath('//input[@type="password"]')
    sign_up_btn = self.browser.find_element_by_xpath('//button[contains(text(), "Sign up")]')
    username_input.send_keys(registered['username'])
    email_input.send_keys(registered['email'])
    password_input.send_keys(registered['password'])
    sign_up_btn.click()
