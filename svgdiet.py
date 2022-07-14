#!/usr/bin/env python

import xml.etree.cElementTree
import hashlib
import os
import argparse

class Cleaner:
    def __init__(self):
        self.removed = 0

    def clean(self, root):
        return self.handle_element(root)

    def handle_element(self, element):
        seen = {}
        duplicates = []
        for child in element:
            # Only deal with leaf nodes - 'rect' tag is the biggest issue here
            if len(child) == 0:
                h = hashlib.md5(str(child.attrib).encode('utf-8')).hexdigest()
                if h not in seen:
                    seen[h] = True
                else:
                    duplicates.append(child)
                    self.removed += 1

        for dupe in duplicates:
            element.remove(dupe)

        for el in element:
            self.handle_element(el)


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_file_size(filename):
    file_size = os.path.getsize(filename)
    file_string = sizeof_fmt(file_size, "B")
    return file_string


def main():

    parser = argparse.ArgumentParser(description='put an svg on a diet')
    parser.add_argument('input_file', help='the input svg')
    parser.add_argument('output_file', help='the output filename')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite existing output file')
    args = parser.parse_args()
    output_file = args.output_file
    input_file = args.input_file
    overwrite = args.overwrite

    xml.etree.cElementTree.register_namespace('', "http://www.w3.org/2000/svg")
    xml.etree.cElementTree.register_namespace('xlink', "http://www.w3.org/1999/xlink")
    tree = xml.etree.cElementTree.parse(input_file)
    root = tree.getroot()

    if not os.path.exists(input_file):
        print(f'input file "{input_file}" does not exist, exiting.')
        exit(-1)
    if os.path.exists(output_file) and not overwrite:
        print(f'output file "{output_file}" already exists but --overwrite was not specified, exiting.')
        exit(-1)

    c = Cleaner()
    c.clean(root)

    tree.write(output_file, xml_declaration=True, default_namespace="", method="xml")

    print(
        f'{os.path.basename(input_file)}: Removed {c.removed} duplicates, reducing file size from {get_file_size(input_file)} to {get_file_size(output_file)}')


main()
