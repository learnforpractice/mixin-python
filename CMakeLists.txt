cmake_minimum_required(VERSION 3.5.0)

project(mixin)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

add_subdirectory(src)
