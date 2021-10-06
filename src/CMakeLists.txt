
add_cython_target(_mixin CXX)

add_library(_mixin MODULE
    ${_mixin}
)

if (WIN32)
    add_compile_definitions(MS_WIN64)
endif()

python_extension_module(_mixin)

add_dependencies(_mixin build_mixin)

target_link_libraries(_mixin ${CMAKE_CURRENT_SOURCE_DIR}/mixin/libmixin.a)

target_include_directories(_mixin PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/mixin
)

add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/mixin/libmixin.a
    COMMAND go build -o libmixin.a -buildmode=c-archive
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/mixin_api.go
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/main.go
    COMMENT "Creating libmixin.a"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/mixin
)

add_custom_target(build_mixin ALL
    COMMAND echo "Building libmixin.a"
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/libmixin.a
    # to make quotes printable,for example
    VERBATIM
)

install(TARGETS _mixin LIBRARY DESTINATION pysrc)

