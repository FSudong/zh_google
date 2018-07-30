from urllib.parse import urlencode

import requests
from requests import RequestException


def get_cookie():
    '''从文件中获得cookies'''
    with open('cookie', 'r') as f:
        acookie = {}
        for line in f.read().split(";"):
            name, value = line.strip().split('=', 1)
            acookie[name] = value
        return acookie


def get_headers():
    '''获得标准头文件'''
    with open('headers', 'r') as f:
        headers = {}
        for line in f.read().split(';\n'):
            name, value = line.split(':', 1)
            headers[name] = value
        return headers

#
headers = get_headers()
cookies = get_cookie()


def save_html(html):
    '''保存网页'''
    with open('html.txt', 'w', encoding='utf-8') as f:
        f.write(html)
        f.close()

zh_url_pools = [
    'https://www.zhihu.com/api/v4/columns/c_137498113/articles?',
    'https://www.zhihu.com/api/v4/columns/dlalchemy/articles?',
    'https://www.zhihu.com/api/v4/columns/xitucheng10/articles?'
]


def get_page_index(url_base, offset):
    parameter ={
        'include': 'data[*].admin_closed_comment, comment_count, suggest_edit, is_title_image_full_screen, can_comment, upvoted_followees, can_open_tipjar, can_tip, voteup_count, voting, topics, review_info, author.is_following',
        'limit': '10',
        'offset': offset
    }
    # url = 'https://www.zhihu.com/api/v4/columns/xitucheng10/articles?' + urlencode(parament)
    #url = 'https://www.zhihu.com/api/v4/columns/xitucheng10/articles?' + urlencode(parament)
    url = url_base + urlencode(parameter)
    print(url)
    headers = get_headers()
    cookies = get_cookie()
    s = requests.Session()
    try:
        req2 = s.get(url, headers=headers, cookies=cookies)
        #req2 = requests.get(url)
        req2.encoding = 'gb18030'
        print(req2.text)
        print(req2.status_code)
        if req2.status_code == 200:
            #            response.encoding = 'utf-8'
            #print('the ' + str(page_num) + 'th page')
            return req2.text
    except RequestException:
        print(req2.status_code)
        print('请求出错')
        return None


