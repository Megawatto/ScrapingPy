import argparse
import csv
import linecache
import os
import threading

from bs4 import BeautifulSoup as bs

import requests

BASE = 'http://kommersant.ru'
fn = ['section', 'date', 'url', 'head', 'body']
start_line = None

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--line', type=int, help='start line')


def get_links():
    with open('data/kom_lenta_links.csv', 'r') as f:
        result = []
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for line in reader:
            result.append(line)
        return result


def replace_text(t):
    return t.strip().replace('\t', ' ').replace('\n', ' ').replace(';', '.').replace('\r', ' ')


def get_content(links=None, suf=None):
    if suf is not None:
        file_name = 'parse_data/kom_lenta_pub_%s.csv' % suf
    else:
        file_name = 'parse_data/kom_lenta_pub.csv'
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(f, delimiter=';', fieldnames=fn)
        writer.writeheader()
        if links is None:
            links = get_links()
        for line in links:
            try:
                response = requests.get('%s%s' % (BASE, line[2]))

                if not response.status_code in [400, 403, 404, 500, 503]:
                    beus = bs(response.content.decode('cp1251').encode('utf-8'), 'html.parser')
                    head = beus.find('h2', attrs={'class': 'article_name'}).text
                    head = replace_text(head)
                    date_news = line[0]
                    content = beus.find('div',
                                        attrs={'id': 'divLetterBranding', 'class': ['article_text_wrapper']})
                    musor = content.find_all('script')
                    for d in musor:
                        d.extract()
                    content = content.text
                    content = replace_text(content)
                    writer.writerow({'section': line[1],
                                     'date': date_news,
                                     'url': line[2],
                                     'head': head,
                                     'body': content})
                    print('complete', threading.current_thread().getName(), line)

                else:
                    print('error %s' % response.status_code, line)
            except Exception as e:
                print('error', line, e)
                continue


if __name__ == '__main__':
    if not os.path.isdir('parse_data'):
        os.mkdir('parse_data')
    if not os.path.isdir('data'):
        raise Exception('no dir data')
    args = parser.parse_args()
    if args.line:
        start_line = args.line

    get_content()
