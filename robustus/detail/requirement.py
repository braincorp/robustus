# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import re
import urlparse
from git_accessor import GitAccessor
import logging
import urllib
from collections import OrderedDict, defaultdict
import string
import hashlib


class RequirementException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class Requirement(object):
    def __init__(self, *args, **kwargs):
        """
        Create requirement.
        @args: name, version
        @kwargs: name, version, url, rob_filename
        Examples:
        >>> Requirement('numpy', '1.7.2')
        Requirement(name='numpy', version='1.7.2')
        >>> Requirement(url='http://requirement.org/requirement.zip')
        Requirement(url='http://requirement.org/requirement.zip')
        >>> Requirement(rob_filename='numpy__1_7_1.rob')
        Requirement(name='numpy', version='1.7.1')
        """
        self.name = kwargs.get('name', None)
        self.version = kwargs.get('version', None)
        self.url = None
        self.path = None
        self.editable = kwargs.get('editable', False)
        if 'url' in kwargs:
            self.url = urlparse.urlparse(kwargs['url'])
        if len(args) > 0:
            self.name = args[0]
            if len(args) > 1:
                self.version = args[1]
        if 'specifier' in kwargs:
            self._from_specifier(kwargs['specifier'])
        elif 'rob_filename' in kwargs:
            self._from_rob(kwargs['rob_filename'])

    def is_ros_package(self):
        """ROS packages are treated differently."""
        return self.name =='ros_overlay'

    def _from_rob(self, rob_filename):
        """
        Return package name and version from package rob file name
        @return: (name, version, url, allow_greater_version)
        Examples:
        >>> Requirement()._from_rob('numpy__1_7_2.rob')
        ('numpy', '1.7.2', None)
        >>> Requirement()._from_rob('scipy.rob')
        ('scipy', None, None)
        >>> Requirement()._from_rob('/path/to/somewhere/scipy.rob')
        ('scipy', None, None)
        """
        assert(rob_filename.endswith('.rob'))

        rob_basename = os.path.basename(rob_filename)
        if rob_basename.find('__') != -1:
            self.name, self.version = rob_basename[:-4].split('__')
            self.version = self.version.replace('_', '.')
        else:
            self.name = rob_basename[:-4]
            self.version = None
        self.url = None

        return self.name, self.version, self.url

    def __repr__(self):
        str = 'Requirement('
        if self.name is not None:
            str += 'name=\'%s\'' % self.name
            if self.version is not None:
                str += ', version=\'%s\'' % self.version
        elif self.url is not None:
            str += 'url=\'%s\'' % self.url.geturl()
        elif self.path is not None:
            str += 'path=\'%s\'' % self.path
        str += ')'
        return str

    def freeze(self):
        """
        @return: string representing requirement in pip format with all necessary flags
        Examples:
        >>> Requirement('numpy', '1.7.2').freeze()
        'numpy==1.7.2'
        >>> Requirement('numpy', '1.7.2', editable=True).freeze()
        '-e numpy==1.7.2'
        >>> Requirement(url='http://requirement.org/requirement.zip').freeze()
        'http://requirement.org/requirement.zip'
        >>> Requirement(url='http://requirement.org/requirement.zip', editable=True).freeze()
        '-e http://requirement.org/requirement.zip'
        """
        str = ''
        if self.editable:
            str += '-e '
        return str + self._freeze_base()

    def _freeze_base(self):
        """
        @return: string representing requirement in pip format without flags
        Examples:
        >>> Requirement('numpy', '1.7.2', editable = True)._freeze_base()
        'numpy==1.7.2'
        >>> Requirement('numpy', '1.7.2', editable = False)._freeze_base()
        'numpy==1.7.2'
        >>> Requirement(url='http://requirement.org/requirement.zip')._freeze_base()
        'http://requirement.org/requirement.zip'
        """
        if self.url is not None:
            return self.url.geturl()
        elif self.path is not None:
            return self.path
        else:
            if self.version is not None:
                return '%s==%s' % (self.name, self.version)
            return self.name

    def rob_filename(self):
        """
        Get filename to store information about cached package.
        TODO: add support for packages installed via urls.
        @return: filename to store package information <package_name>__<package_version>.rob
        (dots replaced with underscores)
        Examples:
        >>> Requirement('numpy', '1.7.2').rob_filename()
        'numpy__1_7_2.rob'
        >>> Requirement('scipy').rob_filename()
        'scipy.rob'
        """
        if self.is_ros_package():
            return self._ros_rob_filename()
        else:
            if self.name is not None:
                if self.version is not None:
                    version = self.version.replace('.', '_')
                    return '%s__%s.rob' % (self.name, version)
            return '%s.rob' % self.name

    def _ros_rob_filename(self):
        """ROS versions can be very long - too long for filenames so we just use a hash."""
        return 'ros_overlay__' + self.version_hash()

    def version_hash(self):
        """Return a string hash of the version useful for unique filenames etc.
        """
        return hashlib.sha256(self.version).hexdigest()


