import os
import sys

import print_to_json

hide_directory_name = False
hide_file_name = False

def print_file(prefix: str, entry: str):
    if hide_file_name:
        entry = ""
        
    print(prefix + "├── 📄 " + entry)

def print_directory(prefix: str, entry: str):
    if hide_directory_name:
        entry = ""

    print(prefix + "├── 📁 " + entry)

def print_file_structure(directory, prefix="", blacklisted_dirs=None, whitelisted_filetypes: list[str] = None, chunk_size=None):
    printed_lines = 0
    
    with os.scandir(directory) as entries:
        sorted_entries = sorted(entries, key=lambda e: e.name.lower())

        for entry in sorted_entries:
            # Skip blacklisted directories and hidden files
            if blacklisted_dirs and entry.name in blacklisted_dirs or entry.name.startswith("."):
                continue

            try:
                if entry.is_dir():
                    if entry.is_dir() and chunk_size and printed_lines >= chunk_size:
                        print("\n-----\n\n")
                        printed_lines = 0
                        
                    print_directory(prefix, entry.name)
                    printed_lines += 1
                    
                    
                    printed_lines += print_file_structure(entry.path, prefix + "│   ", blacklisted_dirs, whitelisted_filetypes, chunk_size)
                else:
                    # Skip files not of whitelisted filetypes
                    if whitelisted_filetypes:
                        foundMatch = False
                        for filetype in whitelisted_filetypes:
                            if entry.name.endswith(filetype):
                                foundMatch = True
                                break

                        if not foundMatch:
                            continue
                    print_file(prefix, entry.name)
                    printed_lines += 1
                    
            except PermissionError as e:
                print(prefix + "├── 📄 " + entry.name + " (Permission Denied)")
                printed_lines += 1
                
            except FileNotFoundError as e:
                print(prefix + "├── 📄 " + entry.name + " (File Not Found)")
                printed_lines += 1
                
            except OSError as e:
                print(prefix + "├── 📄 " + entry.name + " (OS Error)")
                printed_lines += 1

            

    return printed_lines

if __name__ == "__main__":

    directory_to_scan = "The-Prophecy-of-Hank/HandyHank/Assets/HandyHank/Scripts"
    chunk_size = 30 # Adjust this value according to your needs

    print_directory("", directory_to_scan)
    
    print_file_structure(os.getcwd() + "../../" + directory_to_scan, prefix='│   ', whitelisted_filetypes=[".cs"], chunk_size=chunk_size)