# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import logging
import os
from requirement import RequirementException
from utility import ln, write_file, run_shell, fix_rpath, unpack, safe_remove
import shutil
import subprocess
import sys


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if requirement_specifier.version != '1.8.1' and not requirement_specifier.version.startswith('bc'):
        raise RequirementException('can only install panda3d 1.8.1/bc1/bc2')

    panda_install_dir = os.path.join(robustus.cache, 'panda3d-%s' % requirement_specifier.version)

    def in_cache():
        return os.path.isfile(os.path.join(panda_install_dir, 'lib/panda3d.py'))

    if not in_cache() and not ignore_index:
        cwd = os.getcwd()
        panda3d_tgz = None
        panda3d_archive_name = None
        try:
            panda3d_tgz = robustus.download('panda3d', requirement_specifier.version)
            panda3d_archive_name = unpack(panda3d_tgz)

            logging.info('Builduing panda3d')
            os.chdir(panda3d_archive_name)

            # link bullet into panda dependencies dir
            bullet_installations = glob.glob(os.path.join(robustus.env, 'lib/bullet-*'))
            if len(bullet_installations) > 0:
                bullet_dir = bullet_installations[0]
                if sys.platform.startswith('darwin'):
                    panda_thirdparty_dir = 'thirdparty/darwin-libs-a'
                elif sys.platform.startswith('linux'):
                    panda_thirdparty_dir = 'thirdparty/linux-libs-x64'
                else:
                    raise RequirementException('unsupported platform ' + sys.platform)
                os.mkdir('thirdparty')
                os.mkdir(panda_thirdparty_dir)
                os.mkdir(os.path.join(panda_thirdparty_dir, 'bullet'))
                ln(os.path.join(bullet_dir, 'include/bullet'),
                   os.path.join(panda_thirdparty_dir, 'bullet/include'))
                ln(os.path.join(bullet_dir, 'lib'),
                   os.path.join(panda_thirdparty_dir, 'bullet/lib'))

            make_panda_options = ['--nothing',
                                  '--use-python',
                                  '--use-direct',
                                  '--use-bullet',
                                  '--use-zlib',
                                  '--use-png',
                                  '--use-jpeg',
                                  '--use-tiff',
                                  '--use-freetype',
                                  '--use-x11',
                                  '--use-gl',
                                  '--use-nvidiacg',
                                  '--use-pandatool',
                                  '--use-tinydisplay',
                                  '--threads', '4']
            if sys.platform.startswith('darwin'):
                make_panda_options += ['--use-cocoa']
                os.environ['CC'] = 'gcc'
                os.environ['CXX'] = 'g++'

            makepanda_cmd = [robustus.python_executable, 'makepanda/makepanda.py'] + make_panda_options
            # command takes much time and output very long, so run_shell isn't used
            retcode = subprocess.call(makepanda_cmd)
            if retcode != 0:
                raise RequirementException('panda3d build failed')

            # copy panda3d files to cache
            shutil.rmtree(panda_install_dir, ignore_errors=True)
            os.mkdir(panda_install_dir)
            subprocess.call('cp -R built/lib %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/bin %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/include %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/direct %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/pandac %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/models %s' % panda_install_dir, shell=True)
            subprocess.call('cp -R built/etc %s' % panda_install_dir, shell=True)
        finally:
            safe_remove(panda3d_tgz)
            safe_remove(panda3d_archive_name)
            os.chdir(cwd)

    if in_cache():
        # install panda3d to virtualenv
        libdir = os.path.join(robustus.env, 'lib/panda3d')
        shutil.rmtree(libdir, ignore_errors=True)
        os.mkdir(libdir)

        env_etcdir = os.path.join(robustus.env, 'etc')
        if not os.path.isdir(env_etcdir):
            os.mkdir(env_etcdir)
        etcdir = os.path.join(env_etcdir, 'panda3d')
        shutil.rmtree(etcdir, ignore_errors=True)
        os.mkdir(etcdir)

        run_shell('cp -r -p %s/lib/* %s/' % (panda_install_dir, libdir))
        run_shell('cp -r -p %s/direct %s/' % (panda_install_dir, libdir))
        run_shell('cp -r -p %s/pandac %s/' % (panda_install_dir, libdir))
        run_shell('cp -r -p %s/etc/* %s/' % (panda_install_dir, etcdir))

        # modify rpath of libs
        libdir = os.path.abspath(libdir)
        if sys.platform.startswith('darwin'):
            libs = glob.glob(os.path.join(libdir, '*.dylib'))
        else:
            libs = glob.glob(os.path.join(libdir, '*.so'))
        for lib in libs:
            fix_rpath(robustus.env, lib, libdir)

        prc_dir_setup = "import os; os.environ['PANDA_PRC_DIR'] = '%s'" % etcdir
        write_file(os.path.join(robustus.env, 'lib/python2.7/site-packages/panda3d.pth'),
                   'w',
                   '%s\n%s\n' % (libdir, prc_dir_setup))

        # patch panda prc file
        with open(os.path.join(etcdir, 'Config.prc'), 'a') as f:
            extra_options = []
            extra_options.append("# enable antialiasing\n"
                                 "framebuffer-multisample 1\n"
                                 "multisamples 4\n")
            extra_options.append("# disable panda3d transform caching to avoid memory leak in bullet bindings\n"
                                 "garbage-collect-states 0\n")

            extra_options.append("# enable software rendering as fallback\n"
                                 "aux-display p3tinydisplay\n")

            f.write('\n'.join(extra_options))

    else:
        raise RequirementException('can\'t find panda3d-%s in robustus cache' % requirement_specifier.version)
