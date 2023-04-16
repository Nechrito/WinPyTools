from collections import namedtuple
import os

ClassInfo = namedtuple("ClassInfo", ["using_statements", "class_inheritance"])

def get_package_name(cs_file, project_path):
    return os.path.dirname(os.path.relpath(cs_file, project_path)).replace(os.sep, '_')

def get_class_name(cs_file):
    return os.path.splitext(os.path.basename(cs_file))[0]
