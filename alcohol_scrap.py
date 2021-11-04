from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from random import randint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.sulmin  # sulmin db -> alcohols table

# 맥주, 사케, 캌테일, 와인 url
url_list = [
    'https://terms.naver.com/list.naver?cid=42726&categoryId=42726&so=date.dsc&viewType=&categoryType=',
    'https://terms.naver.com/list.naver?cid=42726&categoryId=42746',
    'https://terms.naver.com/list.naver?cid=42726&categoryId=59595',
    'https://terms.naver.com/list.naver?cid=42726&categoryId=60017',
]

driver = webdriver.Chrome('./chromedriver')

# 술 종류별 html 페이지 소스 저장
reqs = []

for url in url_list:
    driver.get(url)  # 드라이버에 해당 url 의 웹페이지를 띄웁니다.
    sleep(5)  # 페이지가 로딩되는 동안 5초 간 기다립니다.
    reqs.append(driver.page_source)  # html 정보를 가져옵니다.
driver.quit()  # 정보를 가져왔으므로 드라이버는 꺼줍니다.

category = ['와인', '칵테일', '맥주', '사케']
i = 0  # 종류 판별 인덱스

for req in reqs:
    soup = BeautifulSoup(req, 'html.parser')
    alcohols = soup.select("#content > div.list_wrap > ul > li") # 종류별 술 리스트
    for alcohol in alcohols:
        name = alcohol.select_one('div.info_area > div.subject > strong > a').text
        desc = alcohol.select_one('div.info_area > p').text.strip()
        if alcohol.select_one('div.thumb_area > div.thumb > a > img') is not None:
            image = alcohol.select_one("div.thumb_area > div.thumb > a > img")['src']
            doc = {
                'cat': category[i],
                'name': name,
                'image': image,
                'desc': desc,
                'reviews': randint(1, 100)
            }
            db.alcohols.insert_one(doc)
    i += 1
