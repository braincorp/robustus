# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import logging
import os
from requirement import RequirementException
from utility import ln, write_file, run_shell
import shutil
import subprocess
import sys


def install(robustus, requirement_specifier, rob_file, ignore_index):
    if requirement_specifier.version != '1.8.1' and requirement_specifier.version != 'bc1':
        raise RequirementException('can only install panda3d 1.8.1/bc1')

    panda_install_dir = os.path.join(robustus.cache, 'panda3d-%s' % requirement_specifier.version)

    def in_cache():
        return os.path.isfile(os.path.join(panda_install_dir, 'lib/panda3d.py'))

    if not in_cache() and not ignore_index:
        logging.info('Downloading panda3d')
        panda3d_archive_name = 'panda3d-%s' % requirement_specifier.version
        panda3d_tgz = panda3d_archive_name + '.tar.gz'
        if requirement_specifier.version == '1.8.1':
            url = 'https://www.panda3d.org/download/panda3d-1.8.1/' + panda3d_tgz
        else:
            url = 'https://s3.amazonaws.com/thirdparty-packages.braincorporation.net/' + panda3d_tgz
        subprocess.call(['wget', '-c', url, '-O', panda3d_tgz])

        logging.info('Unpacking panda3d')
        subprocess.call(['tar', 'xvzf', panda3d_tgz])

        logging.info('Builduing panda3d')
        cwd = os.getcwd()
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
            make_panda_options += ' --use-cocoa'
            os.environ['CC'] = 'gcc'
            os.environ['CXX'] = 'g++'

        subprocess.call([robustus.python_executable, 'makepanda/makepanda.py'] + make_panda_options)

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

        os.chdir(os.path.pardir)
        shutil.rmtree(panda3d_archive_name)
        os.remove(panda3d_tgz)

    if in_cache():
        # install panda3d to virtualenv

        def shell_cp(src_and_dist):
            # mac cp doesn't have --update flag
            if sys.platform.startswith('darwin'):
                cp_update_flag = ''
            else:
                cp_update_flag = ' -u'
            run_shell('cp -r%s -p %s' % (cp_update_flag, src_and_dist))

        libdir = os.path.join(robustus.env, 'lib/panda3d')
        shutil.rmtree(libdir, ignore_errors=True)
        os.mkdir(libdir)

        env_etcdir = os.path.join(robustus.env, 'etc')
        if not os.path.isdir(env_etcdir):
            os.mkdir(env_etcdir)
        etcdir = os.path.join(env_etcdir, 'panda3d')
        shutil.rmtree(etcdir, ignore_errors=True)
        os.mkdir(etcdir)

        shell_cp('%s/lib/* %s/' % (panda_install_dir, libdir))
        shell_cp('%s/direct %s/' % (panda_install_dir, libdir))
        shell_cp('%s/pandac %s/' % (panda_install_dir, libdir))
        shell_cp('%s/etc/* %s/' % (panda_install_dir, etcdir))

        
        # looks like this is redundant
        #incdir = os.path.join(robustus.env, 'include/panda3d')
        #shutil.rmtree(incdir, ignore_errors=True)
        #os.mkdir(incdir)
        #shell_cp('%s/models %s/' % (panda_install_dir, libdir))
        #shell_cp('%s/bin/* %s/bin' % (panda_install_dir, robustus.env))
        #shell_cp('%s/include/* %s/' % (panda_install_dir, incdir))

        env_var_lines = []
        if sys.platform.startswith('darwin'):
            env_var = 'DYLD_LIBRARY_PATH'
        else:
            env_var = 'LD_LIBRARY_PATH'

        if env_var in os.environ:
            lib_path_line = "import os; os.environ['%s'] += ':' + '%s'" % (env_var, libdir)
        else:
            lib_path_line = "import os; os.environ['%s'] = '%s'" % (env_var, libdir)

        env_var_lines.append(lib_path_line)
        env_var_lines.append("import os; os.environ['PANDA_PRC_DIR'] = '%s'" % etcdir)
        #env_var_lines.append("import os; print('LALALA')")

        write_file(os.path.join(robustus.env, 'lib/python2.7/site-packages/panda3d.pth'),
                   'w',
                   # do not add share
                   '%s/lib/panda3d\n%s' % (robustus.env, '\n'.join(env_var_lines)))
        
        def patch_file(filepath, code_to_erase, code_to_insert):
            assert(os.path.exists(filepath))
        
            with open(filepath, 'r') as f:
                content = f.read()
            
            pos = content.find(code_to_erase)
            assert(pos > 0)
            
            new_content = content[:pos] + code_to_insert + content[pos+len(code_to_erase):]
            with open(filepath, 'w') as f:
                f.write(new_content)
        
        
        def patch_extension_native_helpers_py(panda_lib_path):
            extension_native_helpers_path = os.path.join(panda_lib_path, 'pandac/extension_native_helpers.py')
            code_to_erase = '    imp.load_dynamic(module, pathname)'
            code_to_insert = '    cwd = os.getcwd()\n' \
                             '    os.chdir(os.path.dirname(pathname))\n' \
                             '    imp.load_dynamic(module, pathname)\n' \
                             '    os.chdir(cwd)'
            patch_file(extension_native_helpers_path, code_to_erase, code_to_insert)
        
        
        def patch_panda3d_py(panda_lib_path):
            extension_native_helpers_path = os.path.join(panda_lib_path, 'panda3d.py')
            code_to_erase = '        lib = cls.imp.load_dynamic(name, target)'
            code_to_insert = '        import os\n' \
                             '        cwd = os.getcwd()\n' \
                             '        os.chdir(os.path.dirname(target))\n' \
                             '        lib = cls.imp.load_dynamic(name, target)\n' \
                             '        os.chdir(cwd)'
        
            patch_file(extension_native_helpers_path, code_to_erase, code_to_insert)

            another_code_to_erase = 'sys.modules["panda3d"] = this'
            another_code_to_insert = 'sys.modules["panda3d"] = this\n' \
                             'for file in os.listdir(os.path.dirname(__file__)):\n' \
                             '    if file.endswith(".dylib") or file.endswith(".so"):\n' \
                             '        try:\n' \
                             '            panda3d_import_manager.libimport(os.path.splitext(file)[0])\n' \
                             '        except ImportError:\n' \
                             '            pass\n' 
        
            patch_file(extension_native_helpers_path, another_code_to_erase, another_code_to_insert)
        
        patch_extension_native_helpers_py(libdir)
        patch_panda3d_py(libdir)

#         write_file(os.path.join(robustus.env, 'lib/python2.7/site-packages/panda3d.pth'),
#                    'w',
#                    '%s/share/panda3d\n%s/lib/panda3d\n%s' % (robustus.env, robustus.env,
#                                                              '\n'.join(env_var_lines)))


    else:
        raise RequirementException('can\'t find panda3d-%s in robustus cache' % requirement_specifier.version)
