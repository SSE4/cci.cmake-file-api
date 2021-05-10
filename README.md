# CMake File API conan hook

The [conan](https://conan.io) [hook](https://docs.conan.io/en/latest/extending/hooks.html) that automatically generates [components](https://docs.conan.io/en/latest/creating_packages/package_information.html#using-components) for [package_info](https://docs.conan.io/en/latest/reference/conanfile/methods.html#package-info) method via [CMake File API](https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html).

## installation

use [conan config install](https://docs.conan.io/en/latest/reference/commands/consumer/config.html#conan-config-install) command:

```
$ conan config install https://github.com/SSE4/cci.cmake-file-api.git -sf hooks -tf hooks
$ conan config set hooks.cmake_file_api
```

## usage

run [conan create](https://docs.conan.io/en/latest/reference/commands/creator/create.html) against your recipe which use CMake build system.

observe logs (example):

```
[HOOK - cmake_file_api.py] post_build(): found CMake build directory: "C:\Users\SSE4\.conan\data\kuba-zip\0.1.31\_\_\build\6cc50b139b9c3d27b3e9042d5f5372d327b3a9f7"
[HOOK - cmake_file_api.py] post_build(): found CMake project: "zip"
[HOOK - cmake_file_api.py] post_build(): WARN: project name "zip" is different from conanfile name "kuba-zip"
[HOOK - cmake_file_api.py] post_build(): found CMake STATIC_LIBRARY target: "zip" ("zip.lib")
[HOOK - cmake_file_api.py] post_build(): WARN: target name "zip" is different from conanfile name "kuba-zip"
[HOOK - cmake_file_api.py] post_build(): WARN: consider adding the following code to the "package_info" method:
[HOOK - cmake_file_api.py] post_build(): WARN:
self.cpp_info.names["cmake_find_package"] = "zip"
self.cpp_info.names["cmake_find_package_multi"] = "zip"

self.cpp_info.components["zip"].names["cmake_find_package"] = "zip"
self.cpp_info.components["zip"].names["cmake_find_package_multi"] = "zip"
self.cpp_info.components["zip"].libs = ["zip"]
```

the code suggested by the hook's output could be copied into the [package_info](https://docs.conan.io/en/latest/reference/conanfile/methods.html#package-info) method.
