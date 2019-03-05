import os
import sys


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def humanbytes(B):
    "Return the given bytes as a human friendly KB, MB, GB, or TB string"
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return "{0:.0f} {1}".format(B, "Byte")
    elif KB <= B < MB:
        return "{0:.1f} KB".format(B / KB)
    elif MB <= B < GB:
        return "{0:.1f} MB".format(B / MB)
    elif GB <= B < TB:
        return "{0:.1f} GB".format(B / GB)
    elif TB <= B:
        return "{0:.1f} TB".format(B / TB)


def load_module(name, path_to_file):
    if sys.version_info < (3, 0):
        import imp

        return imp.load_source(name, path_to_file)
    if sys.version_info < (3, 5):
        from importlib.machinery import SourceFileLoader

        return SourceFileLoader(name, path_to_file).load_module()
    else:
        import importlib.util

        spec = importlib.util.spec_from_file_location(name, path_to_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
