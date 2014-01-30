# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================


def install(robustus, requirement_specifier, rob_file, ignore_index):
    robustus.install_cmake_package(requirement_specifier, [], ignore_index)