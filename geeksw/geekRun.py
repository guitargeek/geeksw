from geeksw.core import *

def __main__():
    import argparse

    parser = argparse.ArgumentParser(description='The geeks analysis framework inspired by cmssw.')
    parser.add_argument('producers_path', help="Directory with your geeksw modules")
    args = parser.parse_args()

    record = geek_run(args.producers_path)

__main__()
