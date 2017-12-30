"""
Compiles all .proto files found where there is a papi package next to them.
"""
import argparse
import os
import re


def get_papi_parents(rootDir):
    result = []
    for dir_name, sub_dirs, files in os.walk(rootDir):
        if 'papi' in sub_dirs:
            result.append(dir_name)
    return result


def make_expected_output_file(dir, file):
    output = '{}_pb2.py'.format(file[:-6])
    return os.path.join(dir, 'papi', output)


def find_proto_files(papi_parents):
    result = []
    for dir in papi_parents:
        for file in os.listdir(dir):
            full_path = os.path.join(dir, file)
            if not os.path.isfile(full_path):
                continue
            if not re.match(r'.*\.proto$', file):
                continue
            f = (dir, full_path, make_expected_output_file(dir, file))
            result.append(f)
    return result


def remove_files(proto_files):
    for dir_name, source, out in proto_files:
        if os.path.exists(out):
            print('Deleting', out)
            os.remove(out)


def ensure_papi_python_package(dir_name):
    init_script = os.path.join(dir_name, 'papi', '__init__.py')
    if not os.path.exists(init_script):
        print('Creating', init_script)
        open(init_script, 'a').close()


def out_is_older_than_source(source, out):
    if not os.path.exists(out):
        return False
    out_time = os.path.getmtime(out)
    source_time = os.path.getmtime(source)
    return out_time > source_time


def generate_commands(proto_files, force_flag, source_root):
    result = []
    for dir_name, source, out in proto_files:
        ensure_papi_python_package(dir_name)
        needs_update = not out_is_older_than_source(source, out)
        if needs_update or force_flag:
            out_dir = os.path.join(dir_name, 'papi')
            command = 'protoc --python_out={} {}'.format(source_root, source)
            result.append((command, source, out, out_dir))
    return result


def execute(commands, echo_flag):
    for command in commands:
        if echo_flag:
            print('> ', command)
        os.system(command)


def move_out_to_papi(in_out):
    for source, new_out, dir_name in in_out:
        parent_dir = dir_name[:-5]
        generated_out = os.path.join(parent_dir, new_out[len(dir_name)+1:])
        print('Moving', generated_out, new_out)
        os.rename(generated_out, new_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sources', help='The directory for the source root', default='.')
    parser.add_argument('--clean', action='store_true', help='delete existing output files '
                                                             'corresponding to .proto files')

    parser.add_argument('--force', action='store_true',
                        help='force generation of python protobuf classes '
                             'even if output file already exists')
    args = parser.parse_args()

    sources = args.sources
    force_flag = args.force
    clean_flag = args.clean
    echo_flag = True
    papi_parents = get_papi_parents(sources)
    proto_files = find_proto_files(papi_parents)

    if clean_flag:
        remove_files(proto_files)

    protoc_commands = generate_commands(proto_files, force_flag, sources)

    commands = [result[0] for result in protoc_commands]
    execute(commands, echo_flag)
    in_out = [(source, out, dir_name) for _, source, out, dir_name in protoc_commands]
    move_out_to_papi(in_out)
