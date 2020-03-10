import requests
from bs4 import BeautifulSoup
from itertools import islice
# from selenium import webdriver
# from time import sleep
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException
# import os

# CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
# GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome')


def get_vacancy_list(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('li', class_='l-vacancy')
    article_links = [(article.find('a', class_='vt').text,
                      article.find('a', class_='company').text,
                      article.find('a', class_='vt').get('href')) for article in articles]
    return article_links


def get_artickle_list(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('h2', class_='title')
    article_links = [(article.find('a').get('href'), article.text) for article in articles]
    article_links.reverse()
    # article_links = list(islice(article_links, 5))
    return article_links


# def get_vacancy_list(url):
#     options = Options()
#     options.binary_location = GOOGLE_CHROME_BIN
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     options.headless = True
#     driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=options)
#     driver.get(url)
#     for i in range(2):
#         try:
#             more_btn = driver.find_element_by_xpath("//*[@id='vacancyListId']/div/a")
#             more_btn.click()
#             sleep(0.25)
#         except Exception:
#             pass
#     try:
#         vacancy_list = driver.find_elements_by_class_name("vt")
#     except NoSuchElementException:
#         vacancy_list = []
#     links = [item.get_attribute('href') for item in vacancy_list]
#     driver.close()
#     return links


