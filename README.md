# WinPyTools

This repository contains a collection of Python scripts for Windows automation and productivity. The scripts are designed to be executed from the command line and can be used to automate repetitive tasks, manage files and directories, and improve productivity.

The repo contains wildly different scripts for my personal use.

<!-- Showcase res/taskreminder.gif -->
[![Task Reminder](res/taskreminder.gif)](src/task_reminder.py)

## Installation

To install the required dependencies, run the following command:

```ps1
pip install -r requirements.txt
```

## Create executable

To create an executable, run the following command:

```ps1
pyinstaller --onefile --windowed setup.py --name "WinPyTools"
```

## File Tree

The file_tree.py module provides functionality to traverse and display the directory structure of a specified path. It includes classes to print files and directories with customizable options, and to process folder structures with limits on depth, lines, and words. The module also summarizes the traversal results.

### Usage

Execute the Script:

```ps1
python file_tree.py --directory path/to/directory --depth 3 --line 100 --word 500
```

### Example

```ps1
 py .\src\file_tree.py -dir "E:\Repos\WinPyTools\src\"
├── 📁 E:\Repos\WinPyTools\src\
├── 📄 controller.py
├── 📄 file_tree.py
├── 📄 hierarchy.py
├── 📄 open_file_in_vscode.py
├── 📄 pixel_art_analyzer.py
├── 📄 print_to_json.py
├── 📄 python-dotenv.py
├── 📄 save_paint3d_tabs.py
├── 📄 task_reminder.py
```

<!-- Heni -->

```plaintext

gggggggggggggggggggggggg
gggggggggbbbbbbggggggggg
ggggggggbbbbbbbbgggggggg
ggggggggbbbbbbbbgggggggg
ggggggghbmmbbmmbhggggggg
ggggggghbnibbinbhggggggg
ggggggggbbbhhbbbgggggggg
ggggggggbbmmmmbbgggggggg
ggggggggghmbbmhggggggggg
ggggggjjpkmhhmkpjjgggggg
gggggjjjpkkookkpjjjggggg
gggggjjjpkkookkpjjjggggg
gggggjjlpkkookkpljjggggg
gggggjjlpkkookkpljjggggg
gggggjjgkkkookkkgjjggggg
gggggjjgddkcckddgjjggggg
gggggjbbkkkffkkkbbjggggg
ggggggbhffffaaafhbgggggg
ggggggggfffggaafgggggggg
ggggggggfffggaafgggggggg
ggggggggfffggaafgggggggg
ggggggggfffggaafgggggggg
ggggggggfffggfffgggggggg
ggggggggeeeggeeegggggggg

```
