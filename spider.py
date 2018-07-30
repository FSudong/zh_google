import json
import re
from multiprocessing.pool import Pool
from urllib.parse import urlencode

import pymongo
import requests
from pymongo.errors import DuplicateKeyError
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from get_cookie_header import *
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


# 由论文网页提取出 所要的内容
def get_paper_time(url):
    try:
        rep_info = requests.get(url, cookies=cookies, headers=headers)
        if rep_info.status_code == 200:
            soup = BeautifulSoup(rep_info.text, "lxml")
            time_info = soup.select('.ContentItem-time')
            split = time_info[0].string.split(' ')
            time = split[1]
            return time
    except RequestException:
        print('请求出错')
    # print(type(rep_info.text))


# ajax分析出每篇论文的名字 和时间
def parse_page_index(html):
    results = json.loads(html)
    print(results)
    if results and 'data' in results.keys():
        for item in results.get('data'):
            item_title = item['title']
            item_url = item['url']
            time = get_paper_time(item_url)
            # pat_1 = re.compile(r'[\u4e00-\u9fa5]')
            # en_title = "".join(pat_1.split(item_title))
            pro_info = {
                'title':item_title,
                'time':time
            }
            yield pro_info

            # print(type(item['excerpt']))
            # print(item['excerpt'])


# 由名字在 百度学术中搜索 随后找到
def get_paper_info(pro_info):
    en_title = pro_info['title']
    para = {
        'wd': en_title,
        'rsv_bp': 0,
        'tn': 'SE_baiduxueshu_c1gjeupa',
        'rsv_spt': 3,
        'ie': 'utf-8',
        'f': 8,
        'rsv_sug2': 0,
        'sc_f_para': 'sc_tasktype={firstSimpleSearch}',
        'rsv_n': 2
    }
    url_baidu = 'http://xueshu.baidu.com/s?' + urlencode(para)
    req2 = requests.get(url_baidu)
    # print(req2.status_code)
    soup1 = BeautifulSoup(req2.text, "lxml")
    search_list = soup1.select_one('.t.c_font a')
    if search_list:
        # 搜索到了很多文章 默认选取第一个
        # print(search_list['href'])
        rep_detail = requests.get('http://xueshu.baidu.com' + search_list['href'])
        print('http://xueshu.baidu.com' + search_list['href'])
        soup_detail = BeautifulSoup(rep_detail.text, "lxml")
    else:
        # 搜索到了一篇文章
        soup_detail = soup1
        print(url_baidu)
    href_title = soup_detail.select_one('#dtl_l div h3 a')
    if not href_title:
        return None
    autor = soup_detail.select('.author_text a')
    authors = [a.text.strip() for a in autor]
    abstract = soup_detail.select_one('.abstract_wr .abstract')
    paper_info = {
        '_id': href_title.text + 'pw',
        'link': href_title['href'].strip(),
        'real_title': en_title,
        'title': href_title.text,
        'authors': authors,
        'abstract': abstract.text,
        'time': pro_info['time']
    }
    return paper_info


# 存储到mongo-db
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('saved ', result)
            return True
    except DuplicateKeyError:
        print('already exit')
        return None


# 存储到文件
def save_to_file(MONGO_TABLE):
    # 存储目录、
    basic = 'F:\Coding\python\zh_google\data'
    # 最新论文和排行榜论文

    collection = db.get_collection(MONGO_TABLE)
    documents = collection.find()
    num = 0
    year_num = [0 for i in range(500)]
    # 存在mangoDB中的论文 每一篇为doc
    for doc in documents:
        print(doc)
        num = num + 1
        year = int(doc['time'].split('-')[0])
        year_num[year - 1900] = year_num[year - 1900] + 1
        output = open(basic + '\\' + str(year)+'.'+str(year_num[year - 1900]+1000) + '.txt', 'w', encoding="utf-8")
        output.write(doc['title'] + '\n')
        output.write('Abstract:' + doc['abstract'] + '\n')
        # 无keywords
        output.write('None\n')
        # type
        output.write('2\n')
        output.write(doc['link'] + '\n')
        output.write('zhihu\n')
        # 时间无
        output.write(doc['time'])
        output.close()


def main(url, offset):
    html = get_page_index(url, offset)
    for pro_info in parse_page_index(html):
        print(pro_info['title'])
        pro_info['title'].replace('\n', ' ')
        paper_info = get_paper_info(pro_info)
        if paper_info:
            save_to_mongo(paper_info)


if __name__ == '__main__':
    # groups = [i*10 for i in range(10)]
    # pool = Pool()
    # pool.map(main, groups)

    # # 爬取
    # for url_base_num in range(len(zh_url_pools)):
    #     print(url_base_num)
    #     for i in range(16):
    #         main(zh_url_pools[url_base_num], i * 10)
    #存储到文件中
    save_to_file(MONGO_TABLE)
