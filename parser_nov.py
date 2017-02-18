import requests
import argparse
import os
from bs4 import BeautifulSoup as bs
import csv

BASE = 'http://old.novayagazeta.ru'
fn = ['section', 'date', 'url', 'head', 'body']


def get_links():
    with open('data/nov_links.csv', 'r') as f:
        result = []
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for line in reader:
            result.append(line)
        return result


def replace_text(t):
    return t.strip().replace('\t', ' ').replace('\n', ' ').replace(';', '.')


def get_content():
    with open('parse_data/nov_pub.csv', 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, delimiter=';', fieldnames=fn, lineterminator="\n")
        writer.writeheader()
        for line in get_links():
            try:
                res = requests.get('%s%s' % (BASE, line[2]))

                if res.status_code == 404 or res.status_code == 500:
                    print('error %s' % res.status_code, line)
                    continue

                beus = bs(res.content.decode('cp1251').encode('utf-8'), "html.parser")
                head = beus.find_all('h1', attrs={'class': 'b-title-name'})[0].text
                head = replace_text(head)
                date_news = beus.find_all('span', attrs={'class': 'b-title-meta-date'})[0].text.strip()
                content = beus.find_all('div', attrs={'class': ['b-article', ' g-content', ' g-clearfix']})[0]
                if content.find('img'):
                    content.find('img').extract()
                content = content.find_all('p')
                all_text = ''
                for c in content:
                    c = replace_text(c.text)
                    if c:
                        all_text += c
                writer.writerow({'section': line[1], 'date': date_news, 'url': line[2], 'head': head, 'body': all_text})
                print('complete', line)
            except Exception as e:
                print('error', e)


if __name__ == '__main__':
    if not os.path.isdir('parse_data'):
        os.mkdir('parse_data')
    if not os.path.isdir('data'):
        raise Exception('no dir data')
    get_content()
