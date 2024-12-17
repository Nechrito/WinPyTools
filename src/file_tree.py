import os

from typing import List


def print_linebreak():
    text = "\n-----\n\n"
    print(text)
    return text


class FilePrinter:
    def __init__(self, hide_directory_name=False, hide_file_name=False):
        self.hide_directory_name = hide_directory_name
        self.hide_file_name = hide_file_name

    def print_file(self, prefix: str, entry: str):
        if self.hide_file_name:
            entry = ""
        text = prefix + "├── 📄 " + entry
        print(text)
        return text

    def print_directory(self, prefix: str, entry: str):
        if self.hide_directory_name:
            entry = ""
        text = prefix + "├── 📁 " + entry
        print(text)
        return text


class FolderStructureProcessor:
    def __init__(self, depth_limit: int = None, line_limit: int = None, word_limit: int = 3159):
        self.printer = FilePrinter()

        self.depth_limit = depth_limit
        self.line_limit = line_limit
        self.word_limit = word_limit * 2

        self.total_depth = 0
        self.total_line_count = 1
        self.total_words = 0

    def summarize(self) -> object:
        print(f"\n{'=' * 20}\nSUMMARY\n{'=' * 20}\n")

        self.depth_limit = self.depth_limit or "\u221e"
        self.line_limit = self.line_limit or "\u221e"
        self.word_limit = self.word_limit or "\u221e"

        print("Max depth: " + str(self.total_depth - 1) + "/" + str(self.depth_limit))
        print("Total line count: " + str(self.total_line_count) + "/" + str(self.line_limit))
        print("Total word count: " + str(self.total_words // 2) + "/" + str(self.word_limit // 2))

    def get_structure(self, directory, prefix="", blacklisted_dirs=None, whitelisted_filetypes: List[str] = None, depth: int = 0, lines: int = 0):

        self.total_depth = max(self.total_depth, depth)

        if (self.depth_limit and depth > self.depth_limit) or (self.word_limit and self.total_words >= self.word_limit):
            print_linebreak()
            lines = 0
            return lines

        with os.scandir(directory) as entries:
            sorted_entries = sorted(entries, key=lambda e: e.name.lower())

            for entry in sorted_entries:

                # Skip blacklisted directories and hidden files
                if (blacklisted_dirs and entry.name in blacklisted_dirs) or entry.name.startswith("."):
                    continue

                if entry.is_dir():

                    if self.line_limit and lines >= self.line_limit:
                        print_linebreak()
                        lines = 0

                    text = self.printer.print_directory(prefix, entry.name)
                    words = len(text.split(" "))
                    self.total_words += words
                    self.total_line_count += 1

                    self.get_structure(entry.path, prefix + "│   ", blacklisted_dirs, whitelisted_filetypes, depth + 1, lines)

                    if self.word_limit and self.total_words >= self.word_limit:
                        break

                else:
                    # Skip files that are not of whitelisted filetypes
                    if whitelisted_filetypes:

                        foundMatch = False

                        for filetype in whitelisted_filetypes:
                            if entry.name.endswith(filetype):
                                foundMatch = True
                                break

                        if not foundMatch:
                            continue

                    text = self.printer.print_file(prefix, entry.name)
                    words = len(text.split(" "))
                    self.total_words += words
                    self.total_line_count += 1

                    if self.word_limit and self.total_words >= self.word_limit:
                        break

        return lines


import sys
import os
import argparse


def parse_arguments():
    directory = None
    depth_limit = 3
    line_limit = 100
    word_limit = 500

    blacklisted_dirs = ["node_modules", ".git"]
    whitelisted_filetypes = [".py", ".txt"]

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process a directory and print its structure")
    parser.add_argument("-directory", "-d", "-dir", type=str, help="Directory to process", required=True)
    parser.add_argument("-depth", type=int, help="Max depth to print")
    parser.add_argument("-lines", type=int, help="Max lines to print")
    parser.add_argument("-words", type=int, help="Max words to print")
    parser.add_argument("-blacklist", type=str, help="Comma-separated list of directories to blacklist")
    parser.add_argument("-whitelist", type=str, help="Comma-separated list of filetypes to whitelist")

    parser.add_help = True

    args = parser.parse_args()

    if args.directory:
        directory = args.directory
    if args.depth:
        depth_limit = args.depth
    if args.lines:
        line_limit = args.lines
    if args.words:
        word_limit = args.words
    if args.blacklist:
        blacklisted_dirs = args.blacklist.split(",")
    if args.whitelist:
        whitelisted_filetypes = args.whitelist.split(",")

    return directory, depth_limit, line_limit, word_limit, blacklisted_dirs, whitelisted_filetypes


def main():
    directory, depth_limit, line_limit, word_limit, blacklisted_dirs, whitelisted_filetypes = parse_arguments()

    if not directory:
        print("No directory provided")
        sys.exit(1)

    file_printer = FilePrinter()
    file_printer.print_directory("", directory)

    processor = FolderStructureProcessor(depth_limit, line_limit, word_limit)
    processor.get_structure(directory, blacklisted_dirs=blacklisted_dirs, whitelisted_filetypes=whitelisted_filetypes)
    processor.summarize()


if __name__ == "__main__":
    main()
