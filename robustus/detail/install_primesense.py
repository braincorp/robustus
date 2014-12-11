import logging
import os


def install(robustus, requirement_specifier, rob_file, ignore_index):
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
    # patch file, so it'll be able to find primesense shared library
    logging.info('Patching primesense')
    file_to_patch = os.path.join(robustus.env, 'lib/python2.7/site-packages/primesense/openni2.py')
    with open(file_to_patch, "rt") as f:
        content = f.read()
    with open(file_to_patch, "wt") as f:
        f.write(content.replace("_default_dll_directories.append(\".\")",
                                "_default_dll_directories += ['.\', os.path.join(os.path.dirname(sys.executable), os.path.pardir, 'lib')]"))
    # remove cached file if exists
    pyc = os.path.splitext(file_to_patch)[0] + '.pyc'
    if os.path.exists(pyc):
        os.remove(pyc)
