import os
import sys

root_path = sys.argv[1]

def check_modification():   
    lib_name = os.path.join(root_path, 'libmixin.a')
    if not os.path.exists(lib_name):
        return True
    modify_time = os.path.getmtime(lib_name)
    for root, dirs, files in os.walk(root_path):
        for f in files:
            if f[-3:] == '.go':
                f = os.path.join(root, f)
                file_time = os.path.getmtime(f)
                if modify_time < file_time:
                    return True
    return False

r = check_modification()
if r:
    print('mixin lib need to rebuild.')
    os.system(f'touch {root_path}/main.go')
