#!/usr/bin/env python3
# --*-- coding:utf-8 --*--
# __Author__ Aaron


from lxml import etree
from selenium import webdriver
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import csv


class LagouSpider(object):
    driver_path = r'/home/pwp/PycharmProjects/chromedriver'

    def __init__(self, writer):
        self.driver = webdriver.Chrome(executable_path=LagouSpider.driver_path)
        self.url = r'https://www.lagou.com/jobs/list_python%E7%88%AC%E8%99%AB?px=default&city=%E6%B7%B1%E5%9C%B3#filterBox'
        self.positions = []
        self.writer = writer

    def run(self):
        self.driver.get(self.url)
        while True:
            source = self.driver.page_source
            # print(source)
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="pager_container"]/span[last()]')))
            self.request_list_page(source)
            try:
                next_bit = self.driver.find_element_by_xpath('//div[@class="pager_container"]/span[last()]')
                if "pager_next pager_next_disabled" in next_bit.get_attribute('class'):
                    break
                else:
                    next_bit.click()
            except:
                print(source)

            time.sleep(1)

    def request_list_page(self, souce):
        html = etree.HTML(souce)
        links = html.xpath('//a[@class="position_link"]/@href')
        for link in links:
            # print(link)
            self.request_detail_page(link)
            time.sleep(1)

    def request_detail_page(self, url):
        # self.driver.get(url)
        self.driver.execute_script("window.open('%s')" % url)  # 错误写法"window.open(%s)"%url
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@class="name"]'))
        )

        source = self.driver.page_source
        self.pares_detail_page(source)

        # 关闭当前这个详情页
        self.driver.close()
        # 切换回职位列表页
        self.driver.switch_to.window(self.driver.window_handles[0])

    def pares_detail_page(self, source):
        html = etree.HTML(source)
        position_name = html.xpath('//span[@class="name"]/text()')[0]
        job_request_spans = html.xpath('//dd[@class="job_request"]/p/span')
        salary = job_request_spans[0].xpath("./text()")[0].strip()
        city = job_request_spans[1].xpath("./text()")[0].strip()
        city = re.sub('[\s/]', "", city)
        work_years = job_request_spans[2].xpath("./text()")[0].strip()
        work_years = re.sub('[\s/]', "", work_years)
        education = job_request_spans[3].xpath("./text()")[0].strip()
        education = re.sub('[\s/]', "", education)
        desc = "".join(html.xpath('//dd[@class="job_bt"]//text()')).strip()
        desc = re.sub('\n', '', desc)
        company_name = "".join(html.xpath('//em[@class="fl-cn"]/text()')).strip()

        # 以csv文件的方式保存数据
        self.writer.writerow((position_name, company_name, city, work_years, education, desc))
        # 普通方式查看
        position = {
            'name': position_name,
            'company_name': company_name,
            'city': city,
            'work_years': work_years,
            'education': education,
            'desc': desc
        }

        self.positions.append(position)

        print(position)
        print('=' * 82)


def main():
    fp = open('lagou.csv', 'a', newline='', encoding='utf-8')
    writer = csv.writer(fp)
    writer.writerow(('name', 'company_name', 'city', 'work_years', 'education', 'desc'))
    p = LagouSpider(writer)
    p.run()


if __name__ == '__main__':
    main()
