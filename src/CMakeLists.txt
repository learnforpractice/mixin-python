
add_cython_target(_mixin CXX)

add_library(_mixin MODULE
    ${_mixin}
)

if (WIN32)
    add_compile_definitions(MS_WIN64)
    SET(BUILD_TARGET mixin.lib)
    SET(BUILD_LIB_CMD go build -o mixin.dll -buildmode=c-shared && cmake -E copy mixin.dll ${CMAKE_CURRENT_SOURCE_DIR}/../pysrc/mixin.dll && gendef mixin.dll && lib /def:mixin.def /machine:x64 /out:mixin.lib)
else()
    SET(BUILD_TARGET libmixin.a)
    SET(BUILD_LIB_CMD go build -o ${BUILD_TARGET} -buildmode=c-archive)
endif()

python_extension_module(_mixin)

add_dependencies(_mixin build_mixin)

target_link_libraries(_mixin ${CMAKE_CURRENT_SOURCE_DIR}/mixin/${BUILD_TARGET})

target_include_directories(_mixin PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/mixin
)

message(STATUS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/${BUILD_TARGET})
add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/mixin/${BUILD_TARGET}
    COMMAND ${BUILD_LIB_CMD}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/mixin_api.go
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/main.go
    COMMENT "Creating ${BUILD_TARGET}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/mixin
)

add_custom_target(build_mixin ALL
    COMMAND echo "Building ${BUILD_TARGET}"
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/mixin/${BUILD_TARGET}
    # to make quotes printable,for example
    VERBATIM
)

install(TARGETS _mixin LIBRARY DESTINATION pysrc)

