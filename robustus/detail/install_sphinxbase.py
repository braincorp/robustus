# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from utility import unpack, safe_remove, run_shell, fix_rpath, ln
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    build_dir = os.path.join(robustus.cache, 'sphinxbase-%s' % requirement_specifier.version)

    def in_cache():
        return os.path.isdir(build_dir)

    cwd = os.getcwd()
    if not in_cache() and not ignore_index:
        try:
            # build in cache
            os.chdir(robustus.cache)
            archive = robustus.download('sphinxbase', requirement_specifier.version)
            unpack(archive)

            logging.info('Building sphinxbase')
            os.chdir(build_dir)

            # link python-config from system-wide installation, sphinxbase configure requires it
            python_config = os.path.join(robustus.env, 'bin/python-config')
            if not os.path.isfile(python_config):
                ln('/usr/bin/python-config', python_config)

            # there is problem executing this command with run_shell
            retcode = run_shell('./configure'
                                + (' --prefix=%s' % robustus.env)
                                + (' --with-python=%s' % os.path.join(robustus.env, 'bin/python')),
                                shell=True,
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('sphinxbase configure failed')

            retcode = run_shell(['make'], verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('sphinxbase build failed')
        except RequirementException:
            safe_remove(build_dir)
        finally:
            safe_remove(archive)
            os.chdir(cwd)

    if in_cache():
        logging.info('Installing sphinxbase into virtualenv')
        os.chdir(build_dir)
        retcode = run_shell('make install', shell=True, verbose=robustus.settings['verbosity'] >= 1)
        os.chdir(cwd)
        if retcode != 0:
            raise RequirementException('sphinxbase install failed')
        # fix rpath for sphinxbase
        sphinxbase = os.path.join(robustus.env, 'lib/python2.7/site-packages/sphinxbase.so')
        fix_rpath(robustus, robustus.env, sphinxbase, os.path.join(robustus.env, 'lib'))
    else:
        raise RequirementException('can\'t find sphinxbase-%s in robustus cache' % requirement_specifier.version)
