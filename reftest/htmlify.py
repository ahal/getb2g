import os

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

for f in sorted_ls('.'):
    os.system('perl reftest-to-html.pl ' + f + ' > html/' + f.replace('log', 'html'))

