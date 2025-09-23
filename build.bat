@echo off
echo Creating application icon...
python utils/icon.py

echo Building executable...
python build.py

echo Done!
pause 