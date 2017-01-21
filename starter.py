import subprocess

procs = []
sections = ['politics', 'defense_safety', 'media', 'health', 'education']
for section in sections:
    print('start %s' % section)
    procs.append(subprocess.Popen(['python3', 'scrapper.py', '-s' + section, '-d 1000', '-t 0.8']))

for p in procs:
    p.wait()
