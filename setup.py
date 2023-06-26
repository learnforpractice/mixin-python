import os
import sys
import platform

from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize

os.environ["CC"] = "clang"
os.environ["CXX"] = "clang++"

# Require pytest-runner only when running tests
pytest_runner = (['pytest-runner>=2.0,<3dev']
                 if any(arg in sys.argv for arg in ('pytest', 'test'))
                 else [])

setup_requires = pytest_runner

data_files = [
#    ('lib',['src/mixin/mixin.so']),
]

data = []
if platform.system() == 'Windows':
    data.append("mixin.dll")

version = platform.python_version_tuple()
version = '%s.%s' % (version[0], version[1])

dir_name = os.path.dirname(os.path.realpath(__file__))

root_path = os.path.join(dir_name, 'src/mixin')
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

if platform.system() == 'Windows':
    os.system('cd ./src/mixin &&go build -o mixin.dll -buildmode=c-shared && copy mixin.dll ../../pysrc/mixin.dll && gendef mixin.dll && lib /def:mixin.def /machine:x64 /out:mixin.lib')
else:
    os.system('cd ./src/mixin;go build -o libmixin.a -buildmode=c-archive')

ext_modules = [
    Extension(
        'pymixin._mixin',
        sources=[
            'src/_mixin.pyx',
        ],
        include_dirs=[
            'src/mixin',
        ],
        language='c++',
        extra_compile_args=['-std=c++17'],
        extra_link_args=['-L./src/mixin', '-lmixin'],
    )
]

setup(
    name="mixin-python",
    version="0.2.10",
    description="Mixin Binding Project",
    author='learnforpractice',
    url="https://github.com/learnforpractice/mixin-python",
    license="GPL-3.0",
    packages=['pymixin'],
    package_dir={'pymixin': 'pysrc'},
    package_data={'pymixin': data},
    data_files = data_files,
    scripts=[],
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={'language_level': 3, },
    ),
    install_requires=[
        "PyJWT>=2.4.0",
        "websockets>=9.1",
        "cryptography>=3.4.7",
        "dataclasses-json",
        "httpx"
    ],
    tests_require=['pytest'],
    setup_requires=setup_requires,
    include_package_data=True
)
