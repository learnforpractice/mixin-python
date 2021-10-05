import os
for f in os.listdir('./dist'):
    if f.endswith('.whl'):
        print(f)
        break
