import unittest
import selenium
from urllib.request import urlopen
import hashlib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec


class Test1(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("https://yandex.ru/")

    def tearDown(self):
        self.driver.quit()

    def find_input_field(self):
        try:
            wait = WebDriverWait(self.driver, 40)
            wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "input__input")))
            self.element = self.driver.find_element(By.CLASS_NAME, "input__input")
        except selenium.common.exceptions.NoSuchElementException or selenium.common.exceptions.TimeoutException:
            self.fail("Поле поиска не найдено")

    def fill_input_field(self):
        self.element.send_keys("тензор")

    def suggest_table(self):
        try:
            wait = WebDriverWait(self.driver, 40)
            wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "mini-suggest__popup-content")))
            self.element = self.driver.find_element(By.CLASS_NAME, "mini-suggest__popup-content")
        except selenium.common.exceptions.NoSuchElementException or selenium.common.exceptions.TimeoutException:
            self.fail("Таблица с подсказками не найдена")

    def results_table(self):
        ActionChains(self.driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
        try:
            wait = WebDriverWait(self.driver, 40)
            wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "serp-list")))
            self.element = self.driver.find_element(By.CLASS_NAME, "serp-list")
        except selenium.common.exceptions.NoSuchElementException:
            self.fail("Таблица с результатами не найдена")

    def first_links_from_table(self):
        elements = self.element.find_elements(By.CLASS_NAME, "serp-item")
        links = [i.find_element(By.CLASS_NAME, "Link").get_attribute('href') for i in elements[:5]]
        wrong_links = Test1.check_links(links)
        if wrong_links != 0:
            self.fail(f"Из первых пяти результатов - {wrong_links} ведут не на 'tensor.ru'")

    @staticmethod
    def check_links(links):
        count = 0
        for i in links:
            print(f"{links.index(i) + 1}. Результат{' не' if 'tensor.ru' not in i else ''} включает 'tensor.ru'")
            if 'tensor.ru' not in i:
                count += 1
        return count

    def test1_task1(self):
        self.find_input_field()
        self.fill_input_field()
        self.suggest_table()
        self.results_table()
        self.first_links_from_table()


class Test2(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("https://yandex.ru/")

    def tearDown(self):
        self.driver.quit()

    def image_existing(self):
        try:
            serv_list = self.driver.find_element(By.CLASS_NAME, "services-new__list")
            self.element = serv_list.find_element(By.CSS_SELECTOR, '[data-id="images"]')
        except selenium.common.exceptions.NoSuchElementException:
            self.fail("Ссылка «Картинки» не присутствует на странице")

    def image_click(self):
        self.element.click()

    def check_new_page(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        url = self.driver.current_url
        if "https://yandex.ru/images/" not in url:
            self.fail("Переход на новую страницу не произошел")

    def first_category(self):
        try:
            element = self.driver.find_element(By.CLASS_NAME, "PopularRequestList-Item_pos_0")
            category_text = element.get_attribute("data-grid-text")
        except selenium.common.exceptions.NoSuchElementException:
            self.fail("Элемент не найден")
        element.click()
        element = self.driver.find_element(By.CLASS_NAME, "input__control")

        self.assertEqual(element.get_attribute('value'), category_text)

        wait = WebDriverWait(self.driver, 40)
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "serp-item_pos_0")))

    def image_click2(self):
        element = self.driver.find_element(By.CLASS_NAME, "serp-item_pos_0")
        element.click()
        try:
            wait = WebDriverWait(self.driver, 40)
            wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "MMImageContainer")))
        except selenium.common.exceptions.TimeoutException:
            self.fail("Картинка не загрузилась")
        element_url = self.driver.find_element(By.CLASS_NAME, "MMImage-Origin").get_attribute('src')
        self.image_hash = hashlib.md5(urlopen(element_url).read()).hexdigest()

    def next_image(self):
        element = self.driver.find_element(By.CLASS_NAME, "CircleButton_type_next")
        element.click()
        wait = WebDriverWait(self.driver, 40)
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "serp-item_pos_0")))

    def prev_image(self):
        element = self.driver.find_element(By.CLASS_NAME, "CircleButton_type_prev")
        element.click()
        element_url = self.driver.find_element(By.CLASS_NAME, "MMImage-Origin").get_attribute('src')
        image_hash = hashlib.md5(urlopen(element_url).read()).hexdigest()
        if image_hash != self.image_hash:
            self.fail("Несовпадение картинок при нажатии кнопки 'назад'")

    def test1_task2(self):
        self.image_existing()
        self.image_click()
        self.check_new_page()
        self.first_category()
        self.image_click2()
        self.next_image()
        self.prev_image()


if __name__ == '__main__':
    unittest.main()