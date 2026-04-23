#!/usr/bin/env python3
"""Wrap long lines in .tex files to at most WIDTH characters.

Lines longer than WIDTH are broken at word (space) boundaries.
Leading indentation is preserved on all continuation lines.
Lines that cannot be broken (no spaces) are left untouched.

Usage:
  python3 wrap_lines.py file1.tex [file2.tex ...]
  python3 wrap_lines.py --width 80 file1.tex
  python3 wrap_lines.py --dry-run file1.tex   # preview without writing
"""
import argparse
import sys

DEFAULT_WIDTH = 100


def wrap_line(line, width):
    """Break a single line at word boundaries. Returns one or more lines joined by newlines."""
    stripped = line.rstrip('\n')
    if len(stripped) <= width:
        return stripped

    indent_len = len(stripped) - len(stripped.lstrip(' \t'))
    prefix = stripped[:indent_len]
    content = stripped[indent_len:]

    words = [w for w in content.split(' ') if w]
    if not words:
        return stripped

    result = []
    current = prefix

    for word in words:
        if current == prefix:
            current += word
        elif len(current) + 1 + len(word) <= width:
            current += ' ' + word
        else:
            result.append(current)
            current = prefix + word

    if current != prefix:
        result.append(current)

    return '\n'.join(result)


def process(content, width):
    lines = content.split('\n')
    return '\n'.join(wrap_line(line, width) for line in lines)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='+', help='.tex files to process')
    parser.add_argument('--width', type=int, default=DEFAULT_WIDTH,
                        help=f'Max line length (default: {DEFAULT_WIDTH})')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print result to stdout instead of writing files')
    args = parser.parse_args()

    for path in args.files:
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()

        updated = process(original, args.width)

        if args.dry_run:
            sys.stdout.write(updated)
        else:
            if updated != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(updated)
                long_lines = sum(1 for ln in original.split('\n') if len(ln) > args.width)
                print(f'{path}: {long_lines} long lines wrapped')
            else:
                print(f'{path}: no changes')


if __name__ == '__main__':
    main()
