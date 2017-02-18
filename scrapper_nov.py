import requests
import argparse
import os
from bs4 import BeautifulSoup as bs
import csv

BASE = 'http://old.novayagazeta.ru/issues/2017/'
_inc = 2578
timeout = 0
# sections = ['politics', 'inquests', 'columns', 'economy', 'comments', 'society', 'arts', 'sports']

fieldnames = ['num', 'section', 'url']


def get_links():
    global _inc

    with open('data/nov_links.csv', 'w') as f:
        writer = csv.DictWriter(f, dialect='excel', delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        while _inc != 0:
            try:
                res = requests.get('%s/%s.html' % (BASE, _inc))
                if res.status_code == 404 or res.status_code == 500:
                    _inc -= 1
                    print('error %s' % res.status_code, _inc)
                    continue
                beus = bs(res.content, "html.parser")
                result = beus.find_all('a', attrs={'class': 'b-issue-content-item-title-link'})
                for line in result:
                    link = line.attrs['href']
                    section = link[1:].split('/')[0]
                    writer.writerow({'num': _inc, 'section': section, 'url': link})
            except Exception as e:
                print('res code: %s' % res.status_code)
                print(e)
            finally:
                print('complete %s' % _inc)
                _inc -= 1


if __name__ == '__main__':
    get_links()
