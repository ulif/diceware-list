import argparse


def get_cmdline_args(args=None):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Create a wordlist")
    parser.add_argument(
        '-l', '--len', default=8192, type=int,
        help='desired length of generated wordlist. Default: 8192')
    parser.add_argument(
        'dictfile', nargs='+', metavar='DICTFILE',
        type=argparse.FileType('rb'),
        help=("Dictionary file to read possible terms from. "
              "Multiple allowed. `-' will read from stdin."),
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='be verbose.')
    return parser.parse_args(args)


if __name__ == "__main__":
    args = get_cmdline_args()
    print(args)
