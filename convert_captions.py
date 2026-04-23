#!/usr/bin/env python3
"""Convert figure captions to use \figcaption{Title}{Description}.

Transforms:
  \caption{\textbf{Title} Description}  ->  \figcaption{Title}{Description}
  \caption{{\bf [mods] Title} Description}  ->  \figcaption{Title}{Description}

Captions without a leading bold group are left unchanged.

Usage:
  python3 convert_captions.py file1.tex [file2.tex ...]
"""
import re
import sys


def find_closing_brace(text, pos):
    """Return position of the closing brace matching the opening brace at pos."""
    assert text[pos] == '{'
    depth = 0
    i = pos
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            i += 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def extract_title_and_desc(caption_content):
    """
    Given the raw content of \\caption{...}, return (title, description) or None.

    Handles:
      \\textbf{Title} rest
      {\\bf [\\small etc.] Title} rest
    """
    s = caption_content.lstrip()

    # Pattern 1: \textbf{Title} rest
    if s.startswith('\\textbf{'):
        brace_pos = len(caption_content) - len(s) + len('\\textbf')
        end = find_closing_brace(caption_content, brace_pos)
        if end == -1:
            return None
        title = caption_content[brace_pos + 1:end]
        description = caption_content[end + 1:]
        return title, description

    # Pattern 2: {\bf [optional size/font commands] Title} rest
    if s.startswith('{'):
        inner_open = len(caption_content) - len(s)
        inner_close = find_closing_brace(caption_content, inner_open)
        if inner_close == -1:
            return None
        inner = caption_content[inner_open + 1:inner_close].lstrip()
        if not (inner.startswith('\\bf') or inner.startswith('\\bfseries')):
            return None
        # Strip leading font/size declarations
        inner = re.sub(
            r'^(\\bf(?:series)?|\\small|\\normalsize|\\large|\\Large|\\footnotesize)\s*',
            '', inner)
        inner = re.sub(
            r'^(\\bf(?:series)?|\\small|\\normalsize|\\large|\\Large|\\footnotesize)\s*',
            '', inner)
        title = inner.rstrip()
        description = caption_content[inner_close + 1:]
        return title, description

    return None


def convert_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = []
    i = 0
    converted = 0
    skipped = 0

    while i < len(content):
        # Match \caption{ but NOT \caption[ (already has an optional arg)
        m = re.search(r'\\caption\{', content[i:])
        if m is None:
            result.append(content[i:])
            break

        match_start = i + m.start()
        result.append(content[i:match_start])

        brace_open = match_start + len('\\caption')
        brace_close = find_closing_brace(content, brace_open)
        if brace_close == -1:
            result.append(content[match_start:match_start + 9])
            i = match_start + 9
            continue

        caption_content = content[brace_open + 1:brace_close]
        extracted = extract_title_and_desc(caption_content)

        if extracted is not None:
            title, description = extracted
            result.append(f'\\figcaption{{{title}}}{{{description}}}')
            converted += 1
        else:
            result.append(f'\\caption{{{caption_content}}}')
            skipped += 1

        i = brace_close + 1

    new_content = ''.join(result)
    if converted > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return converted, skipped


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    total = 0
    for path in sys.argv[1:]:
        converted, skipped = convert_file(path)
        print(f'{path}: {converted} converted, {skipped} left as-is')
        total += converted

    print(f'\nTotal: {total} captions converted')