class RequirementSpecifier(Requirement):
    def __init__(self, *args, **kwargs):
        """
        Create requirement specifier.
        @args: same as in Requirement
        @kwargs: same as in Requirement plus 'specifier', 'allow_greater_version'
        Examples:
        >>> RequirementSpecifier(url='http://requirement.org/requirement.zip')
        RequirementSpecifier(url='http://requirement.org/requirement.zip')
        >>> RequirementSpecifier(specifier='numpy>=1.7.1')
        RequirementSpecifier(name='numpy', version='1.7.1', allow_greater_version)
        >>> RequirementSpecifier(specifier='-e numpy>=1.7.1')
        RequirementSpecifier(name='numpy', version='1.7.1', allow_greater_version, editable)
        """
        Requirement.__init__(self, *args, **kwargs)
        self.allow_greater_version = kwargs.get('allow_greater_version', False)
        if 'specifier' in kwargs:
            self._from_specifier(kwargs['specifier'])

    def override_branch(self, tag):
        """Modified the specified branch to a given tag or branch."""
        assert self.editable
        if self.url is None:
            logging.info('Ignoring override for local folder')
            return
        actual_url = self.url.geturl()
        assert actual_url[0:3] == 'git'
        match = re.match('(.*)@([^#]*)#(.*)', actual_url)
        assert match is not None
        new_url = match.group(1) + '@' + tag + '#' + match.group(3)
        logging.info('New URL is %s' % new_url)
        self.url = urlparse.urlparse(new_url)

    def _from_specifier(self, specifier):
        """
        Extract requirement name and version from requirement string
        @return: (name, version, url, allow_greater_version, editable)
        Examples:
        >>> RequirementSpecifier()._from_specifier('numpy==1.7.2')
        ('numpy', '1.7.2', False, False)
        >>> RequirementSpecifier()._from_specifier('-e numpy==1.7.2')
        ('numpy', '1.7.2', False, True)
        >>> RequirementSpecifier()._from_specifier('   numpy == 1.7.2  ')
        ('numpy', '1.7.2', False, False)
        >>> RequirementSpecifier()._from_specifier('   numpy >= 1.7.2  ')
        ('numpy', '1.7.2', True, False)
        >>> RequirementSpecifier()._from_specifier('   numpy == 1.7.2  # comment')
        ('numpy', '1.7.2', False, False)
        >>> RequirementSpecifier()._from_specifier('  -e    numpy == 1.7.2  # comment')
        ('numpy', '1.7.2', False, True)
        >>> RequirementSpecifier()._from_specifier('numpy')
        ('numpy', None, False, False)
        >>> RequirementSpecifier()._from_specifier('pytest-cache==0.7')
        ('pytest-cache', '0.7', False, False)
        >>> RequirementSpecifier()._from_specifier('theano==0.6rc3')
        ('theano', '0.6rc3', False, False)
        >>> RequirementSpecifier()._from_specifier('http://some_url/some_package.tar.gz')
        ('http://some_url/some_package.tar.gz', False)
        >>> RequirementSpecifier()._from_specifier('   http://some_url/some_package.tar.gz')
        ('http://some_url/some_package.tar.gz', False)
        >>> RequirementSpecifier()._from_specifier('-e git+https://github.com/company/my_package@branch_name#egg=my_package')
        ('git+https://github.com/company/my_package@branch_name#egg=my_package', True)
        >>> RequirementSpecifier()._from_specifier('/dev')
        ('/dev', False)
        >>> RequirementSpecifier()._from_specifier('-e /dev')
        ('/dev', True)
        >>> RequirementSpecifier()._from_specifier('numpy==1.7.2==1.7.2')
        Traceback (most recent call last):
            ...
        RequirementException: invalid requirement specified "numpy==1.7.2==1.7.2"
        >>> RequirementSpecifier()._from_specifier('   ')
        Traceback (most recent call last):
            ...
        RequirementException: invalid requirement specified ""
        >>> RequirementSpecifier()._from_specifier('numpy==')
        Traceback (most recent call last):
            ...
        RequirementException: invalid requirement specified "numpy=="
        """
        self.name = None
        self.version = None
        self.allow_greater_version = False
        self.editable = False
        self.url = None
        self.path = None

        specifier = specifier.lstrip()
        specifier = specifier.rstrip()
        if specifier.startswith('-e'):
            self.editable = True
            specifier = specifier[2:].lstrip()
        # check if requirement is url
        url = urlparse.urlparse(specifier)
        if len(url.scheme) > 0:
            self.url = url
            # try to extract name from egg, demand name if requirement is editable
            try:
                actual_url, self.name = _split_egg_and_url(self.url.geturl())
            except RequirementException:
                if self.editable:
                    raise

            return self.url.geturl(), self.editable

        path_specifier = self._extract_path_specifier(specifier)
        if path_specifier is not None:
            self.path = path_specifier
            return self.path, self.editable

        mo = re.match(r'^ros_overlay\w*==(.*)', specifier)
        if mo is not None:
            # This is a ROS package description
            self.name = 'ros_overlay'
            self.version = mo.group(1)
            self.allow_greater_version = False
            self.editable = False
        else:
            # check if requirement is in <package>[==|>=]<version> format
            mo = re.match(r'^([\w-]+)\s*(?:([>=]=)?\s*([\w.]+))?\s*(?:#.*)?$', specifier)
            if mo is None:
                raise RequirementException('invalid requirement specified "%s"' % specifier)
            self.name, self.version = mo.group(1, 3)
            # check if user accepts greater version, i.e. >= is used
            version_specifier = mo.group(2)
            if version_specifier is not None and version_specifier == '>=':
                self.allow_greater_version = True

        return self.name, self.version, self.allow_greater_version, self.editable

    def _extract_path_specifier(self, specifier):
        if specifier.isspace() or len(specifier) == 0:
            return None
        try:
            path = os.path.abspath(os.path.expanduser(specifier))
            if os.path.exists(path):
                return path
            else:
                return None
        except SyntaxError:
            return None

    def __repr__(self):
        str = Requirement.__repr__(self).replace('Requirement', 'RequirementSpecifier')[:-1]
        if self.allow_greater_version:
            if len(str) >= len('RequirementSpecifier('):
                str += ', '
            str += 'allow_greater_version'
        if self.editable:
            str += ', editable'
        str += ')'
        return str

    def allows(self, other):
        """
        Check if this requirement specifier allows to install specified requirement.
        I.e. it has same name and version or downloaded from same url.
        @other: requirement
        Examples:
        >>> RequirementSpecifier('numpy', '1.7.2').allows(Requirement('numpy', '1.7.2'))
        True
        >>> RequirementSpecifier('numpy', '1.7.2').allows(Requirement('scipy', '1.7.2'))
        False
        >>> RequirementSpecifier('numpy').allows(Requirement('numpy', '1.7.2'))
        True
        >>> RequirementSpecifier('numpy', '1.7.2').allows(Requirement('numpy'))
        False
        >>> RequirementSpecifier(url='http://req.org/req.zip').allows(Requirement(url='http://req.org/req.zip'))
        True
        """
        if self.url is not None and other.url is not None:
            # downloaded from same url
            return self.url == other.url
        elif self.path is not None and other.path is not None:
            # obtained from the same path
            return self.path == other.path
        elif self.name is not None and other.name is not None:
            # check if name and version match
            # TODO: check for allow_greater_version, note that version can have weird format, i.e. '1.1rc3'
            return self.name == other.name and (self.version is None or other.version == self.version)
        else:
            return False

    def base_name(self):
        """
        @return: string representing base name of the requirement
        Examples:
        >>> RequirementSpecifier(specifier='numpy==1.7.2').base_name()
        'numpy'
        >>> RequirementSpecifier(specifier='-e numpy==1.7.2').base_name()
        'numpy'
        >>> RequirementSpecifier(specifier='numpy').base_name()
        'numpy'
        >>> RequirementSpecifier(specifier='theano==0.6rc3').base_name()
        'theano'
        >>> RequirementSpecifier(specifier='http://some_url/some_package.tar.gz').base_name()
        'http://some_url/some_package.tar.gz'
        >>> RequirementSpecifier(specifier='-e git+https://github.com/company/my_package@branch_name#egg=my_package').base_name()
        'my_package'
        >>> RequirementSpecifier(specifier='git+https://github.com/company/my_package@branch_name#egg=my_package').base_name()
        'my_package'
        >>> RequirementSpecifier(specifier='git+https://github.com/company/my_package').base_name()
        'git+https://github.com/company/my_package'
        >>> RequirementSpecifier(specifier='/dev').base_name()
        '/dev'
        >>> RequirementSpecifier(specifier='-e /dev').base_name()
        '/dev'
        """
        if self.name is not None:
            return self.name
        if self.path is not None:
            return self.path
        if self.url is not None:
            return self.url.geturl()
        raise Exception('Can not compute base name for %s' % self.freeze())


