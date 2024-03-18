# This is NOT a YAML parser.  This script does the bare minimum to match
# comments with keys but may get it wrong.  Output from this script MUST be
# curated by a human.

import sys
import argparse

# Character string used to indicate the comment is a YamlDoc comment.
chars = '#-'


class LineProvider:
    '''
    A simple iterator type class. Mostly needed because occasionally we need
    to push a line back after searching for the end of a multi-line string.
    Also collapses lines that end with '\' into a single line.
    '''
    def __init__(self, inputPath: str):
        with open(inputPath) as f:
            self._lines = f.read().splitlines()
        self._current = 0
        self._previous = None

    def hasNext(self):
        return self._current < len(self._lines)


    def getNext(self):
        self._previous = self._current
        line = self._collect_line()
        return line

    def back(self):
        if self._previous is not None:
            self._current = self._previous
        else:
            self._current -= 1

    def _next_line(self):
        line = self._lines[self._current].rstrip(' ')
        self._current += 1
        return line

    def _collect_line(self):
        segments = []
        collecting = True
        while collecting and self.hasNext():
            line = self._next_line()
            if line.endswith('\\'):
                line = line.rstrip('\\')
            else:
                collecting = False
            segments.append(line)
        return ' '.join(segments)



def get_line_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def print_table_row(path: list, key: str, comments: list):
    key = key.replace('.', '\.')
    if len(path) == 0:
        full_path = key
    else:
        full_path = f"{'.'.join(path)}.{key}"
    print(f"| {full_path} | { ' '.join(comments)} |")


def main(filename: str, chars: str):
    lp = LineProvider(filename)
    path = []
    doc_lines = []
    indent_stack = [ 0 ]
    key = ''
    print("| Key | Description |")
    print("|-----|-------------|")
    while lp.hasNext():
        line = lp.getNext().rstrip()
        if line.lstrip().startswith(chars):
            doc_lines.append(line.replace(chars, '').strip())
            continue

        if len(line.strip()) == 0 or line.lstrip().startswith('#'):
            continue
        indent = get_line_indent(line)
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            path.append(key)
        elif indent < indent_stack[-1]:
            while indent != indent_stack[-1]:
                indent_stack.pop()
                path.pop()

        if ':' in line:
            kv = line.split(':')
            key = kv[0].strip()
            if len(doc_lines) > 0:
                print_table_row(path, key, doc_lines)
                doc_lines = []
        # Skip over multi-line strings
        if line.endswith('|') or line.endswith('|-') or line.endswith('>-'):
            while lp.hasNext() and get_line_indent(line) >= indent:
                line = lp.getNext()
            # The above loop finds the first line that is NOT part of the
            # multi-line string so we need to put that line back into the
            # buffer.
            lp.back()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="yamldoc",
        description="Generate a Markdown table with descriptions of the YAML keys in a Helm Chart's vales.yaml file.",
        epilog="Copyright 2023 The Galaxy Project"
    )
    parser.add_argument('filename', nargs=1)
    parser.add_argument('-c', '--chars', default="#-")
    args = parser.parse_args()
    main(args.filename[0], args.chars)