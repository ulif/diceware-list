import argparse


def get_cmdline_args(args=None):
    """Handle commandline options.
    """
    parser = argparse.ArgumentParser(description="Create a wordlist")
    parser.add_argument(
        '-l', '--length', default=8192, type=int, dest='length',
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


def filtered_by_len(iterator, min_len=3, max_len=None):
    """Get an iterator over words from `iterator`.

    Only words of len `min_len`..`max_len` are included.

    The lines we find (and that meet our requirements) are yielded.
    """
    for line in iterator:
        line = line.strip()
        if (len(line) < min_len) or (max_len and len(line) > max_len):
            continue
        yield line


def generate_wordlist(input_terms, length=8192):
    """Generate a diceware wordlist from dictionary list.

    `input_terms`: iterable over all strings to consider as wordlist item.

    `length`: desired length of wordlist to generate.

    Returns an iterator that yields at most `length` items. Double
    entries are removed.
    """
    last = None
    num = 0
    for term in sorted(input_terms):
        if num >= length:
            break
        if term == last:
            continue
        last = term
        num += 1
        yield term


def term_iterator(file_descriptors):
    """Yield terms from files in `file_descriptors`.

    `file_descriptors` must be open for reading.
    """
    for fd in file_descriptors:
        for term in fd:
            yield term.strip()


def main():
    """Main function of script.

    Output the wordlist determined by commandline args.
    """
    args = get_cmdline_args()
    all_terms = term_iterator(args.dictfile)
    for term in generate_wordlist(all_terms, args.length):
        print(term.decode("utf-8"))


if __name__ == "__main__":
    main()
