#rm src/mixin/libmixin.a
CC=clang CXX=clang++ python3.7 setup.py sdist bdist_wheel --plat-name macosx-10.9-x86_64
