import datetime

import requests
import argparse
import os
from bs4 import BeautifulSoup as bs
import csv
from datetime import datetime, timedelta

BASE = 'http://kommersant.ru/archive/news'
days_inc = 5840
timeout = 0
fieldnames = ['date', 'section', 'url']


def get_links():
    days = 0
    today = datetime.today()
    with open('data/kom_lenta_links.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        while days < days_inc:
            suf = today - timedelta(days=days)
            link = '%s/%s/' % (BASE, suf.strftime('%Y-%m-%d'))
            try:
                response = requests.get(link)
                if not response.status_code in [400, 403, 404, 500, 503]:
                    date = suf.strftime('%Y-%m-%d')
                    beas = bs(response.content, 'html.parser')
                    result = beas.find_all('a', attrs={'class': 'item'})
                    for l in result:
                        writer.writerow({'date': date, 'section': 'news', 'url': l.attrs['href']})
                    print(response.status_code, link, len(result))
                else:
                    print('error', response.status_code, link)
            except Exception as e:
                print('error', response.status_code, link, e)

            days += 1


if __name__ == '__main__':
    if not os.path.isdir('data'):
        os.mkdir('data')
    get_links()
