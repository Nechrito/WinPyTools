import os
import sys

from typing import List

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

    def print_linebreak(self):
        text = "\n-----\n\n"
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

    def summarize(self):
        print(f"\n{'='*20}\nSUMMARY\n{'='*20}\n")

        self.depth_limit = self.depth_limit or '\u221e'
        self.line_limit = self.line_limit or '\u221e'
        self.word_limit = self.word_limit or '\u221e'

        print("Max depth: " + str(self.total_depth - 1) +
              "/" + str(self.depth_limit))
        print("Total line count: " + str(self.total_line_count) +
              "/" + str(self.line_limit))
        print("Total word count: " + str(self.total_words // 2) +
              "/" + str(self.word_limit // 2))

    def get_structure(self, directory, prefix="", blacklisted_dirs=None, whitelisted_filetypes: List[str] = None, depth: int = 0, lines: int = 0):

        self.total_depth = max(self.total_depth, depth)

        if (self.depth_limit and depth > self.depth_limit) or (self.word_limit and self.total_words >= self.word_limit):
            self.printer.print_linebreak()
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
                        self.printer.print_linebreak()
                        lines = 0

                    text = self.printer.print_directory(prefix, entry.name)
                    words = len(text.split(' '))
                    self.total_words += words
                    self.total_line_count += 1

                    self.get_structure(
                        entry.path, prefix + "│   ", blacklisted_dirs, whitelisted_filetypes, depth + 1, lines)

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
                    words = len(text.split(' '))
                    self.total_words += words
                    self.total_line_count += 1

                    if self.word_limit and self.total_words >= self.word_limit:
                        break

        return lines
    

if __name__ == "__main__":
    
    import print_to_json
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get the directory from the .env file
    directory_to_process: str | None = os.path.abspath(os.getenv("DIRECTORY_TO_PROCESS"))
    
    print(f"Constructed path: {directory_to_process}")  # Print the path to check it
    
    file_printer = FilePrinter()
    file_printer.print_directory("", directory_to_process)

    processor = FolderStructureProcessor(depth_limit=7, line_limit=None, word_limit=250000)
    processor.get_structure(directory_to_process, prefix='│   ', whitelisted_filetypes=[".cs"], depth=1, lines=0)

    # processor.summarize()

    # GPT-3 limits
    # 500 words input limit
    # 4,000 characters input limit

    # GPT-4 limits
    # 25,000 words limit
    # ??? characters input limit