import os
import sys
import platform
from setuptools import find_packages
from skbuild import setup

# Require pytest-runner only when running tests
pytest_runner = (['pytest-runner>=2.0,<3dev']
                 if any(arg in sys.argv for arg in ('pytest', 'test'))
                 else [])

setup_requires = pytest_runner

data_files = [
#    ('lib',['src/mixin/mixin.so']),
]

version = platform.python_version_tuple()
version = '%s.%s' % (version[0], version[1])

setup(
    name="mixin-python",
    version="0.2.2",
    description="Mixin Binding Project",
    author='learnforpractice',
    url="https://github.com/learnforpractice/mixin-python",
    license="GPL-3.0",
    packages=['pymixin'],
    package_dir={'pymixin': 'pysrc'},
    package_data={'pymixin': []},
    data_files = data_files,
    scripts=[],
    install_requires=[
        "pycparser==2.19",
        "pycryptodome==3.7.2",
        "PyJWT==2.1.0",
        "python-dateutil==2.7.5",
        "requests==2.21.0",
        "websockets==9.1",
        "cryptography==3.4.7",
        "httpx"
    ],
    tests_require=['pytest'],
    setup_requires=setup_requires,
    include_package_data=True
)
