import os
import subprocess

import uuid

from tqdm import tqdm


def call(cmd):
    """ Takes some system command and returns the output as a string.
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout.read().decode("utf-8")


def strip_server(path):
    """ Removes the server part from xrdfs output.

    Example input:
        root://polgrid4.in2p3.fr:1094//dpm/in2p3.fr/home/cms/trivcat/store/user/rembserj

    Output:
        /dpm/in2p3.fr/home/cms/trivcat/store/user/rembserj

    Note:
        Returns None if the input does not match the right pattern.
    """
    if not path.startswith("root://"):
        return None
    path = path[7:]
    hit = path.find("//")
    if hit < 0:
        return None
    return path[hit + 1 :]


def strip_root_path(path, root):
    assert path.startswith(root)
    return path[len(root) + 1 :]


def ls(path, recursive=False):
    """ If you put the path of a file, it will return None.
    """
    cmd = " ".join(["xrdfs", "polgrid4.in2p3.fr", "ls", "-u", "-R" * (recursive > 0), path])
    out = call(cmd)

    # Check for "Unable to open directory error"
    if "[ERROR]" in out and "[3005]" in out:
        return None

    files = out.split("\n")
    files = filter(lambda f: not f is None, map(strip_server, files))
    files = list(map(lambda f: strip_root_path(f, path), files))
    return files


def walk(root):
    """ Slightly dirty and ridiculous way to get the os.walk functionality because it
    just mimics the file structure in the local filesystem.
    """
    tmp_dirname = os.path.join("/tmp", str(uuid.uuid4()))
    subprocess.call(["mkdir", tmp_dirname])

    files = ls(root, recursive=True)

    print("Reproducing recursive directory structure for walk in " + tmp_dirname + ":")
    for f in tqdm(files):
        tmp_path = os.path.join(tmp_dirname, f)
        if os.path.isfile(os.path.dirname(tmp_path)):
            subprocess.call(["rm", os.path.dirname(tmp_path)])
        subprocess.call(["mkdir", "-p", os.path.dirname(tmp_path)])
        subprocess.call(["touch", tmp_path])

    for r, dirs, files in os.walk(tmp_dirname):
        yield os.path.join(root, r[len(tmp_dirname) + 1 :]), dirs, files

    subprocess.call(["rm", "-rf", tmp_dirname])
