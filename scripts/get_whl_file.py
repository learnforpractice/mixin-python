import os
import sys

search_dir = 'dist'
keyword = ''

if len(sys.argv) >= 2:
    search_dir = sys.argv[1]

if len(sys.argv) >= 3:
    keyword = sys.argv[2]

for f in os.listdir(search_dir):
    if f.endswith('.whl'):
        if keyword and not keyword in f:
            continue
        print(f)
        break
