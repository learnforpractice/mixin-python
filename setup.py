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
    name="mixin",
    version="0.1.0",
    description="Mixin Binding Project",
    author='learnforpractice',
    license="MIT",
    packages=['mixin'],
    package_dir={'mixin': 'pysrc'},
    package_data={'mixin': []},
    data_files = data_files,
    scripts=[],
    install_requires=[
        "pycparser==2.19",
        "pycryptodome==3.7.2",
        "PyJWT==1.7.1",
        "python-dateutil==2.7.5",
        "requests==2.21.0",
        "websockets",
        "httpx"
    ],
    tests_require=['pytest'],
    setup_requires=setup_requires,
    include_package_data=True
)
