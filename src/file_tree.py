import os
import sys

from typing import List

import print_to_json
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
    def __init__(self, depth_limit: int=None, line_limit: int=None, word_limit: int=3159):
        self.printer = FilePrinter()
        
        self.depth_limit = depth_limit
        self.line_limit = line_limit
        self.word_limit = word_limit
        
        self.total_depth_count = 0
        self.total_line_count = 0
        self.total_word_count = 0
        
    def summarize(self):
        print(f"\n\n ----- SUMMARY ----- \n")
        
        print("Total depth count: " + str(self.total_depth_count))
        print("Total line count: " + str(self.total_line_count))
        print("Total word count: " + str(self.total_word_count))

    def get_structure(self, directory, prefix="", blacklisted_dirs=None, whitelisted_filetypes: List[str] = None, depth: int=0, lines: int=0, words: int=0):
        printed_lines = 0
        word_count = 0

        # Use 'self' to access instance variables
        self.total_depth_count += depth
        self.total_line_count += lines
        self.total_word_count += words

        if self.word_limit and self.total_word_count >= self.word_limit:
            return printed_lines, word_count

        with os.scandir(directory) as entries:
            sorted_entries = sorted(entries, key=lambda e: e.name.lower())

            for entry in sorted_entries:
                # Skip blacklisted directories and hidden files
                if blacklisted_dirs and entry.name in blacklisted_dirs or entry.name.startswith("."):
                    continue

                if entry.is_dir():
                    if self.depth_limit and depth > self.depth_limit:
                        return printed_lines, word_count

                    if self.line_limit and printed_lines >= self.line_limit:
                        print("\n-----\n\n")
                        printed_lines = 0

                    text = self.printer.print_directory(prefix, entry.name)

                    printed_lines += 1

                    word_count = len(text.split(' '))

                    printed_lines_sub, word_count_sub = self.get_structure(entry.path, prefix + "│   ", blacklisted_dirs, whitelisted_filetypes, depth + 1)

                    word_count += word_count_sub
                    printed_lines += printed_lines_sub

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

                    printed_lines += 1

                    word_count = len(text.split(' '))


        return printed_lines, word_count

if __name__ == "__main__":
    
    # directory_to_scan = os.path.join(os.getcwd(), directory_to_scan)
    directory_to_process = "The-Prophecy-of-Hank/HandyHank/Assets/HandyHank/Scripts"
    
    file_printer = FilePrinter()
    file_printer.print_directory("", directory_to_process)

    directory_to_scan = os.getcwd() + "../../" + directory_to_process

    processor = FolderStructureProcessor(depth_limit=3, line_limit=20, word_limit=1000)
    printed_lines, word_count = processor.get_structure(directory_to_scan, prefix='│   ', whitelisted_filetypes=[".cs"], depth=0, lines=0, words=0)

    processor.summarize()