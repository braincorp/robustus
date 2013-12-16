import os
import robustus
import shutil
from utility import execute_python_expr


def check_module(test_env, python_imports, package_files, postinstall_script):
    for imp in python_imports:
        assert execute_python_expr(test_env, imp, postinstall_script) == 0
    for file in package_files:
        assert os.path.isfile(os.path.join(test_env, file))


def install_dependencies(test_env, dependencies):
    for dep in dependencies:
        robustus.execute(['--env', test_env, 'install', dep])


def perform_standard_test(package,
                          python_imports=[],
                          package_files=[],
                          dependencies=[],
                          postinstall_script=None,
                          test_env='test_env',
                          test_cache='test_wheelhouse',
                          options=[]):
    """
    create env, install package, check package is available,
    remove env, install package without index, check package is available
    :return: None
    """
    # create env and install bullet into it
    test_env = os.path.abspath(test_env)
    test_cache = os.path.abspath(test_cache)

    robustus.execute(options + ['--cache', test_cache, 'env', test_env])
    install_dependencies(test_env, dependencies)
    robustus.execute(options + ['--env', test_env, 'install', package])
    check_module(test_env, python_imports, package_files, postinstall_script)
    shutil.rmtree(test_env)

    # install again, but using only cache
    robustus.execute(options + ['--cache', test_cache, 'env', test_env])
    install_dependencies(test_env, dependencies)
    robustus.execute(options + ['--env', test_env, 'install', package, '--no-index'])
    check_module(test_env, python_imports, package_files, postinstall_script)
    shutil.rmtree(test_env)
    shutil.rmtree(test_cache)
