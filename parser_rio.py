import argparse
import csv
import os
import re
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup as bs

patt = '/politics/20161206/1482985348.html'
BASE = 'https://ria.ru'
r = re.compile('^__\d{4}-\d\d-\d\d__')
fieldnames = ['date', 'section', 'header', 'content']

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbal', action='store_true', help='verbal output')


def get_link_list():
    list_files = os.listdir('data')
    result = {}
    for file in list_files:
        with open('data/' + file, 'r')as f:
            date = ''
            result[file] = {}
            for line in f:
                rr = r.findall(line)
                if rr:
                    date = rr.pop().replace('__', '').strip()
                    result[file][date] = []
                elif line.strip():
                    result[file][date].append(line.strip())
    return result


def get_content(datas, verb):
    cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    for data in datas:
        print('start parse %s' % data)
        with open('parse_data/' + data + '.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel', delimiter=";")
            writer.writeheader()
            for date in datas[data]:
                for link in datas[data][date]:
                    try:
                        html = urlopen(BASE + link, context=cert)
                        beat = bs(html, "html.parser")
                        header = beat.find('h1', {'class': 'b-article__title'})
                        if header:
                            header = header.get_text()
                        else:
                            print('no content %s' % link)
                            continue
                        content_body = beat.find('div', {'class': ['b-article__body', 'js-mediator-article']})
                        if content_body:
                            content = content_body.find_all('p')
                        else:
                            writer.writerow({'date': date, 'section': data, 'header': header, 'content':''})
                            continue
                        if verb:
                            print(header, data, link)
                        text = ''
                        for c in content:
                            if c.find('div', {'class': 'b-inject'}):
                                continue
                            elif not c.get_text():
                                continue
                            text += c.get_text()
                        writer.writerow({'date': date, 'section': data, 'header': header, 'content': text})
                    except HTTPError as e:
                        print(e)
                        print('error %s' % link)
                        break
                    except URLError as e:
                        print(e)
                        print('error %s' % link)
                        break
                print('parse from date %s completed' % date)
        print('parse from %s completed' % data)


if __name__ == '__main__':
    if not os.path.isdir('parse_data'):
        os.mkdir('parse_data')
    if not os.path.isdir('data'):
        raise Exception('no dir data')

    args = parser.parse_args()
    get_content(get_link_list(), args.verbal)
