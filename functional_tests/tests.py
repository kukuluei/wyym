from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

MAX_WAIT = 10  # 最大等待时间


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        real_server = os.environ.get('REAL_SERVER')
        if real_server:
            if real_server.startswith('http://') or real_server.startswith('https://'):
                self.live_server_url = real_server
            else:
                self.live_server_url = 'http://' + real_server


    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        """等待页面上出现指定文本的表格行"""
        start_time = time.time()
        while True:
            try:
                # 显式等待表格出现
                WebDriverWait(self.browser, MAX_WAIT).until(
                    EC.presence_of_element_located((By.ID, "id_list_table"))
                )
                table = self.browser.find_element(By.ID, "id_list_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException, NoSuchElementException) as e:
                if time.time() - start_time > MAX_WAIT:
                    print(f"DEBUG: Current URL when wait_for_row_in_list_table failed: {self.browser.current_url}")
                    print(f"DEBUG: Page source when wait_for_row_in_list_table failed (first 500 chars): {self.browser.page_source[:500]}")
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        inputbox.send_keys('Buy flowers')
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table('1: Buy flowers')

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Make tea')
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table('1: Buy flowers')
        self.wait_for_row_in_list_table('2: Make tea')

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy flowers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy flowers')

        zhangsan_list_url = self.browser.current_url
        self.assertRegex(zhangsan_list_url, '/lists/.+')

        self.browser.quit()
        self.browser = webdriver.Chrome()

        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', page_text)

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        wangwu_list_url = self.browser.current_url
        self.assertRegex(wangwu_list_url, '/lists/.+')
        self.assertNotEqual(wangwu_list_url, zhangsan_list_url)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', page_text)
        self.assertIn('Buy milk', page_text)

    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
