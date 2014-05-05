# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from utility import unpack, safe_remove, run_shell, fix_rpath, write_file
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    build_dir = os.path.join(robustus.cache, 'pocketsphinx-%s' % requirement_specifier.version)

    # check if already installed
    pocketsphinx = os.path.join(robustus.env, 'lib/python2.7/site-packages/pocketsphinx.so')
    if os.path.isfile(pocketsphinx):
        return

    # unfortunately we can't cache pocketsphinx, it has to be rebuild after reconfigure
    cwd = os.getcwd()
    try:
        # build in cache
        os.chdir(robustus.cache)
        archive = robustus.download('pocketsphinx', requirement_specifier.version)
        unpack(archive)

        logging.info('Building pocketsphinx')
        os.chdir(build_dir)

        sphinxbase_dir = os.path.join(robustus.cache, 'sphinxbase-%s/' % requirement_specifier.version)
        retcode = run_shell('./configure'
                            + (' --prefix=%s' % robustus.env)
                            + (' --with-python=%s' % os.path.join(robustus.env, 'bin/python'))
                            + (' --with-sphinxbase=%s' % sphinxbase_dir)
                            + (' --with-sphinxbase-build=%s' % sphinxbase_dir),
                            shell=True,
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('pocketsphinx configure failed')

        retcode = run_shell(['make'], verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('pocketsphinx build failed')

        logging.info('Installing pocketsphinx into virtualenv')
        retcode = run_shell('make install', shell=True, verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('sphinxbase install failed')

        # fix rpath for pocketsphinx
        fix_rpath(robustus.env, pocketsphinx, os.path.join(robustus.env, 'lib'))
        # there is a super weird bug, first import of pocketsphinx fails http://sourceforge.net/p/cmusphinx/bugs/284/
        write_file(os.path.join(robustus.env, 'lib/python2.7/site-packages/wrap_pocketsphinx.py'),
                   'w',
                   'try:\n'
                   + '    from pocketsphinx import *\n'
                   + 'except:\n'
                   + '    pass\n'
                   + 'from pocketsphinx import *\n')
    except RequirementException:
        safe_remove(build_dir)
    finally:
        safe_remove(archive)
        os.chdir(cwd)
