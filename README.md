robustus
=======

Tool to make and configure python virtualenv, setup necessary packages and cache them if necessary.

When amount of 3rd-party libraries used by project grows it requires much effort and
time to setup working environment with all the libraries and tools installed and paths
configured. Robustus tries to minimize this effort by providing "one command" install
scripts and ability to cache binary versions of packages to reuse them in future.

### Prerequesties
* python 2.7
* virtualenv (to create new robustus environment)
* boto (to download/upload cache to amazon s3 servers)
* rsync (to download/upload cache to samba/ftp/http servers)
* pytest (for testing)


### Usage
First you need to create virtual environment.

    robustus env <dir> --cache <binary package cache dir> <other virtualenv options>

Or you can convert existing virtualenv into robustus environment (it will install
specific pip version and required packages). You can convert even virtualenv where
you installed robustus.

    robustus env <existing virtualenv> --cache <binary package cache dir>

Afterwards you can go to env directory and install packages using usual pip syntax.

    robustus install numpy==1.7.2
    robustus install -r <requirements file>
    robustus install <other pip options>

Robustus will store binary packages in the cache directory specified by --cache option
during creation of virtualenv ('wheelhouse' by default).
or you can specify binary package cache where to install package.

    robustus --cache ~/wheelhouse install numpy==1.7.2

You may also install non pip packages, e.g. opencv or cudamat. Robustus has
platform specific scripts to setup them.

In order to list binary packages cached in robustus cache you can use freeze command.

    robustus freeze

You may also want to reuse existing binary package cache. You can do that by
downloading cache directory before installing packages. Robustus has convenience
command to do that. Cache can be stored as a directory or *.tar.gz, *.tar.bz or
*.zip archive.

    robustus download-cache <cache url>

In the same manner you can upload cache.
  
    robustus upload-cache <cache url>
    robustus --cache ~/wheelhouse upload-cache <cache url>

Make sure that binary package cache is suitable for your platform. It is highly
recommended to use cached packages only on the machine there they have been compiled.
If robustus cache is not empty external packages will be added to robustus cache.

To upload/download from amazon S3 cloud you should also specify bucket name, key and secret key.

    robustus upload-cache cache.tar.bz -b <bucket_name> -k <key> -s <secret_key> --public
    robustus download-cache cache.tar.bz -b <bucket_name> -k <key> -s <secret_key>
    robustus download-cache https://s3.amazonaws.com/<bucket_name>/cache.tar.bz

### Cache Format

Robustus cache is a directory with binary package archives. Packages under distutils are compressed
using [wheel](https://pypi.python.org/pypi/wheel) tool. These are archives created using bdist
with *.whl extension.

Packages which doesn't support distutils doesn't have any specific format. Usually they are stored
just as a directory with set of headers/libraries/executables obtained using library build tool
installation utilities (e.g. cmake install).

Additionally robustus cache has .robustus directory where robustus specific information is stored.
For each cached package there is a file \<package_name\>__\<package_version\>.rob (dots replaced with
underscores). It is needed for robustus to know that package of specific version is stored in cache,
so during install it won't build it again. By default this file is empty, but installation scripts can
use it to store information required to install package (i.e. location of specific library within the
cache).

As you can see you can freely move cache and merge them by just copying files. Though it is dangerous
to remove files from the cache as well as move separate files from one cache to another.


### Tagging

Robustus supports tagging as a way of recording the state of the multi-repo project. Git
tags are created for all editable packages and pushed to the origin repo.

	 robustus tag tag-name

Later, this state can be retrieved by cloning the base repo and 

    git checkout tag-name
    robustus install -r requirements.txt --tag tag-name

Alternatively, you can also checkout a tag after cloning (this will not work if the requirements for the tag version are different) using:

    robustus checkout tag-name

Underneath this functionality is implemented by a useful utility command

	robustus perrepo anything after here

which will run whatever is specified once at each editable repo (including
the base repo). This can be used to update all dependencies (e.g. git pull ...).


### Misc

It it sometimes helpful to perform operations across all the editable repos in an
environment (such as git updates etc.).

    robustus perrepo [--not-base] operation

supports this.

A shortcut

    robustus reset

will reset all the editable repos (including the base repo) to master, discarding any changes.
By default this will warn you first (unless overridden with `-f`).
