from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import os
import ssl
import argparse
import time

BASE = 'https://ria.ru'
days_inc = 1
timeout = 0
sections = ['politics', 'defense_safety', 'media', 'health',
            'education', 'trend/Russia_WCIOM_polls_21112016',
            'company', 'incidents', 'sport', 'religion',
            'culture', 'science', 'disabled',
            'sn', 'ffoms']

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--base', type=str, help='base url address')
parser.add_argument('-d', '--days', default=5, type=int, help='the number of days to parse days')
parser.add_argument('-s', '--sections', nargs='+', type=str, help='section site')
parser.add_argument('-v', '--verbal', action='store_true', help='verbal output')
parser.add_argument('-t', '--timeout', type=float, help='timeout from request')


def get_links(verb):
    global days_inc
    global sections

    cert = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    today = datetime.today()

    for section in sections:
        days = 0
        stats = 0
        if section.find('/'):
            path = section.replace('/', '_')
        else:
            path = section
        with open('data/' + path, 'w') as f:
            while days < days_inc:
                suf = today - timedelta(days=days)
                f.write('__%s__\n' % (suf.strftime('%Y-%m-%d')))
                link = BASE + ('/%s/%s/' % (section, suf.strftime('%Y%m%d')))
                if verb:
                    print('>>>>>>>>>>>>>>> %s %s %s<<<<<<<<<<<<<<<' % (days, link, section))
                try:
                    if timeout:
                        time.sleep(timeout)
                    html = urlopen(link, context=cert)
                    beus = bs(html, "html.parser")
                    result = beus.find_all('div', {'class': 'b-list__item'})
                    for line in result:
                        if verb:
                            print(line.a.attrs['href'])
                        f.write(line.a.attrs['href'] + '\n')
                        stats += 1
                    days += 1
                    f.write('\n')
                except HTTPError as e:
                    print(e)
                    print('error %s %s %s' % (days, link, section))
                    break
                except URLError as e:
                    print(e)
                    print('error %s' % link)
                    break

        print('section <%s> completed, count link=%s' % (section, stats))


if __name__ == '__main__':
    if not os.path.isdir('data'):
        os.mkdir('data')
    args = parser.parse_args()
    if args.days:
        days_inc = args.days
    if args.base:
        BASE = args.base
    if args.sections:
        sections = args.sections
    if args.timeout:
        timeout = args.timeout

    get_links(args.verbal)
