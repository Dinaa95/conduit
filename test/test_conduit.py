from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from login_function import login
from registration_function import registration
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.color import Color
from login_data import registered
from selenium.webdriver.chrome.options import Options
import csv


class TestConduit(object):
    def setup(self):
        browser_options = Options()
        browser_options.headless = True
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)
        URL = "http://localhost:1667/"
        self.browser.get(URL)

    def teardown(self):
        self.browser.quit()

    # test cookies
    def test_check_cookies(self):
        # find elements
        cookie_panel = self.browser.find_element_by_id('cookie-policy-panel')
        decline_cookie_btn = self.browser.find_element_by_xpath('//button/div[contains(text(), "I decline!")]')
        accept_cookie_btn = self.browser.find_element_by_xpath('//button/div[contains(text(), "I accept!")]')
        # assert elements displayed
        assert cookie_panel.is_displayed()
        assert decline_cookie_btn.is_displayed()
        assert accept_cookie_btn.is_displayed()
        # test accept button
        accept_cookie_btn.click()
        # wait until cookie panel disappear
        WebDriverWait(self.browser, 2).until_not(EC.presence_of_element_located((By.ID, 'cookie-policy-panel')))
        # try to find cookie panel again (because of len assert)
        cookie_panel = self.browser.find_elements_by_id('cookie-policy-panel')
        # assert "cookie panel list" len is 0
        assert len(cookie_panel) == 0
        # refresh page
        self.browser.refresh()
        # try to find cookie panel again
        cookie_panel = self.browser.find_elements_by_id('cookie-policy-panel')
        # assert "cookie panel list" len is 0 --> it's not appear on the page after refresh
        assert len(cookie_panel) == 0

    # end of test cookies

    # test registration
    def test_registration(self):
        # register if it's not already registered
        try:
            registration(self)
            time.sleep(4)
            success_msg = self.browser.find_element_by_xpath('//div[text()="Your registration was successful!"]')
            assert success_msg.is_displayed()
        except NoSuchElementException:
            # click OK
            ok_btn = self.browser.find_element_by_xpath('//button[@class="swal-button swal-button--confirm"]')
            ok_btn.click()
            # navigate to register page
            main_register_btn = self.browser.find_element_by_xpath('//a[@href="#/register"]')
            main_register_btn.click()
            # find elements
            username_input = self.browser.find_element_by_xpath('//input[@placeholder="Username"]')
            email_input = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
            password_input = self.browser.find_element_by_xpath('//input[@type="password"]')
            sign_up_btn = self.browser.find_element_by_xpath('//button[contains(text(), "Sign up")]')
            # asserts: the inputs are available
            assert username_input.is_enabled()
            assert email_input.is_enabled()
            assert password_input.is_enabled()
            # fill inputs with data (from login_data)
            username_input.send_keys(registered['username'])
            email_input.send_keys(registered['email'])
            password_input.send_keys(registered['password'])
            # send data
            sign_up_btn.click()
            time.sleep(3)
            # wait for error message
            error_msg = self.browser.find_element_by_xpath('//div[@class="swal-modal"]/div[@class="swal-text"]')
            # assert error message displayed
            assert error_msg.text == 'Email already taken.'

    # end of test registration

    # test login
    def test_login(self):
        # navigate to login page
        main_login_btn = self.browser.find_element_by_xpath('//a[@href="#/login"]')
        main_login_btn.click()
        # find elements
        email_input = self.browser.find_element_by_xpath('//input[@placeholder="Email"]')
        password_input = self.browser.find_element_by_xpath('//input[@type="password"]')
        sign_in_btn = self.browser.find_element_by_xpath('//button[contains(text(), "Sign in")]')
        # assert the inputs are available
        assert email_input.is_enabled()
        assert password_input.is_enabled()
        # fill the inputs with data (from login_data)
        email_input.send_keys(registered['email'])
        password_input.send_keys(registered['password'])
        # send data
        sign_in_btn.click()
        # wait for loading the navbar with name
        time.sleep(1)
        # find navbar
        navbar = self.browser.find_element_by_xpath('//nav')
        # assert profile_name appear on the navbar
        assert registered['username'] in navbar.text
        # assert we got redirected to the main page
        assert self.browser.current_url == 'http://localhost:1667/#/'

    # end of test login

    # test write new article
    def test_new_article(self):
        # run login function
        login(self)
        # navigate to new article page
        main_new_article_btn = self.browser.find_element_by_xpath('//a[@href="#/editor"]')
        main_new_article_btn.click()
        time.sleep(1)
        # find elements
        title = self.browser.find_element_by_xpath('//input[@placeholder="Article Title"]')
        about = self.browser.find_element_by_xpath('//input[@placeholder="What\'s this article about?"]')
        body = self.browser.find_element_by_xpath('//textarea[@placeholder="Write your article (in markdown)"]')
        tags = self.browser.find_element_by_xpath('//input[@class="ti-new-tag-input ti-valid"]')
        submit_btn = self.browser.find_element_by_xpath('//button[@type="submit"]')
        # open file
        with open('test/article_data.txt', 'r', encoding='UTF-8') as article:
            # read line-by-line
            file_content = article.readlines()
        # send keys with specific lines
        title.send_keys(file_content[1].rstrip())
        about.send_keys(file_content[3].rstrip())
        body.send_keys(file_content[5].rstrip())
        tags.send_keys(file_content[7])
        tags.send_keys(file_content[8])
        # submit data
        submit_btn.click()
        time.sleep(1)
        # find elements after write
        article_title = self.browser.find_element_by_css_selector('h1')
        article_author = self.browser.find_element_by_xpath('//a[@class="author"]')
        article_body_text = self.browser.find_element_by_xpath('//div[@class="row article-content"]/div/div[1]/p')
        # asserts: article parts equal to the lines
        assert article_title.text == file_content[1].rstrip()
        assert article_author.text == registered['username']
        assert article_body_text.text == file_content[5].rstrip()
        # empty tag list
        tag_list = []
        tags = self.browser.find_elements_by_xpath('//a[@class="tag-pill tag-default"]')
        # collect tags into a list
        for tag in tags:
            tag_list.append(tag.text)
        # assert tags from article_data were successfully appeared on page
        assert file_content[7].rstrip() and file_content[8].rstrip() in tag_list

    # end of test write new article

    # test edit/modify article
    def test_modify_article(self):
        # run login function
        login(self)
        # navigate to my own profile
        self.browser.get(registered['user_profile_link'])
        time.sleep(1)
        # find the article we want to modify
        article_title = self.browser.find_element_by_xpath('//h1[text()="Just another clickbait article"]')
        # click on article
        article_title.click()
        time.sleep(1)
        edit_btn = self.browser.find_element_by_xpath('//a[@href="#/editor/just-another-clickbait-article"]')
        edit_btn.click()
        time.sleep(1)
        body_input = self.browser.find_element_by_xpath(
            '//textarea[@placeholder="Write your article (in markdown)"]')
        body_input.clear()
        new_article_body = 'I just modified this article. It\'s not about clickbait anymore.'
        body_input.send_keys(new_article_body)
        tags_input = self.browser.find_element_by_xpath('//input[@class="ti-new-tag-input ti-valid"]')
        tags_input.send_keys(Keys.BACKSPACE)
        tags_input.send_keys(Keys.BACKSPACE)
        editor_tags = []
        tags_in_editor = self.browser.find_elements_by_xpath('//li[@class="ti-tag ti-valid"]')
        for tag in tags_in_editor:
            editor_tags.append(tag.text)
        submit_btn = self.browser.find_element_by_xpath('//button[@type="submit"]')
        submit_btn.click()
        time.sleep(1)
        tag_list = []
        tags = self.browser.find_elements_by_xpath('//a[@class="tag-pill tag-default"]')
        # collect tags into a list
        for tag in tags:
            tag_list.append(tag.text)
        article_body_text = self.browser.find_element_by_xpath('//div[@class="row article-content"]/div/div[1]/p')
        assert article_body_text.text == new_article_body
        assert editor_tags == tag_list

    # end of test edit/modify article

    # test delete article
    def test_delete_article(self):
        # run login function
        login(self)
        # navigate to my own profile
        self.browser.get(registered['user_profile_link'])
        time.sleep(1)
        # find the article we want to delete
        article_title = self.browser.find_element_by_xpath('//h1[text()="Just another clickbait article"]')
        # click on article
        article_title.click()
        time.sleep(1)
        # assert delete button displayed
        delete_btn = self.browser.find_element_by_xpath('//button[@class="btn btn-outline-danger btn-sm"]')
        assert delete_btn.is_displayed()
        delete_btn.click()
        time.sleep(4)
        assert self.browser.current_url == 'http://localhost:1667/#/'

    # end of test delete article

    # test collect data from a user's profile
    def test_collect_data(self):
        # run login function
        login(self)
        # navigate to the specific user's profile
        user_profile_link = 'http://localhost:1667/#/@thetester/'
        self.browser.get(user_profile_link)
        time.sleep(1)
        # find elements
        profile_pic_link = self.browser.find_element_by_xpath('//img[@class="user-img"]').get_attribute('src')
        user_name = self.browser.find_element_by_xpath('//div[@class="profile-page"]/div[1]/div/div/div/h4')
        user_bio = self.browser.find_element_by_xpath('//div[@class="profile-page"]/div[1]/div/div/div/p')
        user_article_titles = self.browser.find_elements_by_xpath('//h1')
        # open or create a file, collect data and fill the file with them
        with open('test/collected_data.txt', 'a', encoding='UTF-8') as data_collection:
            # username
            data_collection.write('Current user\'s name: \n' + user_name.text + '\n')
            # picture link
            data_collection.write('Profile picture link: \n' + str(profile_pic_link) + '\n')
            # bio
            data_collection.write('About: \n' + user_bio.text + '\n')
            # articles
            data_collection.write('Articles ' + user_name.text + ' wrote:\n')
            # use for loop to get the article titles
            for title in user_article_titles:
                data_collection.write('- ' + title.text + '\n')
        # open (read only) the created file
        with open('test/collected_data.txt', 'r', encoding='UTF-8') as data_collection:
            # read line-by-line
            collection_content = data_collection.readlines()
        # assert article parts equal to the lines
        assert user_name.text == collection_content[1].rstrip()
        assert str(profile_pic_link) == collection_content[3].rstrip()
        assert user_bio.text == collection_content[5].rstrip()
        assert '- ' + user_article_titles[0].text == collection_content[7].rstrip()

    # end of test collect data from a user's profile

    # create a list out of titles from the main page
    def test_new_list(self):
        # run login function
        login(self)
        # empty list for the article titles
        article_title_list = []
        # find elements
        main_article_title = self.browser.find_elements_by_xpath('//h1')
        conduit_main_text = self.browser.find_element_by_xpath('//h1[@class="logo-font"]')
        # get every title with for loop
        for title in main_article_title:
            # exception: conduit logo is not a title
            if title.text != conduit_main_text.text:
                article_title_list.append(title.text)
        # assert both list contains the same number of elements (-1 because of 'conduit')
        assert len(main_article_title) - 1 == len(article_title_list)

    # end of create list

    # test paginator (go to next page)
    def test_next_page(self):
        # run login function
        login(self)
        # find elements
        first_page = self.browser.find_element_by_xpath('//li[@data-test="page-link-1"]')
        second_page = self.browser.find_element_by_xpath('//li[@data-test="page-link-2"]')
        second_page_link = self.browser.find_element_by_xpath('//li[@data-test="page-link-2"]/a')
        # scroll at the bottom of the page
        page_html = self.browser.find_element_by_xpath('//html')
        page_html.send_keys(Keys.END)
        # assert #1 page is the active page
        assert first_page.get_attribute('class') == 'page-item active'
        time.sleep(1)
        # click on page #2
        second_page_link.click()
        # assert #2 page is the active page, and get the right background color
        second_page_get_color = second_page_link.value_of_css_property('background-color')
        second_page_hex_color = Color.from_string(second_page_get_color).hex
        assert second_page.get_attribute('class') == 'page-item active'
        assert second_page_hex_color == '#5cb85c'

    # end of test paginator

    # test write comments constantly
    def test_write_comment(self):
        # run login function
        login(self)
        # find the first article from main page
        first_article = self.browser.find_element_by_xpath('//div[@class="article-preview"][1]')
        # click on article
        first_article.click()
        time.sleep(1)
        # assert comment form is displayed
        comment_form = self.browser.find_element_by_xpath('//form[@class="card comment-form"]')
        assert comment_form.is_displayed()
        # assert we can write a comment
        comment_textarea = self.browser.find_element_by_xpath('//textarea[@placeholder="Write a comment..."]')
        assert comment_textarea.is_enabled()
        # find post comment button
        send_btn = self.browser.find_element_by_xpath(
            '//button[@class="btn btn-sm btn-primary"][text()="Post Comment"]')
        # writing comments from csv file
        with open('test/comments.csv', 'r', encoding='UTF-8') as comments:
            comment_table = csv.reader(comments)
            for row in comment_table:
                comment_textarea.send_keys(row)
                send_btn.click()
                time.sleep(1)
        # find comments for assert and create a list
        written_comments = self.browser.find_elements_by_xpath('//p[@class="card-text"]')
        written_comment_list = []
        for comment in written_comments:
            written_comment_list.append(comment.text)
        # open csv again and assert if the rows are on the list
        with open('test/comments.csv', 'r', encoding='UTF-8') as comments:
            comment_table = csv.reader(comments)
            for row in comment_table:
                assert row[0] in written_comment_list

    # end of test write comments constantly

    # test logout function
    def test_logout(self):
        # find navbar
        navbar = self.browser.find_element_by_xpath('//nav')
        # assert there is no logout button (text) on navbar
        assert 'Log out' not in navbar.text
        # run login function
        login(self)
        # assert Logout button displayed
        assert 'Log out' in navbar.text
        # find logout button
        log_out_link = self.browser.find_element_by_xpath('//a[contains(text(), "Log out")]')
        # click on logout button
        log_out_link.click()
        # assert there is no logout button (text) on navbar after logout
        assert 'Log out' not in navbar.text
    # end of test logout function
