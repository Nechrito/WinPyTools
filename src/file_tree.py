import os

def print_file_structure(directory, prefix="", blacklisted_dirs=None):
    if blacklisted_dirs is None:
        blacklisted_dirs = []
    
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.name in blacklisted_dirs or entry.name.startswith("."):
                continue
            
            if entry.is_dir():
                print(prefix + "├── 📁 " + entry.name)
                print_file_structure(entry.path, prefix + "│   ", blacklisted_dirs)
            else:
                print(prefix + "├── 📄 " + entry.name)

if __name__ == "__main__":
    print("📁 " + os.path.basename(os.getcwd()))
    print_file_structure(os.getcwd(), "", ["venv", "dist", "build", "tests"])
    print("")
    print("--------------------")
    print("")
    print_file_structure(os.getcwd(), "WinPyTools ")
    print("")
    print("--------------------")
    print("")
    print_file_structure("src", "src ")
    