def _split_egg_and_url(url):
    egg_position = url.find('#egg')
    if egg_position < 0:
        raise RequirementException(
            'Editable git link %s has to contain egg information.'
            'Example: -e git+https://github.com/company/my_package@branch_name#egg=my_package' % 
            url)
    return url[:egg_position], url[egg_position+5:]


def _obtain_requirements_from_remote_package(git_accessor, original_req,
                                             override_tag=None, ignore_missing_refs = False):
    url = original_req.url.geturl()[4:]
    url, name = _split_egg_and_url(url)

    if url.startswith('ssh://git@'):
        # searching '@' after git@
        at_pos = url.find('@', 11) 
    else:
        at_pos = url.find('@')

    if at_pos > 0:
        link, tag = url[:at_pos], url[at_pos+1:]
    else:
        link, tag = url, None
    if override_tag:
        tag = override_tag

    logging.info('Obtaining requirements from remote package %s(%s)' % (link, tag))
    return git_accessor.access(link, tag, 'requirements.txt',
                               ignore_missing_refs = ignore_missing_refs)


def _obtain_requirements_from_local_package(original_req):
    requirement_file_path = os.path.join(original_req.path, 'requirements.txt')
    if os.path.exists(requirement_file_path):
        with open(requirement_file_path, 'r') as req_file:
            content = req_file.readlines()
        return content
    else:
        return None


