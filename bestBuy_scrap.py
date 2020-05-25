import re
import time,sys
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import rake_nltk


url='https://www.bestbuy.com/site/reviews/apple-homepod-space-gray/5902410?variant=A'
driver = webdriver.Chrome('')
driver.get(url)
review_num = int((int(str(driver.find_element_by_css_selector('#reviews-accordion > div.row.ugc-reviews.clearfix > div > div > div > div.reviews-pagination.col-xs-4.col-lg-3').text).split('of ')[1].split(' ')[0].replace(',',''))/20+1))
conn = pymysql.connect(host='host', user='user', password='pwd', db='db', charset='utf8', )
curs = conn.cursor()
sql = "insert into db_name(prod_name,review_head,review_body) values (%s,%s,%s)"
for page_num in range(1,review_num+1):
    try:
        if page_num>1:
            url= f'https://www.bestbuy.com/site/reviews/apple-homepod-space-gray/5902410?variant=A&page={page_num}'
            driver.get(url)
        for bt in driver.find_elements_by_class_name('btn btn-link v-medium btn-trailing-ficon read-more-button'):
            bt.click()
    except Exception as e:
        print("read more button is not existed")
        pass
    try:
        bs = BeautifulSoup(driver.page_source, 'lxml')
        prod_lst = []
        head_lst = []
        body_lst = []
        try:
            for dt in bs.findAll('p',class_='pre-white-space'):
                prod_lst.append('Apple homePod')
                body_lst.append(str(dt.text).replace('\n',' ').strip())
            for dt in bs.findAll('h4',class_='review-title c-section-title heading-5 v-fw-medium'):
                head_lst.append(str(dt.text).replace('\n',' ').strip())
        except:
            print("Maybe end."+ str(page_num))
            break
        input_lst = list(zip(prod_lst,head_lst,body_lst))
        curs.executemany(sql,input_lst)
        conn.commit()
    except Exception as e:
        print("error: "+e+"\n where: "+str(page_num))
        pass