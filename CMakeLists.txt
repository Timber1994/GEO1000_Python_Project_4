cmake_minimum_required(VERSION 3.16)
project(lab4)

set(CMAKE_CXX_STANDARD 14)

add_executable(triangulate triangulate.cpp)

# link statically to prevent errors with mingw on windows
target_link_libraries(triangulate -static)