def do_requirement_recursion(git_accessor, original_req, visited_sites = None,
                             tag=None, ignore_missing_refs = False):
    '''
    Recursive extraction of requirements from -e git+.. pip links.
    @return: list
    '''
    if visited_sites is None:
        visited_sites = {}

    if not original_req.editable or \
            (original_req.url is None and original_req.path is None):
        return [original_req]

    if original_req.freeze() in visited_sites:
        req_file_content = visited_sites[original_req.freeze()]
    else:
        if original_req.url is not None:
            if not original_req.url.geturl().startswith('git+'):
                return [original_req]
            else:
                req_file_content = _obtain_requirements_from_remote_package(
                    git_accessor, original_req, override_tag=tag,
                    ignore_missing_refs = ignore_missing_refs)
        else:
            req_file_content = _obtain_requirements_from_local_package(original_req)
        # why is req_file_content not cleaned before adding it to visited_sites?

        visited_sites[original_req.freeze()] = req_file_content

    if req_file_content is None:
        raise RequirementException('Editable requirement %s does not have a requirements.txt file'
                                   % original_req.freeze())

    return expand_requirements_specifiers(req_file_content, git_accessor, visited_sites,
                                          tag=tag, ignore_missing_refs=ignore_missing_refs) + [original_req]


def _filter_requirements_lines(lines):
    '''
    Remove commented and empty lines. Concatenate lines separated with '\'
    '''
    lines = [l for l in lines if not(l.isspace() or (len(l) < 2))]
    lines = [l for l in lines if not(l[0] == '#')]
    lines = [l.strip() for l in lines]
    filtered_lines = []
    concatenation = ''
    for l in lines:
        if l.endswith('\\'):
            concatenation += l[:-1]
        else:
            if len(concatenation):
                # the last line of concatenation
                concatenation += l
                filtered_lines.append(concatenation)
                concatenation = ''
            else:
                # normal line
                filtered_lines.append(l)
    if len(concatenation):
        filtered_lines.append(concatenation)
    return filtered_lines


