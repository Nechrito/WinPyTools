@echo off
echo Installing necessary packages...
@REM python setup.py install
python -m pip install -r requirements.txt
echo.
echo Converting Python code into an executable...
pip install pyinstaller
pyinstaller --onefile --noconsole --windowed src/task_reminder.py
move dist\task_reminder.exe .
move src\dist\task_reminder.exe .

echo.
echo Cleaning up build files...
if exist build (
    powershell -Command "Remove-Item -Recurse -Force '.\build\'"
) else (
    rmdir /s/q build
)
echo.
echo Cleaning up dist files...
if exist dist (
    powershell -Command "Remove-Item -Recurse -Force '.\dist\'"
) else (
    rmdir /s/q dist
)
echo.

if exist  (
    powershell -Command "Remove-Item -Recurse -Force '.\*.spec\'"
) else (
    rmdir /s/q *.spec
)
echo.
echo Cleaning up __pycache__ files...
if exist __pycache__ (
    powershell -Command "Remove-Item -Recurse -Force '.\__pycache__\'"
) else (
    rmdir /s/q __pycache__
)
echo.
echo Cleaning up .pyc files...
if exist *.pyc (
    powershell -Command "Remove-Item -Recurse -Force '.\*.pyc\'"
) else (
    rmdir /s/q *.pyc
)
echo.
echo Cleaning up .pyo files...
if exist *.pyo (
    powershell -Command "Remove-Item -Recurse -Force '.\*.pyo\'"
) else (
    rmdir /s/q *.pyo
)
echo.
echo Cleaning up .ipynb_checkpoints files...
if exist .ipynb_checkpoints (
    powershell -Command "Remove-Item -Recurse -Force '.\.ipynb_checkpoints\'"
) else (
    rmdir /s/q .ipynb_checkpoints
)
echo.
echo Cleaning up .pytest_cache files...
if exist .pytest_cache (
    powershell -Command "Remove-Item -Recurse -Force '.\.pytest_cache\'"
) else (
    rmdir /s/q .pytest_cache
)
echo.
echo Cleaning up .eggs files...
if exist .eggs (
    powershell -Command "Remove-Item -Recurse -Force '.\.eggs\'"
) else (
    rmdir /s/q .eggs
)
echo.
echo Cleaning up .ipynb files...
if exist *.ipynb (
    powershell -Command "Remove-Item -Recurse -Force '.\*.ipynb\'"
) else (
    rmdir /s/q *.ipynb
)
echo.
echo Task reminder executable created successfully!
pause
