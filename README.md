# WinPyTools

## About

This code is for productivity-boosting Python tools for Windows. The author believes that identifying bottlenecks and patching productivity flaws can make them more productive as a developer.

### Task Reminder

*This is a script to remind me to take a break*
*from coding and do some exercise.*

![Depressed Reminder](res/reminder%20comDepressed.gif)

### Build Commands

#### Setup

This command runs the setup script which installs the necessary packages for the project. This is only needed to be run once after cloning the project.
If the project is already cloned, then this command is not needed

```ps1
python setup.py install
```

#### Convert into an executable (.exe)

This set of commands is for converting the Python code into an executable (.exe) file. The first command installs the PyInstaller package which is used for creating standalone executables from Python scripts

```ps1
pip install pyinstaller
```

The second command converts the Python code into an executable (.exe) file.

```ps1
pyinstaller --onefile --noconsole --windowed --add-data="res;res" src/task_reminder.py
```

The third command moves the executable file into the main directory of the project.

```ps1
move dist\task_reminder.exe .
```

The fourth command removes the build files.

```ps1
# Powershell
Remove-Item -Recurse -Force .\build\

# Command Prompt
rmdir /s/q build
```

The fifth command removes the dist files.

```ps1
# Powershell
Remove-Item -Recurse -Force .\dist\

# Command Prompt
rmdir /s/q dist
```

## Credits

* [PyInstaller](https://www.pyinstaller.org/)
* [Python](https://www.python.org/)

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
