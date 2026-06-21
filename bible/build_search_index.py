import argparse

from bible.search_index import build_search_index


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    build_search_index(args.source_dir, args.output)


if __name__ == "__main__":
    main()
