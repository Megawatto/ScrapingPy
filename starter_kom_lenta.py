import csv
import subprocess

import threading

import parser_kom_lenta

LIMIT = 20000


def get_links():
    with open('data/kom_lenta_links.csv', 'r') as f:
        result = []
        reader = csv.reader(f, delimiter=';')
        next(reader)
        cascade = []

        for line in reader:
            result.append(line)
            if len(result) == 20000:
                cascade.append(result)
                result = []
        cascade.append(result)
        return cascade


procs = []
links = get_links()
for i, l in enumerate(links):
    t = threading.Thread(target=parser_kom_lenta.get_content, args=(l, i), daemon=True)
    t.start()
    print('start', t, i)
    procs.append(t)

for p in procs:
    p.join()