def _filter(string):
    """
    Remove comments and empty lines
    :param string:
    :return: cleaned string
    """
    string = string.strip()
    if not len(string):
        return ""
    # Filter comment lines
    if (string[0] == '#'):
        return ""

    return string


def expand_requirements_specifiers(specifiers_list, git_accessor = None, visited_sites = None, tag=None, ignore_missing_refs = False):
    '''
    Nice dirty hack to have a clean workflow:)
    In order to process hierarchical dependencies, we assume that -e git+ links
    may contain another requirements.txt file that we will include.
    
    Another way of doing that is to have dependencies only in setup.py and
    run 'python setup.py egg_info" for each package and analyse results
    (this is what pip does to process all dependencies in pip).
    However we loosing wheeling capability - robustus will never get control
    back if pip started to process dependencies from egg_info.
    '''

    if visited_sites is None:
        visited_sites = {}

    assert(isinstance(specifiers_list, (list, tuple)))
    requirements = []
    if git_accessor is None:
        git_accessor = GitAccessor()

    # remove comments, empty lines, concatenate lines with '\'
    filtered_lines = _filter_requirements_lines(specifiers_list)

    for line in filtered_lines:
        r = RequirementSpecifier(specifier=line)
        if r.freeze() not in [ritem.freeze() for ritem in requirements]:
            requirements += do_requirement_recursion(git_accessor, r, visited_sites,
                                                     tag=tag,
                                                     ignore_missing_refs = ignore_missing_refs)
            requirements = remove_duplicate_requirements(requirements)

    return requirements


def read_requirement_file(requirement_file, tag, ignore_missing_refs = False, **kwargs):
    with open(requirement_file, 'r') as req_file:
        specifiers_list = req_file.readlines()
    return expand_requirements_specifiers(specifiers_list, tag=tag,
                                          ignore_missing_refs = ignore_missing_refs, **kwargs)


def parse_visited(visited_sites):
    """
    Parse <Dict<list>> visited_sites and determine which packages (+ versions) are included from which repos.

    :param visited_sites: return by argument visited_sites dict from expand_requirements_specifiers()
    :return: defaultdict<set> that maps packages to all repos that included them
    """

    check_list = visited_sites.keys()
    visited = []

    # Stores where package was included from
    package_from = defaultdict(set)

    while len(check_list):
        current_node = check_list.pop(0)

        visited.append(current_node)

        for child in visited_sites[current_node]:
            child = _filter(child)

            # If contains '==', '>=' or 'tar.gz', this is a package name
            if not child in visited and child.find('==') != -1 or child.find('>=') != -1 \
               or child.find('tar.gz') != -1:
                    package_from[child].add(current_node)
    return package_from


def generate_dependency_list(visited_sites):
    '''
    Generate list of all packages that were included, and
    where they were included from, specified by version.

    TODO: ros_overlay is special - figure out how
          to deal with this properly.

    TODO: Ideally, to be installed versions should
          be highlighted.
    '''

    package_from_versioned = parse_visited(visited_sites)

    all_packages = package_from_versioned.keys()

    package_version_from = defaultdict(dict)

    result = ''

    for package in all_packages:
        if package.find('tar.gz') != -1:
            package_ = package
            version = "[^check package name^]"
        else:
            # Ignore > specifier
            package_ = package.replace('>', '=')
            package_, version = package_.split('==')

        package_version_from[package_][version] = package_from_versioned[package]

    # Print packages in alphabetical order (a-z)
    sorted_packages = sorted(package_version_from.keys(), key=str.lower)

    for key in sorted_packages:
        result += '\n %s\n' % (key)
        for version in package_version_from[key].keys():
            result += '\t version %s, included from:\n' % (version)
            for includer in package_version_from[key][version]:
                result += '\t\t%s\n' %(includer)
    return result


def remove_duplicate_requirements(requirements_list):
    '''
    Given list of requirements, removes all duplicates of requirements comparing
    then using base_name() strings. base_name() returns the main name of the package
    without version or branch, therefore we will keep only the most latest entry with
    version.
    '''
    result = OrderedDict()
    ros_overlay_counter = 0
    for r in requirements_list:
        name = r.base_name()
        if name == 'ros_overlay':
            name += str(ros_overlay_counter)
            ros_overlay_counter += 1
        result[name] = r
    return result.values()
