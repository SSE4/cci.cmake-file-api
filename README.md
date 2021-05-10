# CMake File API conan hook

The [conan](https://conan.io) [hook](https://docs.conan.io/en/latest/extending/hooks.html) that automatically generates [components](https://docs.conan.io/en/latest/creating_packages/package_information.html#using-components) for [package_info](https://docs.conan.io/en/latest/reference/conanfile/methods.html#package-info) method via [CMake File API](https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html).

## installation

use [conan config install](https://docs.conan.io/en/latest/reference/commands/consumer/config.html#conan-config-install) command:

```
$ conan config install https://github.com/SSE4/cci.cmake-file-api.git -sf hooks -tf hooks
$ conan config set hooks.cmake_file_api
```
