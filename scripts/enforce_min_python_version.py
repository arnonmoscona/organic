import sys

min_version = (3, 6, 1)

version = tuple((sys.version_info[i] for i in range(3)))
min_version_str = '.'.join([str(i) for i in min_version])
if version[0] < 3:
    eval('print "minimum version of Python is", ' + min_version_str)
if version < min_version:
    print('Python minimum version for {}'.format(min_version_str))
    exit(1)
