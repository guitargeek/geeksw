import shutil
import os


def copy_into(source, destination):
    """ Copy all files from source into destination recursively.

    Overwrites existing files.
    """
    files = []
    for r, d, f in os.walk(source):
        for file in f:
            full_filename = os.path.join(r, file)
            files.append("/".join(full_filename.split("/")[1:]))

    for f in files:
        dirname = os.path.join(destination, os.path.dirname(f))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(os.path.join(source, f), os.path.join(destination, f))


def descend(path):
    d = os.path.expanduser(path)
    l = os.listdir(d)
    subdirectories = [os.path.join(d, o) for o in l if os.path.isdir(os.path.join(d, o))]
    if len(subdirectories) == 0:
        return path
    if len(subdirectories) == 1:
        return descend(subdirectories[0])
    else:
        raise ValueError("Can't descent unambiguously to the bottom of " + path)
