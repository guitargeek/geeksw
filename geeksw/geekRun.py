from .framework import geek_run


def __main__():
    import argparse

    parser = argparse.ArgumentParser(
        description="The geeks analysis framework inspired by CMSSW."
    )
    parser.add_argument("config_file", help="configuration file")
    args = parser.parse_args()

    record = geek_run(args.config_file)
