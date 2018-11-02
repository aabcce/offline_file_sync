IF  NOT EXIST %cd%\..\envwindows (
  echo Unzip envwindows.zip first.
  pause
)

@echo off


set python_executable=%cd%\..\envwindows\python-2.7.13\python.exe

echo "%python_executable% harness.py --task=backup"
%python_executable% harness.py --task=backup