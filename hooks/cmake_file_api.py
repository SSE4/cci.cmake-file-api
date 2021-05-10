# -*- coding: utf-8 -*-

import fnmatch
import json
import os
import sys
import textwrap
from conans import tools

SKIP_TARGETS = ["ZERO_CHECK", "ALL_BUILD"]

component_template = textwrap.dedent("""
        self.cpp_info.components["{component}"].names["cmake_find_package"] = "{name}"
        self.cpp_info.components["{component}"].names["cmake_find_package_multi"] = "{name}"
        self.cpp_info.components["{component}"].libs = ["{link}"]
        {requires}
""")

cmake_template = textwrap.dedent("""
        self.cpp_info.names["cmake_find_package"] = "{name}"
        self.cpp_info.names["cmake_find_package_multi"] = "{name}"
""")

requires_template = 'self.cpp_info.components["{component}"].requires = [{requires}]'

def find_dir_containing_file(conanfile, filename):
    for root, _, filenames in os.walk(conanfile.build_folder):
        for f in filenames:
            if f == filename:
                return root
    return None

def find_cmake_build_dir(conanfile):
    return find_dir_containing_file(conanfile, 'CMakeCache.txt')

def find_cmake_dir(conanfile):
    return find_dir_containing_file(conanfile, 'CMakeLists.txt')

def api_dir(cmake_build_dir):
    return os.path.join(cmake_build_dir, '.cmake', 'api', 'v1')

def create_query(cmake_build_dir):
    query_dir = os.path.join(api_dir(cmake_build_dir), 'query')
    os.makedirs(query_dir)
    tools.save(os.path.join(query_dir, 'codemodel-v2'), '')

def pre_build(output, conanfile, **kwargs):
    if conanfile.name == 'test_package' or conanfile.name is None:
        # not interested in test_package...
        return
    cmake_dir = find_cmake_dir(conanfile)
    if not cmake_dir:
        # probably, doesn't use a CMake build system
        return

    output.info('found CMake directory: "%s"' % cmake_dir)

    for build_dir in [cmake_dir, os.path.join(cmake_dir, "build_folder")]:
        create_query(build_dir)

def run(output, reply_dir, build_type, conanfile_name):
    message = ''
    for filename in os.listdir(reply_dir):
        if fnmatch.fnmatch(filename, "codemodel-v2-*.json"):
            codemodel = json.loads(tools.load(os.path.join(reply_dir, filename)))
            if 'configurations' not in codemodel:
                output.warn("codemodel doesn't have configurations")
                return
            for configuration in codemodel['configurations']:
                if 'name' not in configuration:
                    output.warn("configuration doesn't have a name")
                    continue
                if configuration['name'] == build_type:
                    if 'projects' not in configuration:
                        output.warn("configuration %s doesn't have projects" % configuration['name'])
                        continue
                    if 'targets' not in configuration:
                        output.warn("configuration %s doesn't have targets" % configuration['name'])
                        continue
                    for project in configuration['projects']:
                        if 'name' not in project:
                            output.warn("project doesn't have a name")
                            continue
                        if project['name'] != 'cmake_wrapper':
                            output.info('found CMake project: "%s"' % project['name'])
                            if project['name'] != conanfile_name:
                                name = project['name']
                                output.warn('project name "%s" is different from conanfile name "%s"' % (name, conanfile_name))

                                message += cmake_template.format(name=name)
                    for target in configuration['targets']:
                        if 'name' not in target:
                            output.warn("target doesn't have a name")
                            continue
                        if target['name'] not in SKIP_TARGETS:
                            target_js = json.loads(tools.load(os.path.join(reply_dir, target['jsonFile'])))
                            if 'install' in target_js:
                                if 'name' not in target_js:
                                    output.warn("target.js doesn't have a name")
                                    continue
                                if 'nameOnDisk' not in target_js:
                                    output.warn("target.js doesn't have a nameOnDisk")
                                    continue
                                if 'type' not in target_js:
                                    output.warn("target.js doesn't have a type")
                                    continue
                                name = target_js['name']
                                nameOnDisk = target_js['nameOnDisk']
                                type = target_js['type']
                                dependencies = target_js.get('dependencies', [])
                                requires = []
                                for dependency in dependencies:
                                    if 'id' not in dependency:
                                        output.warn("dependency doesn't have an id")
                                        continue
                                    id = dependency["id"]
                                    dependency_name, _ = id.split("::@")
                                    if dependency_name not in SKIP_TARGETS:
                                        requires.append(dependency_name)
                                if len(requires):
                                    requires = ', '.join(['"%s"' % r for r in requires])
                                    requires = requires_template.format(component=name, requires=requires)
                                else:
                                    requires = ''
                                if type != 'EXECUTABLE':
                                    output.info('found CMake %s target: "%s" ("%s")' % (type, name, nameOnDisk))
                                    link = nameOnDisk
                                    if fnmatch.fnmatch(nameOnDisk, '*.lib'):
                                        link = nameOnDisk[:-4]
                                    if fnmatch.fnmatch(nameOnDisk, '*.dll'):
                                        link = nameOnDisk[:-4]
                                    if fnmatch.fnmatch(nameOnDisk, 'lib*.a'):
                                        link = nameOnDisk[3:-2]
                                    if name != conanfile_name:
                                        output.warn('target name "%s" is different from conanfile name "%s"' % (name, conanfile_name))
                                        message += component_template.format(name=name, component=name, link=link, requires=requires)
                    if message:
                        output.warn('consider adding the following code to the "package_info" method:')
                        output.warn(message)
                    break

def post_build(output, conanfile, **kwargs):
    if conanfile.name == 'test_package' or conanfile.name is None:
        # not interested in test_package...
        return
    cmake_build_dir = find_cmake_build_dir(conanfile)
    if not cmake_build_dir:
        # probably, doesn't use a CMake build system
        return

    output.info('found CMake build directory: "%s"' % cmake_build_dir)

    reply_dir = os.path.join(api_dir(cmake_build_dir), 'reply')

    if not os.path.isdir(reply_dir):
        create_query(cmake_build_dir)

        with tools.chdir(cmake_build_dir):
            # re-run CMake
            conanfile.run('cmake .')

    assert os.path.isdir(reply_dir)
    build_type = conanfile.settings.get_safe('build_type') or 'Debug'

    run(output, reply_dir, build_type, conanfile.name)

class SimpleOutput(object):
    def warn(self, msg):
        print(msg)
    def info(self, msg):
        print(msg)

if __name__ == '__main__':
    output = SimpleOutput()
    run(output, sys.argv[1], "Release", "test")
