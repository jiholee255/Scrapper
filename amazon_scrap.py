import re
import time,sys
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import rake_nltk

driver = webdriver.Chrome('')
EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
# review_num = int((int(str(driver.find_element_by_xpath('//*[@id="filter-info-section"]/span[1]').text).split('of ')[1].split(' ')[0].replace(',',''))/10+1))
conn = pymysql.connect(host='host', user='user', password='pwd', db='db', charset='utf8')
curs = conn.cursor()
sql = "insert into table(product_name,review_star,review_date,review_head,review_body,review_raw_body) values (%s,%s,%s,%s,%s,%s)"
# print(review_num)
pg_lst = [['https://www.amazon.com/Echo-Show-8/product-reviews/B07PF1Y28C/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8','Echo show'],
['https://www.amazon.com/Echo-Dot-3rd-Gen-Sandstone/product-reviews/B07PGL2N7J/ref=cm_cr_othr_d_show_all_btm?ie=UTF8','Echo dot'],
['https://www.amazon.com/Nuevo-Echo-3%C2%AA-generaci%C3%B3n-inteligente/product-reviews/B07NFTVP7P/ref=cm_cr_dp_d_show_all_btm?ie=UTF8','Echo']]
for page,prod_name in pg_lst:
    for page_num in range(1,501):
        url= f'{page}&reviewerType=all_reviews&formatType=current_format&sortBy=recent&pageNumber={page_num}'
        driver.get(url)
        try:
            bs = BeautifulSoup(driver.page_source, 'lxml')
            prod_lst = []
            star_lst = []
            date_lst = []
            head_lst = []
            body_lst = []
            raw_lst = []
            try:
                for dt in bs.findAll('span',class_='a-icon-alt'):
                    prod_lst.append(prod_name)
                    star_lst.append(str(EMOJI.sub(r'',dt.text)).replace('\n',' ').strip())
                for dt in bs.findAll('span',class_='a-size-base a-color-secondary review-date'):
                    date_lst.append(str(EMOJI.sub(r'',dt.text)).replace('\n',' ').strip())
                for dt in bs.findAll('a',class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold'):
                    head_lst.append(str(EMOJI.sub(r'',dt.text)).replace('\n',' ').strip())
                for dt in bs.findAll('span',class_='a-size-base review-text review-text-content'):
                    raw_lst.append(str(EMOJI.sub(r'',dt.text)))
                    body_lst.append(str(EMOJI.sub(r'',dt.text)).replace('\n',' ').strip())
            except Exception as e:
                print("error: "+str(e)+"\n where: "+str(page_num))
                pass
            input_lst = list(zip(prod_lst,star_lst,date_lst,head_lst,body_lst,raw_lst))
            curs.executemany(sql,input_lst)
            conn.commit()
        except Exception as e:
            print("error: "+str(e)+"\n where: "+str(page_num))
            pass