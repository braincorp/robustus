import logging
import os
import robustus
import shutil
from utility import execute_python_expr


def check_module(test_env, python_imports, package_files, postinstall_script):
    for imp in python_imports:
        assert execute_python_expr(test_env, imp, postinstall_script) == 0
    for file in package_files:
        assert os.path.isfile(os.path.join(test_env, file))


def install_dependencies(test_env, dependencies, options):
    for dep in dependencies:
        robustus.execute(options + ['--env', test_env, 'install', dep])


def perform_standard_test(package,
                          python_imports=[],
                          package_files=[],
                          dependencies=[],
                          postinstall_script=None,
                          test_env='test_env',
                          test_cache='test_wheelhouse',
                          options=[],
                          install_options=[]):
    """
    create env, install package, check package is available,
    remove env, install package without index, check package is available
    :return: None
    """
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    # create env and install bullet into it
    test_env = os.path.abspath(test_env)
    test_cache = os.path.abspath(test_cache)

    robustus.execute(options + ['--debug', '--cache', test_cache, 'env', test_env])
    install_dependencies(test_env, dependencies, options)
    robustus.execute(options + ['--debug', '--env', test_env, 'install', package] + install_options)
        
    check_module(test_env, python_imports, package_files, postinstall_script)
    shutil.rmtree(test_env)

    # install again, but using only cache
    robustus.execute(options + ['--debug', '--cache', test_cache, 'env', test_env])
    install_dependencies(test_env, dependencies, options)
    robustus.execute(options + ['--debug', '--env', test_env, 'install', package, '--no-index'] + install_options)
    check_module(test_env, python_imports, package_files, postinstall_script)
    shutil.rmtree(test_env)
    shutil.rmtree(test_cache)
